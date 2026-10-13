"""Keep the evaluation re-export disposition consistent in the inventory."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/evaluation/__init__.py"
SOURCE_BLOB = "2ee39fcc87b2a48b2d1a5ca183c0369c4bc688b1"


def test_historical_evaluation_package_row_matches_disposition_record() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "224"
    assert row["top_level_python_symbols"] == ""
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert SOURCE_BLOB in row["rationale_and_caveat"]
    assert "only re-exports DevelopmentPhase, FrozenEvaluationPhase, and SeedLedger" in row[
        "rationale_and_caveat"
    ]
    assert "does not determine the underlying holdout.py disposition" in row[
        "rationale_and_caveat"
    ]
    assert not (ROOT / "src/lab/evaluation/__init__.py").exists()

    counts = Counter(row["disposition"] for row in rows)
    assert counts == {
        "MOVE": 6,
        "SPLIT": 115,
        "REWRITE": 2,
        "DROP": 891,
        "DEFER": 158,
    }

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 115 |" in migration
    assert "`DROP` | 891 |" in migration
    assert "underlying historical module is" in migration and "separately dispositioned below" in migration
