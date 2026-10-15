"""Keep duplicated historical Observatory snapshot schemas out of TARGET."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_BLOB = "469eb56de0a1ce806eb4dfd693d06691cbf9f220"
SOURCE_PATHS = {
    "lab/src/lab/observatory/snapshot.schema.json",
    "lab/src/lab/observatory/schemas/snapshot.schema.json",
}
SOURCE_SHA256 = "3ffb739a06c7047d184b8c392d6916a0e5b6a71232472048be92d11a7c09e6f0"


def test_historical_observatory_snapshot_schemas_are_dropped_as_target() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] in SOURCE_PATHS]
    assert {row["source_path"] for row in matches} == SOURCE_PATHS
    assert len(matches) == 2

    for row in matches:
        assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
        assert row["git_mode"] == "100644"
        assert row["bytes"] == "61719"
        assert row["top_level_python_symbols"] == ""
        assert row["disposition"] == "DROP"
        assert row["target_owner"] == (
            "No TARGET code owner; historical Lab Observatory schema"
        )
        assert row["target_path_or_status"] == "No TARGET schema/code destination"
        rationale = row["rationale_and_caveat"]
        assert SOURCE_COMMIT in rationale
        assert SOURCE_SHA256 in rationale
        assert "byte-identical" in rationale
        assert "no Biopeia TARGET consumer or authorized schema/wire contract" in rationale
        assert "future Observation semantic-family schemas are unnecessary" in rationale
        assert "source remains read-only" in rationale

    counts = Counter(row["disposition"] for row in rows)
    assert counts == {"MOVE": 8, "SPLIT": 50, "REWRITE": 3, "DROP": 943, "DEFER": 168}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical Observatory snapshot schemas" in migration
    assert SOURCE_BLOB in migration
    assert SOURCE_SHA256 in migration
    bt = chr(96)
    assert f"{bt}SPLIT{bt} | 50 |" in migration
    assert f"{bt}DROP{bt} | 943 |" in migration
    assert "does not claim future Observation semantic-family schemas are unnecessary" in migration
