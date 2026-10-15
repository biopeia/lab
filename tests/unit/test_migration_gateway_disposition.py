"""Keep the historical private-model inference gateway disposition explicit."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/modeling/gateway.py"
SOURCE_BLOB = "93e8e65261450c5c56e77bef13d2f66a6c6264fd"


def test_historical_inference_gateway_is_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "4642"
    assert row["top_level_python_symbols"] == (
        "_torch;load_artifact_model;ArtifactInferenceGateway"
    )
    assert row["disposition"] == "DROP"
    assert row["target_owner"].startswith("Lab historical private-model PyTorch")
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "No model was loaded" in rationale
    assert "not endorsed or security-assessed" in rationale
    assert not (ROOT / "src/lab/modeling/gateway.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 6, "SPLIT": 87, "REWRITE": 2, "DROP": 917, "DEFER": 160}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 87 |" in migration
    assert "`DROP` | 917 |" in migration
    assert "### Historical private-model inference gateway (Lab #222)" in migration
