from email.headerregistry import Group
from urllib import request
from django.http import HttpResponse, JsonResponse
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from attendence.models import Branch
from accounts.models import Faculty , Student
from django.contrib.auth.models import User, Group
from attendence.models import Subject, Lab, Batch, Semester

# Create your views here.
def home_view(request):
    return render(request, 'home.html')

def FacultyLogin_view(request):
    return render(request, 'Faculty/Login.html')

def StudentLogin_view(request):
    return render(request, 'Student/Login.html')

def AdminDashboard_view(request):
    return render(request, 'Admin/Admin_Dashboard.html', {
        'Branch': Branch.objects.all(),
        'Semesters': Semester.objects.all(),
        'Subjects': Subject.objects.all(),
        'Batches': Batch.objects.all(),
        'Faculty': Faculty.objects.all(),
        'Students': Student.objects.all(),
        'Labs': Lab.objects.all(),
    })

def register_student(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        roll = request.POST.get('roll_no')
        phone = request.POST.get('phone')
        semester_id = request.POST.get('semester')
        branch_id = request.POST.get('branch')
        batch_id = request.POST.get('batch')

        print(request.POST)

        if not roll:
            return HttpResponse("Roll number missing")
        
        if User.objects.filter(username=roll).exists():
            messages.error(request, "Student with this Roll Number already exists!")
            return redirect('AdminDashboard_view')

        if Student.objects.filter(roll_no=roll).exists():
            messages.error(request, "Student profile already exists!")
            return redirect('AdminDashboard_view')
        
        # ✅ Create user
        user = User.objects.create_user(
            username=roll,
            email=email,
            password=phone
        )
        user.save()
        # Assign Student group

        group = Group.objects.get(name="Student")
        user.groups.add(group)

        # Create Student profile
        Student.objects.create(
            user=user,
            roll_no=roll,
            name=name,
            email=email,
            phone_number=phone,
            semester_id=semester_id,
            branch_id=branch_id,
            batch_id=batch_id
        )

        
    return redirect('AdminDashboard_view')

def get_subjects_by_semester(request):
    sem_id = request.GET.get('semester_id')

    subjects = Subject.objects.filter(semester_id=sem_id)

    data = []
    for s in subjects:
        data.append({
            'id': s.id,
            'code': s.subject_code,
            'name': s.subject_name,
            'credits': s.credits,
            'type': s.get_subject_type_display()
        })

    return JsonResponse(data, safe=False)


@transaction.atomic
def register_faculty(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        branch_id = request.POST.get("branch")
        branch = Branch.objects.get(id=branch_id)
        print(request.POST) 
        
        # Check duplicate user
        if User.objects.filter(username=email).exists():
            messages.error(request, "Faculty with this email already exists.")
            return redirect("register_faculty")
        
        # Create User
        user = User.objects.create_user(
            username=email,
            email=email,
            password=phone
        )
        user.is_staff = True
        user.save()

        # Create Faculty
        Faculty.objects.create(
            user=user,
            name=name,
            email=email,
            phone_number=phone,
            branch=branch
        )

        faculty_group = Group.objects.get(name="Faculty")
        user.groups.add(faculty_group)


        messages.success(
            request,
            f"Faculty created successfully. Login with {email}"
        )
    return redirect("AdminDashboard_view")

def get_initials(text):
    return "".join(word[0].upper() for word in text.split() if word[0].isalpha())

def to_roman(num):
    roman_map = {
        1: "I", 2: "II", 3: "III", 4: "IV",
        5: "V", 6: "VI", 7: "VII", 8: "VIII"
    }
    return roman_map.get(num, str(num))


def add_subject(request):
    semesters = Semester.objects.all()

    if request.method == "POST":
        code = request.POST.get("subject_code")
        name = request.POST.get("subject_name")
        semester_id = request.POST.get("semester")
        subject_type = request.POST.get("subject_type")

        print(request.POST)

        semester = Semester.objects.get(id=semester_id)

        subject = Subject.objects.create(
            subject_code=code,
            subject_name=name,
            semester=semester,
            subject_type=subject_type
        )

        # 🔥 AUTO CREATE LABS
        if subject_type in ["lab", "theory_lab"]:

            batches = Batch.objects.filter(semester=semester)
            initials = get_initials(subject.subject_name)
            roman_sem = to_roman(semester.semester_number)
            for batch in batches:
                Lab.objects.create(
                    subject=subject,
                    batch=batch,
                    lab_name=f"{initials}- {roman_sem} sem- {batch.batch_name} Lab"
                )

        messages.success(request, "Subject created successfully!")

    return redirect("AdminDashboard_view")

def subject_list(request):
    subjects = Subject.objects.select_related("semester").all()
    semesters = Semester.objects.all()
    return redirect("AdminDashboard_view")


def edit_subject(request, id):
    subject = get_object_or_404(Subject, id=id)
    if request.method == "POST":

        print(request.POST)

        old_type = subject.subject_type
        subject.subject_code = request.POST.get("subject_code")
        subject.subject_name = request.POST.get("subject_name")
        subject.credits = request.POST.get("credits")
        subject.subject_type = request.POST.get("subject_type")
        subject.semester_id = request.POST.get("semester")
        subject.save()

        if subject.subject_type == "theory" and old_type in ["lab", "theory_lab"]:
            Lab.objects.filter(subject=subject).delete()

        # 🔥 LAB CREATION IF CHANGED TO LAB TYPE
        if subject.subject_type in ["lab", "theory_lab"] and old_type == "theory":
            batches = Batch.objects.filter(semester=subject.semester)

            def get_initials(text):
                return "".join(word[0].upper() for word in text.split())

            def to_roman(num):
                roman_map = {1:"I",2:"II",3:"III",4:"IV",5:"V",6:"VI",7:"VII",8:"VIII"}
                return roman_map.get(num, str(num))

            initials = get_initials(subject.subject_name)
            roman_sem = to_roman(subject.semester.semester_number)

            for batch in batches:
                Lab.objects.create(
                    subject=subject,
                    batch=batch,
                    lab_name=f"{initials} - Sem {roman_sem} - {batch.batch_name} Lab"
                )


        messages.success(request, "Subject updated successfully!")
        return redirect("AdminDashboard_view")

def delete_subject(request, id):
    subject = get_object_or_404(Subject, id=id)
    subject.delete()  # Labs auto deleted (CASCADE)
    messages.success(request, "Subject deleted!")
    return redirect("AdminDashboard_view")
    