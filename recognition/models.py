from django.db import models


class FaceEmbedding(models.Model):
    student = models.ForeignKey(
        'accounts.Student',
        on_delete=models.CASCADE,
        related_name='embeddings'
    )

    embedding_vector = models.BinaryField()
    model_version = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Embedding - {self.student.roll_no}"
