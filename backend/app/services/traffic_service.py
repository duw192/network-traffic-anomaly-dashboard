"""Traffic and alert read services."""

from __future__ import annotations

from backend.app.db.database import session_scope
from backend.app.repositories.alert_repository import list_alerts
from backend.app.repositories.traffic_repository import get_traffic_log as fetch_traffic_log
from backend.app.repositories.traffic_repository import list_traffic_logs
from backend.app.schemas import AlertListResponse, AlertResponse, TrafficListResponse, TrafficLogResponse


def _traffic_response(row) -> TrafficLogResponse:
    return TrafficLogResponse(**dict(row))


def _alert_response(row) -> AlertResponse:
    return AlertResponse(**dict(row))


def get_traffic_logs(
    *,
    limit: int,
    offset: int,
    prediction: str | None = None,
    severity: str | None = None,
) -> TrafficListResponse:
    with session_scope() as connection:
        rows, total = list_traffic_logs(
            connection,
            limit=limit,
            offset=offset,
            prediction=prediction,
            severity=severity,
        )
    return TrafficListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[_traffic_response(row) for row in rows],
    )


def get_traffic_log(traffic_id: int) -> TrafficLogResponse | None:
    with session_scope() as connection:
        row = fetch_traffic_log(connection, traffic_id)
    return _traffic_response(row) if row is not None else None


def get_alerts(
    *,
    limit: int,
    offset: int,
    severity: str | None = None,
) -> AlertListResponse:
    with session_scope() as connection:
        rows, total = list_alerts(connection, limit=limit, offset=offset, severity=severity)
    return AlertListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[_alert_response(row) for row in rows],
    )
