"""Load and validate CICIDS2017-style network-flow CSV files.

The module is intentionally reusable: ``preprocess.py`` imports ``load_csv``
so ingestion rules stay identical between the standalone validation command
and the end-to-end preprocessing command.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


DEFAULT_INPUT_PATH = Path("data/raw/sample.csv")
DEFAULT_OUTPUT_PATH = Path("data/processed/traffic_ingested.csv")
REQUIRED_COLUMNS = (
    "destination_port",
    "flow_duration",
    "total_fwd_packets",
    "total_backward_packets",
    "total_length_of_fwd_packets",
    "total_length_of_bwd_packets",
    "label",
)


@dataclass(frozen=True)
class IngestionReport:
    input_path: str
    rows: int
    columns: int
    duplicate_rows: int
    missing_cells: int
    infinite_cells_replaced: int
    required_columns: list[str]


def normalize_column_name(value: str) -> str:
    """Convert a source header to a stable snake_case identifier."""

    value = value.strip().lstrip("\ufeff")
    value = re.sub(r"\.([0-9]+)$", r"_\1", value)
    value = re.sub(r"[^0-9A-Za-z]+", "_", value)
    return value.strip("_").lower()


def normalize_columns(columns: Iterable[str]) -> list[str]:
    normalized = [normalize_column_name(str(column)) for column in columns]
    duplicates = sorted({name for name in normalized if normalized.count(name) > 1})
    if duplicates:
        raise ValueError(f"Duplicate columns after header normalization: {duplicates}")
    return normalized


def validate_required_columns(frame: pd.DataFrame, required: Iterable[str] = REQUIRED_COLUMNS) -> None:
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(
            "Input CSV is missing required columns after normalization: "
            f"{missing}. Available columns: {list(frame.columns)}"
        )


def load_csv(
    input_path: Path | str,
    *,
    required_columns: Iterable[str] = REQUIRED_COLUMNS,
    max_rows: int | None = None,
) -> tuple[pd.DataFrame, IngestionReport]:
    """Read a CSV, normalize headers, validate schema, and replace infinities."""

    path = Path(input_path)
    if not path.is_file():
        raise FileNotFoundError(f"Input CSV does not exist: {path}")
    if path.suffix.lower() != ".csv":
        raise ValueError(f"Expected a .csv input file, received: {path}")

    frame = pd.read_csv(path, nrows=max_rows, low_memory=False, encoding="utf-8-sig")
    if frame.empty:
        raise ValueError(f"Input CSV contains no data rows: {path}")

    frame.columns = normalize_columns(frame.columns)
    validate_required_columns(frame, required_columns)

    numeric = frame.select_dtypes(include=[np.number]).columns
    infinite_count = int(np.isinf(frame[numeric].to_numpy()).sum()) if len(numeric) else 0
    if infinite_count:
        frame.loc[:, numeric] = frame[numeric].replace([np.inf, -np.inf], np.nan)

    report = IngestionReport(
        input_path=str(path),
        rows=int(len(frame)),
        columns=int(len(frame.columns)),
        duplicate_rows=int(frame.duplicated().sum()),
        missing_cells=int(frame.isna().sum().sum()),
        infinite_cells_replaced=infinite_count,
        required_columns=list(required_columns),
    )
    return frame, report


def write_csv(frame: pd.DataFrame, output_path: Path | str) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(path, index=False)
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate and normalize a network-flow CSV file.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT_PATH, help="Raw source CSV path.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_PATH, help="Normalized staging CSV path.")
    parser.add_argument("--max-rows", type=int, default=None, help="Optional row limit for a smoke test.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    frame, report = load_csv(args.input, max_rows=args.max_rows)
    output_path = write_csv(frame, args.output)
    print(json.dumps(asdict(report), indent=2, ensure_ascii=False))
    print(f"Wrote normalized ingestion output to {output_path}")


if __name__ == "__main__":
    main()

