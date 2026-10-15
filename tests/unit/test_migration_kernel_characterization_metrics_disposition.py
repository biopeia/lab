"""Keep the historical run-summary helper disposition explicit."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/kernel_characterization/metrics.py"
SOURCE_BLOB = "3a5cd292c22fbfb8f5ec82ef83f267dc585e8e81"


def test_historical_kernel_metrics_helper_is_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "1747"
    assert row["top_level_python_symbols"] == "_numeric;summarize"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Lab historical run-summary helper; no current TARGET consumer"
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "not claim" in rationale
    assert "future Lab analysis needs are unnecessary" in rationale
    assert not (ROOT / "src/lab/kernel_characterization/metrics.py").exists()

    counts = Counter(row["disposition"] for row in rows)
    assert counts == {"MOVE": 8, "SPLIT": 67, "REWRITE": 3, "DROP": 932, "DEFER": 162}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 67 |" in migration
    assert "`DROP` | 932 |" in migration
    assert "### Historical kernel-characterization run-summary helper" in migration
