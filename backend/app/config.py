"""
Application configuration and settings.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = Field(
        default="sqlite:///./serverops.db",
        description="Database connection URL",
    )

    # CORS
    CORS_ORIGINS: str | None = Field(
        default=None,
        description="Comma-separated CORS origins",
    )

    # AI Configuration
    AI_URL: str = Field(
        default="http://10.17.150.235:8000/v1",
        description="AI service URL",
    )
    AI_MODEL: str = Field(
        default="/models/Qwen/Qwen3-30B-A3B-Instruct-2507",
        description="AI model name",
    )
    GEMINI_API_KEY: str | None = Field(
        default=None,
        description="Google Gemini API key",
    )

    # Health Check
    HEALTH_CHECK_INTERVAL: int = Field(
        default=300,
        description="Health check interval in seconds",
    )

    # Alert Configuration
    ALERT_ENABLED: bool = Field(
        default=True,
        description="Enable alert notifications",
    )
    ALERT_WEBHOOK_URL: str = Field(
        default="http://rdm.cooacloud.com/api/platform/notify/bot",
        description="Alert webhook URL",
    )
    ALERT_ITCODE: str = Field(
        default="libiao1",
        description="Alert recipient itcode",
    )
    ALERT_COMPONENT_NAME: str = Field(
        default="ServerOps",
        description="Alert component name",
    )

    # Application
    APP_NAME: str = "ServerOps API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False)

    class Config:
        env_prefix = "SERVEROPS_"
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra: Any = "allow"

    @property
    def cors_origin_list(self) -> list[str]:
        """Get CORS origins as list."""
        if self.CORS_ORIGINS:
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        return [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:8889",
            "http://127.0.0.1:8889",
        ]


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings