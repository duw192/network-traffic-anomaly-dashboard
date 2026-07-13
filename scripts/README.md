# Scripts

Developer and data-preparation automation.

## Available script

- `create_dataset_sample.py`: creates a reproducible, balanced CICIDS2017 sample with reservoir sampling, bounded memory usage, configurable labels, output path, class size, and random seed.

Run from the repository root:

```powershell
python scripts/create_dataset_sample.py data/raw/MachineLearningCVE/<source-file>.csv --output data/raw/sample.csv
```

Keep reusable ingestion, cleaning, and feature logic in `pipelines/`; scripts should remain thin developer-facing entry points.
