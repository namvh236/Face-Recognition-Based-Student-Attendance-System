"""Nhận diện khuôn mặt: model InsightFace (lazy), cache embedding, so khớp cosine.

Cache `data/face_data.pkl` là dict phẳng `{mssv: embedding}` (embedding thô, chưa chuẩn hoá).
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
    """Khởi tạo InsightFace ở lần gọi đầu (tải model rất nặng, không làm lúc import)."""
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
    """Embedding của khuôn mặt đầu tiên trong ảnh BGR, hoặc None nếu không có mặt nào."""
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
    """Quét thư mục ảnh `<mssv>.<ext>` -> `{mssv: embedding}`. Ảnh lỗi/không có mặt bị bỏ qua.

    `report(msg)` (tuỳ chọn) nhận cảnh báo cho từng ảnh bị bỏ qua.
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


def enroll_face(mssv, frame):
    """Lưu ảnh backup vào ENROLLED_FACES_DIR và cập nhật cache ngay. True nếu có mặt trong ảnh."""
    os.makedirs(ENROLLED_FACES_DIR, exist_ok=True)
    cv2.imwrite(os.path.join(ENROLLED_FACES_DIR, f"{mssv}.jpg"), frame)

    embedding = get_face_embedding(frame)
    if embedding is None:
        return False
    cache = load_cache()
    cache[mssv] = embedding
    save_cache(cache)
    return True


def cosine_similarities(embedding, known_embeddings):
    """Cosine giữa 1 vector và ma trận (N, D) -> mảng (N,)."""
    embedding = embedding.ravel()
    known = np.asarray(known_embeddings)
    return known @ embedding / (np.linalg.norm(embedding) * np.linalg.norm(known, axis=1))
