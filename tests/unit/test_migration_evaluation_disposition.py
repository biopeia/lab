"""Keep the historical private-model evaluation disposition explicit."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/modeling/evaluation.py"
SOURCE_BLOB = "8860f21a4e9b76f324f60b07237229b646a64087"


def test_historical_candidate_evaluation_is_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "5285"
    assert row["top_level_python_symbols"] == (
        "CandidateEvaluation;PromotionPolicy;PromotionDecision;evaluate_candidate"
    )
    assert row["disposition"] == "DROP"
    assert row["target_owner"].startswith("Lab historical private-model held-out")
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "threshold values are not scientific policy" in rationale
    assert "No candidate was evaluated or promoted" in rationale
    assert not (ROOT / "src/lab/modeling/evaluation.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 45, "REWRITE": 3, "DROP": 947, "DEFER": 169}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 45 |" in migration
    assert "`DROP` | 947 |" in migration
    assert "### Historical private-model evaluation and promotion (Lab #220)" in migration
