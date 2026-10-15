"""Keep the historical Observatory integration-test disposition auditable."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/observatory/tests/test_observatory_integration.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "3581df581e56afc91f490d707975c01707b62ca9"
SYMBOLS = "ROOT;REPO_ROOT;_run_resident;ObservatoryIntegrationTests"


def test_observatory_integration_test_row_is_bounded_defer() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = {row["source_path"]: row for row in csv.DictReader(stream, delimiter="\t")}
    row = rows[SOURCE]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "3369"
    assert row["top_level_python_symbols"] == SYMBOLS
    assert row["disposition"] == "DEFER"
    assert "Lab migration/custody owner" in row["target_owner"]
    assert "#260" in row["rationale_and_caveat"] and "#266" in row["rationale_and_caveat"]
    rationale = row["rationale_and_caveat"]
    assert COMMIT in rationale and BLOB in rationale
    assert "two integration tests launch" in rationale or "contains two integration tests" in rationale
    assert "distinct instance_id/run_id values" in rationale
    assert "restart the same historical state file" in rationale
    assert "No authorized TARGET resident registry" in rationale
    assert "Observation #38" in rationale
    assert "Closure trigger:" in rationale
    assert "outside the bounded runtime-transfer causal-cycle profile" in rationale
    assert "no scientific validity" in rationale

    counts = Counter(item["disposition"] for item in rows.values())
    assert counts == {"MOVE": 8, "SPLIT": 31, "REWRITE": 3, "DROP": 949, "DEFER": 181}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "Historical Observatory integration-test disposition (Lab #282)" in migration
    assert BLOB in migration
    assert "`SPLIT` | 31 |" in migration
    assert "`DEFER` | 181 |" in migration
