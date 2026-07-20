"""FastAPI application entry point."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import router
from backend.app.core.config import get_settings
from backend.app.db.database import initialize_database


def create_app() -> FastAPI:
    settings = get_settings()
    initialize_database()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Network traffic anomaly dashboard API.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


app = create_app()
