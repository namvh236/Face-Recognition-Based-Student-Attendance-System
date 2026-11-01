"""Rebuild data/face_data.pkl from photos in data/raw_faces/<mssv>.<jpg|png>.

Run from the repo root: python -m scripts.build_face_cache
"""
import os

from app.config import FACE_CACHE_FILE, RAW_FACES_DIR
from app.services.face_service import embeddings_from_dir, save_cache


def main():
    if not os.path.isdir(RAW_FACES_DIR):
        print(f"Error: directory not found: '{RAW_FACES_DIR}'")
        return

    print("Loading the InsightFace model and processing images...")
    face_data = embeddings_from_dir(RAW_FACES_DIR, report=print)

    if not face_data:
        print("No embeddings were saved.")
        return

    save_cache(face_data)
    print("------------------------------------------------")
    print(f"Saved {len(face_data)} students to '{FACE_CACHE_FILE}'.")


if __name__ == "__main__":
    main()
