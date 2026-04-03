"""
AI Configuration schemas.
"""
from pydantic import BaseModel, ConfigDict, Field


class AIConfigWrite(BaseModel):
    """Schema for creating/updating AI config."""
    ai_url: str = Field(alias="aiUrl")
    ai_model: str = Field(alias="aiModel")

    model_config = ConfigDict(populate_by_name=True)


class AIConfigRead(BaseModel):
    """Schema for reading AI config."""
    id: int | None = None
    ai_url: str = Field(alias="aiUrl")
    ai_model: str = Field(alias="aiModel")
    updated_at: str = Field(alias="updatedAt")

    model_config = ConfigDict(populate_by_name=True)