"""Keep the historical telemetry layout disposition bounded and traceable."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/physics3d/telemetry/schema.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "a683b08f6a7e859cd015be90fb9b1ac688d398ee"
SHA256 = "b18b29e807517d702395985899030abb2f529da81422b3125279260575eed2cc"
def test_legacy_layout_is_deferred_for_authority_custody_and_consumer_contract() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    row = {r["source_path"]: r for r in rows}[SOURCE]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644" and row["bytes"] == "9250"
    assert row["top_level_python_symbols"].split(";") == [
        "TemporalClass", "LayoutRule", "EVENT_RULES", "STATIC_RULES", "STRUCTURAL_RULES",
        "DENSE_RULES", "ALL_RULES", "get_path", "pop_path", "set_path", "PartitionedState",
        "partition_state", "rule_for_channel", "reassemble_state", "event_mode",
    ]
    assert row["disposition"] == "DEFER"
    assert "Lab" in row["target_owner"] and "producer-domain owners" in row["target_owner"]
    assert "No approved TARGET telemetry schema" in row["target_path_or_status"]
    for evidence in (COMMIT, SHA256, "#309", "#310", "#311", "#313", "#314", "#315", "fallback"):
        assert evidence in row["rationale_and_caveat"]
    assert Counter(r["disposition"] for r in rows) == {
        "MOVE": 8, "SPLIT": 14, "REWRITE": 3, "DROP": 950, "DEFER": 197
    }
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert BLOB in migration and SHA256 in migration
    assert "### Historical Physics3D telemetry layout schema disposition (Lab #312)" in migration
