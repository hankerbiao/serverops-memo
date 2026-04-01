"""
API endpoints.
"""
from backend.app.api.chat import router as chat_router
from backend.app.api.servers import router as servers_router
from backend.app.api.tags import router as tags_router

__all__ = ["chat_router", "servers_router", "tags_router"]