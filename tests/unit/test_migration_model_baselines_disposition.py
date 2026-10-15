"""Keep the historical private-model baseline disposition explicit."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/modeling/baselines.py"
SOURCE_BLOB = "03d2e76bac1d507056861aa93ce55a50cfef569e"


def test_historical_private_model_baselines_are_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "3193"
    assert row["top_level_python_symbols"] == (
        "BaselineMetrics;_outcome_transitions;evaluate_uniform_baseline;"
        "evaluate_persistence_baseline;evaluate_frequency_baseline"
    )
    assert row["disposition"] == "DROP"
    assert row["target_owner"].startswith("Lab historical private-model baseline")
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "does not validate, reject, or replace" in rationale
    assert "No study was run" in rationale
    assert not (ROOT / "src/lab/modeling/baselines.py").exists()

    counts = Counter(row["disposition"] for row in rows)
    assert counts == {"MOVE": 6, "SPLIT": 80, "REWRITE": 3, "DROP": 923, "DEFER": 160}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 80 |" in migration
    assert "`DROP` | 923 |" in migration
    assert "### Historical private-model baseline metrics (Lab #216)" in migration
