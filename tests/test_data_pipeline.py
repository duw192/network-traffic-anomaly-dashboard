from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

from pipelines.ingest import load_csv, normalize_column_name
from pipelines.preprocess import preprocess_frame, write_outputs


class DataPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.frame = pd.DataFrame(
            {
                " Destination Port": [80, 53, 50_000, 80, 80],
                " Flow Duration": [1_000_000, 0, 2_000_000, 1_000_000, 1_000_000],
                " Total Fwd Packets": [5, 0, 10, 5, 5],
                " Total Backward Packets": [5, 0, 10, 5, 5],
                " Total Length of Fwd Packets": [500, 0, 2_000, 500, 500],
                " Total Length of Bwd Packets": [500, 0, 2_000, 500, 500],
                " Flow Bytes/s": [1_000.0, np.inf, np.nan, 1_000.0, 999.0],
                " Label": ["BENIGN", "DDoS", "PortScan", "BENIGN", "BENIGN"],
            }
        )

    def test_normalize_column_name(self) -> None:
        self.assertEqual(normalize_column_name(" Fwd Header Length.1 "), "fwd_header_length_1")

    def test_load_and_preprocess(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            input_path = Path(temporary_directory) / "sample.csv"
            self.frame.to_csv(input_path, index=False)

            source, report = load_csv(input_path)
            self.assertEqual(report.infinite_cells_replaced, 1)
            self.assertEqual(report.duplicate_rows, 1)

            processed, metadata = preprocess_frame(source, report)
            self.assertEqual(len(processed), 3)
            self.assertEqual(metadata["cleaning"]["duplicate_rows_removed"], 1)
            self.assertEqual(metadata["cleaning"]["feature_duplicate_rows_removed"], 1)
            self.assertEqual(metadata["class_distribution"], {"0": 1, "1": 2})
            self.assertTrue(np.isfinite(processed.select_dtypes(include=[np.number])).all().all())
            self.assertEqual(processed.loc[0, "is_web_port"], 1)
            self.assertEqual(processed.loc[1, "is_dns_port"], 1)
            self.assertEqual(processed.loc[2, "is_high_port"], 1)

    def test_write_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            input_path = Path(temporary_directory) / "sample.csv"
            output_path = Path(temporary_directory) / "processed.csv"
            metadata_path = Path(temporary_directory) / "metadata.json"
            self.frame.iloc[:2].to_csv(input_path, index=False)
            source, report = load_csv(input_path)
            processed, metadata = preprocess_frame(source, report)
            write_outputs(processed, metadata, output_path, metadata_path)

            self.assertTrue(output_path.is_file())
            self.assertEqual(json.loads(metadata_path.read_text(encoding="utf-8"))["target_column"], "binary_label")


if __name__ == "__main__":
    unittest.main()
