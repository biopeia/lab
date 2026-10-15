"""Historical Lab affordance-to-Observation adapter is not a target contract."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_PATH = "lab/src/lab/observation/symbiont_affordance.py"
SOURCE_BLOB = "5e37fbd287cb4c72199d00bf2541d5e0b6580025"
SYMBOLS = "SYMBIONT_RUNTIME;ACTION_DOMAIN_SOURCE;_lineage;affordance_observation"


def test_historical_affordance_adapter_is_dropped_from_target_migration() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "3752"
    assert row["top_level_python_symbols"] == SYMBOLS
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner for historical adapter"
    assert row["target_path_or_status"] == "No TARGET adapter path"
    assert "does not establish source API" in row["rationale_and_caveat"]
    assert "No scientific validity" in row["rationale_and_caveat"]

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 63, "REWRITE": 3, "DROP": 934, "DEFER": 164}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "Historical Symbiont affordance adapter disposition (Lab #245)" in migration
