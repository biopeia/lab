"""Keep the historical recombination disposition source-backed and bounded."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/evolution/recombination.py"
SOURCE_BLOB = "8ff4517f3f102688c6b9d9780128475418c7764a"


def test_historical_recombination_implementation_is_dropped_not_migrated() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))

    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "2232"
    assert row["top_level_python_symbols"] == "_parts;_set_path;recombine_genomes"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == (
        "Organism (future capability only; no current operation is authorized)"
    )
    assert row["target_path_or_status"] == (
        "No TARGET code destination; any future operation requires a new Organism design"
    )
    assert "Organism #49" in row["rationale_and_caveat"]

    counts = Counter(row["disposition"] for row in rows)
    assert counts == {
        "MOVE": 8,
        "SPLIT": 20,
        "REWRITE": 3,
        "DROP": 950,
        "DEFER": 191,
    }

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_COMMIT in migration
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 20 |" in migration
    assert "`DROP` | 950 |" in migration
    assert "This file performs one Organism-related genome operation" in migration
    assert "historical scientific validity" in migration
    assert not (ROOT / "src/lab/evolution/recombination.py").exists()


def test_neighboring_evolution_rows_are_not_implicitly_reclassified() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = {row["source_path"]: row for row in csv.DictReader(stream, delimiter="\t")}

    assert rows["lab/src/lab/evolution/mutation.py"]["disposition"] == "DROP"
    assert rows["lab/src/lab/evolution/reproduction.py"]["disposition"] == "DROP"
