"""Keep the historical private-model trainer disposition explicit."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/modeling/trainer.py"
SOURCE_BLOB = "e4625c42267ab794a5bbc7f952ae0cb97a4d644c"
SYMBOLS = "TrainingConfig;TrainingMetrics;TrainingResult;TrainingProbe;_torch;_batch_tensors;evaluate_model;_serialize_weights;_load_parent_state;_extend_vocabulary_state;_train_private_model;train_private_model;adapt_private_model"

def test_historical_private_model_trainer_is_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "20490"
    assert row["top_level_python_symbols"] == SYMBOLS
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Lab historical private-model training and adaptation apparatus"
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "No training/adaptation was run" in rationale
    assert "No scientific validity, learning efficacy" in rationale
    assert not (ROOT / "src/lab/modeling/trainer.py").exists()
    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 32, "REWRITE": 3, "DROP": 949, "DEFER": 180}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 32 |" in migration
    assert "`DROP` | 949 |" in migration
    assert "### Historical private-model training and adaptation (Lab #227)" in migration
