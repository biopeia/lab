"""Protect the bounded owner-dependent disposition of the legacy engine."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_PATH = "lab/src/lab/physics3d/engine.py"
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_BLOB = "f98aca80171e64485e39631a89ec3e56c5c7f349"


def test_physics3d_engine_is_deferred_pending_target_runtime_contracts() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "44487"
    assert row["disposition"] == "DEFER"
    assert all(owner in row["target_owner"] for owner in ("World", "Embodiment", "Environment", "Lab"))
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "No authorized TARGET cross-domain runtime/orchestration contract" in row[
        "target_path_or_status"
    ]
    assert "Closure trigger" in rationale
    assert "does not block the separately bounded runtime-transfer profile" in rationale

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 14, "REWRITE": 3, "DROP": 950, "DEFER": 197}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "### Historical Physics3D engine disposition (Lab #297)" in migration
