"""Prediction service for the trained baseline model."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from backend.app.core.config import get_settings
from backend.app.db.database import session_scope
from backend.app.models import AlertRecord, TrafficLogRecord
from backend.app.repositories.alert_repository import create_alert
from backend.app.repositories.traffic_repository import create_traffic_log
from backend.app.schemas import PredictionRequest, PredictionResponse, Severity


WEB_PORTS = {80, 443, 8000, 8080, 8443}
DNS_PORTS = {53}


def _severity_from_score(score: float) -> Severity:
    if score >= 0.9:
        return "critical"
    if score >= 0.75:
        return "high"
    if score >= 0.5:
        return "medium"
    return "low"


def _port_category(dst_port: int) -> str:
    if dst_port <= 1023:
        return "well_known"
    if dst_port <= 49151:
        return "registered"
    return "dynamic_private"


class PredictionService:
    def __init__(self) -> None:
        settings = get_settings()
        self.model_path = Path(settings.model_path)
        self.metadata_path = Path(settings.preprocessing_metadata_path)
        self.model_version = self.model_path.stem
        self._bundle: dict[str, Any] | None = None
        self._metadata: dict[str, Any] | None = None
        if self.model_path.is_file() and self.metadata_path.is_file():
            self._bundle = joblib.load(self.model_path)
            self._metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))

    @property
    def is_model_loaded(self) -> bool:
        return self._bundle is not None and self._metadata is not None

    def _build_feature_frame(self, payload: PredictionRequest) -> pd.DataFrame:
        if self._bundle is None or self._metadata is None:
            raise RuntimeError("Model artifact or preprocessing metadata is not available.")

        duration_seconds = payload.duration
        total_packets = float(payload.packets)
        total_bytes = float(payload.bytes)
        bytes_per_packet = total_bytes / total_packets
        packets_per_second = total_packets / duration_seconds
        bytes_per_second = total_bytes / duration_seconds
        flow_duration_us = duration_seconds * 1_000_000.0
        port_category = _port_category(payload.dst_port)

        values: dict[str, float | int] = {
            "is_well_known_port": int(payload.dst_port <= 1023),
            "is_web_port": int(payload.dst_port in WEB_PORTS),
            "is_dns_port": int(payload.dst_port in DNS_PORTS),
            "is_high_port": int(payload.dst_port >= 49152),
            "port_category_well_known": int(port_category == "well_known"),
            "port_category_registered": int(port_category == "registered"),
            "port_category_dynamic_private": int(port_category == "dynamic_private"),
        }
        raw_numeric = {
            "dst_port": float(payload.dst_port),
            "flow_duration_us": flow_duration_us,
            "total_packets": total_packets,
            "total_bytes": total_bytes,
            "bytes_per_packet": bytes_per_packet,
            "packets_per_second": packets_per_second,
            "bytes_per_second": bytes_per_second,
        }

        scaling = self._metadata.get("scaling_parameters", {})
        for feature_name, parameters in scaling.items():
            source_column = parameters["source_column"]
            transformed = np.log1p(max(raw_numeric[source_column], 0.0))
            values[feature_name] = (
                transformed - float(parameters["center_log_median"])
            ) / float(parameters["scale_log_iqr"])

        feature_columns = self._bundle["feature_columns"]
        return pd.DataFrame([{column: values[column] for column in feature_columns}])

    def predict(self, payload: PredictionRequest) -> PredictionResponse:
        if self._bundle is None:
            score = 0.0
            prediction = 0
        else:
            frame = self._build_feature_frame(payload)
            model = self._bundle["model"]
            prediction = int(model.predict(frame)[0])
            if hasattr(model, "predict_proba"):
                score = float(model.predict_proba(frame)[0][1])
            else:
                score = float(prediction)

        label = "anomaly" if prediction == 1 else "normal"
        severity = _severity_from_score(score) if label == "anomaly" else "low"

        traffic_record = TrafficLogRecord(
            timestamp=payload.timestamp.isoformat(),
            src_ip=payload.src_ip,
            dst_ip=payload.dst_ip,
            src_port=payload.src_port,
            dst_port=payload.dst_port,
            protocol=payload.protocol.upper(),
            duration=payload.duration,
            bytes=payload.bytes,
            packets=payload.packets,
            label=None,
            prediction=label,
            anomaly_score=score,
            severity=severity,
        )

        alert_id: int | None = None
        with session_scope() as connection:
            traffic_log_id = create_traffic_log(connection, traffic_record)
            if label == "anomaly":
                alert_id = create_alert(
                    connection,
                    AlertRecord(
                        traffic_log_id=traffic_log_id,
                        alert_type="model_prediction",
                        severity=severity,
                        message=f"Baseline model flagged traffic as {severity} severity.",
                    ),
                )

        return PredictionResponse(
            prediction=prediction,
            label=label,
            anomaly_score=score,
            severity=severity,
            model_version=self.model_version,
            traffic_log_id=traffic_log_id,
            alert_id=alert_id,
        )


@lru_cache(maxsize=1)
def get_prediction_service() -> PredictionService:
    return PredictionService()
