from django.http import JsonResponse
from django.shortcuts import render

from .models import Lab, Batch

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