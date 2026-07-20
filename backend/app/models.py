"""Persistence data containers used by repositories and services."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TrafficLogRecord:
    timestamp: str
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str
    duration: float
    bytes: int
    packets: int
    label: str | None
    prediction: str
    anomaly_score: float
    severity: str


@dataclass(frozen=True)
class AlertRecord:
    traffic_log_id: int
    alert_type: str
    severity: str
    message: str


@dataclass(frozen=True)
class ModelRunRecord:
    model_version: str
    algorithm: str
    dataset_name: str
    accuracy: float | None
    precision: float | None
    recall: float | None
    f1_score: float | None
    artifact_path: str
