"""
URL configuration for FaceRecongnitionAttendenceSystem project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from accounts.views import *
from attendence.views import *

urlpatterns = [
    path('', home_view, name='home'),
    path('Faculty/Login/', FacultyLogin_view, name='FacultyLogin_view'),
    path('Faculty/', FacultyDashboard_view, name='FacultyDashboard_view'),
    path("Faculty/subjects/", get_faculty_subjects, name="faculty_subjects"),
    path('Faculty/logout/', faculty_logout, name='faculty_logout'),


    path('Student/', StudentLogin_view, name='StudentLogin_view'),
    path('Student/Dashboard/', StudentDash_view, name='StudentDash_view'),
    path("Faculty/students/", get_students_for_subject, name="get_students"),
    path('Student/logout/', student_logout, name='student_logout'),
    
    path('Admin/', AdminDashboard_view, name='AdminDashboard_view'),
    path('Admin/Login/', adminlogin_view, name='adminlogin_view'),
    path('Admin/Faculty/Register/', register_faculty, name='register_faculty'),
    path('Admin/Subject/Add/', add_subject, name='add_subject'),
    path("Admin/Subjects/Edit/<int:id>/", edit_subject, name="edit_subject"),
    path("Admin/Subjects/Delete/<int:id>/", delete_subject, name="delete_subject"),
    path('Admin/Login/Submit/', adminloginsubmit_view, name='adminloginsubmit_view'),

    path('ajax/get-subjects/', get_subjects_by_semester, name='get_subjects'),
    path('ajax/get-faculty-subjects/', get_faculty_subject_list, name='get_faculty_subjects_list'),
    path('Admin/Student/Register/', register_student, name='register_student'),
    path('ajax/get-labs/<int:semester_id>/', get_labs_by_semester, name='get_labs_by_semester'),
    path('register/', register_view, name='Register'),
    path('Admin/link-faculty-subject/', link_faculty_subject, name='link_faculty_subject'),
    path('Admin/enroll-students-subjects/', enroll_students_subjects, name='enroll_students_subjects'),
    path('ajax/get-student-enrollments/', get_student_enrollments, name='get_student_enrollments'),
    path('ajax/get-student-subjects/<int:student_id>/', get_student_subjects, name='get_student_subjects'),
    path('ajax/delete-enrollment/<int:enrollment_id>/', delete_enrollment, name='delete_enrollment'),
    path('ajax/faculty-subjects/<int:faculty_id>/', get_faculty_subjects, name='get_faculty_subjects'),
    path('ajax/delete-faculty-subject/<int:fs_id>/', delete_faculty_subject, name='delete_faculty_subject'),
    path('auto-import-students/', bulk_register_students_auto, name='bulk_register_students_auto'),

    path('admin/', admin.site.urls),
]
