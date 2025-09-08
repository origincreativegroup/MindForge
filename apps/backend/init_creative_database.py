#!/usr/bin/env python3
"""Initialize the creative projects database.

This script creates the required tables for the creative projects module using
the SQLAlchemy models.  It works with both SQLite (for local development) and
Postgres when a connection string is supplied via environment variables.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Allow running this script directly by ensuring the backend package is on the
# path.
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

from models.creative.models import Base, TeamMember

DATABASE_URL = (
    os.getenv("DATABASE_URL") or os.getenv("POSTGRES_URL") or "sqlite:///./mindforge_creative.db"
)

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def create_tables() -> None:
    """Create all database tables based on the SQLAlchemy models."""

    Base.metadata.create_all(bind=engine)
    print("✅ Creative projects database tables created successfully!")


def create_sample_data() -> None:
    """Insert basic seed data for development."""

    db = SessionLocal()
    try:
        # Upsert a couple of team members for demo purposes
        if not db.query(TeamMember).filter_by(id=1).first():
            db.add(TeamMember(id=1, name="Casey AI", email="casey@mindforge.ai", role="ai_assistant"))
        if not db.query(TeamMember).filter_by(id=2).first():
            db.add(TeamMember(id=2, name="Demo User", email="demo@example.com", role="designer"))
        db.commit()
        print("✅ Sample data created!")
    finally:
        db.close()


if __name__ == "__main__":
    print("🎨 Initializing MindForge Creative Projects Database…")
    create_tables()
    create_sample_data()
    print("🎉 Creative projects database setup complete!")

