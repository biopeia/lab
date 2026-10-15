"""Keep the historical snapshot-test disposition and its limits explicit."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/observatory/tests/test_snapshot_versions.py"
SOURCE_BLOB = "04f44728649cce6ae9e245e189b95beaf8bf0d48"


def test_snapshot_version_tests_are_bounded_defer() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "9322"
    assert row["top_level_python_symbols"] == (
        "ROOT;SCHEMA;body_schema_v1;body_schema_v2;cognition;check;"
        "sensory_phenotype;communication_telemetry;SnapshotVersionMatrixTests"
    )
    assert row["disposition"] == "DEFER"
    assert all(term in row["target_owner"] for term in ("Observation", "Organism", "Embodiment"))
    assert "No target-owned composite wire snapshot" in row["target_path_or_status"]
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "Closure trigger" in rationale
    assert "Does not block bounded runtime transfer" in rationale
    assert "no scientific validity" in rationale

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 15, "REWRITE": 3, "DROP": 950, "DEFER": 196}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "### Historical Observatory snapshot-version test disposition (Lab #290)" in migration
