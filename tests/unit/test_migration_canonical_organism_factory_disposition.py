"""Keep the legacy canonical Organism factory out of TARGET code."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/integration/organism/canonical.py"
SOURCE_BLOB = "9b2e8ee25199a9b1a69cb822c695257d1fbf9b2c"


def test_canonical_organism_factory_is_dropped_as_legacy_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))

    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "5110"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner"
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "legacy Symbiont OrganismRuntime" in rationale
    assert "not a replacement claim for host telemetry" in rationale
    assert "Pinned source remains read-only" in rationale
    assert not (ROOT / "src/lab/integration/organism/canonical.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 6, "SPLIT": 86, "REWRITE": 2, "DROP": 918, "DEFER": 160}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 86 |" in migration
    assert "`DROP` | 918 |" in migration
    assert "### Historical canonical Organism factory and restore adapter" in migration
