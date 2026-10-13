"""Keep the historical Observation package-initializer disposition bounded."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/observation/__init__.py"
SOURCE_BLOB = "7c68362376e3d177daf15d86eeed0e916d45702b"


def test_historical_observation_initializer_is_dropped_only() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "207"
    assert row["top_level_python_symbols"] == ""
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Biopeia Lab historical Observation package initializer"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "Drop this historical initializer only" in row["rationale_and_caveat"]
    assert "scientific evidence custody" in row["rationale_and_caveat"]
    assert not (ROOT / "src/lab/observation").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 6, "SPLIT": 119, "REWRITE": 2, "DROP": 886, "DEFER": 159}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 119 |" in migration
    assert "`DROP` | 886 |" in migration
    assert "### Historical Observation package initializer" in migration
