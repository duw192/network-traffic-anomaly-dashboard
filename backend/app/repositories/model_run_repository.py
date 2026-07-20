"""Persistence operations for model-run metadata."""

from __future__ import annotations

import sqlite3

from backend.app.models import ModelRunRecord


def create_model_run(connection: sqlite3.Connection, record: ModelRunRecord) -> int:
    cursor = connection.execute(
        """
        INSERT INTO model_runs (
            model_version, algorithm, dataset_name, accuracy, precision,
            recall, f1_score, artifact_path
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record.model_version,
            record.algorithm,
            record.dataset_name,
            record.accuracy,
            record.precision,
            record.recall,
            record.f1_score,
            record.artifact_path,
        ),
    )
    return int(cursor.lastrowid)


def latest_model_run(connection: sqlite3.Connection) -> sqlite3.Row | None:
    return connection.execute(
        """
        SELECT id, model_version, algorithm, dataset_name, accuracy, precision,
               recall, f1_score, artifact_path, created_at
        FROM model_runs
        ORDER BY created_at DESC, id DESC
        LIMIT 1
        """
    ).fetchone()
