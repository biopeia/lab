from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[2]


def test_historical_body_physiology_adapter_is_bounded_split() -> None:
    inventory = ROOT / "migration/source-inventory-80d372a.tsv"
    with inventory.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    row = next(item for item in rows if item["source_path"] == "lab/src/lab/observation/body_physiology.py")

    assert row["source_blob_at_pinned_commit"] == "a2f3bc375850779d9d07bfe768c056f106d3ec83"
    assert row["top_level_python_symbols"] == "LIVING_BODY_SOURCE;body_physiology_observation"
    assert row["disposition"] == "SPLIT"
    assert "embodiment/physiology.py" in row["target_path_or_status"]
    assert "observation/semantic.py" in row["target_path_or_status"]
    assert "observation_consumer.py" in row["target_path_or_status"]
    assert "BodyPhysiologySample" in row["rationale_and_caveat"]

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical modeled body physiology observation adapter disposition (Lab #229)" in migration
    assert "No scientific validity, measurement status, evidence admission, or equivalence claim is made." in migration
