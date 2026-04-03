"""
AI Configuration services.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Session, select

from backend.app.models.config import AIConfig
from backend.app.schemas.config import AIConfigRead, AIConfigWrite

if TYPE_CHECKING:
    pass


def format_timestamp(value: datetime) -> str:
    """Format datetime to ISO string."""
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def get_ai_config(session: Session) -> "AIConfigRead | None":
    """Get AI config from database."""
    statement = select(AIConfig).limit(1)
    config = session.exec(statement).first()
    if config:
        return AIConfigRead(
            id=config.id,
            aiUrl=config.ai_url,
            aiModel=config.ai_model,
            updatedAt=format_timestamp(config.updated_at),
        )
    return None


def update_ai_config(session: Session, config_data: "AIConfigWrite") -> "AIConfigRead":
    """Update AI config in database."""
    # Get existing config or create new one
    statement = select(AIConfig).limit(1)
    config = session.exec(statement).first()

    if config:
        # Update existing
        config.ai_url = config_data.ai_url
        config.ai_model = config_data.ai_model
        config.updated_at = datetime.now(timezone.utc)
    else:
        # Create new
        config = AIConfig(
            ai_url=config_data.ai_url,
            ai_model=config_data.ai_model,
        )
        session.add(config)

    session.commit()
    session.refresh(config)

    return AIConfigRead(
        id=config.id,
        aiUrl=config.ai_url,
        aiModel=config.ai_model,
        updatedAt=format_timestamp(config.updated_at),
    )