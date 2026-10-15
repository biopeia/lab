"""Keep the cognition-state schema alias linked to its open schema review."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
ALIAS_PATH = "lab/src/lab/observatory/cognition_state.schema.json"
ALIAS_BLOB = "b22e40673ee98ac2d9c12039b685cc2aeb5ca16e"
SCHEMA_PATH = "lab/src/lab/observatory/schemas/cognition_state.schema.json"
SCHEMA_BLOB = "4a64ef2467617deb58e466602319c0cc5939cb71"


def test_cognition_schema_alias_is_bounded_defer_linked_to_schema_review() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = {
            row["source_path"]: row for row in csv.DictReader(stream, delimiter="\t")
        }
    alias = rows[ALIAS_PATH]
    assert alias["source_blob_at_pinned_commit"] == ALIAS_BLOB
    assert alias["git_mode"] == "120000"
    assert alias["bytes"] == "35"
    assert alias["top_level_python_symbols"] == ""
    assert alias["disposition"] == "DEFER"
    assert "#252/#265" in alias["target_path_or_status"]
    assert "No TARGET code owner" in alias["target_owner"]
    assert SOURCE_COMMIT in alias["rationale_and_caveat"]
    assert "schemas/cognition_state.schema.json" in alias["rationale_and_caveat"]
    assert "competent Organism/Observation owners" in alias["rationale_and_caveat"]
    assert "Closure trigger" in alias["rationale_and_caveat"]
    assert "No scientific validity/equivalence/admission" in alias["rationale_and_caveat"]

    schema = rows[SCHEMA_PATH]
    assert schema["source_blob_at_pinned_commit"] == SCHEMA_BLOB
    assert schema["disposition"] == "DROP"

    counts = Counter(row["disposition"] for row in rows.values())
    assert counts == {"MOVE": 8, "SPLIT": 25, "REWRITE": 3, "DROP": 949, "DEFER": 187}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Observatory cognition-state schema alias (Lab #252; underlying schema tracked by #265)" in migration
    assert ALIAS_BLOB in migration
    assert SCHEMA_BLOB in migration
    assert "`DEFER` | 187 |" in migration
