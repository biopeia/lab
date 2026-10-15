"""Bound the split projection responsibility to its explicit TARGET bridge."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_PATH = "lab/src/lab/observation/projection.py"
SOURCE_BLOB = "9ee6e8ccd2ebdcd1896ebe17d035f42a0da48655"
SYMBOLS = "_identity;_copy_number;_copy_bool;runtime_tick_events;_prediction_class;mind_snapshot_from_rich_state"


def test_projection_row_splits_transitional_runtime_view_from_legacy_mind_schema() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "36067"
    assert row["top_level_python_symbols"] == SYMBOLS
    assert row["disposition"] == "SPLIT"
    assert row["target_owner"] == "Observation (runtime projection only); none for legacy Mind view"
    assert row["target_path_or_status"] == (
        "repos/observation/src/observation/projection.py::runtime_tick_events; "
        "mind_snapshot_from_rich_state: No TARGET schema/path authorized"
    )
    rationale = row["rationale_and_caveat"]
    assert "concrete TARGET migration-stage counterpart" in rationale
    assert "no matching TARGET schema, function, or consumer was found" in rationale
    assert "does not define Lab evidence custody/admission" in rationale
    assert not (ROOT / "src/lab/observation/projection.py").exists()

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "Historical runtime/Mind projection disposition (Lab #241)" in migration
    assert "not a stable semantic-family contract" in migration
