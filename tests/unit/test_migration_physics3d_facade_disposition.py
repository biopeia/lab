"""Keep the historical Physics3D package-facade disposition bounded."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/physics3d/__init__.py"
SOURCE_BLOB = "18a8d568dfb995653b5d6e838b62591889412e6a"
SOURCE_SHA256 = "b5aab993112c2c867257104d6e7dd4a3a83c8b2537637b361685c1f787b58982"


def test_historical_physics3d_facade_is_dropped_without_disposing_siblings() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    by_path = {row["source_path"]: row for row in rows}

    row = by_path[SOURCE_PATH]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "259"
    assert row["top_level_python_symbols"] == ""
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Lab historical Physics3D package facade"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert SOURCE_SHA256 in row["rationale_and_caveat"]
    assert "Drop only this historical package facade" in row["rationale_and_caveat"]
    assert "separately inventoried source modules" in row["rationale_and_caveat"]
    assert not (ROOT / "src/lab/physics3d").exists()

    runtime_row = by_path["lab/src/lab/physics3d/runtime.py"]
    assert runtime_row["disposition"] == "SPLIT"

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 6, "SPLIT": 130, "REWRITE": 2, "DROP": 874, "DEFER": 160}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 130 |" in migration
    assert "`DROP` | 874 |" in migration
    assert "### Historical Physics3D package facade" in migration
