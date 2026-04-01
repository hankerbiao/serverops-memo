"""
Tag model for server categorization.
"""
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Column, DateTime
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.app.models.server import Server, Service


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ServerTagLink(SQLModel, table=True):
    """Many-to-many relationship between servers and tags."""
    server_id: str = Field(foreign_key="server.id", primary_key=True)
    tag_id: str = Field(foreign_key="tag.id", primary_key=True)


class TagBase(SQLModel):
    """Base tag model."""
    name: str
    color: str


class Tag(TagBase, table=True):
    """Tag for categorizing servers."""
    id: str = Field(primary_key=True)
    servers: list["Server"] = Relationship(
        back_populates="tags",
        link_model=ServerTagLink,
    )


class ServiceBase(SQLModel):
    """Base service model."""
    name: str
    health_url: str | None = None
    status: str = "online"
    category: str | None = None
    aliases: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    notes: str | None = None


class Service(ServiceBase, table=True):
    """Service running on a server."""
    id: int | None = Field(default=None, primary_key=True)
    server_id: str = Field(foreign_key="server.id", index=True)
    server: "Server" = Relationship(back_populates="services")


class ServerBase(SQLModel):
    """Base server model."""
    name: str
    ip: str
    username: str
    password: str | None = None
    ssh_key: str | None = None
    status: str
    aliases: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    notes: str | None = None


class Server(ServerBase, table=True):
    """Server entity."""
    id: str = Field(primary_key=True)
    last_checked: datetime = Field(
        default_factory=utc_now,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    services: list["Service"] = Relationship(
        back_populates="server",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    tags: list["Tag"] = Relationship(
        back_populates="servers",
        link_model=ServerTagLink,
    )