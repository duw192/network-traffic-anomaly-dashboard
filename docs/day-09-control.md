# Day 09 Control - Backend FastAPI Skeleton

## Scope

Day 09 follows `ke_hoach_3_tuan_network_anomaly_dashboard.docx`: create a minimal FastAPI backend with health, traffic, alerts, metrics, and prediction endpoints.

## Implementation Summary

| Item | Result |
|---|---|
| App entry point | `backend/app/main.py` |
| Routes | `backend/app/api/routes.py` |
| Schemas | `backend/app/schemas.py` |
| Prediction service | `backend/app/services/prediction_service.py` |
| Metrics service | `backend/app/services/metrics_service.py` |
| Traffic service | `backend/app/services/traffic_service.py` |
| Backend tests | `backend/tests/test_api.py` |
| Dependencies | `backend/requirements.txt` |

## Endpoints

| Method | Endpoint | Status | Purpose |
|---|---|---|---|
| `GET` | `/health` | Implemented | Service, database, and model readiness |
| `GET` | `/api/traffic` | Implemented | Paginated traffic logs with optional `prediction` and `severity` filters |
| `GET` | `/api/traffic/{traffic_id}` | Implemented | Single traffic log lookup |
| `GET` | `/api/alerts` | Implemented | Paginated anomaly alerts with optional severity filter |
| `GET` | `/api/metrics` | Implemented | Dashboard counts plus model metrics |
| `POST` | `/api/predict` | Implemented | Validate one flow, run baseline prediction, persist traffic/alert result |

## Run Commands

Install backend dependencies:

```powershell
python -m pip install -r backend/requirements.txt
```

Seed local demo data:

```powershell
python scripts/seed_db.py --limit 500
```

Start API:

```powershell
python -m uvicorn backend.app.main:app --reload
```

Open docs:

```text
http://localhost:8000/docs
```

## Prediction Request Example

```json
{
  "src_ip": "192.168.1.10",
  "dst_ip": "10.0.0.5",
  "src_port": 51520,
  "dst_port": 443,
  "protocol": "TCP",
  "duration": 2.4,
  "bytes": 15000,
  "packets": 120
}
```

## Acceptance Checklist

- [x] `backend/app/main.py` creates the FastAPI application.
- [x] `backend/app/api/routes.py` exposes all Day 09 endpoints.
- [x] `backend/app/schemas.py` validates request/response payloads.
- [x] `backend/app/services/prediction_service.py` loads the Day 07 model when artifacts exist.
- [x] `/api/predict` transforms request fields with Day 05 preprocessing metadata.
- [x] `/api/metrics` reads dashboard database counts and Day 07 metrics.
- [x] Route tests cover health, traffic, alerts, metrics, and prediction persistence.

## Notes

- The backend can start even when model artifacts are missing; `/health` reports `model_loaded=false`.
- SQLite is used for the local MVP so the API is demoable before Docker/PostgreSQL work begins.
- PostgreSQL and migrations remain the target for the Docker/integration phase.
