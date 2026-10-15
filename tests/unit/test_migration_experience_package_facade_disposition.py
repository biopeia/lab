"""Keep the historical Lab experience import facade out of TARGET."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/experience/__init__.py"
SOURCE_BLOB = "52329f0b9a413d88b1ec679be99d01708dcd7c41"


def test_experience_package_facade_is_dropped_without_dispositioning_modules() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "723"
    assert row["top_level_python_symbols"] == ""
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Lab historical package facade"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "definition.py" in row["rationale_and_caveat"]
    assert "safety.py" in row["rationale_and_caveat"]
    assert "does not disposition the underlying modules" in row["rationale_and_caveat"]
    assert not (ROOT / "src/lab/experience/__init__.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 6, "SPLIT": 76, "REWRITE": 3, "DROP": 927, "DEFER": 160}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 76 |" in migration
    assert "`DROP` | 927 |" in migration
    assert "does not disposition the underlying modules" in migration
