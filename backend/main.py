"""
ServerOps API - Main entry point.

This module provides backward compatibility by re-exporting from app.
For new code, import directly from backend.app.
"""
from backend.app.main import app, create_app

__all__ = ["app", "create_app"]