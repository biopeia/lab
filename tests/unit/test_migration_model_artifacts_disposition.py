"""Keep the historical model-artifact store disposition explicit."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/modeling/artifacts.py"
SOURCE_BLOB = "0f5330bee027421e7a58dc204c7e66dfee8babb3"


def test_historical_model_artifact_store_is_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "8025"
    assert row["top_level_python_symbols"] == "ModelArtifact;FileArtifactStore"
    assert row["disposition"] == "DROP"
    assert row["target_owner"].startswith("Lab historical private-model artifact")
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "no model files, manifests, source, or evidence are deleted" in rationale
    assert "No training, artifact admission, or evidence review was performed" in rationale
    assert not (ROOT / "src/lab/modeling/artifacts.py").exists()

    counts = Counter(row["disposition"] for row in rows)
    assert counts == {"MOVE": 8, "SPLIT": 51, "REWRITE": 3, "DROP": 942, "DEFER": 168}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 51 |" in migration
    assert "`DROP` | 942 |" in migration
    assert "### Historical private-model artifact/store implementation (Lab #215)" in migration
