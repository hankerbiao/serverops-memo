"""
Server API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session

from backend.app.database import get_session
from backend.app.schemas import ServerRead, ServerWrite
from backend.app.services import (
    create_server,
    delete_server,
    list_servers,
    update_server,
)

router = APIRouter(prefix="/api/servers", tags=["servers"])


@router.get("", response_model=list[ServerRead])
def get_servers(session: Session = Depends(get_session)) -> list[ServerRead]:
    """Get all servers."""
    return list_servers(session)


@router.post("", response_model=ServerRead, status_code=201)
def post_server(payload: ServerWrite, session: Session = Depends(get_session)) -> ServerRead:
    """Create a new server."""
    return create_server(session, payload)


@router.put("/{server_id}", response_model=ServerRead)
def put_server(
    server_id: str,
    payload: ServerWrite,
    session: Session = Depends(get_session),
) -> ServerRead:
    """Update an existing server."""
    server = update_server(session, server_id, payload)
    if server is None:
        raise HTTPException(status_code=404, detail="Server not found")
    return server


@router.delete("/{server_id}", status_code=204)
def remove_server(server_id: str, session: Session = Depends(get_session)) -> Response:
    """Delete a server."""
    deleted = delete_server(session, server_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Server not found")
    return Response(status_code=204)