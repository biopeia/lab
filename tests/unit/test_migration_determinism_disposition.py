"""Keep the historical private-model determinism disposition explicit."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/modeling/determinism.py"
SOURCE_BLOB = "e3b281b7f51a8a9216a478e754d2999a460038ce"


def test_historical_training_determinism_is_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "1676"
    assert row["top_level_python_symbols"] == (
        "TrainingDeterminism;configure_training_determinism"
    )
    assert row["disposition"] == "DROP"
    assert row["target_owner"].startswith("Lab historical PyTorch private-model")
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "no study/equivalence execution occurred" in rationale
    assert "No scientific validity" in rationale
    assert not (ROOT / "src/lab/modeling/determinism.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 57, "REWRITE": 3, "DROP": 938, "DEFER": 166}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 57 |" in migration
    assert "`DROP` | 938 |" in migration
    assert "### Historical private-model determinism setup (Lab #219)" in migration
