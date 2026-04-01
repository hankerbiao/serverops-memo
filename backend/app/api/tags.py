"""
Tag API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Response
from sqlmodel import Session

from backend.app.database import get_session
from backend.app.schemas import TagRead, TagWrite
from backend.app.services import (
    create_tag,
    delete_tag,
    list_tags,
    update_tag,
)

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=list[TagRead])
def get_tags(session: Session = Depends(get_session)) -> list[TagRead]:
    """Get all tags."""
    return list_tags(session)


@router.post("", response_model=TagRead, status_code=201)
def post_tag(payload: TagWrite, session: Session = Depends(get_session)) -> TagRead:
    """Create a new tag."""
    return create_tag(session, payload)


@router.put("/{tag_id}", response_model=TagRead)
def put_tag(
    tag_id: str,
    payload: TagWrite,
    session: Session = Depends(get_session),
) -> TagRead:
    """Update an existing tag."""
    tag = update_tag(session, tag_id, payload)
    if tag is None:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.delete("/{tag_id}", status_code=204)
def remove_tag(tag_id: str, session: Session = Depends(get_session)) -> Response:
    """Delete a tag."""
    deleted = delete_tag(session, tag_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tag not found")
    return Response(status_code=204)