from django.db import models
from django.contrib.auth.models import User
from django.db.models import CheckConstraint, Q
from django.forms import ValidationError
from django.core.exceptions import ValidationError
from FaceRecongnitionAttendenceSystem import *
from django.db import transaction


class Semester(models.Model):
    semester_number = models.IntegerField()

    def __str__(self):
        return f"Sem {self.semester_number}"

class Branch(models.Model):
    branch_code = models.CharField(max_length=10, unique=True)
    branch_name = models.CharField(max_length=100)

    def __str__(self):
        return self.branch_code

class Batch(models.Model):
    batch_name = models.CharField(max_length=50)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    def __str__(self):
        return self.batch_name

class Subject(models.Model):
    SUBJECT_TYPE_CHOICES = [
        ('theory', 'Theory Only'),
        ('lab', 'Lab Only'),
        ('theory_lab', 'Theory + Lab'),
    ]
    credits = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)],
        default=3
    )
    subject_code = models.CharField(max_length=20, unique=True)
    subject_name = models.CharField(max_length=100)
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)

    subject_type = models.CharField(
        max_length=20,
        choices=SUBJECT_TYPE_CHOICES,
        default='theory_lab'
    )

    # -------- HELPERS --------
    @property
    def is_theory_only(self):
        return self.subject_type == 'theory'

    @property
    def is_lab_only(self):
        return self.subject_type == 'lab'

    @property
    def has_theory_and_lab(self):
        return self.subject_type == 'theory_lab'

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"

class Lab(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name='labs'
    )

    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        related_name='labs',
        null=True,
        blank=True
    )

    lab_name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('subject', 'batch')

    def clean(self):
        # ❌ Lab not allowed for theory-only subjects
        if self.subject.subject_type == 'theory':
            raise ValidationError(
                "Cannot create lab for a theory-only subject."
            )

        # ❌ Batch semester must match subject semester
        if self.batch.semester != self.subject.semester:
            raise ValidationError(
                "Lab batch semester must match subject semester."
            )

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.lab_name} - {self.subject.subject_code} ({self.batch})"

class FacultySubject(models.Model):
    SESSION_CHOICES = [
        ('theory', 'Theory'),
        ('lab', 'Lab'),
    ]

    faculty = models.ForeignKey(
        'accounts.Faculty',
        on_delete=models.CASCADE
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    # Batch is REQUIRED only for lab
    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        null=True,
        default=None,
        blank=True
    )

    session_type = models.CharField(
        max_length=10,
        choices=SESSION_CHOICES
    )

    class Meta:
        constraints = [
            CheckConstraint(
                condition=(
                    Q(session_type='theory', batch__isnull=True) |
                    Q(session_type='lab', batch__isnull=False)
                ),
                name='faculty_batch_required_for_lab'
            )
        ]

    def clean(self):
        # Subject-type enforcement
        if self.subject.is_theory_only and self.session_type != 'theory':
            raise ValidationError("Theory-only subject allows THEORY session only.")

        if self.subject.is_lab_only and self.session_type != 'lab':
            raise ValidationError("Lab-only subject allows LAB session only.")

        # Batch rules
        if self.session_type == 'lab' and not self.batch:
            raise ValidationError("Batch is required for LAB sessions.")

        if self.session_type == 'theory' and self.batch:
            raise ValidationError("Batch must NOT be set for THEORY sessions.")

        # Semester consistency
        if self.batch and self.batch.semester != self.subject.semester:
            raise ValidationError("Batch semester must match subject semester.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.session_type == 'lab':
            return f"{self.faculty} → {self.subject} (Lab - {self.batch})"
        return f"{self.faculty} → {self.subject} (Theory)"

class StudentSubject(models.Model):
    SESSION_CHOICES = [
        ('theory', 'Theory'),
        ('lab', 'Lab'),
        ('both', 'Both'),
    ]

    student = models.ForeignKey(
        'accounts.Student',
        on_delete=models.CASCADE
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

    # Batch required ONLY for lab
    batch = models.ForeignKey(
        Batch,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    session_type = models.CharField(
        max_length=10,
        choices=SESSION_CHOICES
    )

    class Meta:
        unique_together = ('student', 'subject', 'batch', 'session_type')

    def clean(self):
        # Subject-type enforcement
        if self.subject.is_theory_only and self.session_type != 'theory':
            raise ValidationError("Student can enroll only in THEORY session.")

        if self.subject.is_lab_only and self.session_type != 'lab':
            raise ValidationError("Student can enroll only in LAB session.")

        # Batch rules
        if self.session_type == 'lab' and not self.batch:
            raise ValidationError("Batch is required for LAB enrollment.")

        if self.session_type == 'theory' and self.batch:
            raise ValidationError("Batch must NOT be set for THEORY enrollment.")

        # Semester consistency
        if self.batch and self.batch.semester != self.subject.semester:
            raise ValidationError("Batch semester must match subject semester.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.session_type == 'lab':
            return f"{self.student} → {self.subject} (Lab - {self.batch})"
        return f"{self.student} → {self.subject} (Theory)"

class Attendance(models.Model):
    SESSION_CHOICES = [
        ('theory', 'Theory'),
        ('lab', 'Lab'),
    ]
    student = models.ForeignKey(
        'accounts.Student', on_delete=models.CASCADE
    )
    faculty = models.ForeignKey(
        'accounts.Faculty', on_delete=models.CASCADE
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)

    session_type = models.CharField(max_length=10, choices=SESSION_CHOICES)
    date = models.DateField()
    status = models.CharField(
        max_length=10,
        choices=[('present', 'Present'), ('absent', 'Absent')]
    )

    def __str__(self):
        return f"{self.student.roll_no} - {self.date}"
