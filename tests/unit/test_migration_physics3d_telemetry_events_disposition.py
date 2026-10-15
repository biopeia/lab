"""Keep the historical event-stream codec disposition bounded and traceable."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/physics3d/telemetry/events.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "492c9c89f424d9efe6260624fdc4a77577cd67bb"
SHA256 = "23787065c17982ae21452e2b9058668c349a7c8fd41e291531c7c6f16adc53c7"

def test_event_stream_codec_is_deferred_for_target_contract_and_custody() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    by_path = {row["source_path"]: row for row in rows}
    row = by_path[SOURCE]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644" and row["bytes"] == "7369"
    assert row["top_level_python_symbols"].split(";") == [
        "_exact_equal", "_is_prefix", "EventStreamWriter", "EventStreamReader", "iter_event_records"
    ]
    assert row["disposition"] == "DEFER"
    assert "Lab" in row["target_owner"] and "producer-domain owners" in row["target_owner"]
    assert "No approved TARGET event-stream wire/storage contract" in row["target_path_or_status"]
    for evidence in (COMMIT, SHA256, "#311", "#312", "#313", "custody", "temporal"):
        assert evidence in row["rationale_and_caveat"]
    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 14, "REWRITE": 3, "DROP": 950, "DEFER": 197}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert BLOB in migration and SHA256 in migration
    assert "### Historical Physics3D event-stream codec disposition (Lab #309)" in migration
    assert "Disposition is bounded `DEFER`" in migration
