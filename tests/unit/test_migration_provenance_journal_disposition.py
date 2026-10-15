"""Defer durable provenance history until Lab resolves custody and retention."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_PATH = "lab/src/lab/observation/provenance_journal.py"
SOURCE_BLOB = "e4eb2840dc63c52b95cbfce812dda4e9828b7c3f"
SYMBOLS = "ProvenanceJournal;ProvenanceIndex;render_tree"


def test_provenance_journal_is_deferred_with_owner_decision_and_closure_trigger() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "6216"
    assert row["top_level_python_symbols"] == SYMBOLS
    assert row["disposition"] == "DEFER"
    assert row["target_owner"] == "Lab owner (evidence/provenance custody decision required)"
    assert "target path requires custody/admissibility and retention decision" in row["target_path_or_status"]
    rationale = row["rationale_and_caveat"]
    for phrase in (
        "Accountable owner: Lab owner",
        "Missing decision:",
        "Dependency: Lab #45 umbrella / #78 worklist",
        "closure trigger:",
        "does block such a continuity claim",
    ):
        assert phrase in rationale
    assert not (ROOT / "src/lab/observation/provenance_journal.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 46, "REWRITE": 3, "DROP": 947, "DEFER": 168}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "Historical provenance journal disposition (Lab #242)" in migration
    assert "closure trigger" in migration
    assert "`DEFER` | 168 |" in migration
