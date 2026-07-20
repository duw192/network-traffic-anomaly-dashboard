"""Dashboard metrics aggregation service."""

from __future__ import annotations

import json
from pathlib import Path

from backend.app.core.config import get_settings
from backend.app.db.database import session_scope
from backend.app.repositories.traffic_repository import severity_counts, summarize_traffic
from backend.app.schemas import MetricsResponse, ModelMetrics


def _load_model_metrics() -> ModelMetrics:
    metrics_path = Path(get_settings().metrics_path)
    if not metrics_path.is_file():
        return ModelMetrics()
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    return ModelMetrics(
        accuracy=metrics.get("accuracy"),
        precision=metrics.get("precision"),
        recall=metrics.get("recall"),
        f1_score=metrics.get("f1_score"),
        roc_auc=metrics.get("roc_auc"),
    )


def get_dashboard_metrics() -> MetricsResponse:
    with session_scope() as connection:
        summary = summarize_traffic(connection)
        counts = severity_counts(connection)

    total_traffic = int(summary["total_traffic"])
    anomaly_count = int(summary["anomaly_count"])
    anomaly_rate = anomaly_count / total_traffic if total_traffic else 0.0
    return MetricsResponse(
        total_traffic=total_traffic,
        normal_count=int(summary["normal_count"]),
        anomaly_count=anomaly_count,
        anomaly_rate=anomaly_rate,
        average_anomaly_score=float(summary["average_anomaly_score"]),
        severity_counts=counts,
        model_metrics=_load_model_metrics(),
    )
