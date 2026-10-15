"""Track the absence of an authorized target private-model training contract."""

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/physics3d/private_model_training.py"
SOURCE_BLOB = "46a90fb74edc7fad2055686cfb03a5d6be4e343e"
SYMBOLS = "TrainingResultPayload;_PrivateModelRuntime;_tokenizer_path;_target_losses;_paired_reference_evaluation;_train_job;PrivateModelTrainingService"

def test_private_model_training_service_is_deferred_without_target_contract() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644" and row["bytes"] == "29865"
    assert row["top_level_python_symbols"] == SYMBOLS
    assert row["disposition"] == "DEFER"
    assert "No TARGET private-model TrainingRequest/corpus/registry/bridge/training-service contract" in row["target_path_or_status"]
    for evidence in (SOURCE_COMMIT, "do not establish a Biopeia target contract", "Closure trigger", "Lab must define custody/admissibility", "no learning efficacy"):
        assert evidence in row["rationale_and_caveat"]
    counts = Counter(entry["disposition"] for entry in rows)
    assert counts == {"MOVE": 8, "SPLIT": 13, "REWRITE": 3, "DROP": 950, "DEFER": 198}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical Physics3D private-model training service disposition (Lab #302)" in migration
    assert SOURCE_BLOB in migration
