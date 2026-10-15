"""Keep the historical holdout implementation disposition bounded and sourced."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/evaluation/holdout.py"
SOURCE_BLOB = "b9f230fb6ff5b3b33e99cd5be21c6a730d45d85d"


def test_holdout_implementation_drop_is_separate_from_scientific_disposition() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "5018"
    assert row["disposition"] == "DROP"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "predictive_discovery" in row["rationale_and_caveat"]
    assert "does not classify predictive_discovery protocol/results" in row["rationale_and_caveat"]
    assert not (ROOT / "src/lab/evaluation/holdout.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 6, "SPLIT": 81, "REWRITE": 2, "DROP": 923, "DEFER": 160}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 81 |" in migration
    assert "`DROP` | 923 |" in migration
    assert "does not disposition the study protocol/results" in migration
