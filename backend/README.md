# Backend

FastAPI backend for network traffic APIs, anomaly detection workflows, and dashboard data access.

Planned stack:

- FastAPI.
- SQLAlchemy.
- PostgreSQL.
- Pydantic.
- Alembic.

No backend implementation has been added yet.

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

