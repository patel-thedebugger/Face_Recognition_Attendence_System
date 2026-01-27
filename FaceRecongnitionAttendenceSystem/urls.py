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
    path('Faculty/', FacultyLogin_view, name='FacultyLogin_view'),
    path('Student/', StudentLogin_view, name='StudentLogin_view'),
    path('Admin/', AdminDashboard_view, name='AdminDashboard_view'),
    path('Admin/Faculty/Register/', register_faculty, name='register_faculty'),
    path('Admin/Subject/Add/', add_subject, name='add_subject'),
    path("Admin/Subjects/Edit/<int:id>/", edit_subject, name="edit_subject"),
    path("Admin/Subjects/Delete/<int:id>/", delete_subject, name="delete_subject"),
    path('ajax/get-subjects/', get_subjects_by_semester, name='get_subjects'),
    path('Admin/Student/Register/', register_student, name='register_student'),
    path('get-labs/<int:semester_id>/', get_labs_by_semester, name='get_labs_by_semester'),


    path('admin/', admin.site.urls),
]
