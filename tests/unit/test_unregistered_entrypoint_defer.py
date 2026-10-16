"""Keep unregistered study entrypoint candidates individually bounded in the migration ledger."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).parents[2]
MIGRATION = ROOT / "migration"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (MIGRATION / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def test_unregistered_entrypoint_rows_have_source_pinned_bounded_defers() -> None:
    source_rows = read_tsv("source-inventory-80d372a.tsv")
    evidence_rows = read_tsv("study-evidence-map-80d372a.tsv")
    source_by_path = {row["source_path"]: row for row in source_rows}
    candidates = [
        row
        for row in evidence_rows
        if row["record_kind"] == "UNREGISTERED_ENTRYPOINT_CANDIDATE"
    ]
    assert len(candidates) == 49

    for candidate in candidates:
        row = source_by_path[candidate["implementation_path"]]
        assert row["source_blob_at_pinned_commit"] == candidate["implementation_blob"]
        assert row["disposition"] == "DEFER"
        assert row["target_owner"] == "Lab"
        assert row["target_path_or_status"] == (
            "No TARGET path authorized; bounded DEFER tracked in biopeia/lab#45"
        )
        rationale = row["rationale_and_caveat"]
        assert candidate["record_key"] in rationale
        assert candidate["implementation_symbol"] in rationale
        assert candidate["test_link_status"] in rationale
        assert candidate["protocol_or_run_identity_status"] in rationale
        assert "per-file role/protocol assessment" in rationale
        assert "final code-migration disposition" in rationale
        assert "biopeia/lab#45" in rationale
        assert "No TARGET code/result path is authorized" in rationale
        assert "scientific validity" in rationale
