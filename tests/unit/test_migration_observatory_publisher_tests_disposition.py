"""Keep the legacy publisher's test disposition auditable."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/observatory/tests/test_publisher.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "dd8a8891c32669072d04cc367db21ebe8751208b"


def test_historical_publisher_tests_are_bounded_defer() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = {row["source_path"]: row for row in csv.DictReader(stream, delimiter="\t")}
    row = rows[SOURCE]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "2617"
    assert row["top_level_python_symbols"] == "PublisherTests"
    assert row["disposition"] == "DEFER"
    assert "Lab migration/evidence-custody owner" in row["target_owner"]
    rationale = row["rationale_and_caveat"]
    assert COMMIT in rationale and BLOB in rationale
    assert "Five tests assert" in rationale
    assert "StdoutSink JSON-line/flush behavior" in rationale
    assert "JournalSink delegation" in rationale
    assert "whole-file ReplayRecorder output" in rationale
    assert "SnapshotPublisher fan-out" in rationale
    assert "DROP under Lab #259" in rationale
    assert "Lab #256" in rationale and "Observation #38" in rationale
    assert "Closure trigger:" in rationale
    assert "does not block the bounded runtime-transfer profile" in rationale
    assert "no scientific validity" in rationale

    counts = Counter(item["disposition"] for item in rows.values())
    assert counts == {"MOVE": 8, "SPLIT": 19, "REWRITE": 3, "DROP": 950, "DEFER": 192}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "Historical Observatory publisher-test disposition (Lab #283)" in migration
    assert BLOB in migration
    assert "`SPLIT` | 19 |" in migration
    assert "`DEFER` | 192 |" in migration
