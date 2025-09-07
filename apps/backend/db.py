from integrations.database import SessionLocal, init_db

from .models import Base

# Initialize tables on startup
init_db(Base)


def get_db():
    """FastAPI dependency for database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
