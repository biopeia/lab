"""Guard source-pinned Lab custody owner dispositions and provenance boundaries."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

MIGRATION = Path(__file__).parents[2] / "migration"
PIN = "80d372a186513035f85a769db886e505cabba52d"
MAPS = (
    "custody-review-embodiment-kernel-80d372a.tsv",
    "custody-review-experiment-root-readme-80d372a.tsv",
    "custody-review-other-experiments-80d372a.tsv",
    "custody-review-learning-perception-80d372a.tsv",
    "custody-review-research-80d372a.tsv",
    "custody-review-replay-80d372a.tsv",
)
IDENTITY_FIELDS = ("source_commit", "source_blob", "bytes", "content_sha256")
RECONCILED_FIELDS = (
    "artifact_version_or_identity",
    "protocol_or_run_linkage",
    "producer_or_source",
    "seed_and_configuration",
)
ACCEPTED = (
    "LAB_OWNER_ACCEPTED_CUSTODY_CLASSIFICATION; "
    "NOT_SCIENTIFICALLY_VALIDATED; NOT_ADMITTED"
)
EXCEPTION = "LAB_OWNER_DISPOSITION_PENDING; EXCEPTION_DOCUMENTED; NOT_ADMITTED"
EMBODIMENT_RESULT_PREFIX = "lab/experiments/embodiment/"

def owner_reclassified_result(path: str) -> bool:
    return path.startswith(EMBODIMENT_RESULT_PREFIX) and path.endswith("/results.json")


def read_tsv(name: str) -> list[dict[str, str]]:
    with (MIGRATION / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def proposed_class(row: dict[str, str]) -> str:
    return row.get("proposed_review_class") or row.get("custody_classification", "")


def accepted_rationale(proposal: dict[str, str]) -> str:
    rationale = proposal["known_limitations_and_rationale"]
    replacements = (
        (
            "Canonical ledger remains DEFER pending review and reconciliation.",
            "Lab owner accepted this custody classification; it does not establish scientific validation, evidence admission, or migration authorization.",
        ),
        (
            "At proposal time, the canonical ledger was DEFER pending review and reconciliation.",
            "Lab owner accepted this custody classification; it does not establish scientific validation, evidence admission, or migration authorization.",
        ),
        (
            "At proposal time, the canonical custody ledger was DEFER pending independent review.",
            "Lab owner accepted this custody classification; it does not establish scientific validation, evidence admission, or migration authorization.",
        ),
        (
            "Canonical custody ledger remains DEFER pending independent review.",
            "Lab owner accepted this custody classification; it does not establish scientific validation, evidence admission, or migration authorization.",
        ),
        (
            "The canonical custody ledger remains DEFER pending independent review.",
            "Lab owner accepted this custody classification; it does not establish scientific validation, evidence admission, or migration authorization.",
        ),
        (
            "Canonical custody ledger remains DEFER.",
            "Lab owner accepted this custody classification; it does not establish scientific validation, evidence admission, or migration authorization.",
        ),
        (
            "Do not infer unique run provenance or admit as scientific evidence until the missing source/run provenance is resolved.",
            "Do not infer unique run provenance. The Lab owner accepted SCIENTIFIC_EVIDENCE as a custody classification only; these results remain NOT_ADMITTED and NOT_SCIENTIFICALLY_VALIDATED. No run ID or producer is inferred.",
        ),
        (
            "Proposed evidence class only; result payload lacks run_id, software revision and runtime producer metadata, so it is not admitted or scientifically validated here.",
            "SCIENTIFIC_EVIDENCE custody classification only; the result payload lacks run_id, software revision, and runtime producer metadata, so it remains NOT_ADMITTED and NOT_SCIENTIFICALLY_VALIDATED.",
        ),
        (
            "proposed as historical protocol only",
            "classified as PROTOCOL for custody only",
        ),
        (
            "The exact README bytes define generic directory organization and execution boundaries; they contain no study-specific hypothesis, conditions, seeds, method, or execution record. WORKING_ARTIFACT is custody classification only, not deletion or migration authorization.",
            "Generic directory-scope README: organization, file placement, execution boundary, and generic limitation only. The adjacent experiment.toml is the study-specific protocol. Lab owner accepts WORKING_ARTIFACT as custody classification only; no scientific validation, evidence admission, migration, or deletion authorization.",
        ),
        (
            "The JSON records a run_id and base software git SHA; dirty=true means the exact executed tree is not reconstructible. scientifically_valid=true and integrity_pass=true are source-reported fields only. Custody class is not validation or admission.",
            "The result records a run_id and base software git SHA, but software.dirty=true and no patch/worktree diff is preserved, so the exact executed source tree is not reconstructible. Its scientifically_valid=true and integrity_pass=true fields are recorded source claims only, not accepted conclusions. Lab owner accepts SCIENTIFIC_EVIDENCE as custody classification only; NOT_ADMITTED and NOT_SCIENTIFICALLY_VALIDATED.",
        ),
        (
            "Proposed WORKING_ARTIFACT is a repository-process classification only, not scientific admission, migration, deletion, or a final owner disposition.",
            "Lab owner accepted WORKING_ARTIFACT as a repository-process custody classification only; this is not scientific admission, migration, or deletion authorization.",
        ),
    )
    for old, new in replacements:
        rationale = rationale.replace(old, new)
    return rationale


def test_all_477_artifacts_have_identity_matched_owner_dispositions() -> None:
    ledger = read_tsv("scientific-custody-80d372a.tsv")
    proposals: dict[str, dict[str, str]] = {}
    for name in MAPS:
        for row in read_tsv(name):
            assert row["source_path"] not in proposals
            proposals[row["source_path"]] = row

    assert len(ledger) == len(proposals) == 477
    assert len({row["source_path"] for row in ledger}) == len(ledger)
    assert {row["source_path"] for row in ledger} == set(proposals)

    for row in ledger:
        proposal = proposals[row["source_path"]]
        assert row["source_commit"] == proposal["source_commit"] == PIN
        assert all(row[field] == proposal[field] for field in IDENTITY_FIELDS)
        assert row["proposed_review_class"] == proposed_class(proposal)
        assert row["proposal_source_map"].startswith("migration/custody-review-")
        if row["proposal_review_status"] == ACCEPTED:
            assert all(row[field] == proposal[field] for field in RECONCILED_FIELDS)
            assert row["known_limitations_and_rationale"] == accepted_rationale(proposal)
            assert "not reviewed sufficiently" not in row["known_limitations_and_rationale"]
            assert "ledger remains DEFER" not in row["known_limitations_and_rationale"]
            assert "DEFER pending" not in row["known_limitations_and_rationale"]
        if owner_reclassified_result(row["source_path"]):
            assert row["custody_classification"] == "SCIENTIFIC_EVIDENCE"
            assert row["proposal_review_status"] == ACCEPTED
            assert "NOT_ADMITTED" in row["known_limitations_and_rationale"]
            if row["source_path"].endswith("causal-revision-sequence/results.json"):
                assert row["proposed_review_class"] == "SCIENTIFIC_EVIDENCE"
                assert "dirty=true" in row["known_limitations_and_rationale"]
                assert "h1_supported=false" in row["known_limitations_and_rationale"]
            else:
                assert row["proposed_review_class"] == "DEFER"
        elif row["proposed_review_class"] == "DEFER":
            assert row["custody_classification"] == "DEFER"
            assert row["proposal_review_status"] == EXCEPTION
            assert len(row["known_limitations_and_rationale"]) >= 100
            assert "Reopen" in row["known_limitations_and_rationale"]
        else:
            assert row["custody_classification"] == row["proposed_review_class"]
            assert row["proposal_review_status"] == ACCEPTED
            assert "NOT_ADMITTED" in row["proposal_review_status"]


def test_final_classes_are_owner_dispositions_not_admission_claims() -> None:
    ledger = read_tsv("scientific-custody-80d372a.tsv")
    assert Counter(row["custody_classification"] for row in ledger) == {
        "DEFER": 29,
        "HISTORICAL_RECORD": 95,
        "PROTOCOL": 221,
        "SCIENTIFIC_EVIDENCE": 83,
        "WORKING_ARTIFACT": 49,
    }
    assert Counter(row["proposal_review_status"] for row in ledger) == {
        ACCEPTED: 448,
        EXCEPTION: 29,
    }
    assert all(row["custodian"].startswith("Biopeia Lab") for row in ledger)


def test_v024_results_remain_custody_only_and_replay_is_working_artifact() -> None:
    ledger = {
        row["source_path"]: row
        for row in read_tsv("scientific-custody-80d372a.tsv")
    }
    for name in ("baseline.json", "causal.json", "causal_validation.json"):
        row = ledger[f"lab/research/audits/historical/v024/{name}"]
        assert row["custody_classification"] == "SCIENTIFIC_EVIDENCE"
        assert "no unique per-output run_id is asserted" in row["protocol_or_run_linkage"]
        assert row["proposal_review_status"] == ACCEPTED
        assert "NOT_ADMITTED" in row["proposal_review_status"]

    replay = ledger["lab/examples/replays/symbiont-replay.json"]
    assert replay["custody_classification"] == "WORKING_ARTIFACT"
    assert replay["proposal_review_status"] == ACCEPTED
    replay_map = read_tsv("custody-review-replay-80d372a.tsv")[0]
    assert "not a protocol" in replay_map["known_limitations_and_rationale"].lower()


def test_cognitive_cycle_manifest_result_conflicts_remain_explicit_exceptions() -> None:
    ledger = {
        row["source_path"]: row
        for row in read_tsv("scientific-custody-80d372a.tsv")
    }
    paths = (
        "lab/research/studies/cognition/cognitive-cycle/"
        f"2026-10-04-shared-fact-identity-confirmatory-seed{seed}.result.json"
        for seed in (101, 102, 103)
    )
    for path in paths:
        row = ledger[path]
        assert row["custody_classification"] == "DEFER"
        assert row["proposal_review_status"] == EXCEPTION
        assert "confirmatory" in row["known_limitations_and_rationale"]
        assert "exploratory" in row["known_limitations_and_rationale"]


def test_eight_embodiment_results_are_custody_only_not_admitted():
    ledger = read_tsv("scientific-custody-80d372a.tsv")
    results = [
        row
        for row in ledger
        if row["source_path"].startswith("lab/experiments/embodiment/")
        and row["source_path"].endswith("/results.json")
    ]
    assert len(results) == 8
    for row in results:
        assert row["custody_classification"] == "SCIENTIFIC_EVIDENCE"
        assert row["proposal_review_status"] == ACCEPTED
        assert "config_digest=" in row["seed_and_configuration"]
        assert "NOT_ADMITTED" in row["known_limitations_and_rationale"]
        if row["source_path"].endswith("causal-revision-sequence/results.json"):
            assert "run_id=20260921T140357Z-embodiment-causal-revision-sequence-215145d-98d3" in row["protocol_or_run_linkage"]
            assert "software.dirty=true" in row["protocol_or_run_linkage"]
            assert "exact executed source tree not reconstructible" in row["protocol_or_run_linkage"]
            assert "h1_supported=false" in row["known_limitations_and_rationale"]
            assert "scientifically_valid=true" in row["known_limitations_and_rationale"]
        elif row["source_path"].endswith("heredity-leakage-challenge/results.json"):
            assert "run_id=20260921T140452Z-embodiment-heredity-leakage-challenge-215145d-5d8f" in row["protocol_or_run_linkage"]
            assert "software.dirty=true" in row["protocol_or_run_linkage"]
            assert "exact executed source tree not reconstructible" in row["protocol_or_run_linkage"]
            assert "scientifically_valid=true" in row["known_limitations_and_rationale"]
            assert "not accepted conclusions" in row["known_limitations_and_rationale"]
        else:
            assert "candidate protocol=" in row["protocol_or_run_linkage"]
            assert "no uniquely attributable run ID" in row["protocol_or_run_linkage"]
            assert "execution producer/source commit not identified" in row["producer_or_source"]
            assert "No run ID or producer is inferred" in row["known_limitations_and_rationale"]


def test_causal_revision_disposition_and_cross_ledger_records_agree() -> None:
    protocol_id = "embodiment.causal-revision-sequence"
    source_root = "lab/experiments/embodiment/causal-revision-sequence/"
    crosswalk = {
        row["protocol_id"]: row
        for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
    }[protocol_id]
    disposition = {
        row["unit_id"]: row
        for row in read_tsv("study-disposition-register-80d372a.tsv")
    }[protocol_id]
    evidence = {
        row["protocol_id"]: row
        for row in read_tsv("study-evidence-map-80d372a.tsv")
    }[protocol_id]
    inventory = {
        row["source_path"]: row
        for row in read_tsv("source-inventory-80d372a.tsv")
    }
    custody = {
        row["source_path"]: row
        for row in read_tsv("scientific-custody-80d372a.tsv")
    }

    assert crosswalk["candidate_disposition"] == "HISTORICAL_PROTOCOL"
    assert disposition["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert "test_e4_is_deterministic_and_reports_all_phases" in crosswalk[
        "study_test_path_candidates"
    ]
    assert "test_e4_rejects_invalid_steps" in crosswalk["study_test_path_candidates"]
    assert crosswalk["study_test_path_candidates"] != "NONE_FOUND_BY_LITERAL_ID_OR_CALLABLE_SEARCH"
    for test_name in (
        "test_e4_is_deterministic_and_reports_all_phases",
        "test_e4_does_not_encode_h1_as_software_success",
        "test_e4_protocol_is_registered",
        "test_e4_rejects_invalid_steps",
    ):
        assert test_name in evidence["test_symbol_refs"]

    implementation_path = "lab/src/lab/studies/embodiment/causal_revision_sequence.py"
    assert inventory[implementation_path]["disposition"] == "DROP"
    assert inventory[implementation_path]["target_path_or_status"] == "No TARGET implementation path; historical protocol only"
    for filename, expected_class in (
        ("README.md", "PROTOCOL"),
        ("experiment.toml", "PROTOCOL"),
        ("results.json", "SCIENTIFIC_EVIDENCE"),
    ):
        path = source_root + filename
        assert inventory[path]["disposition"] == "DEFER"
        assert "no physical TARGET transfer" in inventory[path]["rationale_and_caveat"]
        assert custody[path]["custody_classification"] == expected_class
        assert custody[path]["proposal_review_status"] == ACCEPTED
        assert "NOT_ADMITTED" in custody[path]["proposal_review_status"]
        assert "NOT_SCIENTIFICALLY_VALIDATED" in custody[path]["proposal_review_status"]

    result = custody[source_root + "results.json"]
    assert "software.dirty=true" in result["protocol_or_run_linkage"]
    assert "exact executed source tree not reconstructible" in result[
        "protocol_or_run_linkage"
    ]
    assert "scientifically_valid=true" in result["known_limitations_and_rationale"]
    assert "not treated as validation" in result["known_limitations_and_rationale"]

    review_summary = (MIGRATION / "custody-review-embodiment-kernel-80d372a.md").read_text(
        encoding="utf-8"
    )
    validation_boundary = review_summary.split("## Validation boundary", 1)[1]
    assert "Seven results lack an attributable run ID" in validation_boundary
    assert "The causal-revision result records a run ID, source SHA, and `config_digest`" in validation_boundary
    assert "software.dirty=true" in validation_boundary
    assert "exact executed tree is not reconstructible" in validation_boundary


def test_proposal_maps_distinguish_historical_state_from_current_ledger() -> None:
    proposal_docs = (
        "custody-review-experiment-root-readme-80d372a.md",
        "custody-review-other-experiments-80d372a.md",
    )
    proposal_tsvs = (
        "custody-review-experiment-root-readme-80d372a.tsv",
        "custody-review-other-experiments-80d372a.tsv",
    )
    for name in proposal_docs:
        assert "proposal-time" in (MIGRATION / name).read_text(encoding="utf-8")
    for name in proposal_tsvs:
        content = (MIGRATION / name).read_text(encoding="utf-8")
        assert "At proposal time" in content
        assert not re.search(
            r"(?:canonical (?:custody )?ledger) remains DEFER", content, re.IGNORECASE
        )


def test_heredity_leakage_disposition_is_bounded_and_cross_ledger_consistent() -> None:
    protocol_id = "embodiment.heredity-leakage-challenge"
    source_root = "lab/experiments/embodiment/heredity-leakage-challenge/"
    crosswalk = {row["protocol_id"]: row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")}[protocol_id]
    disposition = {row["unit_id"]: row for row in read_tsv("study-disposition-register-80d372a.tsv")}[protocol_id]
    links = {row["protocol_id"]: row for row in read_tsv("study-protocol-test-links-80d372a.tsv")}[protocol_id]
    inventory = {row["source_path"]: row for row in read_tsv("source-inventory-80d372a.tsv")}
    custody = {row["source_path"]: row for row in read_tsv("scientific-custody-80d372a.tsv")}

    assert crosswalk["candidate_disposition"] == "HISTORICAL_PROTOCOL"
    assert disposition["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert disposition["source_implementation_TARGET_disposition"] == "DROP"
    assert "software.dirty=true" in disposition["real_run_identity"]
    assert "method equivalence claim is made" in disposition["limitations_and_nonclaims"]
    assert "test_e7_heredity_leakage_replay" in links["test_symbol_links"]
    assert "test_e7_e8_protocols_registered" in links["test_symbol_links"]
    implementation = "lab/src/lab/studies/embodiment/heredity_leakage_challenge.py"
    assert inventory[implementation]["disposition"] == "DROP"
    assert custody[source_root + "README.md"]["custody_classification"] == "WORKING_ARTIFACT"
    assert custody[source_root + "experiment.toml"]["custody_classification"] == "PROTOCOL"
    result = custody[source_root + "results.json"]
    assert result["custody_classification"] == "SCIENTIFIC_EVIDENCE"
    assert result["proposal_review_status"] == ACCEPTED
    assert "NOT_ADMITTED" in result["proposal_review_status"]
    assert "scientifically_valid=true" in result["known_limitations_and_rationale"]
    assert "not accepted conclusions" in result["known_limitations_and_rationale"]
