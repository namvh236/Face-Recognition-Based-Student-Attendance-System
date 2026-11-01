from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import DB_URI

# check_same_thread=False: RecognitionThread (QThread) ghi DB từ thread khác GUI.
engine = create_engine(DB_URI, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_session():
    """Trả về Session mới. Người gọi PHẢI session.close() ở mọi nhánh thoát."""
    return SessionLocal()


def init_db():
    import app.database.models  # noqa: F401  (đăng ký model vào Base.metadata)

    Base.metadata.create_all(engine)
    print("Đã khởi tạo Database thành công!")
