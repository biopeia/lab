"""Keep the historical mutation source row bounded and evidence-backed."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/evolution/mutation.py"
SOURCE_BLOB = "fcd57742df5bdec29de2801aa4b3d68bffb2f4dd"


def test_historical_mutation_implementation_is_dropped_without_dropping_protocols() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))

    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "5019"
    assert row["top_level_python_symbols"] == (
        "_path_parts;_set_path;_family_scale;mutate_genome;"
        "mutate_continuous_fields;mutate_soft_budget;derive_child_genome"
    )
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == (
        "Organism future capability / Lab historical method; "
        "no current TARGET operation authorized"
    )
    assert "Organism #49" in row["rationale_and_caveat"]
    assert "historical protocols/results remain" in row["rationale_and_caveat"]

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {
        "MOVE": 8,
        "SPLIT": 64,
        "REWRITE": 3,
        "DROP": 934,
        "DEFER": 163,
    }

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_COMMIT in migration
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 64 |" in migration
    assert "`DROP` | 934 |" in migration
    assert "Historical genome mutation and developmental-budget intervention" in migration
    assert "Related historical protocols/results remain under their independent Lab #45" in migration
    assert not (ROOT / "src/lab/evolution/mutation.py").exists()


def test_reproduction_source_row_has_an_independent_disposition() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = {row["source_path"]: row for row in csv.DictReader(stream, delimiter="\t")}

    assert rows["lab/src/lab/evolution/reproduction.py"]["disposition"] == "DROP"
