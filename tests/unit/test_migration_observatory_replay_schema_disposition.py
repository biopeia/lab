"""Keep the legacy Observatory replay envelope schema out of TARGET artifacts."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).parents[2]
PATH = "lab/src/lab/observatory/schemas/replay.schema.json"
BLOB = "d1f6f042b4ac49d70a8f4debf665ea4c68f72885"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"

def test_historical_replay_schema_has_bounded_drop_disposition() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    matches = [r for r in rows if r["source_path"] == PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644" and row["bytes"] == "479"
    assert row["disposition"] == "DROP"
    assert row["target_path_or_status"] == "No TARGET replay schema/compatibility contract"
    assert COMMIT in row["rationale_and_caveat"]
    assert "do not delete or disposition historical replay data by implication" in row["rationale_and_caveat"]
    counts = Counter(r["disposition"] for r in rows)
    assert counts == {"MOVE": 8, "SPLIT": 32, "REWRITE": 3, "DROP": 949, "DEFER": 180}
    assert "### Historical Observatory replay schema (Lab #267)" in (ROOT / "MIGRATION.md").read_text()
