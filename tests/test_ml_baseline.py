from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from ml.evaluate import evaluate_model
from ml.train import train_baseline_model


class MlBaselineTests(unittest.TestCase):
    def test_train_and_evaluate_baseline_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            workspace = Path(temporary_directory)
            data_path = workspace / "traffic_processed.csv"
            metadata_path = workspace / "preprocessing_metadata.json"
            model_path = workspace / "baseline_model.pkl"
            metrics_path = workspace / "model_metrics.json"
            confusion_matrix_path = workspace / "confusion_matrix.png"

            feature_columns = ["feature_one", "feature_two", "is_web_port"]
            frame = pd.DataFrame(
                {
                    "record_id": range(1, 13),
                    "feature_one": [0.0, 0.1, 0.2, 0.2, 0.9, 1.0, 1.1, 1.2, 0.3, 0.4, 1.3, 1.4],
                    "feature_two": [1.0, 1.1, 1.2, 1.3, 2.0, 2.1, 2.2, 2.3, 1.4, 1.5, 2.4, 2.5],
                    "is_web_port": [1, 1, 1, 0, 0, 0, 0, 1, 1, 0, 0, 1],
                    "binary_label": [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1],
                }
            )
            frame.to_csv(data_path, index=False)
            metadata_path.write_text(
                json.dumps({"model_feature_columns": feature_columns}),
                encoding="utf-8",
            )

            bundle = train_baseline_model(
                data_path=data_path,
                metadata_path=metadata_path,
                model_path=model_path,
                test_size=0.25,
                random_state=7,
            )
            metrics = evaluate_model(
                model_path=model_path,
                data_path=data_path,
                metrics_path=metrics_path,
                confusion_matrix_path=confusion_matrix_path,
            )

            self.assertTrue(model_path.is_file())
            self.assertTrue(metrics_path.is_file())
            self.assertTrue(confusion_matrix_path.is_file())
            self.assertEqual(bundle["feature_columns"], feature_columns)
            self.assertEqual(metrics["evaluation_rows"], 3)
            self.assertIn("f1_score", metrics)


if __name__ == "__main__":
    unittest.main()
