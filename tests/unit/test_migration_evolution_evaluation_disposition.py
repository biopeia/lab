"""Keep the historical evolution evaluation disposition evidence-backed."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/evolution/evaluation.py"
SOURCE_BLOB = "749b84d3b66da594464a8dc6cd2d21da3460e86c"


def test_historical_evolution_evaluation_row_matches_bounded_drop() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "1279"
    assert row["top_level_python_symbols"] == "EvaluationResult;select_archive"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner established"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert SOURCE_BLOB in row["rationale_and_caveat"]
    assert "no production caller" in row["rationale_and_caveat"]
    assert "does not assess scientific validity" in row["rationale_and_caveat"]
    assert not (ROOT / "src/lab/evolution/evaluation.py").exists()

    counts = Counter(row["disposition"] for row in rows)
    assert counts == {
        "MOVE": 8,
        "SPLIT": 49,
        "REWRITE": 3,
        "DROP": 944,
        "DEFER": 168,
    }

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 49 |" in migration
    assert "`DROP` | 944 |" in migration
    assert "No currently authorized TARGET study/method" in migration
    assert "does not assess scientific validity, utility or equivalence" in migration
