"""Keep the historical Development history reader disposition bounded."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_PATH = "lab/src/lab/observation/development_history.py"
SOURCE_BLOB = "36e96d6d772b16faf1224efea6994018f7f83e1a"
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"


def test_historical_development_history_reader_is_dropped_only() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "14260"
    assert row["top_level_python_symbols"] == (
        "_read_json;_telemetry_manifest_candidates;_number;_nodes;_edges;"
        "_body_schema_counts;_point;_history_snapshot;_snapshot_fingerprint;"
        "_managed_runs;build_development_history"
    )
    assert row["disposition"] == "DROP"
    assert "Frontend v0.1 explicitly excludes history and persistence" in row["target_path_or_status"]
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "does not delete or disposition underlying scientific telemetry/evidence artifacts" in row["rationale_and_caveat"]
    assert "No scientific result" in row["rationale_and_caveat"]

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 65, "REWRITE": 3, "DROP": 933, "DEFER": 163}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "### Historical Development history read model disposition (Lab #235)" in migration
    assert "`DROP` | 933 |" in migration
    assert "Frontend v0.1 explicitly excludes history/persistence" in migration
