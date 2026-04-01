"""
Alert record model for tracking sent alerts.
"""
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AlertRecord(SQLModel, table=True):
    """Record of sent alerts to prevent duplicate notifications."""
    id: int | None = Field(default=None, primary_key=True)
    server_id: str = Field(index=True)
    service_name: str | None = Field(default=None, index=True)
    alert_type: str = Field(default="server")  # "server" or "service"
    sent_at: datetime = Field(default_factory=utc_now)