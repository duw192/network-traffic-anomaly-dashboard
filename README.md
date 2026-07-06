# network-traffic-anomaly-dashboard

Network Traffic Anomaly Detection and Monitoring Dashboard.

This repository is currently in the project-structure stage. It does not contain a working demo, sample dataset, trained model, or production API/UI logic yet.

## Planned Stack

- Frontend: React, TypeScript, Vite, Tailwind CSS, charting library to be selected later.
- Backend: FastAPI, Python, SQLAlchemy, PostgreSQL.
- Data and ML: Pandas, NumPy, scikit-learn, model registry folder.
- Infrastructure: Docker, Docker Compose, CI/CD, cloud deployment later.

The frontend will be a custom web app, not Streamlit.

## Project Structure

```text
.
|-- frontend/          React + TypeScript dashboard app
|-- backend/           FastAPI service and API modules
|-- ml/                Feature engineering, training, inference, evaluation
|-- pipelines/         Data ingestion, processing, orchestration
|-- data/              Raw, external, and processed datasets
|-- models/            Trained model registry artifacts
|-- infra/             Docker, Kubernetes, Terraform, deployment assets
|-- configs/           Shared app and environment configuration templates
|-- scripts/           Developer and automation scripts
|-- docs/              Architecture, dataset, API, and development notes
|-- notebooks/         Research and exploration notebooks
|-- reports/           Analysis reports and generated figures
|-- tests/             Cross-service integration tests
`-- .github/           GitHub workflows
```

## Target Product

The final product will analyze network traffic flow records, detect abnormal behavior, and present network/security KPIs through a modern dashboard.

Planned MVP modules:

- Dataset ingestion from CICIDS2017, UNSW-NB15, or a compatible CSV flow dataset.
- Data cleaning and feature engineering pipeline.
- Binary anomaly model for normal vs abnormal traffic.
- Backend REST APIs for traffic logs, anomaly alerts, model predictions, and metrics.
- React dashboard for traffic trends, protocol usage, top IPs, anomaly counts, and alert details.

## Current Status

- Repository initialized.
- Professional folder structure created.
- No implementation logic added yet.

