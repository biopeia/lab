from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[2]


def test_historical_body_pose_adapter_is_split_without_equivalence_claim() -> None:
    inventory = ROOT / "migration/source-inventory-80d372a.tsv"
    with inventory.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    row = next(item for item in rows if item["source_path"] == "lab/src/lab/observation/body_pose.py")

    assert row["source_blob_at_pinned_commit"] == "9eda624b2fcbcebaf5759faa9c4ec1b8e2f7cdcc"
    assert row["top_level_python_symbols"] == "EMBODIMENT_AUTHORITY;PHYSICS3D_SOURCE;PHYSICS3D_RUNTIME;LAB_PRODUCER;LAB_RUN_ISSUER;body_pose_observation"
    assert row["disposition"] == "SPLIT"
    assert "observation.py::BodyPoseSample" in row["target_path_or_status"]
    assert "observation/embodiment.py::embodiment_body_pose_observation" in row["target_path_or_status"]
    assert "observation_consumer.py" in row["target_path_or_status"]
    assert "not source API or semantic equivalence" in row["rationale_and_caveat"]

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical Body Pose observation adapter disposition (Lab #230)" in migration
    assert "No scientific measurement/validity, evidence admission or equivalence claim is made." in migration
