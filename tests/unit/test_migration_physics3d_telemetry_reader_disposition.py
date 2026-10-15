"""Keep the historical telemetry reader disposition bounded and traceable."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/physics3d/telemetry/reader.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "c9dbc43f6d7b4670d866b62fcde893073d6dd9a0"
SHA256 = "e429820a08f8ed02e173248182ed32c145d4b9fff61bd708cf7eb3195b0c30b2"
def test_legacy_reader_is_deferred_for_schema_custody_and_selection_contract() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    row = {r["source_path"]: r for r in rows}[SOURCE]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644" and row["bytes"] == "2406"
    assert row["top_level_python_symbols"].split(";") == [
        "TelemetryReaderProtocol", "_manifest_version", "detect_telemetry_run", "open_telemetry"
    ]
    assert row["disposition"] == "DEFER"
    assert "Lab" in row["target_owner"] and "producer-domain owners" in row["target_owner"]
    assert "No approved TARGET telemetry reader/schema contract" in row["target_path_or_status"]
    for evidence in (COMMIT, SHA256, "#312", "#313", "#314", "#315", "#305", "custody"):
        assert evidence in row["rationale_and_caveat"]
    assert Counter(r["disposition"] for r in rows) == {
        "MOVE": 8, "SPLIT": 16, "REWRITE": 3, "DROP": 950, "DEFER": 195
    }
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert BLOB in migration and SHA256 in migration
    assert "### Historical Physics3D telemetry reader disposition (Lab #311)" in migration
