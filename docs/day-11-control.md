# Day 11 Control - Database and Mock Data

## Scope

Day 11 follows `ke_hoach_3_tuan_network_anomaly_dashboard.docx`: implement local persistence for traffic logs, alerts, model-run metadata, and seed data for dashboard/API demos.

## Implementation Summary

| Item | Result |
|---|---|
| Database setup | `backend/app/db/database.py` |
| Day 11 compatibility module | `backend/app/database.py` |
| Persistence models | `backend/app/models.py` |
| Traffic repository | `backend/app/repositories/traffic_repository.py` |
| Alert repository | `backend/app/repositories/alert_repository.py` |
| Model-run repository | `backend/app/repositories/model_run_repository.py` |
| Seed script | `scripts/seed_db.py` |
| Database docs | `docs/database.md` |

## Tables

| Table | Purpose |
|---|---|
| `traffic_logs` | Stores flow metadata, known labels, predictions, anomaly score, severity, and creation time |
| `alerts` | Stores anomaly alerts linked to traffic logs |
| `model_runs` | Stores baseline model metadata and evaluation metrics |

## Seed Command

```powershell
python scripts/seed_db.py --limit 500
```

Default input/output behavior:

- Reads `data/processed/traffic_processed.csv`.
- Reads `reports/model_metrics.json` when available.
- Writes SQLite data to `backend/dev.db` through `DATABASE_URL=sqlite:///backend/dev.db`.
- Clears existing local demo rows before reseeding.

## Acceptance Checklist

- [x] Database tables are created automatically on app startup.
- [x] Traffic logs can be inserted, listed, filtered, and fetched by id.
- [x] Alerts can be inserted, listed, and filtered by severity.
- [x] Model-run metadata can be inserted for demo metrics traceability.
- [x] `scripts/seed_db.py` creates traffic logs, anomaly alerts, and one model-run record.
- [x] Generated local SQLite files are ignored by Git.
- [x] Backend tests cover database-backed API behavior.

## Notes

- SQLite is intentionally used for this delivery because it keeps the two-person MVP simple and runnable locally.
- API contracts do not expose SQLite-specific details, so PostgreSQL/SQLAlchemy can replace the repository internals later.
- The seeded source dataset has no real timestamp, source IP, destination IP, source port, or protocol columns. The seed script creates deterministic demo values and keeps the original CICIDS2017 label in `traffic_logs.label`.
