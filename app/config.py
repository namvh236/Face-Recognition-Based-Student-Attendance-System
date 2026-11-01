import os

# Đường dẫn gốc của dự án
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Tài nguyên tĩnh (được commit)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
IMG_DIR = os.path.join(ASSETS_DIR, "img")
STYLES_DIR = os.path.join(ASSETS_DIR, "styles")

# Dữ liệu runtime (sinh ra khi chạy, KHÔNG commit - xem .gitignore)
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "student_management.db")
DB_URI = f"sqlite:///{DB_PATH}"

RAW_FACES_DIR = os.path.join(DATA_DIR, "raw_faces")            # Ảnh gốc nhập tay: <mssv>.jpg|png
ENROLLED_FACES_DIR = os.path.join(DATA_DIR, "enrolled_faces")  # Ảnh chụp khi thêm sinh viên trong app
FACE_CACHE_FILE = os.path.join(DATA_DIR, "face_data.pkl")      # { mssv: embedding }

# Nhận diện khuôn mặt
FACE_MODEL_NAME = "buffalo_l"
FACE_DET_SIZE = (640, 640)
SIMILARITY_THRESHOLD = 0.5  # Cosine similarity tối thiểu để chấp nhận một khuôn mặt
CAMERA_INDEX = 0
