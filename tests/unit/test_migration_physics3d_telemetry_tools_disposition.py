"""Keep the historical telemetry analysis and gate policy disposition auditable."""
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/physics3d/telemetry/tools.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "49a5361e6071b568a05532ad294a65fb51316878"
SHA256 = "7449a5a7c66a081ce91044da94fa77448a41b8c8121c7e459a08ffad1342e503"


def test_telemetry_analysis_tools_are_deferred_pending_contract_and_gate_authority() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    row = {r["source_path"]: r for r in rows}[SOURCE]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644" and row["bytes"] == "7282"
    assert row["top_level_python_symbols"].split(";") == [
        "_read_manifest", "_tree_bytes", "_first_existing", "_v41_breakdown",
        "benchmark_run", "evaluate_acceptance_gates", "compare_runs",
    ]
    assert row["disposition"] == "DEFER"
    assert "No approved TARGET telemetry analysis contract" in row["target_path_or_status"]
    for evidence in (COMMIT, SHA256, "#309", "#313", "#315", "custody", "scientific"):
        assert evidence in row["rationale_and_caveat"]
    assert Counter(r["disposition"] for r in rows) == {
        "MOVE": 8, "SPLIT": 14, "REWRITE": 3, "DROP": 950, "DEFER": 197
    }
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert BLOB in migration and SHA256 in migration
    assert "Historical Physics3D telemetry tools disposition (Lab #314)" in migration
