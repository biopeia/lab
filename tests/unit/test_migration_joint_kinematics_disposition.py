from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[2]


def test_historical_joint_kinematics_adapter_is_split_and_bounded_by_owner_contract() -> None:
    inventory = ROOT / "migration/source-inventory-80d372a.tsv"
    with inventory.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    row = next(item for item in rows if item["source_path"] == "lab/src/lab/observation/joint_kinematics.py")

    assert row["source_blob_at_pinned_commit"] == "6f69da7ae98e638455e85b2833a0ff50071a14b2"
    assert row["top_level_python_symbols"] == "joint_kinematics_observation"
    assert row["disposition"] == "SPLIT"
    assert "physical_projection.py::BodyPhysicalInput" in row["target_path_or_status"]
    assert "semantic.py::SemanticObservation" in row["target_path_or_status"]
    assert "embodiment#75" in row["target_path_or_status"]
    assert "not post-step observation" in row["rationale_and_caveat"]
    assert "No source compatibility" in row["rationale_and_caveat"]

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical Joint Kinematics observation adapter disposition (Lab #237)" in migration
    assert "No source compatibility, measurement/calibration, scientific validity, evidence admission or equivalence claim is made." in migration
