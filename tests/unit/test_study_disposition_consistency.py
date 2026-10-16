"""Keep source-file dispositions consistent with owner-approved study units."""

from __future__ import annotations

import csv
from pathlib import Path

MIGRATION = Path(__file__).parents[2] / "migration"


def read_tsv(name: str) -> list[dict[str, str]]:
    with (MIGRATION / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def test_accepted_historical_custody_is_separate_from_code_migration_disposition() -> None:
    source_rows = read_tsv("source-inventory-80d372a.tsv")
    custody_rows = read_tsv("scientific-custody-80d372a.tsv")
    source = {row["source_path"]: row for row in source_rows}
    custody = {row["source_path"]: row for row in custody_rows}

    assert len(source_rows) == len(source) == 1172
    assert len(custody_rows) == len(custody) == 477
    assert custody.keys() <= source.keys()

    accepted_status = (
        "LAB_OWNER_ACCEPTED_CUSTODY_CLASSIFICATION; "
        "NOT_SCIENTIFICALLY_VALIDATED; NOT_ADMITTED"
    )
    exception_status = "LAB_OWNER_DISPOSITION_PENDING; EXCEPTION_DOCUMENTED; NOT_ADMITTED"
    accepted = {
        path: row
        for path, row in custody.items()
        if row["proposal_review_status"] == accepted_status
    }
    exceptions = {
        path: row
        for path, row in custody.items()
        if row["proposal_review_status"] == exception_status
    }

    assert len(accepted) == 448
    assert len(exceptions) == 29
    assert set(accepted) | set(exceptions) == custody.keys()
    assert {row["custody_classification"] for row in accepted.values()} == {
        "SCIENTIFIC_EVIDENCE",
        "PROTOCOL",
        "HISTORICAL_RECORD",
        "WORKING_ARTIFACT",
    }
    assert {
        classification: sum(
            row["custody_classification"] == classification
            for row in accepted.values()
        )
        for classification in (
            "PROTOCOL",
            "HISTORICAL_RECORD",
            "SCIENTIFIC_EVIDENCE",
            "WORKING_ARTIFACT",
        )
    } == {
        "PROTOCOL": 221,
        "HISTORICAL_RECORD": 95,
        "SCIENTIFIC_EVIDENCE": 83,
        "WORKING_ARTIFACT": 49,
    }

    # Every row is a one-to-one path join and preserves the pinned provenance.
    # Independently verified against git objects at source commit
    # 80d372a186513035f85a769db886e505cabba52d during this bounded reconciliation.
    for path, custody_row in custody.items():
        source_row = source[path]
        assert custody_row["source_repository"] == "alessbarb/symbiont-lab"
        assert custody_row["source_commit"] == "80d372a186513035f85a769db886e505cabba52d"
        assert len(custody_row["content_sha256"]) == 64
        assert all(character in "0123456789abcdef" for character in custody_row["content_sha256"])
        assert source_row["source_blob_at_pinned_commit"] == custody_row["source_blob"]
        assert source_row["bytes"] == custody_row["bytes"]

    preserved_existing_drops = 0
    for path, custody_row in accepted.items():
        source_row = source[path]
        assert source_row["disposition"] == "DROP"
        assert source_row["target_owner"] == "Lab"
        rationale = source_row["rationale_and_caveat"]
        assert "migration/scientific-custody-80d372a.tsv" in rationale
        assert custody_row["proposal_review_status"] == accepted_status
        if "Code-migration disposition: DROP" in rationale:
            assert (
                source_row["target_path_or_status"]
                == "No TARGET artifact bytes are being migrated"
            )
            assert f"`{custody_row['custody_classification']}`" in rationale
            assert "does not authorize deletion" in rationale
            assert "scientifically validate evidence" in rationale
        else:
            # Preserve the narrower owner rationales already recorded before this slice.
            preserved_existing_drops += 1
            assert source_row["target_path_or_status"].startswith("No TARGET ")
            assert (
                path.startswith("lab/experiments/embodiment/label-invariance/")
                or path.startswith(
                    "lab/experiments/embodiment/label-invariance-governed-20261001-0a901ea/"
                )
                or path
                in {
                    "lab/experiments/learning/visual-acquisition-v1/audit/README.md",
                    "lab/experiments/learning/visual-acquisition-v1/audit/experiment.toml",
                }
            )
            assert (
                "Owner disposition in biopeia/lab#62" in rationale
                or "Biopeia Lab issue #57" in rationale
            )

    assert preserved_existing_drops == 29

    for path, custody_row in exceptions.items():
        assert source[path]["disposition"] == "DEFER"
        assert custody_row["custody_classification"] == "DEFER"
        assert custody_row["proposal_review_status"] == exception_status


def test_label_invariance_artifact_disposition_matches_accepted_custody() -> None:
    source_rows = read_tsv("source-inventory-80d372a.tsv")
    custody_rows = read_tsv("scientific-custody-80d372a.tsv")
    source_prefixes = (
        "lab/experiments/embodiment/label-invariance/",
        "lab/experiments/embodiment/label-invariance-governed-20261001-0a901ea/",
    )
    source = {
        row["source_path"]: row
        for row in source_rows
        if row["source_path"].startswith(source_prefixes)
    }
    custody = {
        row["source_path"]: row
        for row in custody_rows
        if row["source_path"].startswith(source_prefixes)
    }

    assert len(source) == len(custody) == 27
    assert {
        row["custody_classification"] for row in custody.values()
    } == {"PROTOCOL", "SCIENTIFIC_EVIDENCE", "HISTORICAL_RECORD"}
    class_counts = {
        classification: sum(
            row["custody_classification"] == classification
            for row in custody.values()
        )
        for classification in ("SCIENTIFIC_EVIDENCE", "PROTOCOL", "HISTORICAL_RECORD")
    }
    assert class_counts == {
        "SCIENTIFIC_EVIDENCE": 24,
        "PROTOCOL": 2,
        "HISTORICAL_RECORD": 1,
    }

    for path, source_row in source.items():
        custody_row = custody[path]
        assert source_row["disposition"] == "DROP"
        assert source_row["target_owner"] == "Lab"
        assert (
            source_row["target_path_or_status"]
            == "No TARGET artifact bytes are being migrated"
        )
        assert source_row["source_blob_at_pinned_commit"] == custody_row["source_blob"]
        assert source_row["bytes"] == custody_row["bytes"]
        assert custody_row["source_repository"] == "alessbarb/symbiont-lab"
        assert custody_row["source_commit"] == "80d372a186513035f85a769db886e505cabba52d"
        assert (
            "LAB_OWNER_ACCEPTED_CUSTODY_CLASSIFICATION"
            in custody_row["proposal_review_status"]
        )
        assert "NOT_SCIENTIFICALLY_VALIDATED" in custody_row["proposal_review_status"]
        assert "NOT_ADMITTED" in custody_row["proposal_review_status"]
        assert "biopeia/lab#62" in source_row["rationale_and_caveat"]
        assert "do not merge, reconcile, or prefer" in source_row["rationale_and_caveat"]
        assert (
            "until custodial owner classifies it"
            not in source_row["rationale_and_caveat"]
        )

    crosswalk = next(
        row
        for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "embodiment.label-invariance"
    )
    assert crosswalk["candidate_disposition"] == "HISTORICAL_PROTOCOL"
    assert (
        crosswalk["experiment_spec_path_candidates"]
        == "lab/experiments/embodiment/label-invariance/experiment.toml"
    )
    candidate_paths = set(
        crosswalk["experiment_artifact_path_candidates"].split(";")
    )
    assert candidate_paths <= source.keys()
    assert len(candidate_paths) == 26  # The protocol TOML is listed as a spec, not a result artifact.


def test_resolved_study_implementations_and_tests_are_dropped() -> None:
    source = {
        row["source_path"]: row
        for row in read_tsv("source-inventory-80d372a.tsv")
    }
    units = read_tsv("study-disposition-register-80d372a.tsv")

    assert len(units) == 18
    by_id = {unit["unit_id"]: unit for unit in units}
    assert len(by_id) == len(units)
    agency_ablation = by_id.pop("learning.agency-acquisition-ablation")
    assert agency_ablation["study_protocol_disposition"] == "DEFER"
    assert agency_ablation["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#123" in agency_ablation["owner_basis"]
    assert "Closure trigger:" in agency_ablation["TARGET_action"]
    assert "NO_DIRECT_TEST_LINK" in agency_ablation["source_evidence_basis"]
    for source_ref in (
        agency_ablation["implementation_path_and_blob"],
        agency_ablation["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    consolidated_intervention = by_id.pop(
        "learning.agency-consolidated-causal-intervention"
    )
    assert consolidated_intervention["study_protocol_disposition"] == "DEFER"
    assert consolidated_intervention["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#133" in consolidated_intervention["owner_basis"]
    assert "Closure trigger:" in consolidated_intervention["TARGET_action"]
    assert "README mixes preregistration and reported diagnostic figures" in (
        consolidated_intervention["source_evidence_basis"]
    )
    assert "5/10 and 7/10" in consolidated_intervention["real_run_identity"]
    assert "No claim of scientific validity" in consolidated_intervention[
        "limitations_and_nonclaims"
    ]
    for source_ref in (
        *consolidated_intervention["protocol_paths_and_blobs"].split(";"),
        consolidated_intervention["implementation_path_and_blob"],
        consolidated_intervention["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    consolidated_crosswalk = next(
        row
        for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.agency-consolidated-causal-intervention"
    )
    assert consolidated_crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#133" in consolidated_crosswalk["basis"]
    embodied_intervention = by_id.pop("learning.agency-embodied-causal-intervention")
    assert embodied_intervention["study_protocol_disposition"] == "DEFER"
    assert embodied_intervention["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#134" in embodied_intervention["owner_basis"]
    assert "Closure trigger:" in embodied_intervention["TARGET_action"]
    assert "no run identifier or execution artifact" in embodied_intervention["real_run_identity"]
    assert "No claim of scientific validity" in embodied_intervention["limitations_and_nonclaims"]
    for source_ref in (
        *embodied_intervention["protocol_paths_and_blobs"].split(";"),
        embodied_intervention["implementation_path_and_blob"],
        embodied_intervention["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    embodied_crosswalk = next(
        row
        for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.agency-embodied-causal-intervention"
    )
    assert embodied_crosswalk["candidate_disposition"] == "DEFER"
    assert "Lab #134" in embodied_crosswalk["basis"]

    executive_bridge = by_id.pop("learning.agency-executive-bridge-ablation")
    assert executive_bridge["study_protocol_disposition"] == "DEFER"
    assert executive_bridge["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#135" in executive_bridge["owner_basis"]
    assert "Closure trigger:" in executive_bridge["TARGET_action"]
    assert "No run/result artifact" in executive_bridge["experiment_artifacts_and_digests"]
    assert "No claim of scientific validity" in executive_bridge["limitations_and_nonclaims"]
    for source_ref in (
        *executive_bridge["protocol_paths_and_blobs"].split(";"),
        executive_bridge["implementation_path_and_blob"],
        executive_bridge["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    executive_crosswalk = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.agency-executive-bridge-ablation"
    )
    assert executive_crosswalk["candidate_disposition"] == "DEFER"
    assert "Lab #135" in executive_crosswalk["basis"]

    high_dimensional = by_id.pop("learning.agency-high-dimensional-acquisition")
    assert high_dimensional["study_protocol_disposition"] == "DEFER"
    assert high_dimensional["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#136" in high_dimensional["owner_basis"]
    assert "Closure trigger:" in high_dimensional["TARGET_action"]
    assert "38429ca2cbb17a4137ca378fc01136f3af1a00d3" in high_dimensional["real_run_identity"]
    assert "not treated as validated findings or admitted scientific evidence" in high_dimensional["limitations_and_nonclaims"]
    for source_ref in (
        *high_dimensional["protocol_paths_and_blobs"].split(";"),
        high_dimensional["implementation_path_and_blob"],
        high_dimensional["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    high_dimensional_crosswalk = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.agency-high-dimensional-acquisition"
    )
    assert high_dimensional_crosswalk["candidate_disposition"] == "DEFER"
    assert "Lab #136" in high_dimensional_crosswalk["basis"]

    intent_persistence = by_id.pop("learning.agency-intent-persistence")
    assert intent_persistence["study_protocol_disposition"] == "DEFER"
    assert intent_persistence["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#137" in intent_persistence["owner_basis"]
    assert "Closure trigger:" in intent_persistence["TARGET_action"]
    assert "No run/result artifact" in intent_persistence["experiment_artifacts_and_digests"]
    assert "No claim of scientific validity" in intent_persistence["limitations_and_nonclaims"]
    for source_ref in (
        *intent_persistence["protocol_paths_and_blobs"].split(";"),
        intent_persistence["implementation_path_and_blob"],
        intent_persistence["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    intent_crosswalk = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.agency-intent-persistence"
    )
    assert intent_crosswalk["candidate_disposition"] == "DEFER"
    assert "Lab #137" in intent_crosswalk["basis"]

    visual_audit = by_id.pop("learning.visual-predictor-audit")
    assert visual_audit["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert visual_audit["source_implementation_TARGET_disposition"] == "DROP"
    implementation_path, expected_blob = visual_audit["implementation_path_and_blob"].split("@", maxsplit=1)
    assert source[implementation_path]["source_blob_at_pinned_commit"] == expected_blob
    assert source[implementation_path]["disposition"] == "DROP"
    somatic_trap = by_id.pop("embodiment.somatic-correlation-trap")
    assert somatic_trap["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert somatic_trap["source_implementation_TARGET_disposition"] == "DROP"
    assert "biopeia/lab/issues/61" in somatic_trap["owner_basis"]
    assert "NOT_ADMITTED" in somatic_trap["custody_ledger_state"]
    assert "NOT_SCIENTIFICALLY_VALIDATED" in somatic_trap["custody_ledger_state"]
    assert "activation/temperature relation" in somatic_trap["limitations_and_nonclaims"]
    for source_ref in (
        somatic_trap["implementation_path_and_blob"],
        somatic_trap["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
        assert source[path]["disposition"] == "DROP"

    temporal_challenge = by_id.pop("embodiment.temporal-causality-challenge")
    assert temporal_challenge["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert temporal_challenge["source_implementation_TARGET_disposition"] == "DROP"
    assert "biopeia/lab#77" in temporal_challenge["owner_basis"]
    assert "BOUNDED" in temporal_challenge["owner_basis"]
    assert "NOT_ADMITTED" in temporal_challenge["custody_ledger_state"]
    assert "NOT_SCIENTIFICALLY_VALIDATED" in temporal_challenge["custody_ledger_state"]
    assert "run_id=20260921T140558Z-embodiment-temporal-causality-challenge-64a24d0-ad61" in temporal_challenge[
        "real_run_identity"
    ]
    assert "software.dirty=true" in temporal_challenge["real_run_identity"]
    assert "uniquely reconstructible execution" in temporal_challenge["real_run_identity"]
    for source_ref in (
        temporal_challenge["implementation_path_and_blob"],
        temporal_challenge["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
        assert source[path]["disposition"] == "DROP"

    temporal_impl = source[
        "lab/src/lab/studies/embodiment/temporal_causality_challenge.py"
    ]
    assert temporal_impl["disposition"] == "DROP"
    assert temporal_impl["target_path_or_status"] == "No TARGET implementation"
    temporal_crosswalk = next(
        row
        for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "embodiment.temporal-causality-challenge"
    )
    assert temporal_crosswalk["candidate_disposition"] == "HISTORICAL_PROTOCOL"
    temporal_result = next(
        row
        for row in read_tsv("scientific-custody-80d372a.tsv")
        if row["source_path"] == "lab/experiments/embodiment/temporal-causality-challenge/results.json"
    )
    assert "run_id=20260921T140558Z-embodiment-temporal-causality-challenge-64a24d0-ad61" in temporal_result[
        "protocol_or_run_linkage"
    ]
    assert "software.dirty=true" in temporal_result["known_limitations_and_rationale"]
    assert "NOT_ADMITTED" in temporal_result["known_limitations_and_rationale"]
    assert "scientific validity" in temporal_crosswalk["basis"]

    continuous_temporal = by_id.pop("learning.continuous-temporal-challenge")
    assert continuous_temporal["study_protocol_disposition"] == "DEFER"
    assert continuous_temporal["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#148" in continuous_temporal["owner_basis"]
    assert "Closure trigger:" in continuous_temporal["TARGET_action"]
    assert "No authorized TARGET question/consumer" in continuous_temporal[
        "source_evidence_basis"
    ]
    assert "no claim of scientific validity" in continuous_temporal["limitations_and_nonclaims"]
    for source_ref in (
        continuous_temporal["implementation_path_and_blob"],
        continuous_temporal["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob

    continuous_temporal_crosswalk = next(
        row
        for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.continuous-temporal-challenge"
    )
    assert continuous_temporal_crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#148" in continuous_temporal_crosswalk["basis"]

    tool_body = by_id.pop("embodiment.tool-body-distinction")
    assert tool_body["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert tool_body["source_implementation_TARGET_disposition"] == "DROP"
    assert "no current authorized TARGET consumer" in tool_body["source_evidence_basis"]
    assert "No scientific validity" in tool_body["limitations_and_nonclaims"]
    assert "software.dirty=true" in tool_body["real_run_identity"]
    assert "not treated as a validated scientific finding" in tool_body[
        "source_evidence_basis"
    ]
    for source_ref in (
        tool_body["implementation_path_and_blob"],
        tool_body["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
        assert source[path]["disposition"] == "DROP"

    tool_body_crosswalk = next(
        row
        for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "embodiment.tool-body-distinction"
    )
    assert tool_body_crosswalk["candidate_disposition"] == "HISTORICAL_PROTOCOL"
    assert "no current authorized Biopeia TARGET consumer" in tool_body_crosswalk[
        "basis"
    ]
    assert "software.dirty=true" in tool_body_crosswalk["basis"]

    tool_body_evidence = next(
        row
        for row in read_tsv("study-evidence-map-80d372a.tsv")
        if row["protocol_id"] == "embodiment.tool-body-distinction"
    )
    assert "custody:PROTOCOL" in tool_body_evidence["artifact_custody_refs"]
    assert "custody:SCIENTIFIC_EVIDENCE" in tool_body_evidence[
        "artifact_custody_refs"
    ]
    assert "NOT_ADMITTED" in tool_body_evidence["artifact_custody_refs"]

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

    yoked = by_id.pop("embodiment.yoked-external-causation")
    assert yoked["study_protocol_disposition"] == "DEFER"
    assert yoked["source_implementation_TARGET_disposition"] == "DROP"
    assert "software.dirty=true" in yoked["real_run_identity"]
    assert "FPR=0.30" in yoked["source_evidence_basis"]
    assert "NOT_ADMITTED" in yoked["custody_ledger_state"]
    assert "NOT_SCIENTIFICALLY_VALIDATED" in yoked["custody_ledger_state"]
    implementation_path, expected_blob = yoked["implementation_path_and_blob"].split(
        "@", maxsplit=1
    )
    assert source[implementation_path]["source_blob_at_pinned_commit"] == expected_blob
    # The study-level source inventory remains DEFER until applicability is resolved;
    # this register separately records that no implementation is ported to TARGET.
    assert source[implementation_path]["disposition"] == "DEFER"
    test_path, expected_blob = yoked["source_test_path_and_blob"].split(
        "@", maxsplit=1
    )
    assert source[test_path]["source_blob_at_pinned_commit"] == expected_blob
    assert source[test_path]["disposition"] == "DROP"
    yoked_crosswalk = next(
        row
        for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "embodiment.yoked-external-causation"
    )
    assert yoked_crosswalk["candidate_disposition"] == "DEFER"
    assert (
        "test_e1_yoked_external_causation_is_deterministic_and_bounded"
        in yoked_crosswalk["study_test_path_candidates"]
    )

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


def test_registered_protocol_crosswalk_matches_resolved_dispositions() -> None:
    units = read_tsv("study-disposition-register-80d372a.tsv")
    crosswalk = read_tsv("study-protocol-crosswalk-80d372a.tsv")
    crosswalk_by_id = {row["protocol_id"]: row for row in crosswalk}

    assert len(crosswalk_by_id) == len(crosswalk)
    somatic_protocol = crosswalk_by_id["embodiment.somatic-correlation-trap"]
    assert somatic_protocol["candidate_disposition"] == "HISTORICAL_PROTOCOL"
    assert "biopeia/lab#61" in somatic_protocol["basis"]
    assert "does not claim scientific validity" in somatic_protocol["basis"]
    for unit in units:
        protocol = crosswalk_by_id[unit["unit_id"]]
        assert protocol["candidate_disposition"] == unit["study_protocol_disposition"]
