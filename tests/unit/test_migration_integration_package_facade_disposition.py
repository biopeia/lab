"""Keep the historical Lab integration package facade out of TARGET."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/integration/__init__.py"
SOURCE_BLOB = "b19fae9ef159d30e7d3d7e614c804a986284c97f"


def test_integration_package_facade_is_dropped_separately_from_runtime() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "311"
    assert row["top_level_python_symbols"] == ""
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Lab historical package facade"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "integrated_habitat.py" in row["rationale_and_caveat"]
    assert "implementation module has its own record in MIGRATION.md" in row[
        "rationale_and_caveat"
    ]
    assert not (ROOT / "src/lab/integration/__init__.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 6, "SPLIT": 80, "REWRITE": 3, "DROP": 923, "DEFER": 160}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 80 |" in migration
    assert "`DROP` | 923 |" in migration
    assert "facade-only record does not itself disposition the implementation module" in migration
