"""Keep unresolved Observatory registry ownership explicit and bounded."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_PATH = "lab/src/lab/observatory/registry.py"
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_BLOB = "22fd3b107ae2141940802972d019af50863c6f8f"
SYMBOLS = (
    "derive_instance_id;new_run_id;_atomic_write_json;write_heartbeat;"
    "_aware_datetime;_valid_registry_record;read_registry;classify_liveness"
)


def test_observatory_registry_is_bounded_defer_pending_owner_decisions() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = {row["source_path"]: row for row in csv.DictReader(stream, delimiter="\t")}
    row = rows[SOURCE_PATH]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "4255"
    assert row["top_level_python_symbols"] == SYMBOLS
    assert row["disposition"] == "DEFER"
    assert "Observation #38" in row["target_owner"]
    assert "Lab #266" in row["target_owner"]
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "classifies heartbeat freshness" in rationale
    assert "no durable instance registry, heartbeat, or liveness service" in rationale
    assert "Closure trigger:" in rationale
    assert "outside the bounded runtime-transfer profile" in rationale
    assert "No scientific validity, equivalence, evidence-admission" in rationale

    counts = Counter(item["disposition"] for item in rows.values())
    assert counts == {"MOVE": 8, "SPLIT": 15, "REWRITE": 3, "DROP": 950, "DEFER": 196}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical Observatory instance registry disposition (Lab #260)" in migration
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 15 |" in migration
    assert "`DEFER` | 196 |" in migration
