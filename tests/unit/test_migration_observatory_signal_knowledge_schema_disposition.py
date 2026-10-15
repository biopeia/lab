"""Keep the historical signal-knowledge schema deferred pending owner contracts."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).parents[2]
PATH = "lab/src/lab/observatory/schemas/signal_knowledge.schema.json"
BLOB = "fe960b2b38ef3655a5aff6867b81a46fbf380a9e"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"

def test_historical_signal_knowledge_schema_has_bounded_defer() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644" and row["bytes"] == "4079"
    assert row["disposition"] == "DEFER"
    assert "no TARGET signal-knowledge wire schema authorized" in row["target_path_or_status"]
    rationale = row["rationale_and_caveat"]
    assert COMMIT in rationale and "100195ff2df5d7feb4e86eead7482858b5a1b2a88956e28efaa825ca67fe2c9d" in rationale
    assert "Organism #169" in rationale and "Organism #45" in rationale
    assert "identity, provenance and epistemic basis" in rationale
    assert "does not block the bounded Lab runtime migration" in rationale
    assert "No source deletion" in rationale
    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 35, "REWRITE": 3, "DROP": 948, "DEFER": 178}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical Observatory signal-knowledge schema (Lab #268)" in migration
    assert "| `SPLIT` | 35 |" in migration and "| `DEFER` | 178 |" in migration
