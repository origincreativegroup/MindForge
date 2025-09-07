"""Database integration layer for MindForge."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mindforge.db")


def get_engine():
    """Create database engine using DATABASE_URL.

    Uses a SQLite database by default for local development but can connect to
    Postgres or any SQLAlchemy-supported backend when ``DATABASE_URL`` is set.
    """
    if DATABASE_URL.startswith("sqlite"):
        return create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    return create_engine(DATABASE_URL)


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db(base):
    """Initialize tables for the given SQLAlchemy ``base``."""
    base.metadata.create_all(bind=engine)
