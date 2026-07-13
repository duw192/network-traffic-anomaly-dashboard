# Pipelines

Day 05 provides a reproducible batch pipeline for the local CICIDS2017 sample.

## Modules

- `ingest.py`: reads CSV, normalizes headers, validates required fields, replaces numeric infinities, and optionally writes a normalized staging file.
- `preprocess.py`: removes exact duplicates, validates and imputes numeric values, maps the binary target, engineers network features, scales model inputs, and writes reproducibility metadata.

## Setup

```powershell
python -m pip install -r pipelines/requirements.txt
```

## Run

Both commands have explicit path flags and repository-relative defaults:

```powershell
python pipelines/ingest.py --input data/raw/sample.csv --output data/processed/traffic_ingested.csv
python pipelines/preprocess.py --input data/raw/sample.csv --output data/processed/traffic_processed.csv --metadata-output data/processed/preprocessing_metadata.json
```

For a fast validation run:

```powershell
python pipelines/preprocess.py --max-rows 100
```

Generated data stays local because `data/processed/*` is ignored by Git. The metadata JSON contains the feature list, label mapping, cleaning counts, medians, and scaling parameters required by training/inference.
