"""Persistence operations for traffic logs."""

from __future__ import annotations

import sqlite3

from backend.app.models import TrafficLogRecord


def create_traffic_log(connection: sqlite3.Connection, record: TrafficLogRecord) -> int:
    cursor = connection.execute(
        """
        INSERT INTO traffic_logs (
            timestamp, src_ip, dst_ip, src_port, dst_port, protocol,
            duration, bytes, packets, label, prediction, anomaly_score, severity
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record.timestamp,
            record.src_ip,
            record.dst_ip,
            record.src_port,
            record.dst_port,
            record.protocol,
            record.duration,
            record.bytes,
            record.packets,
            record.label,
            record.prediction,
            record.anomaly_score,
            record.severity,
        ),
    )
    return int(cursor.lastrowid)


def get_traffic_log(connection: sqlite3.Connection, traffic_id: int) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, timestamp, src_ip, dst_ip, src_port, dst_port, protocol,
               duration, bytes, packets, label, prediction, anomaly_score,
               severity, created_at
        FROM traffic_logs
        WHERE id = ?
        """,
        (traffic_id,),
    ).fetchone()


def list_traffic_logs(
    connection: sqlite3.Connection,
    *,
    limit: int,
    offset: int,
    prediction: str | None = None,
    severity: str | None = None,
) -> tuple[list[sqlite3.Row], int]:
    filters: list[str] = []
    values: list[object] = []
    if prediction:
        filters.append("prediction = ?")
        values.append(prediction)
    if severity:
        filters.append("severity = ?")
        values.append(severity)

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    total = connection.execute(
        f"SELECT COUNT(*) FROM traffic_logs {where_clause}",
        values,
    ).fetchone()[0]
    rows = connection.execute(
        f"""
        SELECT id, timestamp, src_ip, dst_ip, src_port, dst_port, protocol,
               duration, bytes, packets, label, prediction, anomaly_score,
               severity, created_at
        FROM traffic_logs
        {where_clause}
        ORDER BY timestamp DESC, id DESC
        LIMIT ? OFFSET ?
        """,
        [*values, limit, offset],
    ).fetchall()
    return rows, int(total)


def summarize_traffic(connection: sqlite3.Connection) -> dict[str, int | float]:
    row = connection.execute(
        """
        SELECT
            COUNT(*) AS total_traffic,
            SUM(CASE WHEN prediction = 'anomaly' THEN 1 ELSE 0 END) AS anomaly_count,
            SUM(CASE WHEN prediction = 'normal' THEN 1 ELSE 0 END) AS normal_count,
            AVG(anomaly_score) AS average_anomaly_score
        FROM traffic_logs
        """
    ).fetchone()
    return {
        "total_traffic": int(row["total_traffic"] or 0),
        "anomaly_count": int(row["anomaly_count"] or 0),
        "normal_count": int(row["normal_count"] or 0),
        "average_anomaly_score": float(row["average_anomaly_score"] or 0.0),
    }


def severity_counts(connection: sqlite3.Connection) -> dict[str, int]:
    rows = connection.execute(
        """
        SELECT severity, COUNT(*) AS count
        FROM traffic_logs
        GROUP BY severity
        ORDER BY severity
        """
    ).fetchall()
    return {str(row["severity"]): int(row["count"]) for row in rows}
