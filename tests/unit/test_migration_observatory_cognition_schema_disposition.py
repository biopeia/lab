"""Keep the legacy Observatory cognition-state schema out of TARGET artifacts."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).parents[2]
PATH = "lab/src/lab/observatory/schemas/cognition_state.schema.json"
BLOB = "4a64ef2467617deb58e466602319c0cc5939cb71"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"

def test_historical_cognition_schema_has_bounded_drop_disposition() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    matches = [r for r in rows if r["source_path"] == PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644" and row["bytes"] == "11259"
    assert row["disposition"] == "DROP"
    assert row["target_path_or_status"] == "No TARGET cognition-state schema path or authorized projection contract"
    assert COMMIT in row["rationale_and_caveat"]
    assert "not a target semantic contract or scientific result" in row["rationale_and_caveat"]
    counts = Counter(r["disposition"] for r in rows)
    assert counts == {"MOVE": 8, "SPLIT": 34, "REWRITE": 3, "DROP": 948, "DEFER": 179}
    assert "### Historical Observatory cognition-state schema (Lab #265)" in (ROOT / "MIGRATION.md").read_text()
