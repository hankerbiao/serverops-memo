from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class TagWrite(BaseModel):
    id: str | None = None
    name: str
    color: str


class TagRead(BaseModel):
    id: str
    name: str
    color: str


class ServiceWrite(BaseModel):
    name: str
    health_url: str | None = Field(default=None, alias="healthUrl")
    status: str = "online"
    category: str | None = None
    aliases: list[str] = Field(default_factory=list)
    notes: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class ServiceRead(BaseModel):
    name: str
    health_url: str | None = Field(default=None, alias="healthUrl")
    status: str
    category: str | None = None
    aliases: list[str] = Field(default_factory=list)
    notes: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class ServerWrite(BaseModel):
    name: str
    ip: str
    username: str
    password: str | None = None
    ssh_key: str | None = Field(default=None, alias="sshKey")
    status: str
    tags: list[TagWrite] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)
    notes: str | None = None
    services: list[ServiceWrite]

    model_config = ConfigDict(populate_by_name=True)


class ServerRead(BaseModel):
    id: str
    name: str
    ip: str
    username: str
    password: str | None = None
    ssh_key: str | None = Field(default=None, alias="sshKey")
    status: str
    last_checked: str = Field(alias="lastChecked")
    tags: list[TagRead] = Field(default_factory=list)
    aliases: list[str] = Field(default_factory=list)
    notes: str | None = None
    services: list[ServiceRead]

    model_config = ConfigDict(populate_by_name=True)


class ChatRequest(BaseModel):
    message: str


class AssistantRecord(BaseModel):
    type: str
    server_id: str = Field(alias="serverId")
    server_name: str = Field(alias="serverName")
    service_name: str | None = Field(default=None, alias="serviceName")
    status: str
    health_url: str | None = Field(default=None, alias="healthUrl")
    notes: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class AssistantKnowledge(BaseModel):
    title: str
    snippet: str


class AssistantAnswer(BaseModel):
    summary: str
    records: list[AssistantRecord] = Field(default_factory=list)
    knowledge: list[AssistantKnowledge] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list, alias="nextActions")

    model_config = ConfigDict(populate_by_name=True)


class AssistantResponse(BaseModel):
    answer: AssistantAnswer


class ChatResponse(BaseModel):
    reply: str
    used_fallback: bool = Field(alias="usedFallback")

    model_config = ConfigDict(populate_by_name=True)


class ExtractedService(BaseModel):
    name: str
    health_url: str | None = Field(default=None, alias="healthUrl")
    notes: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class ExtractedServerInfo(BaseModel):
    ip: str | None = None
    username: str | None = None
    password: str | None = None
    aliases: list[str] = Field(default_factory=list)
    notes: str | None = None
    services: list[ExtractedService] = Field(default_factory=list)


class ExtractServerRequest(BaseModel):
    description: str


class ExtractServerResponse(BaseModel):
    success: bool
    data: ExtractedServerInfo | None = None
    error: str | None = None
