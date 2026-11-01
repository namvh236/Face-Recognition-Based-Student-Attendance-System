"""Face recognition: lazy InsightFace model, embedding cache, cosine matching.

The cache (`data/face_data.pkl`) is a flat `{mssv: embedding}` dict of raw, unnormalized embeddings.
"""
import os
import pickle
import threading

import cv2
import numpy as np

from app.config import (
    ENROLLED_FACES_DIR,
    FACE_CACHE_FILE,
    FACE_DET_SIZE,
    FACE_MODEL_NAME,
)

IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png")

_face_app = None
_face_app_lock = threading.Lock()


def get_face_app():
    """Create the InsightFace app on first use (model load is slow, so never at import time)."""
    global _face_app
    if _face_app is None:
        with _face_app_lock:
            if _face_app is None:
                import onnxruntime
                from insightface.app import FaceAnalysis

                available = onnxruntime.get_available_providers()
                providers = [p for p in ("CUDAExecutionProvider", "CPUExecutionProvider") if p in available]
                app = FaceAnalysis(name=FACE_MODEL_NAME, providers=providers)
                app.prepare(ctx_id=0, det_size=FACE_DET_SIZE)
                _face_app = app
    return _face_app


def get_face_embedding(image):
    """Embedding of the first face in a BGR image, or None if no face is found."""
    faces = get_face_app().get(image)
    return faces[0].embedding if faces else None


def load_cache():
    if os.path.exists(FACE_CACHE_FILE):
        try:
            with open(FACE_CACHE_FILE, "rb") as f:
                return pickle.load(f)
        except Exception:
            return {}
    return {}


def save_cache(data):
    os.makedirs(os.path.dirname(FACE_CACHE_FILE), exist_ok=True)
    with open(FACE_CACHE_FILE, "wb") as f:
        pickle.dump(data, f)


def embeddings_from_dir(directory, report=None):
    """Scan a directory of `<mssv>.<ext>` images -> `{mssv: embedding}`.

    Unreadable images and images without a face are skipped; `report(msg)`, if given, is told why.
    """
    result = {}
    if not os.path.isdir(directory):
        return result
    for name in sorted(os.listdir(directory)):
        if not name.lower().endswith(IMAGE_EXTENSIONS):
            continue
        img = cv2.imread(os.path.join(directory, name))
        if img is None:
            if report:
                report(f"[-] Không đọc được ảnh: {name}")
            continue
        embedding = get_face_embedding(img)
        if embedding is None:
            if report:
                report(f"[-] Không tìm thấy khuôn mặt nào trong ảnh {name}")
            continue
        result[os.path.splitext(name)[0]] = embedding
    return result


def enroll_face(mssv, frame, embedding):
    """Save the photo to ENROLLED_FACES_DIR and store its embedding in the cache."""
    os.makedirs(ENROLLED_FACES_DIR, exist_ok=True)
    cv2.imwrite(os.path.join(ENROLLED_FACES_DIR, f"{mssv}.jpg"), frame)

    cache = load_cache()
    cache[mssv] = embedding
    save_cache(cache)


def cosine_similarities(embedding, known_embeddings):
    """Cosine similarity between one vector and an (N, D) matrix -> array of shape (N,)."""
    embedding = embedding.ravel()
    known = np.asarray(known_embeddings)
    return known @ embedding / (np.linalg.norm(embedding) * np.linalg.norm(known, axis=1))
