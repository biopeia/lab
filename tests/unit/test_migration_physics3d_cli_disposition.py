"""Pin the historical Physics3D CLI drop without broad domain claims."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/physics3d/cli.py"
SOURCE_BLOB = "e0e4a390f25db1b6f6bfe807222b3153b5eb3d6e"


def test_historical_physics3d_cli_is_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "7508"
    assert row["top_level_python_symbols"] == "run_replay;main"
    assert row["disposition"] == "DROP"
    assert "No TARGET owner" in row["target_owner"]
    assert "No TARGET CLI" in row["target_path_or_status"]
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "is transferred" in row["rationale_and_caveat"]
    assert "No source bytes are deleted" in row["rationale_and_caveat"]

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 29, "REWRITE": 3, "DROP": 949, "DEFER": 183}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "### Historical Lab Physics3D CLI disposition (Lab #293)" in migration
