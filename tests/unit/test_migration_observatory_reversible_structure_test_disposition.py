"""Keep the historical cognition-state mutation test disposition auditable."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/observatory/tests/test_reversible_structure_contract.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "d80f10280f219d428f5619d02f2776bb44b8fcbd"


def test_historical_remove_node_schema_assertion_is_bounded_defer() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = {row["source_path"]: row for row in csv.DictReader(stream, delimiter="\t")}
    row = rows[SOURCE]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "379"
    assert row["top_level_python_symbols"] == "ROOT;test_cognition_state_accepts_remove_node_mutations"
    assert row["disposition"] == "DEFER"
    assert "Lab #265 coordinator" in row["target_owner"]
    rationale = row["rationale_and_caveat"]
    assert COMMIT in rationale and BLOB in rationale
    assert "checks only that remove_node appears" in rationale
    assert "does not execute a graph mutation" in rationale
    assert "Lab #265" in rationale
    assert "Closure trigger:" in rationale
    assert "does not block it" in rationale
    assert "no scientific validity" in rationale

    counts = Counter(item["disposition"] for item in rows.values())
    assert counts == {"MOVE": 8, "SPLIT": 19, "REWRITE": 3, "DROP": 950, "DEFER": 192}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "Historical reversible-structure contract test disposition (Lab #286)" in migration
    assert BLOB in migration
    assert "`SPLIT` | 19 |" in migration
    assert "`DEFER` | 192 |" in migration
