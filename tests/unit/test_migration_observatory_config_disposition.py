"""Keep historical Observatory runtime defaults out of TARGET configuration."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/observatory/config.py"
SOURCE_BLOB = "3400ea0a13552fd3d62cd2bc5178daada89792f8"


def test_observatory_config_is_dropped_as_historical_runtime_configuration() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = {
            row["source_path"]: row for row in csv.DictReader(stream, delimiter="\t")
        }
    row = rows[SOURCE_PATH]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "1334"
    assert row["top_level_python_symbols"] == (
        "DEFAULT_OBSERVATORY_DIR;DEFAULT_SERVER_HOST;DEFAULT_SERVER_PORT;"
        "DEFAULT_SSE_POLL_SECONDS;DEFAULT_HEARTBEAT_INTERVAL_SECONDS;"
        "STALE_HEARTBEAT_FACTOR;INGESTION_MAX_TICKS;INGESTION_MAX_SENSORY_PARTS;"
        "INGESTION_MAX_COGNITIVE_REGIONS;INGESTION_MAX_BODY_PARTS;"
        "INGESTION_MAX_BODY_DEPENDENCIES"
    )
    assert row["disposition"] == "DROP"
    assert "No TARGET owner" in row["target_owner"]
    assert "No TARGET observability server" in row["target_path_or_status"]
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "lab/src/lab/observatory/server.py" in rationale
    assert "lab/src/lab/observatory/adapter.py" in rationale
    assert "Lab #250" in rationale
    assert "not as a claim that future presentation or transport is unnecessary" in rationale
    assert "No scientific validity/equivalence/admission claim" in rationale

    counts = Counter(item["disposition"] for item in rows.values())
    assert counts == {"MOVE": 8, "SPLIT": 46, "REWRITE": 3, "DROP": 947, "DEFER": 168}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical Observatory operational configuration (Lab #253)" in migration
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 46 |" in migration
    assert "`DROP` | 947 |" in migration
    assert "`DEFER` | 168 |" in migration
