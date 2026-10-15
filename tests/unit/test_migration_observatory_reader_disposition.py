"""Keep the legacy Observatory filesystem reader out of TARGET."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/observation/observatory.py"
SOURCE_BLOB = "47c42c8ffa09828989342f7b7f95d6382aefe66c"
SYMBOLS = (
    "observatory_package_root;valid_instance_id;_read_json_object;_registry_api;"
    "parse_journal_line;read_journal;ObservatorySource"
)


def test_legacy_observatory_reader_is_dropped_with_pinned_provenance() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "7710"
    assert row["top_level_python_symbols"] == SYMBOLS
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert "Observation #38" in row["rationale_and_caveat"]
    assert "historical source read-only" in row["rationale_and_caveat"]
    assert not (ROOT / "src/lab/observation/observatory.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 13, "REWRITE": 3, "DROP": 950, "DEFER": 198}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "Historical Observatory read adapter disposition (Lab #238)" in migration
    assert "`DROP` | 950 |" in migration
