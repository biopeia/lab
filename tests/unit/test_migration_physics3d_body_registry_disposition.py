"""Keep the historical Lab body catalogue disposition evidence-backed and bounded."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/integration/physics3d/bodies.py"
SOURCE_BLOB = "e7753adda5aeb2c302f7477f882af39c9cdbaba9"


def test_historical_body_catalogue_composition_is_dropped_without_claiming_future_need() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    by_path = {row["source_path"]: row for row in rows}

    row = by_path[SOURCE_PATH]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "1201"
    assert row["top_level_python_symbols"] == (
        "ANTHROPOMORPHIC_V6_VISION;DEFAULT_BODY_REGISTRY"
    )
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner identified"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "Embodiment body presets" in row["rationale_and_caveat"]
    assert "Modality VisualApparatus" in row["rationale_and_caveat"]
    assert "No approved TARGET consumer" in row["rationale_and_caveat"]
    assert "newly specified for a concrete TARGET consumer" in row[
        "rationale_and_caveat"
    ]

    target_sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in (ROOT / "src/lab").rglob("*.py")
    )
    assert "ANTHROPOMORPHIC_V6_VISION" not in target_sources
    assert "DEFAULT_BODY_REGISTRY" not in target_sources

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 44, "REWRITE": 3, "DROP": 948, "DEFER": 169}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 44 |" in migration
    assert "`DROP` | 948 |" in migration
    assert "### Historical Lab Physics3D body registry and vision composition" in migration
