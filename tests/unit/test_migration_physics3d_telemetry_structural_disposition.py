"""Keep the historical structural telemetry codec disposition auditable."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/physics3d/telemetry/structural.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "e2ad894ae01cfbe1d5246040c0716cef25f7dd90"
SHA256 = "196075f5cfe6fcc298c9b6e05e799fc7f8b4a4de76998541c61bac1a46c5895f"
def test_structural_codec_is_deferred_for_identity_and_ast_contract() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    row = {r["source_path"]: r for r in rows}[SOURCE]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644" and row["bytes"] == "3995"
    assert row["top_level_python_symbols"].split(";") == [
        "_identity_token", "_key_tokens_for_list", "structural_view", "logical_view"
    ]
    assert row["disposition"] == "DEFER"
    assert "Lab" in row["target_owner"] and "producer-domain owners" in row["target_owner"]
    assert "No approved TARGET structural telemetry AST/schema" in row["target_path_or_status"]
    for evidence in (COMMIT, SHA256, "#309", "#310", "#311", "#312", "#314", "#315", "identity"):
        assert evidence in row["rationale_and_caveat"]
    assert Counter(r["disposition"] for r in rows) == {
        "MOVE": 8, "SPLIT": 13, "REWRITE": 3, "DROP": 950, "DEFER": 198
    }
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert BLOB in migration and SHA256 in migration
    assert "### Historical Physics3D structural telemetry codec disposition (Lab #313)" in migration
