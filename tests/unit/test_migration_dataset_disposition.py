"""Keep the historical private-model dataset encoder disposition explicit."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/modeling/dataset.py"
SOURCE_BLOB = "365fa2e2feec1187616c6616704593ba2d287ecb"


def test_historical_dataset_encoding_is_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "5348"
    assert row["top_level_python_symbols"] == (
        "EncodedSplit;EncodedCorpus;_encode_split;encode_corpus"
    )
    assert row["disposition"] == "DROP"
    assert row["target_owner"].startswith("Lab historical private-model corpus")
    assert row["target_path_or_status"] == "No TARGET code destination"
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "No study was run" in rationale
    assert "No scientific validity, outcome validity" in rationale
    assert not (ROOT / "src/lab/modeling/dataset.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 59, "REWRITE": 3, "DROP": 936, "DEFER": 166}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 59 |" in migration
    assert "`DROP` | 936 |" in migration
    assert "### Historical private-model corpus encoding (Lab #218)" in migration
