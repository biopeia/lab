"""Keep the historical Observatory architecture inventory out of TARGET."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_BLOB = "38def6dbfef9e01d6352d17c4d87ce6facbd7aaf"
SOURCE_PATH = "lab/src/lab/observatory/ARCHITECTURE.md"


def test_historical_observatory_architecture_inventory_is_dropped_as_target() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1

    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "3759"
    assert row["top_level_python_symbols"] == ""
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == (
        "No TARGET owner; historical Observatory architecture inventory"
    )
    assert row["target_path_or_status"] == "No TARGET document destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "not a scientific protocol, result, or evidence artifact" in rationale
    assert "source remains read-only and preserved" in rationale
    assert "this does not claim that future visualization or Observation documentation is unnecessary" in rationale

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 41, "REWRITE": 3, "DROP": 948, "DEFER": 172}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical Observatory architecture inventory" in migration
    assert SOURCE_BLOB in migration
    assert "| `SPLIT` | 41 |" in migration
    assert "| `DROP` | 948 |" in migration


def test_historical_observatory_readme_is_dropped_as_target_documentation() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    source_path = "lab/src/lab/observatory/README.md"
    matches = [row for row in rows if row["source_path"] == source_path]
    assert len(matches) == 1

    row = matches[0]
    assert (
        row["source_blob_at_pinned_commit"]
        == "f4e3c4710ac5bc14f612c82a1c7ade809df8ee3c"
    )
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "20019"
    assert row["top_level_python_symbols"] == ""
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == (
        "No TARGET owner; historical Symbiont Observatory documentation"
    )
    assert row["target_path_or_status"] == "No TARGET document destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "not a scientific protocol, result, or evidence artifact" in rationale
    assert "read-only and preserved" in rationale
    assert "does not claim future Biopeia visualization" in rationale

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical Observatory user and operator README" in migration
    assert "f4e3c4710ac5bc14f612c82a1c7ade809df8ee3c" in migration
    assert "| `SPLIT` | 41 |" in migration
    assert "| `DROP` | 948 |" in migration
