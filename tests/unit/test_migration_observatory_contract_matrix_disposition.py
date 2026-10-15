"""Keep the historical Observatory compatibility matrix out of TARGET artifacts."""
from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
PATH = "lab/src/lab/observatory/schemas/CONTRACT_MATRIX.md"
BLOB = "dfaed5b57aa8750b22665200e7badc063aef7179"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"


def test_historical_contract_matrix_has_bounded_drop_disposition() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    matches = [r for r in rows if r["source_path"] == PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["git_mode"] == "100644" and row["bytes"] == "3093"
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner"
    assert row["target_path_or_status"] == "No TARGET compatibility-matrix path"
    rationale = row["rationale_and_caveat"]
    assert COMMIT in rationale and "95ae294d7e636c56ae869b834a67d9fb6904910caf415af3e02ec1a74e206c96" in rationale
    assert "not itself a schema or executable consumer contract" in rationale
    assert "separately inventoried schemas" in rationale
    counts = Counter(r["disposition"] for r in rows)
    assert counts == {"MOVE": 8, "SPLIT": 16, "REWRITE": 3, "DROP": 950, "DEFER": 195}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical Observatory compatibility matrix (Lab #263)" in migration
    assert BLOB in migration
