"""Keep the historical evolution re-export disposition narrowly scoped."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/evolution/__init__.py"
SOURCE_BLOB = "fd96fd72dd947913e2bc183c36b53c343cccae7f"


def test_historical_evolution_reexport_row_matches_bounded_disposition() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "1105"
    assert row["top_level_python_symbols"] == ""
    assert row["disposition"] == "DROP"
    assert "Lab (historical scientific apparatus" in row["target_owner"]
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert SOURCE_BLOB in row["rationale_and_caveat"]
    assert "Drop only this legacy re-export facade" in row["rationale_and_caveat"]
    assert "does not classify the sibling implementation rows" in row["rationale_and_caveat"]
    assert not (ROOT / "src/lab/evolution/__init__.py").exists()

    counts = Counter(row["disposition"] for row in rows)
    assert counts == {
        "MOVE": 8,
        "SPLIT": 68,
        "REWRITE": 3,
        "DROP": 932,
        "DEFER": 161,
    }

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 68 |" in migration
    assert "`DROP` | 932 |" in migration
    assert "remain separate inventory rows" in migration
    assert "a package-level facade may be `DROP` when separately dispositioned" in migration
