import re
from django.http import JsonResponse
from django.shortcuts import render
from accounts.models import Faculty,Student
from django.contrib import messages
from django.shortcuts import redirect
from .models import Lab, Batch, StudentSubject , Subject, FacultySubject
from accounts.views import *

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
        print("Students found:", students.count())
        assigned_count = 0

        for student in students:
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
        return redirect('adminDashboard_view')
