"""Evaluate a trained anomaly-detection baseline on processed traffic data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


DEFAULT_MODEL_PATH = Path("models/baseline_model.pkl")
DEFAULT_DATA_PATH = Path("data/processed/traffic_processed.csv")
DEFAULT_METRICS_PATH = Path("reports/model_metrics.json")
DEFAULT_CONFUSION_MATRIX_PATH = Path("reports/confusion_matrix.png")


def _json_ready(value: Any) -> Any:
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    return value


def load_model_bundle(model_path: Path) -> dict[str, Any]:
    bundle = joblib.load(model_path)
    required_keys = {"model", "feature_columns", "target_column", "test_record_ids"}
    missing_keys = required_keys.difference(bundle)
    if missing_keys:
        raise ValueError(f"Model bundle is missing required keys: {sorted(missing_keys)}")
    return bundle


def build_test_frame(data_path: Path, bundle: dict[str, Any]) -> pd.DataFrame:
    frame = pd.read_csv(data_path)
    missing_columns = [
        column
        for column in [*bundle["feature_columns"], bundle["target_column"], "record_id"]
        if column not in frame.columns
    ]
    if missing_columns:
        raise ValueError(f"Evaluation data is missing required columns: {missing_columns}")

    test_record_ids = set(bundle["test_record_ids"])
    test_frame = frame.loc[frame["record_id"].isin(test_record_ids)].copy()
    if test_frame.empty:
        raise ValueError("No evaluation rows matched the saved test record ids.")
    return test_frame


def calculate_metrics(
    model: Any,
    test_frame: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
) -> dict[str, Any]:
    x_test = test_frame[feature_columns]
    y_true = test_frame[target_column].astype(int)
    y_pred = model.predict(x_test)

    metrics: dict[str, Any] = {
        "accuracy": accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall": recall_score(y_true, y_pred, zero_division=0),
        "f1_score": f1_score(y_true, y_pred, zero_division=0),
        "confusion_matrix": confusion_matrix(y_true, y_pred, labels=[0, 1]),
        "classification_report": classification_report(
            y_true,
            y_pred,
            labels=[0, 1],
            target_names=["normal", "anomaly"],
            output_dict=True,
            zero_division=0,
        ),
    }

    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba(x_test)
        if probabilities.shape[1] == 2 and len(set(y_true)) == 2:
            metrics["roc_auc"] = roc_auc_score(y_true, probabilities[:, 1])

    return _json_ready(metrics)


def write_metrics(metrics: dict[str, Any], metrics_path: Path) -> None:
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(
        json.dumps(metrics, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_confusion_matrix(metrics: dict[str, Any], output_path: Path) -> None:
    matrix = np.array(metrics["confusion_matrix"])
    output_path.parent.mkdir(parents=True, exist_ok=True)

    figure, axis = plt.subplots(figsize=(5.5, 4.5))
    image = axis.imshow(matrix, interpolation="nearest", cmap="Blues")
    figure.colorbar(image, ax=axis)
    axis.set(
        xticks=np.arange(2),
        yticks=np.arange(2),
        xticklabels=["Predicted normal", "Predicted anomaly"],
        yticklabels=["Actual normal", "Actual anomaly"],
        ylabel="True label",
        xlabel="Predicted label",
        title="Baseline Confusion Matrix",
    )

    threshold = matrix.max() / 2 if matrix.size else 0
    for row in range(matrix.shape[0]):
        for column in range(matrix.shape[1]):
            axis.text(
                column,
                row,
                format(matrix[row, column], "d"),
                ha="center",
                va="center",
                color="white" if matrix[row, column] > threshold else "black",
            )

    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)


def evaluate_model(
    model_path: Path = DEFAULT_MODEL_PATH,
    data_path: Path = DEFAULT_DATA_PATH,
    metrics_path: Path = DEFAULT_METRICS_PATH,
    confusion_matrix_path: Path = DEFAULT_CONFUSION_MATRIX_PATH,
) -> dict[str, Any]:
    bundle = load_model_bundle(model_path)
    test_frame = build_test_frame(data_path, bundle)
    metrics = calculate_metrics(
        bundle["model"],
        test_frame,
        bundle["feature_columns"],
        bundle["target_column"],
    )
    metrics.update(
        {
            "model_path": str(model_path),
            "data_path": str(data_path),
            "evaluation_rows": len(test_frame),
            "test_record_ids_count": len(bundle["test_record_ids"]),
            "feature_columns": bundle["feature_columns"],
            "target_column": bundle["target_column"],
            "confusion_matrix_path": str(confusion_matrix_path),
        }
    )
    write_metrics(metrics, metrics_path)
    write_confusion_matrix(metrics, confusion_matrix_path)
    return metrics


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--metrics-output", type=Path, default=DEFAULT_METRICS_PATH)
    parser.add_argument(
        "--confusion-matrix-output",
        type=Path,
        default=DEFAULT_CONFUSION_MATRIX_PATH,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    metrics = evaluate_model(
        model_path=args.model,
        data_path=args.data,
        metrics_path=args.metrics_output,
        confusion_matrix_path=args.confusion_matrix_output,
    )
    print(json.dumps(metrics, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
