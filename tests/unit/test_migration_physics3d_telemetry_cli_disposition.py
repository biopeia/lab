from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = "lab/src/lab/physics3d/telemetry/cli.py"


def test_physics3d_telemetry_cli_is_dropped_without_disposing_underlying_tools() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    row = next(item for item in rows if item["source_path"] == SOURCE)

    assert row["source_blob_at_pinned_commit"] == "7fdeaa4b535902afabe13160d52cb2964ddfdf3c"
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "1602"
    assert row["top_level_python_symbols"] == "benchmark_main"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET CLI owner"
    assert "No target CLI consumer" in row["target_path_or_status"]
    assert "not its pinned source" in row["rationale_and_caveat"]
    assert "#314/#315" in row["rationale_and_caveat"]


def test_physics3d_telemetry_cli_disposition_is_documented_and_counted() -> None:
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "Historical Physics3D telemetry CLI disposition (Lab #307)" in migration
    assert "No CLI or gate was run" in migration
    assert "| `SPLIT` | 15 |" in migration
    assert "| `DEFER` | 196 |" in migration
    assert "| `DROP` | 950 |" in migration

