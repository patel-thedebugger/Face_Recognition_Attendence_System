import csv
import re
from django.http import JsonResponse
from django.shortcuts import render
import requests
from accounts.models import Faculty,Student
from django.contrib import messages
from django.shortcuts import redirect
from .models import Lab, Batch, StudentSubject , Subject, FacultySubject
from accounts.views import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET

# Create your views here.

def get_labs_by_semester(request, semester_id):
    batchs = Batch.objects.filter(semester_id=semester_id)

    data = {
        "batchs": [
            {"id": batch.id, "name": batch.batch_name}
            for batch in batchs
        ]
    }
    return JsonResponse(data)

def get_faculty_subject_list(request):
    faculty_subjects = FacultySubject.objects.select_related(
        'faculty', 'subject', 'batch'
    )

    faculty_map = {}

    for fs in faculty_subjects:
        faculty = fs.faculty

        if faculty.id not in faculty_map:
            faculty_map[faculty.id] = {
                "id": f"{get_initials(faculty.branch.branch_name)}_{faculty.id}",
                "ID": faculty.id,
                "name": faculty.name,
                "branch": faculty.branch.branch_name,
                "subjects": []
            }

        if fs.session_type == "theory":
            label = f"{get_initials(fs.subject.subject_name)} "+"(T)"
        elif fs.session_type == "lab" and fs.batch:
            label = f"{get_initials(fs.subject.subject_name)} ({fs.batch.batch_name})"
        else:
            label = f"{get_initials(fs.subject.subject_name)} (No Batch)"
        
        faculty_map[faculty.id]["subjects"].append(label)

    return JsonResponse({
        "faculty_data": list(faculty_map.values())
    })

def link_faculty_subject(request):


    if request.method == "POST":
        print(request.POST)
        faculty_id = request.POST.get('faculty_id')
        subject_ids = request.POST.getlist('subjects')
        session_type = request.POST.get('session_type')
        batch_id = request.POST.get('batch_id')

        faculty = Faculty.objects.get(id=faculty_id)
        batch = Batch.objects.get(id=batch_id) if batch_id else None
        print(batch_id ,"   ", batch)
        for subject_id in subject_ids:
            subject = Subject.objects.get(id=subject_id)

            try:
                if(batch_id is None):
                    if(subject.subject_type == 'lab'):
                        messages.error(request, f"Batch must be selected for lab subject: {subject.subject_name}")
                        return redirect('AdminDashboard_view')
                    else:
                        batch = None

                FacultySubject.objects.create(
                    faculty=faculty,
                    subject=subject,
                    batch=batch,
                    session_type=session_type
                )
            except Exception as e:
                print(f"Error linking {subject.subject_name}: {str(e)}")
                messages.error(request, f"Error for {subject.subject_name}: {str(e)}")
                return redirect('AdminDashboard_view')
        print("Subjects linked successfully!")
        messages.success(request, "Subjects linked successfully!")
        return redirect('AdminDashboard_view')
    
def enroll_students_subjects(request):
    print(request.POST)
    if request.method == "POST":
        semester_id = request.POST.get("semester_id")
        range_input = request.POST.get("student_range")
        subject_ids = request.POST.getlist("subjects")

        # Match pattern: 12302130501001-90
        match = re.match(r"(\d+)(\d{3})-(\d+)", range_input)

        if not match:
            messages.error(request, "Invalid format. Use 12302130501001-90")
            return redirect('your_page')

        prefix = match.group(1)      # 12302130501
        start = int(match.group(2))  # 001
        end = int(match.group(3))    # 90

        student_ids = [
            f"{prefix}{str(i).zfill(3)}" for i in range(start, end + 1)
        ]
        print("Generated Student IDs:", student_ids)
        students = Student.objects.filter(roll_no__in=student_ids)
        print(students)
        print("Students found:", students.count())
        assigned_count = 0

        for student in students:
            if student.semester.id != int(semester_id):
                print(f"Skipping {student.roll_no}: Semester mismatch.")
                continue
            for subject_id in subject_ids:
                subject = Subject.objects.get(id=subject_id)

                # 🔹 THEORY ONLY SUBJECT
                if subject.is_theory_only:
                    StudentSubject.objects.get_or_create(
                        student=student,
                        subject=subject,
                        batch=None,
                        session_type='theory'
                    )

                # 🔹 LAB ONLY SUBJECT
                elif subject.is_lab_only:
                    batch = Batch.objects.filter(semester_id=semester_id).first()
                    StudentSubject.objects.get_or_create(
                        student=student,
                        subject=subject,
                        batch=batch,
                        session_type='lab'
                    )

                # 🔹 BOTH THEORY + LAB SUBJECT
                else:
                    # Theory entry
                    StudentSubject.objects.get_or_create(
                        student=student,
                        subject=subject,
                        batch=None,
                        session_type='theory'
                    )

                    # Lab entry
                    batch = Batch.objects.filter(semester_id=semester_id).first()
                    StudentSubject.objects.get_or_create(
                        student=student,
                        subject=subject,
                        batch=batch,
                        session_type='lab'
                    )

                
                assigned_count += 1
        print(f"{assigned_count} enrollments created successfully!")
        messages.success(request, f"{assigned_count} enrollments created successfully!")
        return redirect('AdminDashboard_view')

def get_student_enrollments(request):
    enrollments = StudentSubject.objects.select_related(
        'student', 'subject'
    )

    student_map = {}

    for e in enrollments:
        s = e.student

        if s.id not in student_map:
            student_map[s.id] = {
                "id": s.id,
                "name": s.name,
                "roll": s.roll_no,
                "semester": s.semester.semester_number,
                "section": f"{s.branch.branch_code} - {s.batch.batch_name} Batch",
                "subjects": set()
            }

        student_map[s.id]["subjects"].add(
            get_initials(e.subject.subject_name)
        )
    
    for student in student_map.values():
        student["subjects"] = list(student["subjects"])

    return JsonResponse({"students": list(student_map.values())})

def get_student_subjects(request, student_id):
    enrollments = StudentSubject.objects.filter(student_id=student_id).select_related('subject')

    data = {
        "name": enrollments.first().student.name,
        "roll": enrollments.first().student.roll_no,
        "subjects": []
    }

    for e in enrollments:
        data["subjects"].append({
            "name": get_initials(e.subject.subject_name),
            "session_type": e.session_type,
            "enrollment_id": e.id
        })

    return JsonResponse(data)

def delete_enrollment(request, enrollment_id):
    e = StudentSubject.objects.get(id=enrollment_id)
    student_id = e.student.id
    e.delete()
    return JsonResponse({"success": True, "student_id": student_id})

def get_faculty_subjects(request, faculty_id):

    qs = FacultySubject.objects.filter(faculty_id=faculty_id).select_related('subject','batch','faculty')

    first = qs.first()
    data = {
        "name": first.faculty.name if first else "",
        "code": first.faculty.id if first else "",
        "subjects": []
    }

    for e in qs:
        data["subjects"].append({
            "id": e.id,
            "subject_code": e.subject.subject_code,
            "subject_name": get_initials(e.subject.subject_name),
            "session_type": e.session_type,
            "batch": e.batch.batch_name if e.batch else None
        })

    return JsonResponse(data)

def delete_faculty_subject(request, fs_id):
    FacultySubject.objects.filter(id=fs_id).delete()
    return JsonResponse({"success": True})

@require_GET
@csrf_exempt
def bulk_register_students_auto(request):

    SHEET_URL = "https://docs.google.com/spreadsheets/d/1nIkWXwaZA5Hrt906mykupHvEfdF2ZUAlw4PvlW8OzkU/export?format=csv"

    try:
        response = requests.get(SHEET_URL)
        response.raise_for_status()
    except Exception as e:
        return JsonResponse({"status": "error", "message": "Failed to fetch Google Sheet"})

    decoded = response.content.decode('utf-8').splitlines()
    reader = csv.DictReader(decoded)

    count = 0
    skipped = 0

    for row in reader:
        try:
            semester = Semester.objects.get(semester_number=row['Semester'])
            branch = Branch.objects.get(branch_code=row['Branch'])
            batch = Batch.objects.get(batch_name=row['Batch'], semester=semester)

            roll = row['Enrollment Number']
            name = row['Full Name']
            email = row['College Email_id']
            phone = row['Phone Number']

            if User.objects.filter(username=roll).exists():
                skipped += 1
                continue

            user = User.objects.create_user(
                username=roll,
                email=email,
                password=phone
            )

            group = Group.objects.get(name="Student")
            user.groups.add(group)

            Student.objects.get_or_create(
                roll_no=roll,
                defaults={
                    'user': user,
                    'name': name,
                    'email': email,
                    'phone_number': phone,
                    'semester': semester,
                    'branch': branch,
                    'batch': batch
                }
            )

            count += 1

        except Exception as e:
            print("Row error:", e)

    return JsonResponse({
        "status": "success",
        "message": f"{count} students imported, {skipped} skipped (already exist)"
    })

@login_required
# def get_faculty_subjects(request):
#     session_type = request.GET.get("session_type")
#     faculty = Faculty.objects.get(user=request.user)

#     qs = FacultySubject.objects.filter(
#         faculty=faculty,
#         session_type=session_type
#     ).select_related("subject", "batch")

#     data = []
#     for fs in qs:
#         label = fs.subject.subject_name
#         if fs.session_type == "lab":
#             label += f" ({fs.batch.batch_name})"

#         data.append({
#             "id": fs.id,   # IMPORTANT
#             "label": label,
#         })

#     return JsonResponse({"subjects": data})

@login_required
def get_students_for_subject(request):
    fs_id = request.GET.get("faculty_subject_id")

    if not fs_id:
        return JsonResponse({"students": []})

    faculty = Faculty.objects.get(user=request.user)

    fs = FacultySubject.objects.select_related(
        "subject", "batch"
    ).get(id=fs_id, faculty=faculty)

    # 🔥 MAIN FILTER
    students_qs = StudentSubject.objects.filter(
        subject=fs.subject,
        session_type=fs.session_type
    )

    # Lab → batch required
    if fs.session_type == "lab":
        students_qs = students_qs.filter(batch=fs.batch)

    data = []
    for ss in students_qs.select_related("student"):
        data.append({
            "id": ss.student.id,
            "roll": ss.student.enrollment_no,
            "name": ss.student.name,
        })

    return JsonResponse({"students": data})

def delete_faculty(request, faculty_id):
    print("Deleting faculty with ID:", faculty_id)
    Faculty.objects.filter(id=faculty_id).delete()
    return JsonResponse({"success": True})