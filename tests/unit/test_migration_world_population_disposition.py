import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def test_world_population_row_has_evidence_backed_responsibility_split_and_drop_boundary():
    inventory = ROOT / "migration/source-inventory-80d372a.tsv"
    with inventory.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))

    matches = [row for row in rows if row["source_path"] == "lab/src/lab/world/population.py"]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == "bcb046937b036fad9264599a7832afd95e810d29"
    assert row["top_level_python_symbols"] == "founder_placement;PopulationTickRecord;PopulationGenesisRuntime"
    assert row["disposition"] == "SPLIT"
    for owner in ("World", "Environment", "Organism", "Embodiment"):
        assert owner in row["target_owner"]
    assert "no Lab-owned population runtime" in row["target_owner"]
    for target in ("src/world/durable_runtime.py", "src/environment/resource.py", "src/organism/transition.py", "src/embodiment/physiology.py"):
        assert target in row["target_path_or_status"]
    assert "not one-to-one replacements" in row["rationale_and_caveat"]
    assert "DROP as TARGET implementation" in row["rationale_and_caveat"]


def test_world_population_disposition_is_recorded_in_migration_ledger():
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### `PopulationGenesisRuntime` source row disposition (Lab #320)" in migration
    assert "private `_rigs` storage" in migration
    assert "no TARGET population factory" in migration
