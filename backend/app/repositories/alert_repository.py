"""Persistence operations for anomaly alerts."""

from __future__ import annotations

import sqlite3

from backend.app.models import AlertRecord


def create_alert(connection: sqlite3.Connection, record: AlertRecord) -> int:
    cursor = connection.execute(
        """
        INSERT INTO alerts (traffic_log_id, alert_type, severity, message)
        VALUES (?, ?, ?, ?)
        """,
        (record.traffic_log_id, record.alert_type, record.severity, record.message),
    )
    return int(cursor.lastrowid)


def list_alerts(
    connection: sqlite3.Connection,
    *,
    limit: int,
    offset: int,
    severity: str | None = None,
) -> tuple[list[sqlite3.Row], int]:
    filters: list[str] = []
    values: list[object] = []
    if severity:
        filters.append("severity = ?")
        values.append(severity)

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    total = connection.execute(
        f"SELECT COUNT(*) FROM alerts {where_clause}",
        values,
    ).fetchone()[0]
    rows = connection.execute(
        f"""
        SELECT id, traffic_log_id, alert_type, severity, message, created_at
        FROM alerts
        {where_clause}
        ORDER BY created_at DESC, id DESC
        LIMIT ? OFFSET ?
        """,
        [*values, limit, offset],
    ).fetchall()
    return rows, int(total)
