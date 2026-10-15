"""Keep the empty historical Physics3D integration package marker out of TARGET."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/integration/physics3d/__init__.py"
SOURCE_BLOB = "2c55cd785f6933fffd22f011447f38cc79d8e216"


def test_physics3d_integration_package_marker_is_dropped_only() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "81"
    assert row["top_level_python_symbols"] == ""
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Lab historical package facade"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "does not disposition separately inventoried integrated runtime" in row[
        "rationale_and_caveat"
    ]
    assert not (ROOT / "src/lab/integration/physics3d/__init__.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 6, "SPLIT": 97, "REWRITE": 2, "DROP": 907, "DEFER": 160}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 97 |" in migration
    assert "`DROP` | 907 |" in migration
    assert "Drop this historical package marker only" in migration
