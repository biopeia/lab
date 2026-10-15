from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = "lab/src/lab/physics3d/settling.py"


def test_physics3d_settling_row_is_pinned_and_bounded_defer() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    row = next(item for item in rows if item["source_path"] == SOURCE)

    assert row["source_blob_at_pinned_commit"] == "0f77e2ca231e0550bfc9e74d47750cdfeea2d068"
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "4539"
    assert row["top_level_python_symbols"] == "SettlingResult;SETTLING_MAX_STEPS;settle_passive_body"
    assert row["disposition"] == "DEFER"
    assert row["target_owner"] == "Embodiment / World / Lab (scientific evidence custody only)"
    assert "No target-owned passive-settling contract" in row["target_path_or_status"]
    assert "Embodiment must decide" in row["rationale_and_caveat"]
    assert "explicit DROP" in row["rationale_and_caveat"]


def test_physics3d_settling_disposition_records_missing_authority_and_counts() -> None:
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "Historical Physics3D passive settling disposition (Lab #304)" in migration
    assert "does not block target runtime extraction" in migration
    assert "| `DEFER` | 194 |" in migration

