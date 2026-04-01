"""
Database models (backward compatibility).

Import from backend.app.models instead.
"""
from backend.app.models import Server, ServerBase, ServerTagLink, Service, ServiceBase, Tag, TagBase, utc_now

__all__ = ["Server", "ServerBase", "ServerTagLink", "Service", "ServiceBase", "Tag", "TagBase", "utc_now"]