import os
import cv2
import numpy as np

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from insightface.app import FaceAnalysis


# Path to embeddings database
EMBEDDING_FILE = os.path.join("recognition", "embeddings.npy")

# data = np.load("recognition/embeddings.npy", allow_pickle=True).item()

# for k, v in data.items():
#     print(k, v.shape, v.dtype)
#     break
# Initialize RetinaFace + ArcFace
face_app = FaceAnalysis(name="buffalo_l")
face_app.prepare(ctx_id=0)   # Use GPU (ctx_id=0) if available, otherwise set to -1 for CPU


@login_required
@require_POST
# @csrf_exempt
def process_attendance(request):

    image_file = request.FILES.get("image")

    if not image_file:
        return JsonResponse({"error": "No image uploaded"}, status=400)

    # Load embeddings database
    database = np.load(EMBEDDING_FILE, allow_pickle=True).item()

    # Convert uploaded image to OpenCV format
    image_array = np.frombuffer(image_file.read(), np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    # Detect faces using RetinaFace
    faces = face_app.get(image)
    print(f"Detected {len(faces)} faces in the uploaded image.")
    # print("Database sample:")
    # for k, v in database.items():
    #     print(k, type(v), len(v))
    #     print("First embedding shape:", np.array(v[0]).shape)
    
    recognized_students = []

    for face in faces:

        embedding = face.embedding.astype(np.float32).flatten()
        embedding = embedding / np.linalg.norm(embedding)

        best_match = None
        best_score = -1

        for student_id, db_embedding in database.items():

            # Ensure correct format
            db_embedding = np.array(db_embedding, dtype=np.float32).flatten()

            # Skip invalid
            if db_embedding.shape[0] != 512:
                continue

            db_embedding = db_embedding / np.linalg.norm(db_embedding)

            # Cosine similarity (no double normalization)
            score = np.dot(embedding, db_embedding)

            # DEBUG
            # print(f"{student_id}: {score:.3f}")

            if score > best_score:
                best_score = score
                best_match = student_id

        print(f"Match -> {best_match}, Score -> {best_score:.3f}")

        if best_match is not None and best_score >= 0.5:
            recognized_students.append(best_match)

    # Remove duplicates
    recognized_students = list(set(recognized_students))

    return JsonResponse({
        "recognized_students": recognized_students
    })