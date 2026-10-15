"""Keep the historical private-model outcome-metric disposition explicit."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/modeling/outcome_metrics.py"
SOURCE_BLOB = "6540b1d7ac18e3220ba5580184cfeacc259c9e4d"

def test_historical_outcome_metrics_are_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "2300"
    assert row["top_level_python_symbols"] == "_torch;evaluate_outcome_model"
    assert row["disposition"] == "DROP"
    assert row["target_owner"].startswith("Lab historical private-model outcome")
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "No study or candidate evaluation was run" in rationale
    assert "No scientific-validity, outcome validity" in rationale
    assert not (ROOT / "src/lab/modeling/outcome_metrics.py").exists()
    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 44, "REWRITE": 3, "DROP": 948, "DEFER": 169}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 44 |" in migration
    assert "`DROP` | 948 |" in migration
    assert "### Historical private-model outcome metrics (Lab #223)" in migration
