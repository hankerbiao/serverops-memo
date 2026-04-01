"""
Chat-related schemas.
"""
from pydantic import BaseModel, ConfigDict, Field


class ChatRequest(BaseModel):
    """Schema for chat request."""
    message: str


class AssistantRecord(BaseModel):
    """Schema for assistant record."""
    type: str
    server_id: str = Field(alias="serverId")
    server_name: str = Field(alias="serverName")
    service_name: str | None = Field(default=None, alias="serviceName")
    status: str
    health_url: str | None = Field(default=None, alias="healthUrl")
    notes: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class AssistantKnowledge(BaseModel):
    """Schema for assistant knowledge."""
    title: str
    snippet: str


class AssistantAnswer(BaseModel):
    """Schema for assistant answer."""
    summary: str
    records: list[AssistantRecord] = Field(default_factory=list)
    knowledge: list[AssistantKnowledge] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list, alias="nextActions")

    model_config = ConfigDict(populate_by_name=True)


class AssistantResponse(BaseModel):
    """Schema for assistant response."""
    answer: AssistantAnswer


class ChatResponse(BaseModel):
    """Schema for chat response."""
    reply: str
    used_fallback: bool = Field(alias="usedFallback")

    model_config = ConfigDict(populate_by_name=True)


class ExtractedService(BaseModel):
    """Schema for extracted service."""
    name: str
    health_url: str | None = Field(default=None, alias="healthUrl")
    notes: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class ExtractedServerInfo(BaseModel):
    """Schema for extracted server info."""
    ip: str | None = None
    username: str | None = None
    password: str | None = None
    aliases: list[str] = Field(default_factory=list)
    notes: str | None = None
    services: list[ExtractedService] = Field(default_factory=list)


class ExtractServerRequest(BaseModel):
    """Schema for extract server request."""
    description: str


class ExtractServerResponse(BaseModel):
    """Schema for extract server response."""
    success: bool
    data: ExtractedServerInfo | None = None
    error: str | None = None