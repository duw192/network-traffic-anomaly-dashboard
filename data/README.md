# Data

Dataset artifacts are stored locally and intentionally excluded from Git.

```text
data/
|-- raw/         Original downloaded datasets
|-- external/    Third-party reference files
`-- processed/   Cleaned and transformed datasets
```

Large datasets should not be committed to Git.

Current local Day 05 outputs:

- `data/processed/traffic_processed.csv`: cleaned dashboard/ML dataset.
- `data/processed/preprocessing_metadata.json`: cleaning report, model feature contract, and scaling parameters.

Regenerate both artifacts with `python pipelines/preprocess.py` from the repository root.
