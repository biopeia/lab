"""Keep the historical offspring implementation excluded from TARGET code."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/evolution/reproduction.py"
SOURCE_BLOB = "4f990ac460e0b4104b925730e5705aa9179b70ae"


def test_historical_reproduction_implementation_is_dropped_not_migrated() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))

    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "2085"
    assert row["top_level_python_symbols"] == "create_offspring_package"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Organism future capability / Lab historical method"
    assert "Organism #49" in row["rationale_and_caveat"]
    assert "Lab #45" in row["rationale_and_caveat"]
    assert "no scientific validity" in row["rationale_and_caveat"]

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {
        "MOVE": 6,
        "SPLIT": 91,
        "REWRITE": 2,
        "DROP": 913,
        "DEFER": 160,
    }

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_COMMIT in migration
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 91 |" in migration
    assert "`DROP` | 913 |" in migration
    assert "Historical offspring-package implementation" in migration
    assert "protocol/result artifacts remain separately governed by Lab #45" in migration
    assert not (ROOT / "src/lab/evolution/reproduction.py").exists()
