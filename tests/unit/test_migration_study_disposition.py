"""Keep the historical modeling study orchestration disposition explicit."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/modeling/study.py"
SOURCE_BLOB = "203a1aace30839a5490db32fce9b15be7cfc9f91"

def test_historical_modeling_study_orchestration_is_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "10043"
    assert row["top_level_python_symbols"] == "ModelFamilyResult;PrivateModelStudyResult;CrossIndividualResult;RegimeShiftResult;_request;run_model_family_study;cross_evaluate_individual_models;remap_encoded_corpus;evaluate_regime_shift"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Lab historical private-model and temporal study orchestration"
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "No study/evaluation was executed" in rationale
    assert "No scientific validity, efficacy, interpretation" in rationale
    assert not (ROOT / "src/lab/modeling/study.py").exists()
    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 13, "REWRITE": 3, "DROP": 950, "DEFER": 198}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 13 |" in migration
    assert "`DROP` | 950 |" in migration
    assert "### Historical private-model and temporal study orchestration (Lab #225)" in migration
