"""Keep the historical Observatory body-schema alias linked to its open schema review."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
ALIAS_PATH = "lab/src/lab/observatory/body_schema.schema.json"
ALIAS_BLOB = "a8aac03965d0416b6e8849db4c582638cbfe6c2f"
SCHEMA_PATH = "lab/src/lab/observatory/schemas/body_schema.schema.json"
SCHEMA_BLOB = "4f393ed9161c3ba8e9672dc78edbb1bef9cd516d"


def test_body_schema_alias_is_bounded_defer_linked_to_underlying_schema() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = {
            row["source_path"]: row for row in csv.DictReader(stream, delimiter="\t")
        }

    alias = rows[ALIAS_PATH]
    assert alias["source_blob_at_pinned_commit"] == ALIAS_BLOB
    assert alias["git_mode"] == "120000"
    assert alias["bytes"] == "31"
    assert alias["top_level_python_symbols"] == ""
    assert alias["disposition"] == "DEFER"
    assert "#251/#264" in alias["target_path_or_status"]
    assert "No TARGET code owner" in alias["target_owner"]
    assert SOURCE_COMMIT in alias["rationale_and_caveat"]
    assert "schemas/body_schema.schema.json" in alias["rationale_and_caveat"]
    assert "competent Organism/Observation owners" in alias["rationale_and_caveat"]
    assert "Closure trigger" in alias["rationale_and_caveat"]
    assert "No scientific validity/equivalence/admission" in alias["rationale_and_caveat"]

    schema = rows[SCHEMA_PATH]
    assert schema["source_blob_at_pinned_commit"] == SCHEMA_BLOB
    assert schema["disposition"] == "DROP"
    assert schema["target_owner"] == "No TARGET schema owner for this legacy projection"

    counts = Counter(row["disposition"] for row in rows.values())
    assert counts == {"MOVE": 8, "SPLIT": 41, "REWRITE": 3, "DROP": 948, "DEFER": 172}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Observatory body-schema alias (Lab #251; underlying schema tracked by #264)" in migration
    assert ALIAS_BLOB in migration
    assert SCHEMA_BLOB in migration
    assert "`DEFER` | 172 |" in migration
    assert "no scientific validity, equivalence, or evidence-admission claim" in migration
