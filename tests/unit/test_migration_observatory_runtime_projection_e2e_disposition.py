"""Keep the historical runtime projection end-to-end test disposition auditable."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/observatory/tests/test_runtime_projection_e2e.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "30fb83886faf6ef06a59787643ca01376f634259"
SHA256 = "e7c8ed732f708bfa0fd5dbfabc9815cda83e8192a185ee962f2245b1a6a75d59"


def test_historical_runtime_projection_test_is_bounded_defer() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = {row["source_path"]: row for row in csv.DictReader(stream, delimiter="\t")}
    row = rows[SOURCE]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "8692"
    assert row["disposition"] == "DEFER"
    assert "Lab #287 coordinator" in row["target_owner"]
    assert row["target_path_or_status"] == "No TARGET composite snapshot/test path authorized"
    rationale = row["rationale_and_caveat"]
    assert COMMIT in rationale and BLOB in rationale and SHA256 in rationale
    assert "Verified eight test functions" in rationale
    assert "does not split into authorized TARGET test destinations" in rationale
    assert "Observation #38" in rationale
    assert "closure trigger:" in rationale
    assert "does not block bounded runtime transfer" in rationale
    assert "no scientific validity" in rationale

    counts = Counter(item["disposition"] for item in rows.values())
    assert counts == {"MOVE": 8, "SPLIT": 16, "REWRITE": 3, "DROP": 950, "DEFER": 195}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "Historical Observatory runtime-projection E2E test disposition (Lab #287)" in migration
    assert BLOB in migration and SHA256 in migration
    assert "`SPLIT` | 16 |" in migration
    assert "`DEFER` | 195 |" in migration
