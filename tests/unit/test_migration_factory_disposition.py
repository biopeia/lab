"""Keep the historical private-model factory disposition explicit."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/modeling/factory.py"
SOURCE_BLOB = "7fce0166b3659fefadbae72e7a83752f6a43d4d7"


def test_historical_private_model_factory_is_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "8645"
    assert row["top_level_python_symbols"] == "FactoryResult;PrivateModelFactory"
    assert row["disposition"] == "DROP"
    assert row["target_owner"].startswith("Lab historical private-model training")
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "current Organism target has no corresponding" in rationale
    assert "No training, evaluation, adoption, or promotion occurred" in rationale
    assert "No scientific validity, autonomy" in rationale
    assert not (ROOT / "src/lab/modeling/factory.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 6, "SPLIT": 88, "REWRITE": 2, "DROP": 916, "DEFER": 160}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 88 |" in migration
    assert "`DROP` | 916 |" in migration
    assert "### Historical private-model factory and adoption orchestration (Lab #221)" in migration
