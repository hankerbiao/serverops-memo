"""
Database connection and session management.
"""
from __future__ import annotations

from collections.abc import Generator
from typing import Any

from sqlmodel import Session, SQLModel, create_engine

from backend.app.config import settings


def get_engine() -> Any:
    """Create database engine."""
    database_url = settings.DATABASE_URL
    connect_args: dict[str, bool] = {}
    if database_url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    return create_engine(database_url, connect_args=connect_args)


_engine = get_engine()


def get_engine_instance() -> Any:
    """Get the engine instance."""
    return _engine


def init_db() -> None:
    """Initialize database tables."""
    SQLModel.metadata.create_all(_engine)


def get_session() -> Generator[Session, None, None]:
    """Get database session."""
    with Session(_engine) as session:
        yield session