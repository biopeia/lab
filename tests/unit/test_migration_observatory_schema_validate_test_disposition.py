"""Keep the historical Observatory schema test out of TARGET tests."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_PATH = "lab/src/lab/observatory/tests/test_schema_validate.py"
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_BLOB = "d6754edd98b6e26315ee2f95d13d7e4038642bba"


def test_historical_schema_validation_test_has_bounded_drop_disposition() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))

    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "3912"
    assert row["top_level_python_symbols"] == (
        "SchemaValidateConditionalTests;SignalKnowledgeSchemaTests"
    )
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner"
    assert row["target_path_or_status"] == "No TARGET test destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "historical Lab Observatory's custom JSON-schema validation behavior" in rationale
    assert "structural, not scientific evidence" in rationale
    assert "preserve its source and provenance read-only" in rationale
    assert "does not claim future schema validation" in rationale

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 7, "SPLIT": 75, "REWRITE": 3, "DROP": 927, "DEFER": 160}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical Observatory schema-validation tests" in migration
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 75 |" in migration
    assert "`DROP` | 927 |" in migration
    assert "This does not claim future schema validation" in migration
