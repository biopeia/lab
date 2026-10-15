"""Keep the historical kernel-characterization facade disposition bounded."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/kernel_characterization/__init__.py"
SOURCE_BLOB = "072aea65d990b64db4936ead4e0fb0861cb46ca1"


def test_historical_kernel_characterization_facade_is_dropped_only() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "343"
    assert row["top_level_python_symbols"] == ""
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Lab historical kernel-characterization package facade"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "Drop this historical package facade only" in row["rationale_and_caveat"]
    assert "sibling config and characterization/study modules remain separate" in row[
        "rationale_and_caveat"
    ]
    assert not (ROOT / "src/lab/kernel_characterization").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 6, "SPLIT": 90, "REWRITE": 2, "DROP": 914, "DEFER": 160}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 90 |" in migration
    assert "`DROP` | 914 |" in migration
    assert "### Historical kernel-characterization package facade" in migration
