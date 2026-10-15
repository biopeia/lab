"""Keep the historical Lab run-definition API out of TARGET."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
TARGET_MAIN_COMMIT = "acfb5c6c44eb8fec3eebdcaf236c2b94d3d355a4"
SOURCE_PATH = "lab/src/lab/experience/definition.py"
SOURCE_BLOB = "1bbf7ea86a90f44203024888a1cfa029c5419ebd"
SOURCE_SYMBOLS = (
    "RunKind;TerminationReason;EXIT_BUDGET;EXIT_STOP;EXIT_BODY_NON_VIABLE;"
    "EXIT_DISCONNECTED;EXIT_ERROR;GUARD_PREFIX;resolve_termination;Situation;"
    "RunDefinition;DEFINITIONS;DEFAULT_DEFINITION_ID;run_definition;"
    "run_definition_catalog"
)


def test_experience_run_definition_is_dropped_without_scientific_claims() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "6593"
    assert row["top_level_python_symbols"] == SOURCE_SYMBOLS
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET code owner; historical Lab run apparatus"
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert TARGET_MAIN_COMMIT in rationale
    assert "no Organism-owned state" in rationale
    assert "absence of a current TARGET consumer" in rationale
    assert "does not decide whether a future Biopeia run-definition capability is useful" in rationale
    assert "classify related protocols/results" in rationale

    assert not (ROOT / "src/lab/experience/definition.py").exists()
    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 35, "REWRITE": 3, "DROP": 948, "DEFER": 178}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert SOURCE_COMMIT in migration
    assert TARGET_MAIN_COMMIT in migration
    assert "### Historical Lab run-definition module" in migration
    assert "does not decide whether a future Biopeia run-definition capability is useful" in migration
    assert "`SPLIT` | 35 |" in migration
    assert "`DROP` | 948 |" in migration
