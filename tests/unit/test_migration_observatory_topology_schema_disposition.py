"""Keep the legacy cognition-topology wire schema behind owner authorization."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).parents[2]
PATH = "lab/src/lab/observatory/schemas/topology.schema.json"
BLOB = "6525f49ddf3271b0ff6f8fde7fe516da791f9059"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"

def test_historical_topology_schema_has_bounded_defer() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644" and row["bytes"] == "1669"
    assert row["disposition"] == "DEFER"
    assert "no TARGET cognition-topology projection/checkpoint schema authorized" in row["target_path_or_status"]
    rationale = row["rationale_and_caveat"]
    assert COMMIT in rationale and "4c735bd03d4a0f46306441a68ff4e0abcdbdbf86da50fdfd08d4005e56254441" in rationale
    assert "Organism #169" in rationale and "Organism #45" in rationale and "Observation #38" in rationale
    assert "private cognitive-structure fields" in rationale
    assert "does not block the bounded Lab runtime migration" in rationale
    counts = Counter(row["disposition"] for row in rows)
    assert counts == {"MOVE": 8, "SPLIT": 20, "REWRITE": 3, "DROP": 950, "DEFER": 191}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical Observatory topology schema (Lab #270)" in migration
    assert "| `SPLIT` | 20 |" in migration and "| `DEFER` | 191 |" in migration
