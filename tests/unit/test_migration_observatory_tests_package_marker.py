"""Keep a historical test-package marker out of TARGET code and tests."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/observatory/tests/__init__.py"
SOURCE_BLOB = "4e1fc67df6cac9182eac14d80d7c79420feb5709"


def test_historical_observatory_test_package_marker_is_dropped_only() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "38"
    assert row["top_level_python_symbols"] == ""
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Lab historical test package marker"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "do not migrate the source suite" in row["rationale_and_caveat"]
    assert "scientific evidence disposition" in row["rationale_and_caveat"]
    assert not (ROOT / "src/lab/observatory/tests/__init__.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 30, "REWRITE": 3, "DROP": 949, "DEFER": 182}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 30 |" in migration
    assert "`DROP` | 949 |" in migration
    assert "### Historical Observatory test package marker" in migration
