"""Keep the legacy Organism host adapter out of the TARGET migration."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/integration/organism/host_sources.py"
SOURCE_BLOB = "1ed9fb9bdb1325ffe219416ce473eaf2f9a13bf6"


def test_legacy_host_source_adapter_is_dropped_without_target_destination() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))

    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "2868"
    assert row["top_level_python_symbols"] == "HostSource"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner"
    assert row["target_path_or_status"] == "No TARGET implementation path"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "no authorized TARGET consumer" in row["rationale_and_caveat"]
    assert "historical source remains read-only" in row["rationale_and_caveat"]

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 16, "REWRITE": 3, "DROP": 950, "DEFER": 195}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 16 |" in migration
    assert "`DROP` | 950 |" in migration
    assert not (ROOT / "src/lab/integration/organism/host_sources.py").exists()
