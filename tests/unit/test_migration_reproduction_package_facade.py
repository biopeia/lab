"""Keep the historical reproduction import facade out of TARGET."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/reproduction/__init__.py"
SOURCE_BLOB = "302e1d96cd93da7dc7baaf3ff63c387bd9015d76"


def test_reproduction_package_facade_is_dropped_without_dispositioning_siblings() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "313"
    assert row["top_level_python_symbols"] == ""
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Lab historical package facade"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "authority.py" in row["rationale_and_caveat"]
    assert "runtime.py" in row["rationale_and_caveat"]
    assert "not dispositioned here" in row["rationale_and_caveat"]
    assert not (ROOT / "src/lab/reproduction/__init__.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 6, "SPLIT": 119, "REWRITE": 2, "DROP": 886, "DEFER": 159}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 119 |" in migration
    assert "`DROP` | 886 |" in migration
    assert "Historical reproduction package facade" in migration
    assert "The sibling modules remain independent inventory items" in migration
