"""Legacy Lab world scene/presentation protocol has no TARGET owner path."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_PATH = "lab/src/lab/observation/world_scene.py"
SOURCE_BLOB = "fdf54be9b1dce8c0347c0ea4c40abf2cb6299699"
SYMBOLS = "SCENE_CONTRACT;project_world_scene;WorldScenePublisher;apply_world_event"


def test_historical_world_scene_protocol_is_dropped() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "6704"
    assert row["top_level_python_symbols"] == SYMBOLS
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner for historical view/transport"
    assert row["target_path_or_status"] == "No TARGET scene projection or publisher path"
    assert "not this Lab viewer schema" in row["rationale_and_caveat"]
    assert "No evidence admission" in row["rationale_and_caveat"]
    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 51, "REWRITE": 3, "DROP": 942, "DEFER": 168}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "Historical World scene presentation disposition (Lab #247)" in migration
