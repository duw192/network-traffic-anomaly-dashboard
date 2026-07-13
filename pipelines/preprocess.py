"""Clean CICIDS2017 flow data and build dashboard/ML-ready features."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    from pipelines.ingest import IngestionReport, load_csv
except ModuleNotFoundError:  # Supports: python pipelines/preprocess.py
    from ingest import IngestionReport, load_csv


DEFAULT_INPUT_PATH = Path("data/raw/sample.csv")
DEFAULT_OUTPUT_PATH = Path("data/processed/traffic_processed.csv")
DEFAULT_METADATA_PATH = Path("data/processed/preprocessing_metadata.json")
NORMAL_LABELS = {"benign", "normal", "0"}
WEB_PORTS = {80, 443, 8000, 8080, 8443}
DNS_PORTS = {53}

SOURCE_NUMERIC_COLUMNS = (
    "destination_port",
    "flow_duration",
    "total_fwd_packets",
    "total_backward_packets",
    "total_length_of_fwd_packets",
    "total_length_of_bwd_packets",
)
MODEL_BASE_COLUMNS = (
    "dst_port",
    "flow_duration_us",
    "total_packets",
    "total_bytes",
    "bytes_per_packet",
    "packets_per_second",
    "bytes_per_second",
)


def _json_value(value: Any) -> Any:
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    return value


def _clean_label(series: pd.Series) -> pd.Series:
    cleaned = series.astype("string").str.strip()
    # Some CICIDS2017 mirrors contain a damaged dash in "Web Attack - ...".
    for damaged_dash in ("\ufffd", "ï¿½", "â€“", "â€”"):
        cleaned = cleaned.str.replace(damaged_dash, "-", regex=False)
    return cleaned.str.replace(r"\s+", " ", regex=True)


def _port_category(port: pd.Series) -> pd.Categorical:
    categories = pd.cut(
        port,
        bins=[-1, 1023, 49151, 65535],
        labels=["well_known", "registered", "dynamic_private"],
    )
    return pd.Categorical(categories, categories=["well_known", "registered", "dynamic_private"])


def _safe_rate(numerator: pd.Series, denominator: pd.Series) -> pd.Series:
    safe_denominator = denominator.where(denominator > 0)
    return numerator.div(safe_denominator).replace([np.inf, -np.inf], np.nan)


def _impute_median(frame: pd.DataFrame, columns: list[str]) -> dict[str, dict[str, float | int]]:
    details: dict[str, dict[str, float | int]] = {}
    for column in columns:
        missing = int(frame[column].isna().sum())
        median = frame[column].median(skipna=True)
        if pd.isna(median):
            raise ValueError(f"Cannot impute '{column}' because it has no valid numeric values.")
        frame[column] = frame[column].fillna(float(median))
        details[column] = {"missing_values": missing, "median": float(median)}
    return details


def _log_robust_scale(frame: pd.DataFrame, columns: tuple[str, ...]) -> dict[str, dict[str, float | str]]:
    """Add deterministic log1p + median/IQR scaled features.

    The implementation avoids coupling Day 05 to a fitted sklearn object. The
    emitted metadata contains every parameter needed to reproduce inference.
    """

    parameters: dict[str, dict[str, float | str]] = {}
    for column in columns:
        transformed = np.log1p(frame[column].clip(lower=0).astype(float))
        center = float(transformed.median())
        q1 = float(transformed.quantile(0.25))
        q3 = float(transformed.quantile(0.75))
        scale = q3 - q1
        if not np.isfinite(scale) or scale == 0:
            scale = 1.0
        output_column = f"feature_{column}_scaled"
        frame[output_column] = (transformed - center) / scale
        parameters[output_column] = {
            "source_column": column,
            "transform": "log1p_then_robust_scale",
            "center_log_median": center,
            "scale_log_iqr": scale,
        }
    return parameters


def preprocess_frame(
    source: pd.DataFrame,
    ingestion_report: IngestionReport | None = None,
    *,
    drop_duplicates: bool = True,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Return a cleaned feature table and reproducibility metadata."""

    frame = source.copy()
    rows_before = len(frame)
    duplicates_removed = int(frame.duplicated().sum()) if drop_duplicates else 0
    if drop_duplicates:
        frame = frame.drop_duplicates().reset_index(drop=True)

    frame["label"] = _clean_label(frame["label"])
    missing_labels = int(frame["label"].isna().sum() + frame["label"].eq("").sum())
    if missing_labels:
        frame = frame.loc[frame["label"].notna() & frame["label"].ne("")].reset_index(drop=True)
    if frame.empty:
        raise ValueError("No rows remain after removing records without labels.")

    for column in SOURCE_NUMERIC_COLUMNS:
        frame[column] = pd.to_numeric(frame[column], errors="coerce").replace([np.inf, -np.inf], np.nan)

    invalid_ranges = {
        "destination_port": ~frame["destination_port"].between(0, 65535),
        "flow_duration": frame["flow_duration"] < 0,
        "total_fwd_packets": frame["total_fwd_packets"] < 0,
        "total_backward_packets": frame["total_backward_packets"] < 0,
        "total_length_of_fwd_packets": frame["total_length_of_fwd_packets"] < 0,
        "total_length_of_bwd_packets": frame["total_length_of_bwd_packets"] < 0,
    }
    invalid_counts: dict[str, int] = {}
    for column, mask in invalid_ranges.items():
        invalid_counts[column] = int(mask.fillna(False).sum())
        frame.loc[mask.fillna(False), column] = np.nan

    imputation = _impute_median(frame, list(SOURCE_NUMERIC_COLUMNS))

    processed = pd.DataFrame(index=frame.index)
    processed["dst_port"] = frame["destination_port"].round().astype("int64")
    processed["flow_duration_us"] = frame["flow_duration"].astype(float)
    processed["total_packets"] = (
        frame["total_fwd_packets"] + frame["total_backward_packets"]
    ).astype(float)
    processed["total_bytes"] = (
        frame["total_length_of_fwd_packets"] + frame["total_length_of_bwd_packets"]
    ).astype(float)
    processed["bytes_per_packet"] = _safe_rate(processed["total_bytes"], processed["total_packets"])
    duration_seconds = processed["flow_duration_us"] / 1_000_000.0
    processed["packets_per_second"] = _safe_rate(processed["total_packets"], duration_seconds)
    processed["bytes_per_second"] = _safe_rate(processed["total_bytes"], duration_seconds)

    derived_imputation = _impute_median(
        processed, ["bytes_per_packet", "packets_per_second", "bytes_per_second"]
    )
    imputation.update(derived_imputation)

    processed["port_category"] = _port_category(processed["dst_port"])
    processed["is_well_known_port"] = (processed["dst_port"] <= 1023).astype("int8")
    processed["is_web_port"] = processed["dst_port"].isin(WEB_PORTS).astype("int8")
    processed["is_dns_port"] = processed["dst_port"].isin(DNS_PORTS).astype("int8")
    processed["is_high_port"] = (processed["dst_port"] >= 49152).astype("int8")

    for category in ("well_known", "registered", "dynamic_private"):
        processed[f"port_category_{category}"] = processed["port_category"].eq(category).astype("int8")

    processed["attack_type"] = frame["label"].astype(str)
    processed["binary_label"] = (
        ~frame["label"].str.lower().isin(NORMAL_LABELS)
    ).astype("int8")

    encoded_columns = [
        "is_well_known_port",
        "is_web_port",
        "is_dns_port",
        "is_high_port",
        "port_category_well_known",
        "port_category_registered",
        "port_category_dynamic_private",
    ]
    feature_signature = [*MODEL_BASE_COLUMNS, *encoded_columns]
    conflicting_feature_vectors = int(
        processed.groupby(feature_signature, dropna=False)["binary_label"].nunique().gt(1).sum()
    )
    feature_duplicates_removed = int(
        processed.duplicated(subset=[*feature_signature, "binary_label"]).sum()
    )
    processed = processed.drop_duplicates(
        subset=[*feature_signature, "binary_label"], keep="first"
    ).reset_index(drop=True)
    processed.insert(0, "record_id", np.arange(1, len(processed) + 1, dtype=np.int64))

    scaling = _log_robust_scale(processed, MODEL_BASE_COLUMNS)

    feature_columns = [
        column
        for column in processed.columns
        if column.startswith("feature_") or column.startswith("port_category_") or column.startswith("is_")
    ]
    output_order = [
        "record_id",
        "dst_port",
        "flow_duration_us",
        "total_packets",
        "total_bytes",
        "bytes_per_packet",
        "packets_per_second",
        "bytes_per_second",
        "port_category",
        "is_well_known_port",
        "is_web_port",
        "is_dns_port",
        "is_high_port",
        "port_category_well_known",
        "port_category_registered",
        "port_category_dynamic_private",
        *[f"feature_{column}_scaled" for column in MODEL_BASE_COLUMNS],
        "attack_type",
        "binary_label",
    ]
    processed = processed.loc[:, output_order]

    metadata: dict[str, Any] = {
        "pipeline_version": "day-05-v1",
        "input": asdict(ingestion_report) if ingestion_report else None,
        "cleaning": {
            "rows_before": int(rows_before),
            "rows_after": int(len(processed)),
            "duplicate_rows_removed": duplicates_removed,
            "feature_duplicate_rows_removed": feature_duplicates_removed,
            "conflicting_feature_vectors_kept": conflicting_feature_vectors,
            "rows_without_label_removed": missing_labels,
            "invalid_values_replaced": invalid_counts,
            "median_imputation": imputation,
        },
        "label_mapping": {"normal_values": sorted(NORMAL_LABELS), "normal": 0, "anomaly": 1},
        "output_columns": list(processed.columns),
        "model_feature_columns": feature_columns,
        "target_column": "binary_label",
        "scaling_parameters": scaling,
        "class_distribution": {
            str(key): int(value) for key, value in processed["binary_label"].value_counts().sort_index().items()
        },
        "attack_type_distribution": {
            str(key): int(value) for key, value in processed["attack_type"].value_counts().items()
        },
    }
    return processed, metadata


def write_outputs(
    processed: pd.DataFrame,
    metadata: dict[str, Any],
    output_path: Path | str,
    metadata_path: Path | str,
) -> tuple[Path, Path]:
    output = Path(output_path)
    metadata_output = Path(metadata_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    metadata_output.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(output, index=False)
    metadata_output.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False, default=_json_value) + "\n",
        encoding="utf-8",
    )
    return output, metadata_output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create the Day 05 processed traffic dataset.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH, help="Raw or ingested CSV path.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH, help="Processed CSV path.")
    parser.add_argument(
        "--metadata-output",
        type=Path,
        default=DEFAULT_METADATA_PATH,
        help="JSON path for cleaning and scaling metadata.",
    )
    parser.add_argument("--max-rows", type=int, default=None, help="Optional row limit for a smoke test.")
    parser.add_argument(
        "--keep-duplicates",
        action="store_true",
        help="Keep exact duplicate rows (not recommended for model training).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    source, ingestion_report = load_csv(args.input, max_rows=args.max_rows)
    processed, metadata = preprocess_frame(
        source, ingestion_report, drop_duplicates=not args.keep_duplicates
    )
    output, metadata_output = write_outputs(processed, metadata, args.output, args.metadata_output)
    print(
        json.dumps(
            {
                "rows": len(processed),
                "columns": len(processed.columns),
                "class_distribution": metadata["class_distribution"],
                "processed_csv": str(output),
                "metadata_json": str(metadata_output),
            },
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
