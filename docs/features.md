# Network Traffic Feature Contract

## 1. Purpose

This document defines the Day 05 feature-engineering contract for the Network Traffic Anomaly Dashboard. It connects the CICIDS2017 source columns to a compact, explainable dataset that can serve both the Day 07 baseline model and later dashboard/database work.

The current `MachineLearningCVE` sample is flow-based but does not contain timestamp, source/destination IP, source port, or protocol. The first MVP therefore uses destination-port, duration, packet, byte, rate, and attack-label information only.

## 2. Pipeline Contract

| Stage | Default input | Default output | Responsibility |
|---|---|---|---|
| Ingestion | `data/raw/sample.csv` | `data/processed/traffic_ingested.csv` | Normalize headers, validate required columns, replace numeric infinity, report source quality |
| Preprocessing | `data/raw/sample.csv` | `data/processed/traffic_processed.csv` | Remove duplicate rows, clean/impute values, engineer/encode/scale features |
| Metadata | Preprocessing run | `data/processed/preprocessing_metadata.json` | Persist cleaning counts, label mapping, model features, medians, and scaling parameters |

All paths can be overridden through CLI flags. Generated CSV/JSON artifacts remain local because `data/processed/*` is ignored by Git.

## 3. Required Source Columns

Headers are trimmed and converted to `snake_case` during ingestion.

| CICIDS2017 header | Normalized name | Use |
|---|---|---|
| `Destination Port` | `destination_port` | Port context, category, and service flags |
| `Flow Duration` | `flow_duration` | Flow duration in microseconds and rate denominator |
| `Total Fwd Packets` | `total_fwd_packets` | Total packet count |
| `Total Backward Packets` | `total_backward_packets` | Total packet count |
| `Total Length of Fwd Packets` | `total_length_of_fwd_packets` | Total byte count |
| `Total Length of Bwd Packets` | `total_length_of_bwd_packets` | Total byte count |
| `Label` | `label` | Original attack type and binary target |

The pipeline fails early with an actionable error if any required column is missing.

## 4. Cleaning Rules

1. Normalize UTF-8 BOM, surrounding whitespace, punctuation, and casing in headers.
2. Replace numeric `+inf`/`-inf` with missing values.
3. Remove exact raw duplicate rows by default. Use `--keep-duplicates` only for a deliberate diagnostic run.
4. Coerce required numeric fields; malformed values become missing.
5. Treat ports outside `0..65535` and negative duration/packet/byte values as invalid.
6. Impute invalid/missing required numeric values with the median computed from the current training dataset.
7. For zero-duration or zero-packet divisions, create missing rates first and then median-impute; never emit infinity.
8. Preserve the cleaned source attack name as `attack_type`.
9. Map `BENIGN`, `NORMAL`, or `0` (case-insensitive) to `binary_label = 0`; every other non-empty label maps to `1`.
10. After feature projection, remove duplicate `model features + binary_label` rows to reduce train/test leakage. Keep identical feature vectors with conflicting targets because they represent label ambiguity that must remain visible.

The exact medians and transformation parameters are written to `preprocessing_metadata.json`. Day 07 training and later inference must use that metadata rather than recomputing values per request.

## 5. Dashboard/Context Columns

These columns remain in interpretable units for API and dashboard use.

| Column | Type/unit | Meaning |
|---|---|---|
| `record_id` | integer | Stable row identifier within one generated artifact |
| `dst_port` | integer | Destination port (`0..65535`) |
| `flow_duration_us` | float, microseconds | Original CICIDS2017 flow duration |
| `total_packets` | float | Forward + backward packets |
| `total_bytes` | float, bytes | Forward + backward packet length |
| `bytes_per_packet` | float | `total_bytes / total_packets` |
| `packets_per_second` | float | `total_packets / (flow_duration_us / 1,000,000)` |
| `bytes_per_second` | float | `total_bytes / (flow_duration_us / 1,000,000)` |
| `port_category` | category | IANA-style numeric port range |
| `attack_type` | string | Cleaned original CICIDS2017 label |
| `binary_label` | integer | Target: `0 = normal`, `1 = anomaly` |

## 6. Encoded Port Features

| Feature | Rule |
|---|---|
| `is_well_known_port` | `dst_port <= 1023` |
| `is_web_port` | Port in `{80, 443, 8000, 8080, 8443}` |
| `is_dns_port` | Port equals `53` |
| `is_high_port` | `dst_port >= 49152` |
| `port_category_well_known` | Port range `0..1023` |
| `port_category_registered` | Port range `1024..49151` |
| `port_category_dynamic_private` | Port range `49152..65535` |

The three `port_category_*` columns are one-hot encoded. `port_category` remains as readable context and must not be passed directly to a numeric model.

## 7. Scaled Model Features

The CICIDS2017 numeric distributions are strongly right-skewed. Each model base value is therefore transformed with `log1p(max(value, 0))`, then robust-scaled:

```text
scaled_value = (log1p(value) - median_log) / IQR_log
```

If the interquartile range is zero, the scale is set to `1.0`. Parameters are stored in metadata.

| Output feature | Source |
|---|---|
| `feature_dst_port_scaled` | `dst_port` |
| `feature_flow_duration_us_scaled` | `flow_duration_us` |
| `feature_total_packets_scaled` | `total_packets` |
| `feature_total_bytes_scaled` | `total_bytes` |
| `feature_bytes_per_packet_scaled` | `bytes_per_packet` |
| `feature_packets_per_second_scaled` | `packets_per_second` |
| `feature_bytes_per_second_scaled` | `bytes_per_second` |

The Day 07 model input contract is the seven scaled features plus the four service flags and three port-category one-hot columns. The target is `binary_label`. Exclude `record_id`, readable context columns, `attack_type`, and `binary_label` from `X`.

## 8. Current Day 05 Output Profile

The full local sample run produced:

| Check | Result |
|---|---:|
| Raw rows | 50,000 |
| Exact duplicate rows removed | 2,945 |
| Feature-level duplicate rows removed | 1,198 |
| Processed rows | 45,857 |
| Output columns | 25 |
| Normal rows (`0`) | 23,760 |
| Anomaly rows (`1`) | 22,097 |
| Missing cells in final output | 0 |
| Infinite numeric cells in final output | 0 |

The processed class distribution differs from the original 25k/25k sample because raw and feature-level duplicate removal is performed before model training. Thirty-two feature vectors have conflicting binary labels; both targets are kept so the ambiguity is not hidden.

## 9. Known Limitations

- No timestamp: the current artifact cannot support a true chronological traffic trend or time-based split.
- No source/destination IP: top-IP and IP-level drill-down are unavailable.
- No protocol field: protocol distribution and TCP/UDP/ICMP flags cannot be produced reliably.
- A random train/test split on this balanced sample is acceptable for the MVP baseline, but final reporting must state that it is not a chronological/network-environment generalization test.
- Rate features can contain legitimate extreme values for very short flows; log + robust scaling reduces their effect but does not remove real outliers.

## 10. Commands

```powershell
python -m pip install -r pipelines/requirements.txt
python pipelines/ingest.py --input data/raw/sample.csv --output data/processed/traffic_ingested.csv
python pipelines/preprocess.py --input data/raw/sample.csv --output data/processed/traffic_processed.csv --metadata-output data/processed/preprocessing_metadata.json
python -m unittest discover -s tests -p "test_*.py" -v
```
