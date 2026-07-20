"""Train a supervised baseline model for network-traffic anomaly detection."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

try:
    from ml.evaluate import (
        DEFAULT_CONFUSION_MATRIX_PATH,
        DEFAULT_DATA_PATH,
        DEFAULT_METRICS_PATH,
        DEFAULT_MODEL_PATH,
        evaluate_model,
    )
except ModuleNotFoundError:
    from evaluate import (
        DEFAULT_CONFUSION_MATRIX_PATH,
        DEFAULT_DATA_PATH,
        DEFAULT_METRICS_PATH,
        DEFAULT_MODEL_PATH,
        evaluate_model,
    )


DEFAULT_METADATA_PATH = Path("data/processed/preprocessing_metadata.json")
DEFAULT_RANDOM_STATE = 42
DEFAULT_TEST_SIZE = 0.2


def load_feature_columns(metadata_path: Path) -> list[str]:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    feature_columns = metadata.get("model_feature_columns")
    if not isinstance(feature_columns, list) or not feature_columns:
        raise ValueError("Metadata does not contain a valid 'model_feature_columns' list.")
    return [str(column) for column in feature_columns]


def load_training_data(
    data_path: Path,
    metadata_path: Path,
    target_column: str,
) -> tuple[pd.DataFrame, pd.Series, pd.Series, list[str]]:
    frame = pd.read_csv(data_path)
    feature_columns = load_feature_columns(metadata_path)
    required_columns = [*feature_columns, target_column, "record_id"]
    missing_columns = [column for column in required_columns if column not in frame.columns]
    if missing_columns:
        raise ValueError(f"Training data is missing required columns: {missing_columns}")

    x = frame[feature_columns]
    y = frame[target_column].astype(int)
    record_ids = frame["record_id"].astype(int)
    if y.nunique() < 2:
        raise ValueError("Supervised training requires at least two target classes.")
    return x, y, record_ids, feature_columns


def train_baseline_model(
    data_path: Path = DEFAULT_DATA_PATH,
    metadata_path: Path = DEFAULT_METADATA_PATH,
    model_path: Path = DEFAULT_MODEL_PATH,
    target_column: str = "binary_label",
    test_size: float = DEFAULT_TEST_SIZE,
    random_state: int = DEFAULT_RANDOM_STATE,
) -> dict[str, Any]:
    x, y, record_ids, feature_columns = load_training_data(data_path, metadata_path, target_column)
    x_train, x_test, y_train, y_test, _, test_record_ids = train_test_split(
        x,
        y,
        record_ids,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    model = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=random_state,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)

    bundle = {
        "model": model,
        "model_type": "RandomForestClassifier",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "data_path": str(data_path),
        "metadata_path": str(metadata_path),
        "feature_columns": feature_columns,
        "target_column": target_column,
        "random_state": random_state,
        "test_size": test_size,
        "train_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "train_class_distribution": {
            str(label): int(count) for label, count in y_train.value_counts().sort_index().items()
        },
        "test_class_distribution": {
            str(label): int(count) for label, count in y_test.value_counts().sort_index().items()
        },
        "test_record_ids": [int(record_id) for record_id in test_record_ids.tolist()],
    }
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, model_path)
    return bundle


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--metadata", type=Path, default=DEFAULT_METADATA_PATH)
    parser.add_argument("--model-output", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--metrics-output", type=Path, default=DEFAULT_METRICS_PATH)
    parser.add_argument(
        "--confusion-matrix-output",
        type=Path,
        default=DEFAULT_CONFUSION_MATRIX_PATH,
    )
    parser.add_argument("--target-column", default="binary_label")
    parser.add_argument("--test-size", type=float, default=DEFAULT_TEST_SIZE)
    parser.add_argument("--random-state", type=int, default=DEFAULT_RANDOM_STATE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    train_baseline_model(
        data_path=args.data,
        metadata_path=args.metadata,
        model_path=args.model_output,
        target_column=args.target_column,
        test_size=args.test_size,
        random_state=args.random_state,
    )
    metrics = evaluate_model(
        model_path=args.model_output,
        data_path=args.data,
        metrics_path=args.metrics_output,
        confusion_matrix_path=args.confusion_matrix_output,
    )
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
