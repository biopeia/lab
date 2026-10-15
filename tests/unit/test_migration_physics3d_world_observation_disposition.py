"""Pin the bounded disposition of the historical World-observation adapter."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/physics3d/world_observation.py"
SOURCE_BLOB = "76b380080757ad1a9819b5eb2664539d3febe818"
SOURCE_SHA256 = "c552e7ab0cb0d9aae13356009c9139e9e1204202d963b4bb6ea9c68bcfbbd40a"


def test_physics3d_world_observation_adapter_is_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matching = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matching) == 1
    row = matching[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "6325"
    assert row["top_level_python_symbols"] == "PhysicsWorldObserver"
    assert row["disposition"] == "DROP"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert row["target_owner"] == "No TARGET owner: historical Lab Physics3D observer adapter"
    for evidence in (
        SOURCE_COMMIT,
        SOURCE_SHA256,
        "path commit 40adf60c42322c06b225e9169dbb77b126c04257",
        "Environment static/dynamic physical state",
        "Embodiment receptor sampling",
        "World causal composition/publication",
        "not scientific validity or TARGET behavior",
    ):
        assert evidence in row["rationale_and_caveat"]

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 36, "REWRITE": 3, "DROP": 948, "DEFER": 177}
    assert not (ROOT / "src/lab/physics3d/world_observation.py").exists()


def test_world_observation_disposition_is_recorded_in_migration_ledger() -> None:
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical PhysicsWorldObserver adapter disposition (Lab #316)" in migration
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 36 |" in migration
    assert "`DROP` | 948 |" in migration
    assert "This disposition does not rule out a separately designed TARGET physical-observation composition." in migration
