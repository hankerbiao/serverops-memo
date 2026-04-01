"""
Server and tag CRUD services.
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlmodel import Session, select

from backend.app.models import Server, Service, Tag
from backend.app.schemas.server import ServerRead, ServerWrite, TagRead, TagWrite


def format_timestamp(value: datetime) -> str:
    """Format datetime to ISO string."""
    return value.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def to_tag_read(tag: Tag) -> TagRead:
    """Convert Tag model to TagRead schema."""
    return TagRead(id=tag.id, name=tag.name, color=tag.color)


def to_server_read(server: Server) -> ServerRead:
    """Convert Server model to ServerRead schema."""
    return ServerRead(
        id=server.id,
        name=server.name,
        ip=server.ip,
        username=server.username,
        password=server.password,
        sshKey=server.ssh_key,
        status=server.status,
        lastChecked=format_timestamp(server.last_checked),
        tags=[to_tag_read(tag) for tag in server.tags],
        aliases=list(server.aliases or []),
        notes=server.notes,
        services=[
            {
                "name": service.name,
                "healthUrl": service.health_url,
                "status": service.status,
                "category": service.category,
                "aliases": list(service.aliases or []),
                "notes": service.notes,
            }
            for service in server.services
        ],
    )


def list_servers(session: Session) -> list[ServerRead]:
    """List all servers."""
    statement = select(Server).order_by(Server.last_checked.desc())
    servers = session.exec(statement).unique().all()
    return [to_server_read(server) for server in servers]


def list_tags(session: Session) -> list[TagRead]:
    """List all tags."""
    statement = select(Tag).order_by(Tag.name.asc())
    tags = session.exec(statement).all()
    return [to_tag_read(tag) for tag in tags]


def _resolve_tags(session: Session, payload_tags: list[TagWrite]) -> list[Tag]:
    """Resolve tags from payload, creating new ones if needed."""
    resolved: list[Tag] = []
    for payload_tag in payload_tags:
        tag = None
        if payload_tag.id:
            tag = session.get(Tag, payload_tag.id)
        if tag is None:
            statement = select(Tag).where(Tag.name == payload_tag.name)
            tag = session.exec(statement).first()
        if tag is None:
            tag = Tag(
                id=payload_tag.id or uuid4().hex,
                name=payload_tag.name,
                color=payload_tag.color,
            )
            session.add(tag)
            session.flush()
        else:
            tag.name = payload_tag.name
            tag.color = payload_tag.color
            session.add(tag)
        resolved.append(tag)
    return resolved


def create_tag(session: Session, payload: TagWrite) -> TagRead:
    """Create a new tag."""
    tag = Tag(id=payload.id or uuid4().hex, name=payload.name, color=payload.color)
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return to_tag_read(tag)


def update_tag(session: Session, tag_id: str, payload: TagWrite) -> TagRead | None:
    """Update an existing tag."""
    tag = session.get(Tag, tag_id)
    if tag is None:
        return None
    tag.name = payload.name
    tag.color = payload.color
    session.add(tag)
    session.commit()
    session.refresh(tag)
    return to_tag_read(tag)


def delete_tag(session: Session, tag_id: str) -> bool:
    """Delete a tag."""
    tag = session.get(Tag, tag_id)
    if tag is None:
        return False
    session.delete(tag)
    session.commit()
    return True


def create_server(session: Session, payload: ServerWrite) -> ServerRead:
    """Create a new server."""
    server = Server(
        id=uuid4().hex,
        name=payload.name,
        ip=payload.ip,
        username=payload.username,
        password=payload.password or None,
        ssh_key=payload.ssh_key or None,
        status=payload.status,
        aliases=list(payload.aliases),
        notes=payload.notes or None,
        last_checked=datetime.now(timezone.utc),
        services=[
            Service(
                name=service.name,
                health_url=service.health_url or None,
                status=service.status or "online",
                category=service.category or None,
                aliases=list(service.aliases),
                notes=service.notes or None,
            )
            for service in payload.services
        ],
        tags=_resolve_tags(session, payload.tags),
    )
    session.add(server)
    session.commit()
    session.refresh(server)
    return to_server_read(server)


def update_server(session: Session, server_id: str, payload: ServerWrite) -> ServerRead | None:
    """Update an existing server."""
    server = session.get(Server, server_id)
    if server is None:
        return None

    server.name = payload.name
    server.ip = payload.ip
    server.username = payload.username
    server.password = payload.password or None
    server.ssh_key = payload.ssh_key or None
    server.status = payload.status
    server.aliases = list(payload.aliases)
    server.notes = payload.notes or None
    server.last_checked = datetime.now(timezone.utc)
    server.tags = _resolve_tags(session, payload.tags)

    server.services.clear()
    for service in payload.services:
        server.services.append(
            Service(
                name=service.name,
                health_url=service.health_url or None,
                status=service.status or "online",
                category=service.category or None,
                aliases=list(service.aliases),
                notes=service.notes or None,
                server_id=server.id,
            )
        )

    session.add(server)
    session.commit()
    session.refresh(server)
    return to_server_read(server)


def delete_server(session: Session, server_id: str) -> bool:
    """Delete a server."""
    server = session.get(Server, server_id)
    if server is None:
        return False

    session.delete(server)
    session.commit()
    return True