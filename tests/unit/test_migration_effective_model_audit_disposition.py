"""Protect the bounded defer and evidence-authority trigger for model audits."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/physics3d/effective_model_audit.py"
CLI_PATH = "lab/src/lab/physics3d/effective_model_audit_cli.py"
CLI_BLOB = "79efc42e6ab1d42f7aa12de8066b712d0e5dbcc7"
SOURCE_BLOB = "33d20da18a82ea2d1e5013619eae606a8c30509f"


def test_effective_model_audit_is_bounded_defer() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "21990"
    assert row["disposition"] == "DEFER"
    assert "Lab #330" in row["target_owner"]
    assert all(term in row["target_owner"] for term in ("Embodiment", "Environment", "World"))
    assert "No authorized TARGET effective-model audit contract" in row["target_path_or_status"]
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "Closure trigger" in rationale
    assert "outside the bounded runtime-transfer profile" in rationale
    assert "no model correctness" in rationale

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 29, "REWRITE": 3, "DROP": 949, "DEFER": 183}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "### Historical Physics3D effective-model audit disposition (Lab #294)" in migration
    assert CLI_BLOB in migration
    assert "### Historical Physics3D effective-model audit CLI disposition (Lab #295)" in migration
