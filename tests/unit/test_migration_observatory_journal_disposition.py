"""Keep the legacy Observatory journal custody blocker explicit."""

import csv
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/observatory/journal.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "bad69fb063b32a949ae50b765672b69f8f61dffa"


def test_observatory_journal_is_deferred_pending_custody_decision() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["bytes"] == "3957"
    assert row["top_level_python_symbols"] == "Journal"
    assert row["disposition"] == "DEFER"
    assert "Lab owner" in row["target_owner"]
    assert "No TARGET journal schema, retention policy, or authorized storage path" in row["target_path_or_status"]
    assert COMMIT in row["rationale_and_caveat"]
    assert "Closure trigger:" in row["rationale_and_caveat"]
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "Historical Observatory journal disposition (Lab #256)" in migration
    assert BLOB in migration
