"""Keep the historical integrated habitat out of TARGET code."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/integration/integrated_habitat.py"
SOURCE_BLOB = "20b8de5348f05930cffc583efced5d72a3105ac7"


def test_integrated_habitat_runtime_is_dropped_as_target_implementation() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))

    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "19401"
    assert row["top_level_python_symbols"] == (
        "IntegratedHabitatConfig;IntegratedTickSummary;IntegratedHabitatRuntime"
    )
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "No separable TARGET responsibility in this file is retained" in row[
        "rationale_and_caveat"
    ]
    assert "pinned source remains read-only" in row["rationale_and_caveat"]
    assert not (ROOT / "src/lab/integration/integrated_habitat.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 23, "REWRITE": 3, "DROP": 949, "DEFER": 189}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 23 |" in migration
    assert "`DROP` | 949 |" in migration
    assert "The historical study/protocol/results and source artifacts are separate" in migration
