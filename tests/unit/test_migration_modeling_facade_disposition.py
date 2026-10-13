"""Keep the historical modeling package-facade disposition bounded."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/modeling/__init__.py"
SOURCE_BLOB = "3bf74d0ff1633c094853d49a1d5dcc637cbec7dc"
TARGET_MAIN = "d58ff1fdeb6e4450a72d264fca4251311b2a0bdd"
REEXPORTED_MODULES = {
    "architectures.py",
    "artifacts.py",
    "baselines.py",
    "context_tree.py",
    "dataset.py",
    "evaluation.py",
    "factory.py",
    "gateway.py",
    "reservoir.py",
    "study.py",
    "temporal_evaluation.py",
    "trainer.py",
}


def test_historical_modeling_facade_is_dropped_without_disposing_modules() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    by_path = {row["source_path"]: row for row in rows}

    row = by_path[SOURCE_PATH]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "2367"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Lab historical package facade"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "Drop only this historical package-level import facade" in row[
        "rationale_and_caveat"
    ]
    assert TARGET_MAIN in row["rationale_and_caveat"]
    assert not (ROOT / "src/lab/modeling").exists()

    module_rows = {
        path.rsplit("/", 1)[1]: by_path[path]
        for path in by_path
        if path.startswith("lab/src/lab/modeling/")
        and path != SOURCE_PATH
    }
    assert REEXPORTED_MODULES <= module_rows.keys()
    # The facade disposition must not silently dispose its independently inventoried modules.
    assert all(module_rows[name]["disposition"] == "SPLIT" for name in REEXPORTED_MODULES)

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 6, "SPLIT": 128, "REWRITE": 2, "DROP": 876, "DEFER": 160}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 128 |" in migration
    assert "`DROP` | 876 |" in migration
    assert "### Historical modeling package facade" in migration
