"""Keep the historical Observatory HTML out of the Biopeia TARGET."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/observatory/world.html"
SOURCE_BLOB = "725250dd6c5fbc1b657be88ddb0ccd0397edb31c"
SOURCE_SHA256 = "d321d005540f0169edc9a3ee8301df52d19dfdf258ddd3bc250d17766fd8f70a"


def test_historical_observatory_world_html_is_dropped_as_target_implementation() -> None:
    inventory_path = ROOT / "migration/source-inventory-80d372a.tsv"
    with inventory_path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))

    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "66976"
    assert row["top_level_python_symbols"] == ""
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Lab historical Observatory UI implementation"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert SOURCE_SHA256 in row["rationale_and_caveat"]
    assert "Future Lab visualization is separately tracked by lab#63" in row[
        "rationale_and_caveat"
    ]
    assert "does not claim visualization is unnecessary" in row["rationale_and_caveat"]

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 24, "REWRITE": 3, "DROP": 949, "DEFER": 188}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert SOURCE_SHA256 in migration
    assert "### Historical Observatory world visualization" in migration
    assert "`SPLIT` | 24 |" in migration
    assert "`DROP` | 949 |" in migration
    assert not (ROOT / "src/lab/observatory/world.html").exists()
