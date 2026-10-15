"""Keep the historical private-model architecture disposition explicit."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/modeling/architectures.py"
SOURCE_BLOB = "e35ff6df4dd2ef8649ca2d365c9d1947cc1a2aa2"


def test_historical_model_architectures_are_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "9882"
    assert row["top_level_python_symbols"] == (
        "ArchitectureSpec;ArchitectureCapacityError;architecture_spec;"
        "_gru_parameter_count;resolve_architecture_spec;architecture_spec_from_manifest;"
        "_torch;build_model;count_parameters"
    )
    assert row["disposition"] == "DROP"
    assert row["target_owner"].startswith("Lab historical private-model")
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "No training or evaluation was run" in rationale
    assert "not a scientific-validity" in rationale
    assert not (ROOT / "src/lab/modeling/architectures.py").exists()

    counts = Counter(row["disposition"] for row in rows)
    assert counts == {"MOVE": 8, "SPLIT": 37, "REWRITE": 3, "DROP": 948, "DEFER": 176}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 37 |" in migration
    assert "`DROP` | 948 |" in migration
    assert "### Historical private-model architectures (Lab #214)" in migration
