"""HTTP routes for traffic logs, alerts, metrics, and predictions."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from backend.app.schemas import (
    AlertListResponse,
    HealthResponse,
    MetricsResponse,
    PredictionRequest,
    PredictionResponse,
    TrafficListResponse,
    TrafficLogResponse,
)
from backend.app.services.metrics_service import get_dashboard_metrics
from backend.app.services.prediction_service import get_prediction_service
from backend.app.services.traffic_service import (
    get_alerts,
    get_traffic_log,
    get_traffic_logs,
)


router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health() -> HealthResponse:
    prediction_service = get_prediction_service()
    return HealthResponse(
        status="ok",
        database="ready",
        model_loaded=prediction_service.is_model_loaded,
    )


@router.get("/api/traffic", response_model=TrafficListResponse, tags=["traffic"])
def list_traffic(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    prediction: str | None = Query(default=None, pattern="^(normal|anomaly)$"),
    severity: str | None = Query(default=None, pattern="^(low|medium|high|critical)$"),
) -> TrafficListResponse:
    return get_traffic_logs(limit=limit, offset=offset, prediction=prediction, severity=severity)


@router.get("/api/traffic/{traffic_id}", response_model=TrafficLogResponse, tags=["traffic"])
def read_traffic_log(traffic_id: int) -> TrafficLogResponse:
    traffic_log = get_traffic_log(traffic_id)
    if traffic_log is None:
        raise HTTPException(status_code=404, detail="Traffic log not found.")
    return traffic_log


@router.get("/api/alerts", response_model=AlertListResponse, tags=["alerts"])
def list_alerts(
    limit: int = Query(default=50, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    severity: str | None = Query(default=None, pattern="^(low|medium|high|critical)$"),
) -> AlertListResponse:
    return get_alerts(limit=limit, offset=offset, severity=severity)


@router.get("/api/metrics", response_model=MetricsResponse, tags=["metrics"])
def read_metrics() -> MetricsResponse:
    return get_dashboard_metrics()


@router.post("/api/predict", response_model=PredictionResponse, tags=["prediction"])
def predict(payload: PredictionRequest) -> PredictionResponse:
    return get_prediction_service().predict(payload)
