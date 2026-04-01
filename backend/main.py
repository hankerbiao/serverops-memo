from __future__ import annotations

from contextlib import asynccontextmanager
import os
from pathlib import Path
import sys

from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session


REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.db import get_session, init_db, get_engine
from backend.schemas import AssistantResponse, ChatRequest, ChatResponse, ExtractServerRequest, ExtractServerResponse, ServerRead, ServerWrite, TagRead, TagWrite
from backend.services import (
    create_server,
    create_tag,
    delete_server,
    delete_tag,
    extract_server_info,
    generate_assistant_answer,
    generate_chat_reply,
    list_servers,
    list_tags,
    start_health_check_scheduler,
    update_server,
    update_tag,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()

    # 启动健康检查调度器 (每5分钟检查一次)
    def session_factory():
        from sqlmodel import Session
        return Session(get_engine())

    start_health_check_scheduler(session_factory, interval_seconds=300)

    yield


def get_allowed_origins() -> list[str]:
    configured = os.getenv("SERVEROPS_CORS_ORIGINS")
    if configured:
        return [origin.strip() for origin in configured.split(",") if origin.strip()]

    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8889",
        "http://127.0.0.1:8889",
    ]


def create_app() -> FastAPI:
    app = FastAPI(title="ServerOps API", lifespan=lifespan)
    allowed_origins = get_allowed_origins()
    use_local_origin_regex = not os.getenv("SERVEROPS_CORS_ORIGINS")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$" if use_local_origin_regex else None,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/servers", response_model=list[ServerRead])
    def get_servers(session: Session = Depends(get_session)) -> list[ServerRead]:
        return list_servers(session)

    @app.post("/api/servers", response_model=ServerRead, status_code=201)
    def post_server(payload: ServerWrite, session: Session = Depends(get_session)) -> ServerRead:
        return create_server(session, payload)

    @app.put("/api/servers/{server_id}", response_model=ServerRead)
    def put_server(
        server_id: str,
        payload: ServerWrite,
        session: Session = Depends(get_session),
    ) -> ServerRead:
        server = update_server(session, server_id, payload)
        if server is None:
            raise HTTPException(status_code=404, detail="Server not found")
        return server

    @app.delete("/api/servers/{server_id}", status_code=204)
    def remove_server(server_id: str, session: Session = Depends(get_session)) -> Response:
        deleted = delete_server(session, server_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Server not found")
        return Response(status_code=204)

    @app.get("/api/tags", response_model=list[TagRead])
    def get_tags(session: Session = Depends(get_session)) -> list[TagRead]:
        return list_tags(session)

    @app.post("/api/tags", response_model=TagRead, status_code=201)
    def post_tag(payload: TagWrite, session: Session = Depends(get_session)) -> TagRead:
        return create_tag(session, payload)

    @app.put("/api/tags/{tag_id}", response_model=TagRead)
    def put_tag(tag_id: str, payload: TagWrite, session: Session = Depends(get_session)) -> TagRead:
        tag = update_tag(session, tag_id, payload)
        if tag is None:
            raise HTTPException(status_code=404, detail="Tag not found")
        return tag

    @app.delete("/api/tags/{tag_id}", status_code=204)
    def remove_tag(tag_id: str, session: Session = Depends(get_session)) -> Response:
        deleted = delete_tag(session, tag_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Tag not found")
        return Response(status_code=204)

    @app.post("/api/chat", response_model=ChatResponse)
    def post_chat(payload: ChatRequest, session: Session = Depends(get_session)) -> ChatResponse:
        reply, used_fallback = generate_chat_reply(payload.message, list_servers(session))
        return ChatResponse(reply=reply, usedFallback=used_fallback)

    @app.post("/api/assistant/query", response_model=AssistantResponse)
    def query_assistant(payload: ChatRequest, session: Session = Depends(get_session)) -> AssistantResponse:
        answer = generate_assistant_answer(payload.message, list_servers(session))
        return AssistantResponse(answer=answer)

    @app.post("/api/ai/extract-server", response_model=ExtractServerResponse)
    def post_extract_server(payload: ExtractServerRequest) -> ExtractServerResponse:
        try:
            extracted = extract_server_info(payload.description)
            return ExtractServerResponse(success=True, data=extracted)
        except Exception as e:
            return ExtractServerResponse(success=False, error=str(e))

    return app


app = create_app()
