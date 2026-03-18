from django.db import models
from attendence.models import Subject, Batch
from accounts.models import Student, Faculty


class FaceEmbedding(models.Model):

    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        related_name="face_embedding"
    )

    embedding = models.BinaryField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"FaceEmbedding - {self.student.roll_no}"


class RecognitionLog(models.Model):

    SESSION_CHOICES = [
        ('theory', 'Theory'),
        ('lab', 'Lab')
    ]

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.CASCADE
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE
    )

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

    image = models.ImageField(
        upload_to="attendance_images/"
    )

    recognized_students = models.ManyToManyField(
        Student,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject.subject_code} - {self.created_at}"