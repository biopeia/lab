"""Protect evidence limits and owners for the historical equivalence tool."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_PATH = "lab/src/lab/physics3d/equivalence.py"
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_BLOB = "db6a9b34ada3f706d28e40b921ea2a418fc84c52"


def test_equivalence_tool_is_deferred_to_contract_and_evidence_policy() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "13944"
    assert row["disposition"] == "DEFER"
    assert all(owner in row["target_owner"] for owner in ("Lab", "World", "Embodiment"))
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "Closure trigger" in row["rationale_and_caveat"]
    assert "No authorized TARGET snapshot-equivalence contract" in row["target_path_or_status"]

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 26, "REWRITE": 3, "DROP": 949, "DEFER": 186}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "### Historical Physics3D snapshot-equivalence disposition (Lab #298)" in migration
