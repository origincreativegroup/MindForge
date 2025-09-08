"""Database utilities for the lightweight test environment.

This module provides a minimal SQLAlchemy setup so that modules depending on
``get_db`` or ``Base`` can be imported during tests.  The real project uses a
more elaborate configuration, but for the purposes of unit tests an in-memory
SQLite database is sufficient.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# SQLite database stored in the repository root.  ``check_same_thread`` is
# required for SQLite when using the connection in different threads (e.g. the
# test runner).
DATABASE_URL = "sqlite:///./mindforge.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# Base class for ORM models
Base = declarative_base()


def init_db(base: declarative_base = Base) -> None:
    """Create database tables for all metadata defined on ``base``."""

    base.metadata.create_all(bind=engine)


# Initialize tables on import so that routers relying on them can be imported
# without additional setup.
init_db(Base)


@contextmanager
def get_db() -> Generator:
    """FastAPI dependency that yields a database session."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

