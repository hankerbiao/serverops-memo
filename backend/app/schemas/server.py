"""
Server-related schemas.
"""
from pydantic import BaseModel, ConfigDict, Field


class TagWrite(BaseModel):
    """Schema for creating/updating a tag."""
    id: str | None = None
    name: str
    color: str


class TagRead(BaseModel):
    """Schema for reading a tag."""
    id: str
    name: str
    color: str


class ServiceWrite(BaseModel):
    """Schema for creating/updating a service."""
    name: str
    health_url: str | None = Field(default=None, alias="healthUrl")
    status: str = "online"
    category: str | None = None
    aliases: list[str] = Field(default_factory=list)
    notes: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class ServiceRead(BaseModel):
    """Schema for reading a service."""
    name: str
    health_url: str | None = Field(default=None, alias="healthUrl")
    status: str
    category: str | None = None
    aliases: list[str] = Field(default_factory=list)
    notes: str | None = None

    model_config = ConfigDict(populate_by_name=True)


class ServerWrite(BaseModel):
    """Schema for creating/updating a server."""
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
    """Schema for reading a server."""
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