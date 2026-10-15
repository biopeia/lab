"""Keep the historical Observatory journal-test disposition auditable."""

import csv
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/observatory/tests/test_journal.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "7cddecc56a0dc102c134cb305a61de124826789a"


def test_journal_tests_defer_with_the_unresolved_custody_contract() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "4562"
    assert row["top_level_python_symbols"] == "JournalTests"
    assert row["disposition"] == "DEFER"
    assert "Lab #280 coordinator" in row["target_owner"]
    assert "#256" in row["target_owner"] and "#242" in row["target_owner"]
    rationale = row["rationale_and_caveat"]
    assert COMMIT in rationale and BLOB in rationale
    assert "per-run append sequencing" in rationale
    assert "no TARGET journal schema" in rationale
    assert "Closure trigger:" in rationale
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "Historical Observatory journal-test disposition (Lab #280)" in migration
    assert BLOB in migration
