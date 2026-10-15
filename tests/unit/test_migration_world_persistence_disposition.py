import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_world_persistence_row_has_explicit_owner_split_and_aggregate_drop():
    inventory = ROOT / "migration/source-inventory-80d372a.tsv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == "lab/src/lab/world/persistence.py"]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == "0871079c908d2efb0329c3f0571a1d22671f12d7"
    assert row["disposition"] == "SPLIT"
    for owner in ("World", "Environment", "Organism", "Embodiment"):
        assert owner in row["target_owner"]
    for target in ("src/world/durable_runtime.py", "src/world/owner_checkpoint_store.py", "src/organism/checkpoint.py", "src/embodiment/checkpoint.py"):
        assert target in row["target_path_or_status"]
    assert "DROP the old schema" in row["rationale_and_caveat"]
    assert "No Lab-owned aggregate persistence path" in row["rationale_and_caveat"]


def test_world_persistence_disposition_is_recorded_in_migration_ledger():
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### `WorldStorage` and aggregate checkpoint source row disposition (Lab #319)" in migration
    assert "opaque checkpoint references" in migration
    assert "do not establish current cross-owner durability" in migration
