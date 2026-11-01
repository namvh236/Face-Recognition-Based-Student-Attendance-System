from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import DB_URI

# check_same_thread=False: RecognitionThread (a QThread) writes to the DB off the GUI thread.
engine = create_engine(DB_URI, connect_args={"check_same_thread": False}, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_session():
    """Return a new Session. The caller MUST close it on every exit path."""
    return SessionLocal()


def init_db():
    import app.database.models  # noqa: F401  (registers models on Base.metadata)

    Base.metadata.create_all(engine)
    print("Database initialized.")
