# Architecture

This document defines the planned high-level architecture. Implementation details will be added after the project structure is approved.

```text
CSV / network flow dataset
        |
        v
Data ingestion pipeline
        |
        v
Cleaning + feature engineering
        |
        v
PostgreSQL database
        |
        v
ML training + inference modules
        |
        v
FastAPI backend
        |
        v
React dashboard
```

## Main Components

- Frontend: browser-based dashboard for monitoring traffic and anomaly alerts.
- Backend: API layer for traffic, anomalies, metrics, predictions, and auth later.
- ML: feature processing, training, evaluation, and inference modules.
- Pipelines: batch ingestion and processing jobs.
- Database: relational storage for traffic records, model predictions, and alert history.

