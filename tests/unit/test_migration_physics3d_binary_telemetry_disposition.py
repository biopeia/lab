from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
SOURCE = "lab/src/lab/physics3d/telemetry/binary.py"


def test_physics3d_binary_telemetry_codec_is_pinned_and_deferred() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    row = next(item for item in rows if item["source_path"] == SOURCE)

    symbols = row["top_level_python_symbols"].split(";")
    assert row["source_blob_at_pinned_commit"] == "74372cbf18081db4fc96295122c415ca53c5bb03"
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "43726"
    assert len(symbols) == 34
    assert symbols[0] == "encode_uvarint"
    assert symbols[-1] == "BinaryTickBucket"
    assert row["disposition"] == "DEFER"
    assert "Lab #312" in row["target_path_or_status"]
    assert "owner-authorized DROP" in row["rationale_and_caveat"]


def test_physics3d_binary_telemetry_disposition_records_limits_and_counts() -> None:
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "Historical Physics3D binary telemetry codec disposition (Lab #306)" in migration
    assert "no target consumer or accepted binary" in migration
    assert "no compatibility, integrity, durability" in migration
    assert "| `SPLIT` | 19 |" in migration
    assert "| `DEFER` | 192 |" in migration

