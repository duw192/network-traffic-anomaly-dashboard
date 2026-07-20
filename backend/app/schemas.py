"""Pydantic request and response schemas for the backend API."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["low", "medium", "high", "critical"]
PredictionLabel = Literal["normal", "anomaly"]


class HealthResponse(BaseModel):
    status: Literal["ok"]
    database: Literal["ready"]
    model_loaded: bool


class TrafficLogResponse(BaseModel):
    id: int
    timestamp: datetime
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    duration: float
    bytes: int
    packets: int
    label: str | None = None
    prediction: PredictionLabel
    anomaly_score: float
    severity: Severity
    created_at: datetime


class TrafficListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[TrafficLogResponse]


class AlertResponse(BaseModel):
    id: int
    traffic_log_id: int
    alert_type: str
    severity: Severity
    message: str
    created_at: datetime


class AlertListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[AlertResponse]


class ModelMetrics(BaseModel):
    accuracy: float | None = None
    precision: float | None = None
    recall: float | None = None
    f1_score: float | None = None
    roc_auc: float | None = None


class MetricsResponse(BaseModel):
    total_traffic: int
    normal_count: int
    anomaly_count: int
    anomaly_rate: float
    average_anomaly_score: float
    severity_counts: dict[str, int]
    model_metrics: ModelMetrics


class PredictionRequest(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    src_ip: str = Field(examples=["192.168.1.10"])
    dst_ip: str = Field(examples=["10.0.0.5"])
    src_port: int = Field(ge=0, le=65535)
    dst_port: int = Field(ge=0, le=65535)
    protocol: str = Field(default="TCP", min_length=2, max_length=10)
    duration: float = Field(gt=0, description="Flow duration in seconds.")
    bytes: int = Field(ge=0)
    packets: int = Field(gt=0)


class PredictionResponse(BaseModel):
    prediction: int
    label: PredictionLabel
    anomaly_score: float
    severity: Severity
    model_version: str
    traffic_log_id: int | None = None
    alert_id: int | None = None
