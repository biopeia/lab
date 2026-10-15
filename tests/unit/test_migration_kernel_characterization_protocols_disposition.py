"""Keep the historical kernel-characterization protocol disposition explicit."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/kernel_characterization/protocols.py"
SOURCE_BLOB = "1d056c3cb86d36c0b9e36fcee507fb9da3671992"


def test_historical_kernel_protocol_data_is_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "727"
    assert row["top_level_python_symbols"] == "DEFAULT_SEEDS;Phase;K1_PHASES;phases"
    assert row["disposition"] == "DROP"
    assert row["target_owner"].startswith("Lab historical kernel-characterization")
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "not a scientific-validity" in rationale
    assert "remain preserved" in rationale
    assert not (ROOT / "src/lab/kernel_characterization/protocols.py").exists()

    counts = Counter(row["disposition"] for row in rows)
    assert counts == {"MOVE": 8, "SPLIT": 13, "REWRITE": 3, "DROP": 950, "DEFER": 198}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 13 |" in migration
    assert "`DROP` | 950 |" in migration
    assert "### Historical kernel-characterization protocol data (Lab #212)" in migration
