"""Create a balanced Day 03 sample from CICIDS2017-style CSV files."""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path


DEFAULT_NORMAL_VALUES = {"benign", "normal", "0"}


def normalize_header(value: str) -> str:
    return value.strip().lstrip("\ufeff")


def label_bucket(label: str, normal_values: set[str]) -> str:
    return "normal" if label.strip().lower() in normal_values else "anomaly"


def safe_console_text(value: str) -> str:
    return value.encode("ascii", "backslashreplace").decode("ascii")


def reservoir_add(rows: list[dict[str, str]], row: dict[str, str], limit: int, seen: int, rng: random.Random) -> None:
    if len(rows) < limit:
        rows.append(row)
        return

    index = rng.randrange(seen)
    if index < limit:
        rows[index] = row


def read_rows(
    input_paths: list[Path],
    label_column: str,
    normal_values: set[str],
    per_class: int,
    seed: int,
) -> tuple[list[str], list[dict[str, str]], dict[str, int]]:
    rng = random.Random(seed)
    selected: dict[str, list[dict[str, str]]] = {"normal": [], "anomaly": []}
    seen = {"normal": 0, "anomaly": 0}
    label_counts: dict[str, int] = {}
    output_header: list[str] | None = None

    for path in input_paths:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise ValueError(f"CSV has no header: {path}")

            header = [normalize_header(column) for column in reader.fieldnames]
            label_lookup = {column.lower(): column for column in header}
            normalized_label = normalize_header(label_column).lower()
            if normalized_label not in label_lookup:
                raise ValueError(f"Label column '{label_column}' not found in {path}. Found: {header}")

            actual_label = label_lookup[normalized_label]
            if output_header is None:
                output_header = header

            for raw_row in reader:
                row = {normalize_header(key): value for key, value in raw_row.items() if key is not None}
                label_value = row.get(actual_label, "")
                bucket = label_bucket(label_value, normal_values)
                label_counts[label_value] = label_counts.get(label_value, 0) + 1
                seen[bucket] += 1
                reservoir_add(selected[bucket], row, per_class, seen[bucket], rng)

    if output_header is None:
        raise ValueError("No rows were read from the input files.")

    rows = selected["normal"] + selected["anomaly"]
    rng.shuffle(rows)
    return output_header, rows, label_counts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create data/raw/sample.csv from CICIDS2017-style CSV files.")
    parser.add_argument("inputs", nargs="+", type=Path, help="One or more source CSV files.")
    parser.add_argument("--output", type=Path, default=Path("data/raw/sample.csv"), help="Output sample CSV path.")
    parser.add_argument("--label-column", default="Label", help="Name of the source label column.")
    parser.add_argument("--per-class", type=int, default=25_000, help="Maximum rows to keep for each binary class.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible sampling.")
    parser.add_argument(
        "--normal-values",
        nargs="*",
        default=sorted(DEFAULT_NORMAL_VALUES),
        help="Label values treated as normal traffic.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    normal_values = {value.lower() for value in args.normal_values}
    header, rows, label_counts = read_rows(args.inputs, args.label_column, normal_values, args.per_class, args.seed)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=header, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows):,} rows to {args.output}")
    print("Source label distribution:")
    for label, count in sorted(label_counts.items(), key=lambda item: item[1], reverse=True):
        print(f"- {safe_console_text(label)}: {count:,}")


if __name__ == "__main__":
    main()
