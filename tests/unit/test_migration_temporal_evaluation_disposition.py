"""Keep the historical temporal challenger evaluation disposition explicit."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/modeling/temporal_evaluation.py"
SOURCE_BLOB = "40cee786463b5161ba397686eebb357833b31137"

def test_historical_temporal_evaluation_is_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "3433"
    assert row["top_level_python_symbols"] == "DiscreteTemporalMetrics;_fit_sequences;evaluate_vomm_challenger"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Lab historical held-out temporal challenger evaluation"
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "No study/evaluation was run" in rationale
    assert "No metric validity, scientific validity" in rationale
    assert not (ROOT / "src/lab/modeling/temporal_evaluation.py").exists()
    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 6, "SPLIT": 77, "REWRITE": 3, "DROP": 926, "DEFER": 160}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 77 |" in migration
    assert "`DROP` | 926 |" in migration
    assert "### Historical temporal challenger evaluation (Lab #226)" in migration
