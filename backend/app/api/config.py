"""
AI Configuration API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from backend.app.database import get_session
from backend.app.schemas.config import AIConfigRead, AIConfigWrite
from backend.app.services.config_service import get_ai_config, update_ai_config

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("/ai", response_model=AIConfigRead)
def get_config(session: Session = Depends(get_session)) -> AIConfigRead:
    """Get AI config from database."""
    config = get_ai_config(session)
    if config is None:
        raise HTTPException(status_code=404, detail="AI config not found")
    return config


@router.put("/ai", response_model=AIConfigRead)
def put_config(
    payload: AIConfigWrite,
    session: Session = Depends(get_session),
) -> AIConfigRead:
    """Update AI config in database."""
    return update_ai_config(session, payload)