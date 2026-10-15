"""Keep the historical evolution-lineage disposition evidence-backed."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/evolution/lineage.py"
SOURCE_BLOB = "0a9566b08ad245706162c1f8c3b67f2a8132921e"


def test_historical_evolution_lineage_is_dropped_without_target_or_science_claim() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "4114"
    assert row["top_level_python_symbols"] == "LineageRecord;GenomeLineageRecord;LineageArchive"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner established"
    assert row["target_path_or_status"] == "No TARGET code destination"
    for evidence in (SOURCE_COMMIT, SOURCE_BLOB, "no TARGET consumer", "source tests are not migrated"):
        assert evidence in row["rationale_and_caveat"]
    for prohibited_claim in ("scientific validity", "evidence admission", "method-equivalence"):
        assert prohibited_claim in row["rationale_and_caveat"]
    assert not (ROOT / "src/lab/evolution/lineage.py").exists()

    counts = Counter(row["disposition"] for row in rows)
    assert counts == {
        "MOVE": 6,
        "SPLIT": 84,
        "REWRITE": 2,
        "DROP": 920,
        "DEFER": 160,
    }

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 84 |" in migration
    assert "`DROP` | 920 |" in migration
    assert "Historical evolution lineage implementation" in migration
