"""
Database configuration (backward compatibility).

Import from backend.app.database instead.
"""
from backend.app.database import get_engine, get_session, init_db

__all__ = ["get_engine", "get_session", "init_db"]