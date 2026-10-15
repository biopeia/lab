import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_world_runtime_source_row_has_explicit_owner_split_and_drop_boundary():
    inventory = ROOT / "migration/source-inventory-80d372a.tsv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))

    matches = [row for row in rows if row["source_path"] == "lab/src/lab/world/runtime.py"]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == "de62c2b2e56cb5c6a08fb431441ff3ecb8db9844"
    assert row["disposition"] == "SPLIT"
    assert "class/API itself is DROP" in row["rationale_and_caveat"]
    assert "src/world/runtime.py" in row["target_path_or_status"]
    assert "Environment" in row["target_owner"]
    assert "Embodiment" in row["target_owner"]
    assert "Observation" in row["target_owner"]
    assert "tick-delay semantics" in row["rationale_and_caveat"]
    assert "no Lab-owned runtime" in row["target_owner"]


def test_world_runtime_final_disposition_is_recorded_in_migration_ledger():
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### `WorldRuntimeState` source row disposition (Lab #321)" in migration
    assert "host-time pacing is not causal progression" in migration
    assert "No Lab TARGET consumer/path for this class was found" in migration
