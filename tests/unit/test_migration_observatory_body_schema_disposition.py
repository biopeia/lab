"""Keep the legacy Observatory body self-knowledge schema out of TARGET artifacts."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).parents[2]
PATH = "lab/src/lab/observatory/schemas/body_schema.schema.json"
BLOB = "4f393ed9161c3ba8e9672dc78edbb1bef9cd516d"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"

def test_historical_body_schema_has_bounded_drop_disposition() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    matches = [r for r in rows if r["source_path"] == PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644" and row["bytes"] == "4195"
    assert row["disposition"] == "DROP"
    assert row["target_path_or_status"] == "No TARGET schema path or compatibility contract"
    assert COMMIT in row["rationale_and_caveat"]
    assert "not an authoritative Embodiment physical-body schema" in row["rationale_and_caveat"]
    counts = Counter(r["disposition"] for r in rows)
    assert counts == {"MOVE": 8, "SPLIT": 45, "REWRITE": 3, "DROP": 947, "DEFER": 169}
    assert "### Historical Observatory body self-knowledge schema (Lab #264)" in (ROOT / "MIGRATION.md").read_text()
