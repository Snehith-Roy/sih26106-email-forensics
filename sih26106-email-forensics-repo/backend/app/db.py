"""
Database connection — SQLAlchemy engine & session factory.

Uses DATABASE_URL env var (set by docker-compose to PostgreSQL, defaults to
SQLite for local dev so nobody needs Postgres running to test the pipeline).
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Default: file-based SQLite in models_store (relative to backend/)
# Set DATABASE_URL env var for PostgreSQL in production (docker-compose sets this).
DEFAULT_SQLITE = os.path.join(os.path.dirname(__file__), "..", "models_store", "email_forensics.db")
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE}")

connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False  # needed for SQLite + FastAPI async

engine = create_engine(DATABASE_URL, connect_args=connect_args, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_test_engine():
    """Return an in-memory SQLite engine for tests."""
    from sqlalchemy.pool import StaticPool
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


def get_db():
    """FastAPI dependency — yields a DB session, ensures cleanup."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Call once at startup (after Base is imported)."""
    Base.metadata.create_all(bind=engine)
