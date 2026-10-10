"""Keep source-file dispositions consistent with owner-approved study units."""

from __future__ import annotations

import csv
from pathlib import Path

MIGRATION = Path(__file__).parents[2] / "migration"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (MIGRATION / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def test_recurrent_restoration_source_implementation_is_dropped() -> None:
    source = {
        row["source_path"]: row
        for row in read_tsv("source-inventory-80d372a.tsv")
    }
    unit = {
        row["unit_id"]: row
        for row in read_tsv("study-disposition-register-80d372a.tsv")
    }["continuity.recurrent-restoration"]
    row = source["lab/src/lab/studies/continuity/recurrent_restoration.py"]

    assert row["source_blob_at_pinned_commit"] == (
        "41dba8d3b2c5dae41ba83bc83ecf8858840e969b"
    )
    assert unit["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert unit["source_implementation_TARGET_disposition"] == "DROP"
    assert row["disposition"] == unit["source_implementation_TARGET_disposition"]
    assert "scientific validation" in row["rationale_and_caveat"]
