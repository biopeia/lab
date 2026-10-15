"""Lab subsystem readiness is not an Observation semantic family."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_PATH = "lab/src/lab/observation/subsystem_status.py"
SOURCE_BLOB = "c20ec51d7c3cd37eb498f1b43d773ed2f30c61f8"
SYMBOLS = "ABSENT;DISABLED;NOT_READY;IDLE;ACTIVE;LIFECYCLES;generative_status"


def test_subsystem_status_is_dropped_from_target_migration() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "2087"
    assert row["top_level_python_symbols"] == SYMBOLS
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert "operational readiness" in row["rationale_and_caveat"]
    assert "no scientific validity" in row["rationale_and_caveat"]

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 15, "REWRITE": 3, "DROP": 950, "DEFER": 196}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "Historical subsystem status disposition (Lab #244)" in migration
