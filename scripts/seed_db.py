"""Seed the local backend SQLite database with traffic logs and model metadata."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.db.database import initialize_database, session_scope
from backend.app.models import AlertRecord, ModelRunRecord, TrafficLogRecord
from backend.app.repositories.alert_repository import create_alert
from backend.app.repositories.model_run_repository import create_model_run
from backend.app.repositories.traffic_repository import create_traffic_log


DEFAULT_PROCESSED_DATA = Path("data/processed/traffic_processed.csv")
DEFAULT_METRICS_PATH = Path("reports/model_metrics.json")


def _severity(label: str, score: float) -> str:
    if label == "normal":
        return "low"
    if score >= 0.9:
        return "critical"
    if score >= 0.75:
        return "high"
    return "medium"


def seed_database(
    processed_data_path: Path = DEFAULT_PROCESSED_DATA,
    metrics_path: Path = DEFAULT_METRICS_PATH,
    limit: int = 500,
) -> dict[str, int]:
    initialize_database()
    frame = pd.read_csv(processed_data_path, nrows=limit)
    metrics = json.loads(metrics_path.read_text(encoding="utf-8")) if metrics_path.is_file() else {}
    base_time = datetime(2026, 7, 13, 9, 0, tzinfo=timezone.utc)

    traffic_count = 0
    alert_count = 0
    with session_scope() as connection:
        connection.execute("DELETE FROM alerts")
        connection.execute("DELETE FROM traffic_logs")
        connection.execute("DELETE FROM model_runs")

        for index, row in frame.reset_index(drop=True).iterrows():
            label = "anomaly" if int(row["binary_label"]) == 1 else "normal"
            score = 0.92 if label == "anomaly" else 0.08
            severity = _severity(label, score)
            timestamp = base_time + timedelta(seconds=index * 30)
            traffic_id = create_traffic_log(
                connection,
                TrafficLogRecord(
                    timestamp=timestamp.isoformat(),
                    src_ip=f"192.168.{index % 20}.{10 + index % 200}",
                    dst_ip=f"10.0.{index % 8}.{5 + index % 120}",
                    src_port=49152 + (index % 12000),
                    dst_port=int(row["dst_port"]),
                    protocol="TCP" if int(row["dst_port"]) in {80, 443} else "UDP",
                    duration=float(row["flow_duration_us"]) / 1_000_000.0,
                    bytes=int(row["total_bytes"]),
                    packets=max(int(row["total_packets"]), 1),
                    label=str(row["attack_type"]),
                    prediction=label,
                    anomaly_score=score,
                    severity=severity,
                ),
            )
            traffic_count += 1
            if label == "anomaly":
                create_alert(
                    connection,
                    AlertRecord(
                        traffic_log_id=traffic_id,
                        alert_type="seeded_label",
                        severity=severity,
                        message=f"Seeded CICIDS2017 record labelled {row['attack_type']}.",
                    ),
                )
                alert_count += 1

        create_model_run(
            connection,
            ModelRunRecord(
                model_version="baseline_model",
                algorithm="RandomForestClassifier",
                dataset_name=processed_data_path.name,
                accuracy=metrics.get("accuracy"),
                precision=metrics.get("precision"),
                recall=metrics.get("recall"),
                f1_score=metrics.get("f1_score"),
                artifact_path="models/baseline_model.pkl",
            ),
        )

    return {"traffic_logs": traffic_count, "alerts": alert_count, "model_runs": 1}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--processed-data", type=Path, default=DEFAULT_PROCESSED_DATA)
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS_PATH)
    parser.add_argument("--limit", type=int, default=500)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = seed_database(
        processed_data_path=args.processed_data,
        metrics_path=args.metrics,
        limit=args.limit,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
