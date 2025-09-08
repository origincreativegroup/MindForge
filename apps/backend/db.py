"""Database utilities for the lightweight test environment.

This module provides a minimal SQLAlchemy setup so that modules depending on
``get_db`` or ``Base`` can be imported during tests.  The real project uses a
more elaborate configuration, but for the purposes of unit tests an in-memory
SQLite database is sufficient.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# Use a Postgres connection when available, falling back to a local SQLite
# database for tests and development.
DATABASE_URL = (
    os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or "sqlite:///./mindforge.db"
)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
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

