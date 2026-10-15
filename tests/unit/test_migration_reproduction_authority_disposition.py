"""Keep the historical population and lineage authority out of TARGET."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/reproduction/authority.py"
SOURCE_BLOB = "090a4ea9da61f6e36ddf504b931ed1609a73e388"


def test_historical_population_authority_is_dropped_not_reassigned() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))

    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "8155"
    assert row["top_level_python_symbols"] == "BirthRecord;DeathRecord;HabitatBirthAuthority"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET code destination"
    assert row["target_path_or_status"] == "No TARGET implementation retained"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "Organism #49" in row["rationale_and_caveat"]
    assert "World `src/world/durable_runtime.py`" in row["rationale_and_caveat"]
    assert "not equivalent" in row["rationale_and_caveat"]
    assert "does not claim reproduction" in row["rationale_and_caveat"]

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 72, "REWRITE": 3, "DROP": 928, "DEFER": 161}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical habitat population and lineage authority disposition (Lab #317)" in migration
    assert SOURCE_BLOB in migration
    assert "World presence lifecycle is not a biological birth/death authority" in migration
    assert "`SPLIT` | 72 |" in migration
    assert "`DROP` | 928 |" in migration
