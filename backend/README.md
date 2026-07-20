# Backend

FastAPI backend for network traffic APIs, anomaly detection workflows, and dashboard data access.

Implemented local MVP stack:

- FastAPI.
- Pydantic.
- SQLite.
- `joblib` baseline model loading.

PostgreSQL, SQLAlchemy, and Alembic remain planned for the Docker/integration phase.

## Run Locally

```powershell
python -m pip install -r backend/requirements.txt
python scripts/seed_db.py --limit 500
python -m uvicorn backend.app.main:app --reload
```

API docs are available at `http://localhost:8000/docs`.

## Implemented Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Service, database, and model readiness |
| `GET` | `/api/traffic` | Paginated/filterable traffic logs |
| `GET` | `/api/traffic/{traffic_id}` | Single traffic log |
| `GET` | `/api/alerts` | Paginated/filterable alerts |
| `GET` | `/api/metrics` | Dashboard counts and model metrics |
| `POST` | `/api/predict` | Run baseline prediction and persist the result |

## Structure

```text
backend/
|-- app/
|   |-- api/
|   |   `-- v1/
|   |-- core/
|   |-- db/
|   |-- models/
|   |-- repositories/
|   |-- schemas/
|   |-- services/
|   `-- workers/
|-- alembic/
|   `-- versions/
`-- tests/
```
