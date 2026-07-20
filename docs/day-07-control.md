# Day 07 Control - ML Baseline

## Scope

Day 07 follows `ke_hoach_3_tuan_network_anomaly_dashboard.docx`: train a simple baseline model, save the model artifact, export evaluation metrics, and generate a confusion matrix.

## Implementation Summary

| Item | Result |
|---|---|
| Training script | `ml/train.py` |
| Evaluation script | `ml/evaluate.py` |
| Input dataset | `data/processed/traffic_processed.csv` |
| Feature contract | `data/processed/preprocessing_metadata.json` -> `model_feature_columns` |
| Target column | `binary_label` |
| Model | `RandomForestClassifier` |
| Split | Stratified 80/20 train/test |
| Random seed | `42` |
| Saved model | `models/baseline_model.pkl` |
| Metrics output | `reports/model_metrics.json` |
| Confusion matrix output | `reports/confusion_matrix.png` |

## Feature Inputs

The baseline uses the 14 model-ready columns exported by the Day 05 preprocessing metadata:

- `is_well_known_port`
- `is_web_port`
- `is_dns_port`
- `is_high_port`
- `port_category_well_known`
- `port_category_registered`
- `port_category_dynamic_private`
- `feature_dst_port_scaled`
- `feature_flow_duration_us_scaled`
- `feature_total_packets_scaled`
- `feature_total_bytes_scaled`
- `feature_bytes_per_packet_scaled`
- `feature_packets_per_second_scaled`
- `feature_bytes_per_second_scaled`

## Reproducibility Contract

`models/baseline_model.pkl` is a `joblib` bundle, not only a raw estimator. It stores:

- fitted `RandomForestClassifier`;
- feature column order;
- target column name;
- source data and metadata paths;
- train/test row counts;
- train/test class distribution;
- random state and test size;
- test `record_id` values used by `ml/evaluate.py`.

This makes evaluation repeatable even if the processed CSV row order is later changed.

## Commands

Train and evaluate in one step:

```powershell
python ml/train.py
```

Evaluate an existing model bundle:

```powershell
python ml/evaluate.py
```

Custom paths:

```powershell
python ml/train.py `
  --data data/processed/traffic_processed.csv `
  --metadata data/processed/preprocessing_metadata.json `
  --model-output models/baseline_model.pkl `
  --metrics-output reports/model_metrics.json `
  --confusion-matrix-output reports/confusion_matrix.png
```

## Evaluation Result

| Metric | Value |
|---|---:|
| Evaluation rows | 9,172 |
| Accuracy | 0.9913 |
| Precision | 0.9918 |
| Recall | 0.9900 |
| F1-score | 0.9909 |
| ROC AUC | 0.9996 |

Confusion matrix:

| Actual \\ Predicted | Normal | Anomaly |
|---|---:|---:|
| Normal | 4,716 | 36 |
| Anomaly | 44 | 4,376 |

## Acceptance Checklist

- [x] `ml/train.py` exists and trains a baseline model.
- [x] `ml/evaluate.py` exists and evaluates the saved model.
- [x] Model is saved to `models/baseline_model.pkl`.
- [x] Metrics are saved to `reports/model_metrics.json`.
- [x] Confusion matrix is saved to `reports/confusion_matrix.png`.
- [x] Feature order is loaded from preprocessing metadata.
- [x] Evaluation split is reproducible through saved test `record_id` values.
- [x] Documentation explains commands, artifacts, metrics, and limitations.

## Notes and Limitations

- The current baseline is intentionally simple and optimized for a portfolio MVP, not production IDS deployment.
- The sample is balanced, so metrics should not be interpreted as production traffic prevalence.
- The current CICIDS2017 export does not include timestamp, source IP, destination IP, source port, or protocol, so model behavior is limited to flow duration, byte/packet/rate, and destination-port features.
- Future work should compare Logistic Regression, Isolation Forest, and time/network-split validation once richer data is available.
