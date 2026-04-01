"""
Pydantic schemas.
"""
from backend.app.schemas.chat import (
    AssistantAnswer,
    AssistantKnowledge,
    AssistantRecord,
    AssistantResponse,
    ChatRequest,
    ChatResponse,
    ExtractServerRequest,
    ExtractServerResponse,
    ExtractedServerInfo,
    ExtractedService,
)
from backend.app.schemas.server import (
    ServerRead,
    ServerWrite,
    ServiceRead,
    ServiceWrite,
    TagRead,
    TagWrite,
)

__all__ = [
    # Server schemas
    "ServerRead",
    "ServerWrite",
    "ServiceRead",
    "ServiceWrite",
    "TagRead",
    "TagWrite",
    # Chat schemas
    "ChatRequest",
    "ChatResponse",
    "AssistantResponse",
    "AssistantAnswer",
    "AssistantRecord",
    "AssistantKnowledge",
    "ExtractServerRequest",
    "ExtractServerResponse",
    "ExtractedServerInfo",
    "ExtractedService",
]