"""Keep source-file dispositions consistent with owner-approved study units."""

from __future__ import annotations

import csv
from pathlib import Path

MIGRATION = Path(__file__).parents[2] / "migration"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (MIGRATION / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def test_resolved_study_implementations_and_tests_are_dropped() -> None:
    source = {
        row["source_path"]: row
        for row in read_tsv("source-inventory-80d372a.tsv")
    }
    units = read_tsv("study-disposition-register-80d372a.tsv")

    assert len(units) == 7
    by_id = {unit["unit_id"]: unit for unit in units}
    assert len(by_id) == len(units)
    visual_audit = by_id.pop("learning.visual-predictor-audit")
    assert visual_audit["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert visual_audit["source_implementation_TARGET_disposition"] == "DROP"
    implementation_path, expected_blob = visual_audit["implementation_path_and_blob"].split("@", maxsplit=1)
    assert source[implementation_path]["source_blob_at_pinned_commit"] == expected_blob
    assert source[implementation_path]["disposition"] == "DROP"
    new_method = by_id.pop("embodiment.hidden-common-cause")
    assert new_method["study_protocol_disposition"] == "REIMPLEMENT_METHOD"
    assert new_method["source_implementation_TARGET_disposition"] == "DROP"

    label_invariance = by_id.pop("embodiment.label-invariance")
    assert label_invariance["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert label_invariance["source_implementation_TARGET_disposition"] == "DROP"
    assert "biopeia/lab#62" in label_invariance["owner_basis"]
    assert "biopeia/organism#98" in label_invariance["TARGET_action"]
    assert "do not merge, reconcile, or prefer" in label_invariance["limitations_and_nonclaims"]
    for source_ref in (
        label_invariance["implementation_path_and_blob"],
        label_invariance["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
        assert source[path]["disposition"] == "DROP"

    crosswalk = read_tsv("study-protocol-crosswalk-80d372a.tsv")
    label_rows = [
        row for row in crosswalk if row["protocol_id"] == "embodiment.label-invariance"
    ]
    assert len(label_rows) == 1
    assert label_rows[0]["candidate_disposition"] == "HISTORICAL_PROTOCOL"
    assert "biopeia/lab#62" in label_rows[0]["basis"]
    assert "biopeia/organism#98" in label_rows[0]["basis"]

    custody = {
        row["source_path"]: row
        for row in read_tsv("scientific-custody-80d372a.tsv")
    }
    assert custody[
        "lab/experiments/embodiment/label-invariance/README.md"
    ]["custody_classification"] == "PROTOCOL"
    assert custody[
        "lab/experiments/embodiment/label-invariance/experiment.toml"
    ]["custody_classification"] == "PROTOCOL"
    assert custody[
        "lab/experiments/embodiment/label-invariance/results.json"
    ]["custody_classification"] == "SCIENTIFIC_EVIDENCE"
    assert custody[
        "lab/experiments/embodiment/label-invariance-governed-20261001-0a901ea/README.md"
    ]["custody_classification"] == "HISTORICAL_RECORD"
    assert "NOT_ADMITTED" in custody[
        "lab/experiments/embodiment/label-invariance/results.json"
    ]["proposal_review_status"]

    for unit in by_id.values():
        assert unit["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
        assert unit["source_implementation_TARGET_disposition"] == "DROP"
        for source_ref in (
            unit["implementation_path_and_blob"],
            unit["source_test_path_and_blob"],
        ):
            path, expected_blob = source_ref.split("@", maxsplit=1)
            row = source[path]
            assert row["source_blob_at_pinned_commit"] == expected_blob
            assert row["disposition"] == "DROP"
