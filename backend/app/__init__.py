"""
ServerOps Backend Application.
"""
from backend.app.config import settings
from backend.app.main import app, create_app

__all__ = ["app", "create_app", "settings"]