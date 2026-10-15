"""Keep the legacy v4.1 telemetry contract disposition auditable."""
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/physics3d/telemetry/v41.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "4dc2d12f30448d58071799bc8f4b2ad90727bbe0"
SHA256 = "dc957b1d2564b8cf44cfdc4efa44272607c841b79cd648a2d9a194bfb424f73d"


def test_legacy_v41_contract_is_deferred_pending_schema_custody_and_consumer() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    row = {r["source_path"]: r for r in rows}[SOURCE]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644" and row["bytes"] == "50819"
    assert row["top_level_python_symbols"].split(";") == [
        "SCHEMA_VERSION", "ENVELOPE_TYPE", "ZERO_HASH", "_utc_now", "_record_mapping",
        "_write_json", "_append_line", "_stream_offsets", "_exact_equal",
        "_stream_record_hash", "TelemetryV41Writer", "AsyncTelemetryV41Writer",
        "TelemetryV41Reader", "load_v41_tick_records", "load_v41_transitions",
        "_verify_checkpoint_file", "_verify_checkpoint_reference", "verify_v41_run",
    ]
    assert row["disposition"] == "DEFER"
    assert "No approved TARGET v4.1 telemetry schema/wire contract" in row["target_path_or_status"]
    for token in (COMMIT, SHA256, "#309", "#314", "custody", "checkpoint", "scientific"):
        assert token in row["rationale_and_caveat"]
    assert Counter(r["disposition"] for r in rows) == {
        "MOVE": 8, "SPLIT": 13, "REWRITE": 3, "DROP": 950, "DEFER": 198
    }
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert BLOB in migration and SHA256 in migration
    assert "Historical Physics3D telemetry v4.1 writer and verifier disposition (Lab #315)" in migration
