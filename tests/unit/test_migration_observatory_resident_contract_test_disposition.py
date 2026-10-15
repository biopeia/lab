"""Keep the historical resident-contract test disposition auditable."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/observatory/tests/test_resident_contract.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "3b877574c1eddb5b3ac3a9d34ac8df2fd380c673"


def test_historical_resident_contract_tests_are_bounded_defer() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = {row["source_path"]: row for row in csv.DictReader(stream, delimiter="\t")}
    row = rows[SOURCE]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "6497"
    assert row["top_level_python_symbols"] == "ROOT;REPO_ROOT;ResidentContractTests"
    assert row["disposition"] == "DEFER"
    assert "Organism owner" in row["target_owner"]
    rationale = row["rationale_and_caveat"]
    assert COMMIT in rationale and BLOB in rationale
    assert "Three subprocess tests launch" in rationale
    assert "legacy snapshot schema/version" in rationale
    assert "canonical first-tick topology and journal segment" in rationale
    assert "revision-zero topology" in rationale
    assert "Lab #260/#266" in rationale and "Observation #38" in rationale
    assert "Closure trigger:" in rationale
    assert "does not block it" in rationale
    assert "no scientific validity" in rationale

    counts = Counter(item["disposition"] for item in rows.values())
    assert counts == {"MOVE": 8, "SPLIT": 33, "REWRITE": 3, "DROP": 949, "DEFER": 179}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "Historical Observatory resident-contract test disposition (Lab #285)" in migration
    assert BLOB in migration
    assert "`SPLIT` | 33 |" in migration
    assert "`DEFER` | 179 |" in migration
