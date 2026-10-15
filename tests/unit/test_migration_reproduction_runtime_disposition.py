"""Keep the historical clonal-budding adapter out of TARGET."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/reproduction/runtime.py"
SOURCE_BLOB = "1f24d3c045f971f4e69c4df019da7da1b581aa72"


def test_clonal_budding_runtime_is_dropped_as_historical_composite() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))

    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "6956"
    assert row["top_level_python_symbols"] == "materialize_clonal_bud;_birth_surfaces_available"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET code destination"
    assert row["target_path_or_status"] == "No TARGET implementation retained"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "Organism #49" in row["rationale_and_caveat"]
    assert "Lab #317" in row["rationale_and_caveat"]
    assert "no claim that reproduction is unnecessary" in row["rationale_and_caveat"]

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 6, "SPLIT": 98, "REWRITE": 2, "DROP": 906, "DEFER": 160}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical clonal-budding runtime disposition (Lab #318)" in migration
    assert SOURCE_BLOB in migration
    assert "no target offspring initializer/path is established" in migration
    assert "not scientific validation or evidence of target equivalence" in migration
    assert "`SPLIT` | 98 |" in migration
    assert "`DROP` | 906 |" in migration
