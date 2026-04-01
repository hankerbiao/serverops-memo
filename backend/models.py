from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime
from sqlmodel import Field, Relationship, SQLModel


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ServerTagLink(SQLModel, table=True):
    server_id: str = Field(foreign_key="server.id", primary_key=True)
    tag_id: str = Field(foreign_key="tag.id", primary_key=True)


class TagBase(SQLModel):
    name: str
    color: str


class Tag(TagBase, table=True):
    id: str = Field(primary_key=True)
    servers: list["Server"] = Relationship(
        back_populates="tags",
        link_model=ServerTagLink,
    )


class ServiceBase(SQLModel):
    name: str
    health_url: str | None = None
    status: str = "online"
    category: str | None = None
    aliases: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    notes: str | None = None


class Service(ServiceBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    server_id: str = Field(foreign_key="server.id", index=True)
    server: "Server" = Relationship(back_populates="services")


class ServerBase(SQLModel):
    name: str
    ip: str
    username: str
    password: str | None = None
    ssh_key: str | None = None
    status: str
    aliases: list[str] = Field(default_factory=list, sa_column=Column(JSON, nullable=False))
    notes: str | None = None


class Server(ServerBase, table=True):
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
