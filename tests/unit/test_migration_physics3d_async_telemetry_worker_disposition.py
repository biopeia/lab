from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = "lab/src/lab/physics3d/telemetry/async_worker.py"


def test_async_telemetry_worker_is_pinned_and_deferred_to_contracts() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    row = next(item for item in rows if item["source_path"] == SOURCE)

    assert row["source_blob_at_pinned_commit"] == "1284969522e713685e7cfac58e165d35f1059627"
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "3223"
    assert row["top_level_python_symbols"] == "AsyncTelemetryWorker"
    assert row["disposition"] == "DEFER"
    assert "#312" in row["target_path_or_status"]
    assert "Lab must decide" in row["rationale_and_caveat"]
    assert "owner-authorized DROP" in row["rationale_and_caveat"]


def test_async_telemetry_worker_records_custody_boundary_and_counts() -> None:
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "Historical Physics3D asynchronous telemetry worker disposition (Lab #305)" in migration
    assert "no durability, evidence-admissibility" in migration
    assert "| `SPLIT` | 22 |" in migration
    assert "| `DEFER` | 190 |" in migration

