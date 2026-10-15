"""Keep a legacy Observatory symlink alias out of the Biopeia TARGET."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/observatory/topology.schema.json"
SOURCE_BLOB = "d83405ac5e7eac3565e2ff88caf159e2a59f1f62"
SCHEMA_PATH = "lab/src/lab/observatory/schemas/topology.schema.json"
SCHEMA_BLOB = "6525f49ddf3271b0ff6f8fde7fe516da791f9059"


def test_topology_schema_alias_is_dropped_without_dispositioning_target_schema() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = {row["source_path"]: row for row in csv.DictReader(stream, delimiter="\t")}

    alias = rows[SOURCE_PATH]
    assert alias["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert alias["git_mode"] == "120000"
    assert alias["bytes"] == "28"
    assert alias["disposition"] == "DROP"
    assert alias["target_path_or_status"] == "No TARGET code destination"
    assert alias["target_owner"] == "No TARGET code owner; historical Observatory schema alias"
    rationale = alias["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "`schemas/topology.schema.json`" in rationale
    assert "UC-0001" in rationale
    assert "No scientific validity or equivalence claim" in rationale

    schema = rows[SCHEMA_PATH]
    assert schema["source_blob_at_pinned_commit"] == SCHEMA_BLOB
    assert schema["disposition"] == "SPLIT"
    assert schema["target_owner"] == "Observation / Lab"

    counts = Counter(row["disposition"] for row in rows.values())
    assert counts == {"MOVE": 6, "SPLIT": 98, "REWRITE": 2, "DROP": 906, "DEFER": 160}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert SCHEMA_BLOB in migration
    assert "### Historical Observatory topology schema alias" in migration
    assert "| `SPLIT` | 98 |" in migration
    assert "| `DROP` | 906 |" in migration
