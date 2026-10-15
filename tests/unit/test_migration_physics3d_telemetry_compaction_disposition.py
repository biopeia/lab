"""Keep the historical telemetry compaction disposition bounded and auditable."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/physics3d/telemetry/compaction.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "dfe2e3b51c140fc85f51be74da4b257b5ae874e5"
SHA256 = "fc61dbe77c5ec023488e5748a5d436ff14ccaacc84f1aa474debd88a36b04d4b"


def test_compaction_is_deferred_pending_cross_domain_telemetry_contract() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    by_path = {row["source_path"]: row for row in rows}
    row = by_path[SOURCE]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "11044"
    assert row["top_level_python_symbols"].split(";") == [
        "canonical_json_bytes", "payload_sha256", "_escape_pointer_segment",
        "_unescape_pointer_segment", "join_pointer", "split_pointer", "_exact_equal",
        "ObjectStore", "CompactionPolicy", "StateDiffer", "StatePatcher",
    ]
    assert row["disposition"] == "DEFER"
    assert "Lab" in row["target_owner"] and "producer-domain owners" in row["target_owner"]
    assert "No approved TARGET telemetry compaction/reference contract" in row["target_path_or_status"]
    for evidence in (COMMIT, SHA256, "#311", "#312", "#313", "custody", "integrity"):
        assert evidence in row["rationale_and_caveat"]
    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 14, "REWRITE": 3, "DROP": 950, "DEFER": 197}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert BLOB in migration and SHA256 in migration
    assert "### Historical Physics3D telemetry compaction utility disposition (Lab #308)" in migration
    assert "Disposition is bounded `DEFER`, not `SPLIT`" in migration
