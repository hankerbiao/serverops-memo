"""
AI Configuration model.
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AIConfigBase(SQLModel):
    """Base AI config model."""
    ai_url: str
    ai_model: str


class AIConfig(AIConfigBase, table=True):
    """AI configuration stored in database."""
    id: int | None = Field(default=None, primary_key=True)
    updated_at: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )