"""Application settings loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "Network Traffic Anomaly Dashboard API"
    app_version: str = "0.1.0"
    database_url: str = "sqlite:///backend/dev.db"
    model_path: str = "models/baseline_model.pkl"
    preprocessing_metadata_path: str = "data/processed/preprocessing_metadata.json"
    metrics_path: str = "reports/model_metrics.json"
    cors_origins: list[str] | None = None


def _parse_cors_origins(value: str | None) -> list[str]:
    if not value:
        return ["http://localhost:5173", "http://127.0.0.1:5173"]
    return [origin.strip() for origin in value.split(",") if origin.strip()]


def get_settings() -> Settings:
    return Settings(
        app_name=os.getenv("APP_NAME", Settings.app_name),
        app_version=os.getenv("APP_VERSION", Settings.app_version),
        database_url=os.getenv("DATABASE_URL", Settings.database_url),
        model_path=os.getenv("MODEL_PATH", Settings.model_path),
        preprocessing_metadata_path=os.getenv(
            "PREPROCESSING_METADATA_PATH",
            Settings.preprocessing_metadata_path,
        ),
        metrics_path=os.getenv("MODEL_METRICS_PATH", Settings.metrics_path),
        cors_origins=_parse_cors_origins(os.getenv("CORS_ORIGINS")),
    )


def resolve_sqlite_path(database_url: str) -> Path:
    if database_url.startswith("sqlite:///"):
        return Path(database_url.removeprefix("sqlite:///"))
    if database_url.startswith("sqlite://"):
        return Path(database_url.removeprefix("sqlite://"))
    raise ValueError("Only sqlite database URLs are supported by the current local MVP.")
