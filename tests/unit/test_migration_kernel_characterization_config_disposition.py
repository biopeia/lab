"""Keep the historical kernel-characterization config out of TARGET."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/kernel_characterization/config.py"
SOURCE_BLOB = "011e47d5527d3cc0844d97b187a047fd533356da"
SYMBOLS = {"BASELINE_KERNEL", "KernelVariant", "complete_kernel"}


def test_historical_kernel_config_is_dropped_as_one_lab_responsibility() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))

    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["bytes"] == "4182"
    assert set(row["top_level_python_symbols"].split(";")) == SYMBOLS
    assert row["disposition"] == "DROP"
    assert "Organism owns KernelLimits" in row["target_owner"]
    assert "src/organism/cognition/limits.py" in row["target_path_or_status"]
    for evidence in (
        SOURCE_COMMIT,
        "13720935595fedabec2c376dc933629b0deae5aa",
        SOURCE_BLOB,
        "no kernel_characterization package or tracked consumer",
        "not SPLIT",
        "no scientific-validity",
    ):
        assert evidence in row["rationale_and_caveat"]

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 61, "REWRITE": 3, "DROP": 935, "DEFER": 165}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical kernel-characterization config disposition (Lab #209)" in migration
    assert SOURCE_BLOB in migration
    assert "**Disposition: DROP the entire historical config module as TARGET code, not" in migration
    assert "`SPLIT` | 61 |" in migration
    assert "`DROP` | 935 |" in migration
