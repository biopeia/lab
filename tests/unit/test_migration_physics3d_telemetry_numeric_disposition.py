"""Keep the historical numeric-frame codec disposition traceable."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/physics3d/telemetry/numeric.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "a43ee4d66749543e32b1f0999b513a08522a65fb"
SHA256 = "bab887e1f75ef52fa9debffbc603ec30d3f27da3bbf5c08b624869a363684069"
def test_numeric_frame_codec_is_deferred_for_contract_and_custody() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    row = {r["source_path"]: r for r in rows}[SOURCE]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644" and row["bytes"] == "11631"
    assert row["top_level_python_symbols"].split(";") == [
        "_template_and_values", "_inflate", "_exact_equal", "FrameSchemaRegistryWriter",
        "FrameStreamWriter", "FrameSchemaRegistryReader", "FrameStreamReader",
    ]
    assert row["disposition"] == "DEFER"
    assert "Lab" in row["target_owner"] and "producer-domain owners" in row["target_owner"]
    assert "No approved TARGET numeric-frame schema/registry" in row["target_path_or_status"]
    for evidence in (COMMIT, SHA256, "#311", "#312", "#313", "custody", "sparse"):
        assert evidence in row["rationale_and_caveat"]
    assert Counter(r["disposition"] for r in rows) == {
        "MOVE": 8, "SPLIT": 14, "REWRITE": 3, "DROP": 950, "DEFER": 197
    }
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert BLOB in migration and SHA256 in migration
    assert "### Historical Physics3D numeric-frame codec disposition (Lab #310)" in migration
