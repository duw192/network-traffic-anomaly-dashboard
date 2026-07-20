from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from backend.app.db.database import initialize_database, session_scope
from backend.app.main import create_app
from backend.app.models import AlertRecord, TrafficLogRecord
from backend.app.repositories.alert_repository import create_alert
from backend.app.repositories.traffic_repository import create_traffic_log
from backend.app.services.prediction_service import get_prediction_service


class BackendApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temporary_directory.name) / "test.db"
        os.environ["DATABASE_URL"] = f"sqlite:///{self.database_path}"
        get_prediction_service.cache_clear()
        initialize_database()

        with session_scope() as connection:
            traffic_id = create_traffic_log(
                connection,
                TrafficLogRecord(
                    timestamp="2026-07-13T09:00:00+00:00",
                    src_ip="192.168.1.10",
                    dst_ip="10.0.0.5",
                    src_port=51520,
                    dst_port=443,
                    protocol="TCP",
                    duration=2.4,
                    bytes=15000,
                    packets=120,
                    label="BENIGN",
                    prediction="normal",
                    anomaly_score=0.08,
                    severity="low",
                ),
            )
            create_alert(
                connection,
                AlertRecord(
                    traffic_log_id=traffic_id,
                    alert_type="test",
                    severity="low",
                    message="Seeded test alert.",
                ),
            )

        self.client = TestClient(create_app())

    def tearDown(self) -> None:
        get_prediction_service.cache_clear()
        os.environ.pop("DATABASE_URL", None)
        self.temporary_directory.cleanup()

    def test_health_traffic_alerts_and_metrics(self) -> None:
        self.assertEqual(self.client.get("/health").status_code, 200)

        traffic_response = self.client.get("/api/traffic?limit=10")
        self.assertEqual(traffic_response.status_code, 200)
        self.assertEqual(traffic_response.json()["total"], 1)

        alert_response = self.client.get("/api/alerts")
        self.assertEqual(alert_response.status_code, 200)
        self.assertEqual(alert_response.json()["total"], 1)

        metrics_response = self.client.get("/api/metrics")
        self.assertEqual(metrics_response.status_code, 200)
        self.assertEqual(metrics_response.json()["total_traffic"], 1)

    def test_prediction_persists_traffic_record(self) -> None:
        response = self.client.post(
            "/api/predict",
            json={
                "src_ip": "192.168.1.11",
                "dst_ip": "10.0.0.8",
                "src_port": 51521,
                "dst_port": 443,
                "protocol": "TCP",
                "duration": 1.4,
                "bytes": 9000,
                "packets": 80,
            },
        )

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn(body["label"], {"normal", "anomaly"})
        self.assertIsNotNone(body["traffic_log_id"])

        traffic_response = self.client.get("/api/traffic")
        self.assertEqual(traffic_response.json()["total"], 2)


if __name__ == "__main__":
    unittest.main()
