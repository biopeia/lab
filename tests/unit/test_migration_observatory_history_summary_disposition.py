"""Keep the historical Observatory history-summary disposition auditable."""

import csv
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/observatory/history_summary.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "6461b3fce7d0f9e3be0381d4e64177331a6af313"


def test_history_summary_is_dropped_without_disposing_journal_records() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["bytes"] == "2557"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner; historical journal rollup utility"
    assert COMMIT in row["rationale_and_caveat"]
    assert BLOB in row["rationale_and_caveat"]
    assert "does not dispose of source journal records" in row["rationale_and_caveat"]
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "Historical Observatory history-summary disposition (Lab #254)" in migration
    assert BLOB in migration
