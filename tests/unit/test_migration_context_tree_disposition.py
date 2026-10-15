"""Keep the historical temporal challenger disposition explicit."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/modeling/context_tree.py"
SOURCE_BLOB = "6ee1533579f2d588b6a4422c3bd007a2f45c18ac"


def test_historical_variable_order_challenger_is_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "5859"
    assert row["top_level_python_symbols"] == "DecayedVariableOrderMarkov"
    assert row["disposition"] == "DROP"
    assert row["target_owner"].startswith("Lab historical variable-order Markov")
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "No study was run" in rationale
    assert "no validity, efficacy, method-equivalence" in rationale
    assert not (ROOT / "src/lab/modeling/context_tree.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 61, "REWRITE": 3, "DROP": 935, "DEFER": 165}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 61 |" in migration
    assert "`DROP` | 935 |" in migration
    assert "### Historical variable-order Markov challenger (Lab #217)" in migration
