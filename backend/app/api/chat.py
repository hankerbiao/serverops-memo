"""
Chat API endpoints.
"""
from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.app.database import get_session
from backend.app.schemas import (
    AssistantResponse,
    ChatRequest,
    ChatResponse,
    ExtractServerRequest,
    ExtractServerResponse,
)
from backend.app.services import (
    extract_server_info,
    generate_assistant_answer,
    generate_chat_reply,
    list_servers,
)

router = APIRouter(tags=["chat"])


@router.post("/api/chat", response_model=ChatResponse)
def post_chat(payload: ChatRequest, session: Session = Depends(get_session)) -> ChatResponse:
    """Chat with AI assistant (Gemini)."""
    reply, used_fallback = generate_chat_reply(payload.message, list_servers(session))
    return ChatResponse(reply=reply, usedFallback=used_fallback)


@router.post("/api/assistant/query", response_model=AssistantResponse)
def query_assistant(payload: ChatRequest, session: Session = Depends(get_session)) -> AssistantResponse:
    """Query AI assistant with local AI."""
    answer = generate_assistant_answer(payload.message, list_servers(session))
    return AssistantResponse(answer=answer)


@router.post("/api/ai/extract-server", response_model=ExtractServerResponse)
def post_extract_server(payload: ExtractServerRequest) -> ExtractServerResponse:
    """Extract server info from natural language description."""
    try:
        extracted = extract_server_info(payload.description)
        return ExtractServerResponse(success=True, data=extracted)
    except Exception as e:
        return ExtractServerResponse(success=False, error=str(e))