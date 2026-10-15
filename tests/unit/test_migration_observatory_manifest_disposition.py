"""Keep unresolved authority and custody for the legacy capture manifest explicit."""

import csv
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/observatory/manifest.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "e002f1a246b40317d9feea99083666b1e85fe143"


def test_capture_manifest_is_deferred_pending_authority_and_custody() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["bytes"] == "6374"
    assert row["disposition"] == "DEFER"
    assert "Lab owner" in row["target_owner"]
    assert "No authorized TARGET capture-manifest schema" in row["target_path_or_status"]
    assert COMMIT in row["rationale_and_caveat"]
    assert "Closure trigger:" in row["rationale_and_caveat"]
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "Historical Observatory capture-manifest disposition (Lab #257)" in migration
    assert BLOB in migration
