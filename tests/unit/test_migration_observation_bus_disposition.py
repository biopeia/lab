from pathlib import Path
import csv

ROOT = Path(__file__).resolve().parents[2]


def test_historical_observation_bus_is_split_from_legacy_transport() -> None:
    inventory = ROOT / "migration/source-inventory-80d372a.tsv"
    with inventory.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    row = next(item for item in rows if item["source_path"] == "lab/src/lab/observation/bus.py")

    assert row["source_blob_at_pinned_commit"] == "f270ded3e9963456eea3d18c94ba0b1d2bfb3e81"
    assert row["top_level_python_symbols"] == "ObservationMessage;_with_rebase_notice;ObservationBus"
    assert row["disposition"] == "SPLIT"
    assert "observation/plane.py::ObservationPlane" in row["target_path_or_status"]
    assert "observation_consumer.py::associate_stream_messages" in row["target_path_or_status"]
    assert "DROP the historical event-bus implementation" in row["rationale_and_caveat"]

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical Lab ObservationBus disposition (Lab #231)" in migration
    assert "not the old SSE bus" in migration
