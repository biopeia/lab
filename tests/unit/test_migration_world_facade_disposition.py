"""Keep the historical Lab World aggregate import facade out of TARGET."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/world/__init__.py"
SOURCE_BLOB = "73fb4a3b7f9c3380b6aa94f11f1bb62bbe494d02"


def test_historical_world_aggregate_facade_is_dropped_only() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "1401"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Lab historical package facade"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "re-exports Environment genesis helpers" in row["rationale_and_caveat"]
    assert "separately inventoried modules" in row["rationale_and_caveat"]
    assert not (ROOT / "src/lab/world/__init__.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 34, "REWRITE": 3, "DROP": 948, "DEFER": 179}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 34 |" in migration
    assert "`DROP` | 948 |" in migration
    assert "Historical Lab World aggregate facade" in migration
    assert "do not preserve its import path" in migration
