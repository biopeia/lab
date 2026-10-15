"""Keep the legacy local-host composition out of TARGET code."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_PATH = "lab/src/lab/integration/organism/local_host.py"
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH_COMMIT = "7a63ec3ce140514e085789f498e7c73a72eca3fc"
SOURCE_BLOB = "c5841f9a91c42e4dd2ba702aa79371497f35eab0"
SOURCE_SHA256 = "4eacc161e68fb5b6a82c0d28d64d71984e84d8e63dea942727627a0c79a4ef99"
SYMBOLS = (
    "_discovery;_readings;discover_local_host;sample_local_host;perceive_local_host;"
    "learn_local_host_rhythms;monitor_local_host;acclimate_local_host;"
    "track_local_host_drift;second_look_at_local_host"
)


def test_legacy_local_host_composition_is_dropped_without_target_destination() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))

    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "6386"
    assert row["top_level_python_symbols"] == SYMBOLS
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert SOURCE_PATH_COMMIT in row["rationale_and_caveat"]
    assert SOURCE_SHA256 in row["rationale_and_caveat"]
    assert "no consumer" in row["rationale_and_caveat"]
    assert "Historical source remains read-only" in row["rationale_and_caveat"]

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 6, "SPLIT": 100, "REWRITE": 2, "DROP": 904, "DEFER": 160}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 100 |" in migration
    assert "`DROP` | 904 |" in migration
    assert not (ROOT / "src/lab/integration/organism/local_host.py").exists()
