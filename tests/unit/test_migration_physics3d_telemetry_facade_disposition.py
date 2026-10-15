"""Keep the historical Physics3D telemetry package-facade disposition bounded."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/physics3d/telemetry/__init__.py"
SOURCE_BLOB = "d947446f8caf7b9c0a39bb91b61de8161b587dd7"
SOURCE_SHA256 = "446644aaf51d1fde398269751e78a7d51d8a060a4fd38ae4dd3d41636cdccc58"
TARGET_MAIN = "f3d5283302b4b71222820254fbecfc3f754d9fad"


def test_historical_telemetry_facade_is_dropped_without_disposing_siblings() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    by_path = {row["source_path"]: row for row in rows}

    row = by_path[SOURCE_PATH]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "530"
    assert row["top_level_python_symbols"] == ""
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Lab historical Physics3D telemetry package facade"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert SOURCE_SHA256 in row["rationale_and_caveat"]
    assert TARGET_MAIN in row["rationale_and_caveat"]
    assert "Drop only this historical package facade" in row["rationale_and_caveat"]
    assert "sibling telemetry modules remain separately inventoried" in row[
        "rationale_and_caveat"
    ]
    assert not (ROOT / "src/lab/physics3d/telemetry").exists()

    sibling_rows = {
        path: sibling
        for path, sibling in by_path.items()
        if path.startswith("lab/src/lab/physics3d/telemetry/") and path != SOURCE_PATH
    }
    assert "lab/src/lab/physics3d/telemetry/reader.py" in sibling_rows
    assert "lab/src/lab/physics3d/telemetry/v41.py" in sibling_rows
    assert all(sibling["disposition"] == "SPLIT" for sibling in sibling_rows.values())

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 62, "REWRITE": 3, "DROP": 934, "DEFER": 165}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert TARGET_MAIN in migration
    assert "`SPLIT` | 62 |" in migration
    assert "`DROP` | 934 |" in migration
    assert "### Historical Physics3D telemetry package facade" in migration
