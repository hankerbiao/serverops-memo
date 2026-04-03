"""
ServerOps FastAPI Application.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api import chat_router, config_router, servers_router, tags_router
from backend.app.config import settings
from backend.app.database import get_engine, init_db
from backend.app.services import start_health_check_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Initialize database
    init_db()

    # Initialize AI config default if not exists
    from sqlmodel import Session, select

    from backend.app.models.config import AIConfig

    with Session(get_engine()) as session:
        statement = select(AIConfig).limit(1)
        existing = session.exec(statement).first()
        if not existing:
            # Create default AI config from settings
            default_config = AIConfig(
                ai_url=settings.AI_URL,
                ai_model=settings.AI_MODEL,
            )
            session.add(default_config)
            session.commit()
            print(f"Initialized AI config with default URL: {settings.AI_URL}")

    # Start health check scheduler
    from sqlmodel import Session

    def session_factory():
        return Session(get_engine())

    start_health_check_scheduler(session_factory)

    yield


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Health check endpoint
    @app.get("/api/health")
    def health_check() -> dict[str, str]:
        return {"status": "ok"}

    # Register routers
    app.include_router(servers_router)
    app.include_router(tags_router)
    app.include_router(chat_router)
    app.include_router(config_router)

    return app


# Default app instance
app = create_app()