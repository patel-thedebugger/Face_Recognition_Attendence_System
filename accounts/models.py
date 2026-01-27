import uuid
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    roll_no = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)

    branch = models.ForeignKey(
        'attendence.Branch',
        on_delete=models.SET_NULL,
        null=True
    )

    batch = models.ForeignKey(
        'attendence.Batch',
        on_delete=models.SET_NULL,
        null=True
    )
    semester = models.ForeignKey(
        'attendence.Semester',
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return self.roll_no


class Faculty(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)

    branch = models.ForeignKey(
        'attendence.Branch',
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self):
        return self.email

