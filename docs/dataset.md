# Dataset

## Current Status

Day 03 decision: use `CICIDS2017` as the primary MVP dataset.

`data/raw/sample.csv` has been generated from the local CICIDS2017 `MachineLearningCVE` CSV files. The sample is balanced for the first MVP: 25,000 normal rows and 25,000 anomaly rows.

## Dataset Decision

| Item | Value |
|---|---|
| Dataset name | CICIDS2017 |
| Source URL | https://www.unb.ca/cic/datasets/ids-2017.html |
| Local original CSV path | `data/raw/MachineLearningCVE/*.csv` |
| Local sample path | `data/raw/sample.csv` |
| Actual sample size | 50,000 rows, 79 columns |
| Sample class balance | 25,000 normal, 25,000 anomaly |
| Problem type | Binary classification: `normal` vs `anomaly` |
| Target label column | `Label` |
| Binary label mapping | `0 = normal`, `1 = anomaly` |
| Backup dataset | UNSW-NB15 |

## Why CICIDS2017 Fits This Project

CICIDS2017 is a good first dataset for this portfolio MVP because it contains labeled network flows and machine-learning-ready CSV files generated from network traffic. The official dataset description says it includes benign traffic and common attacks, with labeled flows based on timestamps, IPs, ports, protocols, and attack labels.

This matches the planned architecture in `docs/architecture.md`:

- Batch CSV ingestion instead of real-time packet capture.
- Binary anomaly detection for `normal` vs `anomaly`.
- Flow-based features for duration, packets, bytes, protocol, and ports.
- Dashboard metrics such as anomaly rate, traffic volume, destination-port distribution, attack-label distribution, and alert severity.
- Baseline scikit-learn model in Week 1.

Important limitation: the local `MachineLearningCVE` CSV files do not include source IP, destination IP, timestamp, or protocol columns. The MVP should avoid promising top IP and protocol-distribution charts until a richer flow export is added. For the first dashboard, use destination port, flow duration, packet/byte totals, attack label, and derived rate features.

## Source Notes

Primary source:

- CICIDS2017: https://www.unb.ca/cic/datasets/ids-2017.html

Backup source:

- UNSW-NB15: https://research.unsw.edu.au/projects/unsw-nb15-dataset

If CICIDS2017 is used in the final report or README, cite the dataset paper listed by the official CICIDS2017 page:

`Iman Sharafaldin, Arash Habibi Lashkari, and Ali A. Ghorbani, "Toward Generating a New Intrusion Detection Dataset and Intrusion Traffic Characterization", ICISSP, 2018.`

## Raw Data Policy

Large raw datasets must not be committed to Git.

This repository already ignores:

- `data/raw/*`
- `data/external/*`
- `data/processed/*`

Keep only scripts, documentation, notebooks, and small reproducible metadata in Git. Keep downloaded CICIDS2017 CSV files local.

## How To Create The Day 03 Sample

After downloading CICIDS2017 MachineLearningCSV files into `data/raw/MachineLearningCVE/`, run:

```powershell
python scripts/create_dataset_sample.py data/raw/MachineLearningCVE/<source-file>.csv --output data/raw/sample.csv
```

For multiple source CSV files:

```powershell
python scripts/create_dataset_sample.py data/raw/MachineLearningCVE/<file-1>.csv data/raw/MachineLearningCVE/<file-2>.csv --output data/raw/sample.csv
```

The script keeps up to 25,000 normal and 25,000 anomaly rows by default. It treats `BENIGN` as normal and all other labels as anomaly.

The current sample was generated from these local files:

- `Monday-WorkingHours.pcap_ISCX.csv`
- `Tuesday-WorkingHours.pcap_ISCX.csv`
- `Wednesday-workingHours.pcap_ISCX.csv`
- `Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv`
- `Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv`
- `Friday-WorkingHours-Morning.pcap_ISCX.csv`
- `Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv`
- `Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv`

## Logical Schema

The MVP should normalize the selected dataset into the following logical fields where possible.

| Logical field | CICIDS2017 source column | Type | Required | Notes |
|---|---|---|---:|---|
| `timestamp` | Not available in current sample | datetime/string | No | Cannot support time-series trend until a timestamped export is added |
| `src_ip` | Not available in current sample | string | No | Cannot support top source IP in the first MVP |
| `dst_ip` | Not available in current sample | string | No | Cannot support destination-IP logs in the first MVP |
| `src_port` | Not available in current sample | integer | No | Current sample only has destination port |
| `dst_port` | `Destination Port` | integer | Yes | Destination port and port category |
| `protocol` | Not available in current sample | string/integer | No | Cannot support protocol distribution in the first MVP |
| `duration` | `Flow Duration` | float | Yes | Flow duration |
| `bytes` | `Total Length of Fwd Packets` + `Total Length of Bwd Packets` | integer/float | Yes | Derived total bytes |
| `packets` | `Total Fwd Packets` + `Total Backward Packets` | integer/float | Yes | Derived total packets |
| `label` | `Label` | string | Yes | Original label |
| `binary_label` | derived from `Label` | integer | Yes | `0 = normal`, `1 = anomaly` |

## Initial Feature Plan

Features to create during Day 05 preprocessing:

- `bytes_per_packet`
- `packets_per_second`
- `bytes_per_second`
- `port_category`
- `is_well_known_port`
- `is_web_port`
- `is_dns_port`
- `is_high_port`

Recommended safety rules:

- Replace zero duration with a small safe denominator when creating rate features.
- Replace zero packets with a safe denominator when creating `bytes_per_packet`.
- Convert `inf` and `-inf` values to missing values before model training.
- Keep the original `Label` for auditability and create a separate `binary_label`.

## Exploration Checklist

- [x] Download CICIDS2017 CSV locally.
- [x] Generate `data/raw/sample.csv`.
- [x] Confirm row count and column count.
- [x] Print all columns.
- [x] Identify the label column.
- [x] Count normal vs anomaly records.
- [x] Check missing values.
- [x] Check duplicate rows.
- [x] Confirm which columns map to the logical schema.
- [ ] Open `notebooks/01_data_exploration.ipynb`.
- [ ] Inspect numeric ranges and outliers interactively.
- [ ] Document limitations and assumptions.

Day 03 sample findings:

| Metric | Value |
|---|---:|
| Rows | 50,000 |
| Columns | 79 |
| Normal rows | 25,000 |
| Anomaly rows | 25,000 |
| Missing cells | 36 |
| Duplicate rows | 2,945 |

Sample label distribution:

| Label | Rows |
|---|---:|
| `BENIGN` | 25,000 |
| `DoS Hulk` | 10,231 |
| `PortScan` | 7,171 |
| `DDoS` | 5,762 |
| `DoS GoldenEye` | 498 |
| `FTP-Patator` | 358 |
| `SSH-Patator` | 276 |
| `DoS slowloris` | 269 |
| `DoS Slowhttptest` | 252 |
| `Bot` | 93 |
| `Web Attack - Brute Force` | 54 |
| `Web Attack - XSS` | 32 |
| `Infiltration` | 3 |
| `Web Attack - Sql Injection` | 1 |

## Risks and Decisions

| Topic | Decision | Reason |
|---|---|---|
| Dataset choice | Use CICIDS2017 | It is flow-based, labeled, and aligned with the dashboard MVP |
| Missing IP/timestamp/protocol fields | Keep them optional and adjust dashboard scope | The local MachineLearningCVE CSV files do not include these columns |
| Label mapping | `BENIGN` -> `0`, all other labels -> `1` | Keeps the first MVP as binary anomaly detection |
| Class imbalance handling | Use balanced local sample for exploration, preserve raw distribution for later evaluation notes | CICIDS2017 attack classes can be uneven |
| Features to drop | Drop duplicate/constant columns such as repeated header-length fields if confirmed during preprocessing | Keeps baseline model simple and explainable |
