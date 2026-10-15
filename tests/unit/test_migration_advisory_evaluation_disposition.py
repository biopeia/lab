"""Keep the historical advisory-evaluation disposition auditable."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_PATH = "lab/src/lab/evaluation/advisory_evaluation.py"
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_BLOB = "e2d11c6420ea03b86f4de2fb072342d0fd94d864"


def test_historical_advisory_evaluation_module_is_dropped_without_target_claim() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "7457"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert SOURCE_BLOB in row["rationale_and_caveat"]
    assert "Organism main 26778028c4058d96ba2f2b77199df7852a03def1" in row["rationale_and_caveat"]
    assert "no TARGET consumer in Lab main 8febcad282e9c0ed0340dc255ae1c85b7cdd8992" in row["rationale_and_caveat"]
    assert "makes no claim about the scientific validity or usefulness" in row["rationale_and_caveat"]
    assert not (ROOT / "src/lab/evaluation/advisory_evaluation.py").exists()

    counts = Counter(row["disposition"] for row in rows)
    assert counts == {
        "MOVE": 6,
        "SPLIT": 86,
        "REWRITE": 2,
        "DROP": 918,
        "DEFER": 160,
    }

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 86 |" in migration
    assert "`DROP` | 918 |" in migration
    assert "A future capability requires a newly specified TARGET source and workflow." in migration
