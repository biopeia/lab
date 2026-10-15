"""Keep the historical Observatory replay schema symlink alias out of TARGET."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
ALIAS_PATH = "lab/src/lab/observatory/replay.schema.json"
ALIAS_BLOB = "5f31831c1a9cd170f8384475e33c26e95742a3db"
SCHEMA_PATH = "lab/src/lab/observatory/schemas/replay.schema.json"
SCHEMA_BLOB = "d1f6f042b4ac49d70a8f4debf665ea4c68f72885"


def test_replay_schema_alias_drop_does_not_disposition_underlying_schema() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = {row["source_path"]: row for row in csv.DictReader(stream, delimiter="\t")}

    alias = rows[ALIAS_PATH]
    assert alias["source_blob_at_pinned_commit"] == ALIAS_BLOB
    assert alias["git_mode"] == "120000"
    assert alias["bytes"] == "26"
    assert alias["disposition"] == "DROP"
    assert alias["target_path_or_status"] == "No TARGET alias/path destination"
    assert alias["target_owner"] == (
        "No TARGET code owner; historical Observatory replay schema alias"
    )
    rationale = alias["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "`schemas/replay.schema.json`" in rationale
    assert "88f0c6a4af97c62cf3d1bcb80767051014b64f0387c63c27393d76da346be155" in rationale
    assert "#267" in rationale
    assert "UC-0001" in rationale
    assert "No scientific validity or equivalence claim" in rationale
    assert "adds no independent schema/API/behavior/contract" in rationale
    assert "no TARGET import/consumer of the alias was identified" in rationale
    assert "Lab #267 remains independent and unresolved" in rationale

    schema = rows[SCHEMA_PATH]
    assert schema["source_blob_at_pinned_commit"] == SCHEMA_BLOB
    assert schema["disposition"] == "DROP"
    assert schema["target_owner"] == "No TARGET owner for historical replay envelope"

    counts = Counter(row["disposition"] for row in rows.values())
    assert counts == {"MOVE": 8, "SPLIT": 29, "REWRITE": 3, "DROP": 949, "DEFER": 183}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert ALIAS_BLOB in migration
    assert SCHEMA_BLOB in migration
    assert "### Historical Observatory replay schema alias (Lab #261; sibling tracked by #267)" in migration
    assert "| `SPLIT` | 29 |" in migration
    assert "| `DROP` | 949 |" in migration
