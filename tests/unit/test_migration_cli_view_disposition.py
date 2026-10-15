"""Keep the retired Hex World CLI view excluded from TARGET code."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/world/cli_view.py"
SOURCE_BLOB = "0f0ed5fcb41253a05b37413de3f6cdd08f1297ab"


def test_historical_hex_world_cli_view_is_dropped_without_future_ui_claim() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "15581"
    assert row["top_level_python_symbols"] == "_label;_calculate_density;world_snapshot;render_world"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "private population._rigs state" in row["rationale_and_caveat"]
    assert "future visualization must be newly authored against passive Observation publications" in row[
        "rationale_and_caveat"
    ]
    assert "no claim is made that future visualization is unnecessary" in row[
        "rationale_and_caveat"
    ]
    assert not (ROOT / "src/lab/world/cli_view.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 20, "REWRITE": 3, "DROP": 950, "DEFER": 191}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 20 |" in migration
    assert "`DROP` | 950 |" in migration
    assert "### Historical Hex World CLI visualization" in migration
