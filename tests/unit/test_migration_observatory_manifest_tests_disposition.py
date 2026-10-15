"""Keep the historical Observatory manifest-test disposition auditable."""

import csv
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/observatory/tests/test_manifest.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "22763bb6941654000d1bc7cf0941a6f7c71d5736"


def test_manifest_tests_defer_pending_manifest_and_registry_contracts() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "8115"
    assert row["top_level_python_symbols"] == "ManifestTests"
    assert row["disposition"] == "DEFER"
    assert "#257" in row["target_owner"] and "#260" in row["target_owner"]
    rationale = row["rationale_and_caveat"]
    assert COMMIT in rationale and BLOB in rationale
    assert "no authorized capture schema" in rationale
    assert "legacy canonical-organism integration adapter" in rationale
    assert "closure trigger" in rationale.lower()
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "Historical Observatory manifest-test disposition (Lab #281)" in migration
    assert BLOB in migration
