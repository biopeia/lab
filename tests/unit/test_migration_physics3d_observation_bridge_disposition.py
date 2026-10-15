"""Do not migrate the historical Physics3D observation bridge as-is."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/observation/physics3d.py"
SOURCE_BLOB = "116d19599724ddfb785e7e8ea4eaacfeb0c27a4a"
SYMBOLS = (
    "_body_descriptor_for_state;_optional_text;_topology_revision;"
    "EventSink;Physics3DObservationBridge"
)


def test_physics3d_observation_bridge_is_dropped_with_provenance() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "26053"
    assert row["top_level_python_symbols"] == SYMBOLS
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner"
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert "raw solver/body payloads" in rationale
    assert "Historical source remains read-only" in rationale
    assert "no physical/scientific validity" in rationale
    assert not (ROOT / "src/lab/observation/physics3d.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 63, "REWRITE": 3, "DROP": 934, "DEFER": 164}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "Historical Physics3D observation bridge disposition (Lab #239)" in migration
    assert "`src/embodiment/observation.py`" in migration
    assert "`DROP` | 934 |" in migration
