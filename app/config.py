import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Static resources (committed)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMG_DIR = os.path.join(ASSETS_DIR, "img")
STYLES_DIR = os.path.join(ASSETS_DIR, "styles")

# Runtime data (generated, gitignored)
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "student_management.db")
DB_URI = f"sqlite:///{DB_PATH}"

RAW_FACES_DIR = os.path.join(DATA_DIR, "raw_faces")            # Hand-placed photos: <mssv>.jpg|png
ENROLLED_FACES_DIR = os.path.join(DATA_DIR, "enrolled_faces")  # Photos captured by the "add student" dialog
FACE_CACHE_FILE = os.path.join(DATA_DIR, "face_data.pkl")      # { mssv: embedding }

# Face recognition
FACE_MODEL_NAME = "buffalo_l"
FACE_DET_SIZE = (640, 640)
SIMILARITY_THRESHOLD = 0.5  # Minimum cosine similarity to accept a match
CAMERA_INDEX = 0
