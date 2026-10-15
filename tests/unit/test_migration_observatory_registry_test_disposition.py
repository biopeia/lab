"""Keep the historical registry-test disposition auditable."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/observatory/tests/test_registry.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "11b7d3d51f701b0c8fa31ae28ab7042ab9809c0b"


def test_historical_registry_tests_are_bounded_defer() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = {row["source_path"]: row for row in csv.DictReader(stream, delimiter="\t")}
    row = rows[SOURCE]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "2989"
    assert row["top_level_python_symbols"] == "RegistryTests"
    assert row["disposition"] == "DEFER"
    assert "Lab #260 coordinator" in row["target_owner"]
    rationale = row["rationale_and_caveat"]
    assert COMMIT in rationale and BLOB in rationale
    assert "Five tests assert" in rationale
    assert "stable hashed local instance identity" in rationale
    assert "atomic per-instance heartbeat" in rationale
    assert "alive/stale/expired freshness categories" in rationale
    assert "Lab #266" in rationale and "Observation #38" in rationale
    assert "Closure trigger:" in rationale
    assert "does not block it" in rationale
    assert "no scientific validity" in rationale

    counts = Counter(item["disposition"] for item in rows.values())
    assert counts == {"MOVE": 8, "SPLIT": 26, "REWRITE": 3, "DROP": 949, "DEFER": 186}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "Historical Observatory registry-test disposition (Lab #284)" in migration
    assert BLOB in migration
    assert "`SPLIT` | 26 |" in migration
    assert "`DEFER` | 186 |" in migration
