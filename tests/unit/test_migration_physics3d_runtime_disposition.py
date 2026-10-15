from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = "lab/src/lab/physics3d/runtime.py"


def test_physics3d_runtime_row_has_pinned_split_and_concrete_target_paths() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    row = next(item for item in rows if item["source_path"] == SOURCE)

    assert row["source_blob_at_pinned_commit"] == "d2a70e298d05547c1aadb75195ab6c0f17496a43"
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "112656"
    assert row["top_level_python_symbols"].split(";") == [
        "LONGITUDINAL_CONTRACT",
        "metabolic_cost_from_actuator_work",
        "WORLD_BODY_ID",
        "PhysicsServerDisconnected",
        "Tick3D",
        "Physics3DEmbodimentRuntime",
    ]
    assert row["disposition"] == "SPLIT"
    assert row["target_owner"] == "Organism / World / Embodiment / Environment / Observation"
    for path in (
        "organism/src/organism/actuation/system.py",
        "world/src/world/causal_cycle.py",
        "world/src/world/adapters/mujoco.py",
        "embodiment/src/embodiment/physics3d/physical_transition.py",
        "embodiment/src/embodiment/checkpoint.py",
        "environment/src/environment/physical.py",
        "observation/src/observation/embodiment.py",
    ):
        assert path in row["target_path_or_status"]


def test_physics3d_runtime_disposition_records_boundaries_and_counts() -> None:
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "Historical Physics3D runtime disposition (Lab #303)" in migration
    assert "no source implementation is approved to move" in migration
    assert "no autonomy, scientific" in migration
    assert "| `SPLIT` | 20 |" in migration

