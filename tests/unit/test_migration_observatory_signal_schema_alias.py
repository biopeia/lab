"""Drop the legacy symlink without changing its deferred schema target."""
from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
ALIAS_PATH = "lab/src/lab/observatory/signal_knowledge.schema.json"
ALIAS_BLOB = "012e142f6b6d3489adc6982ee01473e338b76477"
SCHEMA_PATH = "lab/src/lab/observatory/schemas/signal_knowledge.schema.json"
SCHEMA_BLOB = "fe960b2b38ef3655a5aff6867b81a46fbf380a9e"
TARGET_SHA256 = "ead3631c068819492a6a2e7f2fcfc980f6e84f3cbc89c9b52e33dc7d2553a741"


def test_signal_knowledge_symlink_is_dropped_without_dispositioning_target_schema() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = {row["source_path"]: row for row in csv.DictReader(stream, delimiter="\t")}

    alias = rows[ALIAS_PATH]
    assert alias["source_blob_at_pinned_commit"] == ALIAS_BLOB
    assert alias["git_mode"] == "120000" and alias["bytes"] == "36"
    assert alias["disposition"] == "DROP"
    assert alias["target_owner"] == "No TARGET code owner; historical Observatory schema alias"
    assert alias["target_path_or_status"] == "No TARGET schema/code destination"
    rationale = alias["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale and "schemas/signal_knowledge.schema.json" in rationale
    assert TARGET_SHA256 in rationale and "Lab #268" in rationale
    assert "no scientific validity/equivalence/admission" in rationale

    schema = rows[SCHEMA_PATH]
    assert schema["source_blob_at_pinned_commit"] == SCHEMA_BLOB
    assert schema["disposition"] == "DEFER"
    assert schema["target_owner"] == (
        "Organism semantic owner; Lab custody only for separately dispositioned scientific evidence"
    )
    counts = Counter(row["disposition"] for row in rows.values())
    assert counts == {"MOVE": 8, "SPLIT": 43, "REWRITE": 3, "DROP": 948, "DEFER": 170}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical Observatory signal-knowledge schema alias (Lab #272)" in migration
    assert ALIAS_BLOB in migration and SCHEMA_BLOB in migration and TARGET_SHA256 in migration
    assert "| `SPLIT` | 43 |" in migration and "| `DROP` | 948 |" in migration
