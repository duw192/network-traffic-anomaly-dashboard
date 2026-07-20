# Database Design

## Purpose

The database stores traffic logs, anomaly alerts, and model-run metadata used by the FastAPI backend and future React dashboard.

The Day 11 implementation uses SQLite for a local MVP. PostgreSQL remains the target database for the Docker/integration phase, but route and schema contracts are intentionally database-agnostic.

## Configuration

Default local database URL:

```text
sqlite:///backend/dev.db
```

Override with:

```powershell
$env:DATABASE_URL = "sqlite:///backend/dev.db"
```

The current backend supports SQLite URLs. PostgreSQL support should be added when Docker Compose and migrations are implemented.

## Tables

### `traffic_logs`

| Column | Type | Required | Description |
|---|---|---|---|
| `id` | Integer | Yes | Primary key |
| `timestamp` | Text datetime | Yes | Flow timestamp or deterministic demo timestamp |
| `src_ip` | Text | Yes | Source IP address |
| `dst_ip` | Text | Yes | Destination IP address |
| `src_port` | Integer | Yes | Source port |
| `dst_port` | Integer | Yes | Destination port |
| `protocol` | Text | Yes | Protocol label such as `TCP` or `UDP` |
| `duration` | Real | Yes | Flow duration in seconds |
| `bytes` | Integer | Yes | Total bytes |
| `packets` | Integer | Yes | Total packets |
| `label` | Text | No | Known dataset label when available |
| `prediction` | Text | Yes | `normal` or `anomaly` |
| `anomaly_score` | Real | Yes | Model anomaly probability/score |
| `severity` | Text | Yes | `low`, `medium`, `high`, or `critical` |
| `created_at` | Text datetime | Yes | Insert timestamp |

### `alerts`

| Column | Type | Required | Description |
|---|---|---|---|
| `id` | Integer | Yes | Primary key |
| `traffic_log_id` | Integer | Yes | Related `traffic_logs.id` |
| `alert_type` | Text | Yes | Alert source or category |
| `severity` | Text | Yes | `low`, `medium`, `high`, or `critical` |
| `message` | Text | Yes | Human-readable alert message |
| `created_at` | Text datetime | Yes | Insert timestamp |

### `model_runs`

| Column | Type | Required | Description |
|---|---|---|---|
| `id` | Integer | Yes | Primary key |
| `model_version` | Text | Yes | Model version or artifact stem |
| `algorithm` | Text | Yes | Training algorithm |
| `dataset_name` | Text | Yes | Dataset artifact used for training/evaluation |
| `accuracy` | Real | No | Accuracy score |
| `precision` | Real | No | Precision score |
| `recall` | Real | No | Recall score |
| `f1_score` | Real | No | F1 score |
| `artifact_path` | Text | Yes | Saved model path |
| `created_at` | Text datetime | Yes | Insert timestamp |

## Seed Data

Seed local demo records with:

```powershell
python scripts/seed_db.py --limit 500
```

The seed script:

- reads processed traffic features from `data/processed/traffic_processed.csv`;
- creates deterministic demo IPs, ports, protocols, and timestamps;
- maps `binary_label=0` to `normal` and `binary_label=1` to `anomaly`;
- creates alerts for anomalous rows;
- stores Day 07 model metrics when `reports/model_metrics.json` exists.

## Repository Boundary

Routes do not write SQL directly. The allowed call direction is:

```text
route -> service -> repository -> database
```

This keeps API validation, business logic, and persistence logic separate for later PostgreSQL and migration upgrades.
