"""Keep historical Observatory publisher disposition separate from World publication."""

import csv
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/observatory/publisher.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "16860fd39c55472f7b6f8f8df26a170ca1e91f4f"


def test_legacy_observatory_publisher_is_dropped_without_equivalence_claim() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["bytes"] == "2100"
    assert row["top_level_python_symbols"] == "Sink;StdoutSink;JournalSink;ReplayRecorder;SnapshotPublisher"
    assert row["disposition"] == "DROP"
    assert COMMIT in row["rationale_and_caveat"]
    assert "different contract, not a replacement or behavioral-equivalence claim" in row["rationale_and_caveat"]
    assert "journal data retention is separately unresolved in Lab #256" in row["rationale_and_caveat"]
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "Historical Observatory publisher disposition (Lab #259)" in migration
    assert BLOB in migration
