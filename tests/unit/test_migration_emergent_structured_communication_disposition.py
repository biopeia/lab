from __future__ import annotations
import csv
from collections import Counter
from pathlib import Path
ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
PROTOCOL_BLOB = "a4221271d51ec895b8ba1222204597d5e2935c7d"
RESULT_BLOB = "6c0c60a67a94c0f8e1ca82ee4a84d6b270083aba"

def test_emergent_structured_communication_has_bounded_manifest_disposition() -> None:
    with (ROOT / "migration/study-disposition-register-80d372a.tsv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["unit_id"] == "learning.emergent-structured-communication"]
    assert len(matches) == 1
    row = matches[0]
    assert row["study_protocol_disposition"] == "DEFER"
    assert row["source_commit"] == SOURCE_COMMIT
    assert PROTOCOL_BLOB in row["protocol_paths_and_blobs"]
    assert RESULT_BLOB in row["experiment_artifacts_and_digests"]
    assert row["real_run_identity"].startswith("NOT_IDENTIFIED")
    assert "all_gates_pass" in row["source_evidence_basis"]
    assert "esc6_productive_generalization" in row["source_evidence_basis"]
    assert "not admitted" in row["limitations_and_nonclaims"]
    assert "biopeia/lab#153" in row["owner_basis"]
    assert Counter(item["study_protocol_disposition"] for item in rows) == {
        "DEFER": 68, "HISTORICAL_PROTOCOL": 15, "REIMPLEMENT_METHOD": 1
    }
    with (ROOT / "migration/study-protocol-crosswalk-80d372a.tsv").open(encoding="utf-8", newline="") as stream:
        crosswalk = list(csv.DictReader(stream, delimiter="\t"))
    unit = [item for item in crosswalk if item["protocol_id"] == "learning.emergent-structured-communication"]
    assert len(unit) == 1
    assert unit[0]["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#153" in unit[0]["basis"]
    assert "no run_id" in unit[0]["basis"]
    doc = (ROOT / "migration/study-protocol-crosswalk-80d372a.md").read_text(encoding="utf-8")
    assert "84 manifest-level decisions" in doc
    assert "For #153" in doc
