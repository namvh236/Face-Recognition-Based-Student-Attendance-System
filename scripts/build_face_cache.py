"""Dựng lại data/face_data.pkl từ ảnh trong data/raw_faces/<mssv>.<jpg|png>.

Chạy từ thư mục gốc: python -m scripts.build_face_cache
"""
import os

from app.config import FACE_CACHE_FILE, RAW_FACES_DIR
from app.services.face_service import embeddings_from_dir, save_cache


def main():
    if not os.path.isdir(RAW_FACES_DIR):
        print(f"Lỗi: Không tìm thấy thư mục '{RAW_FACES_DIR}'!")
        return

    print("Đang khởi tạo model AI (InsightFace) và xử lý ảnh...")
    face_data = embeddings_from_dir(RAW_FACES_DIR, report=print)

    if not face_data:
        print("Không có dữ liệu nào được lưu.")
        return

    save_cache(face_data)
    print("------------------------------------------------")
    print(f"Đã lưu {len(face_data)} sinh viên vào '{FACE_CACHE_FILE}'. Có thể điểm danh ngay.")


if __name__ == "__main__":
    main()
