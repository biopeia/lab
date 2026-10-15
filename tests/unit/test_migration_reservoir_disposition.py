"""Keep the historical temporal challenger model disposition explicit."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/modeling/reservoir.py"
SOURCE_BLOB = "f901fa48f1744fec08dcef5a40a2eac825174150"

def test_historical_temporal_challenger_is_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "8156"
    assert row["top_level_python_symbols"] == "SparseEchoStateRegressor"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Lab historical continuous temporal challenger model"
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "No study/model run or scientific comparison was conducted" in rationale
    assert "No scientific-validity, learning-efficacy" in rationale
    assert not (ROOT / "src/lab/modeling/reservoir.py").exists()
    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 22, "REWRITE": 3, "DROP": 949, "DEFER": 190}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 22 |" in migration
    assert "`DROP` | 949 |" in migration
    assert "### Historical continuous temporal challenger model (Lab #224)" in migration
