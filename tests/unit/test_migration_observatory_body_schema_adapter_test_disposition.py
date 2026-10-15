"""Keep the legacy body-schema adapter tests out of TARGET tests."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/observatory/tests/test_body_schema_adapter.py"
SOURCE_BLOB = "66c27df821f6ee57d7ea5e51b175381c56a575ec"


def test_historical_body_schema_adapter_test_is_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "6494"
    assert row["top_level_python_symbols"] == (
        "result;sense_part;region_part;body_schema_v1;body_schema_v2;BodySchemaAdapterTests"
    )
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET test owner"
    assert row["target_path_or_status"] == "No TARGET test destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "not a target-owned schema/contract or scientific result" in row["rationale_and_caveat"]
    assert "future body self-knowledge observation or safeguards are unnecessary" in row["rationale_and_caveat"]
    assert not (ROOT / "src/lab/observatory/tests/test_body_schema_adapter.py").exists()

    counts = Counter(row["disposition"] for row in rows)
    assert counts == {"MOVE": 8, "SPLIT": 33, "REWRITE": 3, "DROP": 949, "DEFER": 179}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 33 |" in migration
    assert "`DROP` | 949 |" in migration
    assert "### Historical Observatory body-schema adapter test (Lab #276)" in migration
