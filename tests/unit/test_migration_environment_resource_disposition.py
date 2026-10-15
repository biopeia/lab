from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[2]


def test_historical_environment_resource_adapter_is_dispositioned_without_equivalence_claim() -> None:
    inventory = ROOT / "migration/source-inventory-80d372a.tsv"
    with inventory.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    row = next(item for item in rows if item["source_path"] == "lab/src/lab/observation/environment_resource.py")

    assert row["source_blob_at_pinned_commit"] == "c849ed5be32744799949d0529a65e37965ace9e2"
    assert row["top_level_python_symbols"] == "ENVIRONMENT_AUTHORITY;WORLD_STATE_ISSUER;WORLD_ENVIRONMENT_SOURCE;WORLD_RUNTIME_PRODUCER;resource_state_observation"
    assert row["disposition"] == "SPLIT"
    assert "identified_resource.py::project_committed_resource_state" in row["target_path_or_status"]
    assert "environment.py::environment_resource_state_observation" in row["target_path_or_status"]
    assert "material_transfer.py" in row["target_path_or_status"]
    assert "not source API or semantic equivalence" in row["rationale_and_caveat"]

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical Environment resource observation adapter disposition (Lab #236)" in migration
    assert "No scientific measurement/validity, evidence admission or equivalence claim is made." in migration
