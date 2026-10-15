"""Keep the historical Observatory contract tests out of TARGET tests."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/observatory/tests/test_contract.py"
SOURCE_BLOB = "21d05a8ad1bd5fc0b9e341838e4d3caa55f602a7"


def test_historical_observatory_contract_tests_are_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "9307"
    assert row["top_level_python_symbols"] == (
        "ROOT;_read_js_bundle;ObservatoryContractTests;"
        "ObserverProvenanceContractTests;SensoryWorldMapContractTests"
    )
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET test owner"
    assert row["target_path_or_status"] == "No TARGET test destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "including unresolved DEFER rows" in row["rationale_and_caveat"]
    assert "not independent target contracts or scientific evidence" in row["rationale_and_caveat"]
    assert not (ROOT / "src/lab/observatory/tests/test_contract.py").exists()

    counts = Counter(row["disposition"] for row in rows)
    assert counts == {"MOVE": 8, "SPLIT": 43, "REWRITE": 3, "DROP": 948, "DEFER": 170}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 43 |" in migration
    assert "`DROP` | 948 |" in migration
    assert "### Historical Observatory contract test suite (Lab #277)" in migration
