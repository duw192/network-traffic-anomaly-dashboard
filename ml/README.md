# ML

Machine learning workspace for anomaly detection.

Implemented baseline:

- `ml/train.py` trains a supervised `RandomForestClassifier` when `binary_label` is available.
- `ml/evaluate.py` reloads the saved model bundle, evaluates the fixed test split, writes metrics JSON, and exports a confusion-matrix PNG.

Default command:

```powershell
python ml/train.py
```

Default outputs:

- `models/baseline_model.pkl`
- `reports/model_metrics.json`
- `reports/confusion_matrix.png`

The model bundle stores feature names, target column, train/test class distribution, random seed, and test `record_id` values so evaluation is reproducible.
