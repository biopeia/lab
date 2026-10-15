"""Keep the historical history-summary characterization test disposition auditable."""

import csv
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/observatory/tests/test_history_summary.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "172039a1ab472acd38fc82cbb6822175cf3bbff3"


def test_history_summary_test_is_dropped_with_its_legacy_helper() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "1217"
    assert row["top_level_python_symbols"] == "test_summary_covers_raw_and_compacted_segments_without_replacing_them"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner; test for dropped historical helper"
    assert COMMIT in row["rationale_and_caveat"]
    assert BLOB in row["rationale_and_caveat"]
    assert "does not dispose of source journal records" in row["rationale_and_caveat"]
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "Historical Observatory history-summary test disposition (Lab #279)" in migration
    assert BLOB in migration
