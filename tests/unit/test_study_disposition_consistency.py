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


def test_continuous_temporal_controls_has_bounded_issue_disposition() -> None:
    crosswalk = next(
        row
        for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.continuous-temporal-controls"
    )
    disposition = next(
        row
        for row in read_tsv("study-disposition-register-80d372a.tsv")
        if row["unit_id"] == "learning.continuous-temporal-controls"
    )

    assert crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#149" in crosswalk["basis"]
    assert disposition["study_protocol_disposition"] == "DEFER"
    assert disposition["source_implementation_TARGET_disposition"] == "DEFER"
    assert disposition["source_commit"] == "80d372a186513035f85a769db886e505cabba52d"
    assert "experiment.toml@52fe0da29c26373f8bee2322adc69798469a6e63" in disposition[
        "protocol_paths_and_blobs"
    ]
    assert "NOT_ESTABLISHED" in disposition["real_run_identity"]
    assert "Do not port" in disposition["TARGET_action"]
    assert "biopeia/lab#149" in disposition["owner_basis"]


def test_cultural_foundation_has_bounded_issue_disposition() -> None:
    crosswalk = next(
        row
        for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.cultural-foundation"
    )
    disposition = next(
        row
        for row in read_tsv("study-disposition-register-80d372a.tsv")
        if row["unit_id"] == "learning.cultural-foundation"
    )

    assert crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#150" in crosswalk["basis"]
    assert disposition["study_protocol_disposition"] == "DEFER"
    assert disposition["source_implementation_TARGET_disposition"] == "DEFER"
    assert disposition["source_commit"] == "80d372a186513035f85a769db886e505cabba52d"
    assert "experiment.toml@a705f1a7cbd8022f620d910f463ba3d733bb0bfd" in disposition[
        "protocol_paths_and_blobs"
    ]
    assert "NOT_ESTABLISHED" in disposition["real_run_identity"]
    assert "do not port" in disposition["TARGET_action"]
    assert "biopeia/lab#150" in disposition["owner_basis"]


def test_cumulative_culture_has_bounded_issue_disposition() -> None:
    crosswalk = next(
        row
        for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.cumulative-culture"
    )
    disposition = next(
        row
        for row in read_tsv("study-disposition-register-80d372a.tsv")
        if row["unit_id"] == "learning.cumulative-culture"
    )

    assert crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#151" in crosswalk["basis"]
    assert "no run/result artifact" in crosswalk["basis"]
    assert "do not port" in crosswalk["basis"]
    assert disposition["study_protocol_disposition"] == "DEFER"
    assert disposition["source_implementation_TARGET_disposition"] == "DEFER"
    assert disposition["source_commit"] == "80d372a186513035f85a769db886e505cabba52d"
    assert "experiment.toml@d29c42a6b2da9070d4ee49d4e3c6fd933d143935" in disposition[
        "protocol_paths_and_blobs"
    ]
    assert "README.md@8ef3630a9a5d2025d249bae8b571cc35f75cf50e" in disposition[
        "protocol_paths_and_blobs"
    ]
    assert "NOT_ESTABLISHED" in disposition["real_run_identity"]
    assert "Do not port" in disposition["TARGET_action"]
    assert "biopeia/lab#151" in disposition["owner_basis"]
    source = {
        row["source_path"]: row
        for row in read_tsv("source-inventory-80d372a.tsv")
    }
    for source_ref in (
        *disposition["protocol_paths_and_blobs"].split(";"),
        disposition["implementation_path_and_blob"],
        disposition["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob


def test_embodied_behavioral_ablation_has_bounded_issue_disposition() -> None:
    crosswalk = next(
        row
        for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.embodied-behavioral-ablation"
    )
    disposition = next(
        row
        for row in read_tsv("study-disposition-register-80d372a.tsv")
        if row["unit_id"] == "learning.embodied-behavioral-ablation"
    )

    assert crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#152" in crosswalk["basis"]
    assert disposition["study_protocol_disposition"] == "DEFER"
    assert disposition["source_implementation_TARGET_disposition"] == "DEFER"
    assert disposition["source_commit"] == "80d372a186513035f85a769db886e505cabba52d"
    assert "experiment.toml@c5842fd9603b91420331c2a265a015e718bf81e2" in disposition[
        "protocol_paths_and_blobs"
    ]
    assert "results.json@10440f38a59c47e838e9260c6e145de7ac6baa7d@sha256:9caca76bdf94a904b6fa71fd8c88e7d1fcdd3af816e813802fea4fc5a1dc42af" in disposition[
        "experiment_artifacts_and_digests"
    ]
    assert "20260921T140646Z-learning-embodied-behavioral-ablation-64a24d0-05c9" in disposition[
        "real_run_identity"
    ]
    assert "NOT_ADMITTED" in disposition["custody_ledger_state"]
    assert "biopeia/lab#152" in disposition["owner_basis"]
    source = {
        row["source_path"]: row
        for row in read_tsv("source-inventory-80d372a.tsv")
    }
    for source_ref in (
        *disposition["protocol_paths_and_blobs"].split(";"),
        disposition["implementation_path_and_blob"],
        *disposition["source_test_path_and_blob"].split(";"),
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob


def test_resolved_study_implementations_and_tests_are_dropped() -> None:
    source = {
        row["source_path"]: row
        for row in read_tsv("source-inventory-80d372a.tsv")
    }
    units = read_tsv("study-disposition-register-80d372a.tsv")

    assert len(units) == 92
    fairness = next(unit for unit in units if unit["unit_id"] == "learning.structural-producer-fairness")
    assert fairness["study_protocol_disposition"] == "DEFER"
    assert fairness["source_implementation_TARGET_disposition"] == "DROP"
    assert "biopeia/lab#187" in fairness["owner_basis"]
    assert "No result/run artifact" in fairness["experiment_artifacts_and_digests"]
    structured = next(unit for unit in units if unit["unit_id"] == "learning.structured-causal-experience")
    assert structured["study_protocol_disposition"] == "DEFER"
    assert structured["source_implementation_TARGET_disposition"] == "DROP"
    assert "biopeia/lab#188" in structured["owner_basis"]
    assert "No result/run artifact" in structured["experiment_artifacts_and_digests"]
    generalization = next(unit for unit in units if unit["unit_id"] == "learning.structured-causal-generalization")
    assert generalization["study_protocol_disposition"] == "DEFER"
    assert generalization["source_implementation_TARGET_disposition"] == "DROP"
    assert "biopeia/lab#189" in generalization["owner_basis"]
    assert "No result/run artifact" in generalization["experiment_artifacts_and_digests"]
    characterization = next(unit for unit in units if unit["unit_id"] == "learning.structured-communication-characterization")
    assert characterization["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert characterization["source_implementation_TARGET_disposition"] == "DROP"
    assert "biopeia/lab#190" in characterization["owner_basis"]
    assert "2ffbd811d626aebe233974af16600b26c9f3c2ed" in characterization["experiment_artifacts_and_digests"]
    assert "NOT_ADMITTED" in characterization["limitations_and_nonclaims"]
    crosswalk = (MIGRATION / "study-protocol-crosswalk-80d372a.md").read_text(encoding="utf-8")
    assert crosswalk.count("manifest-level decisions**:") == 1
    assert f"records **{len(units)} manifest-level decisions**:" in crosswalk
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
    binding_history = by_id.pop(
        "learning.agency-acquisition-reuse-closure-binding-history"
    )
    assert binding_history["study_protocol_disposition"] == "DEFER"
    assert binding_history["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#124" in binding_history["owner_basis"]
    assert "other eight candidate manifests" in binding_history["TARGET_action"]
    assert "NOT_ESTABLISHED" in binding_history["real_run_identity"]
    assert "not independently validated" in binding_history["limitations_and_nonclaims"]
    for source_ref in (
        *binding_history["protocol_paths_and_blobs"].split(";"),
        binding_history["implementation_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    binding_history_alias = next(
        row
        for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.agency-acquisition-reuse-closure-binding-history"
    )
    assert binding_history_alias["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#124" in binding_history_alias["basis"]
    assert "manifest-specific alias" in binding_history_alias["resolution_method"]
    chance_corrected = by_id.pop(
        "learning.agency-acquisition-reuse-closure-chance-corrected"
    )
    assert chance_corrected["study_protocol_disposition"] == "DEFER"
    assert chance_corrected["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#125" in chance_corrected["owner_basis"]
    assert "other eight candidate manifests" in chance_corrected["TARGET_action"]
    assert "NOT_ESTABLISHED" in chance_corrected["real_run_identity"]
    assert "No experiment was executed" in chance_corrected["limitations_and_nonclaims"]
    for source_ref in (
        *chance_corrected["protocol_paths_and_blobs"].split(";"),
        chance_corrected["implementation_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    chance_corrected_alias = next(
        row
        for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.agency-acquisition-reuse-closure-chance-corrected"
    )
    assert chance_corrected_alias["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#125" in chance_corrected_alias["basis"]
    assert "manifest-specific alias" in chance_corrected_alias["resolution_method"]
    factorized = by_id.pop("learning.agency-acquisition-reuse-closure-factorized")
    assert factorized["study_protocol_disposition"] == "DEFER"
    assert factorized["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#126" in factorized["owner_basis"]
    assert "other eight manifests" in factorized["TARGET_action"]
    assert "NOT_ESTABLISHED" in factorized["real_run_identity"]
    assert "no physical-body test result" in factorized["limitations_and_nonclaims"]
    for source_ref in (
        *factorized["protocol_paths_and_blobs"].split(";"),
        factorized["implementation_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    factorized_alias = next(
        row
        for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.agency-acquisition-reuse-closure-factorized"
    )
    assert factorized_alias["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#126" in factorized_alias["basis"]
    assert "manifest-specific alias" in factorized_alias["resolution_method"]
    membership_bh = by_id.pop(
        "learning.agency-acquisition-reuse-closure-membership-bh"
    )
    assert membership_bh["study_protocol_disposition"] == "DEFER"
    assert "dc9ecfe25f7ac442629f0ed256cc83053891a151" in membership_bh[
        "protocol_paths_and_blobs"
    ]
    assert "03db814778ce0d53bcce82dccd6166dc60a4739d" in membership_bh[
        "protocol_paths_and_blobs"
    ]
    assert "agency-acquisition-reuse-closure-membership-bh/README.md" in membership_bh[
        "protocol_paths_and_blobs"
    ]
    assert "agency-acquisition-reuse-closure-membership-bh/experiment.toml" in membership_bh[
        "protocol_paths_and_blobs"
    ]
    assert "agency-acquisition-reuse-closure-factorized/" not in membership_bh[
        "protocol_paths_and_blobs"
    ]
    assert "no result/run artifact" in membership_bh["experiment_artifacts_and_digests"]
    assert "biopeia/lab#127" in membership_bh["owner_basis"]
    assert "Closure trigger:" in membership_bh["TARGET_action"]
    assert "no experiment was run" in membership_bh["limitations_and_nonclaims"]
    membership_bh_alias = next(
        row
        for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.agency-acquisition-reuse-closure-membership-bh"
    )
    assert membership_bh_alias["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#127" in membership_bh_alias["basis"]
    assert "manifest-specific alias" in membership_bh_alias["resolution_method"]
    assert "agency-acquisition-reuse-closure-membership-bh/experiment.toml" in membership_bh_alias[
        "experiment_spec_path_candidates"
    ]
    assert "agency-acquisition-reuse-closure-factorized/" not in membership_bh_alias[
        "experiment_spec_path_candidates"
    ]
    membership_bhb = by_id.pop("learning.agency-acquisition-reuse-closure-membership-bhb")
    assert membership_bhb["study_protocol_disposition"] == "DEFER"
    assert "0e2aac6eed147f6e264dcabef72dd81b465d0172" in membership_bhb["protocol_paths_and_blobs"]
    assert "cdffae49deb9f69b9116bb6aeb9d2e343c2e34c2" in membership_bhb["protocol_paths_and_blobs"]
    assert "biopeia/lab#128" in membership_bhb["owner_basis"]
    membership_bhb_alias = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == "learning.agency-acquisition-reuse-closure-membership-bhb")
    assert membership_bhb_alias["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#128" in membership_bhb_alias["basis"]
    membership_m = by_id.pop("learning.agency-acquisition-reuse-closure-membership-m")
    assert membership_m["study_protocol_disposition"] == "DEFER"
    assert "6c253be10196ebcc60a3be92218e77bb70533cd2" in membership_m["protocol_paths_and_blobs"]
    assert "1fc1f1b203680f09d8501ce615c9aebe72454c0b" in membership_m["protocol_paths_and_blobs"]
    assert "biopeia/lab#129" in membership_m["owner_basis"]
    membership_m_alias = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == "learning.agency-acquisition-reuse-closure-membership-m")
    assert membership_m_alias["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#129" in membership_m_alias["basis"]
    membership_t = by_id.pop("learning.agency-acquisition-reuse-closure-membership-t")
    assert membership_t["study_protocol_disposition"] == "DEFER"
    assert "413ba899365605c8b083e0c68200c3231d2586a8" in membership_t["protocol_paths_and_blobs"]
    assert "f75255c3b3ee54bc9bcf65dc154921ee0d60d895" in membership_t["protocol_paths_and_blobs"]
    assert "biopeia/lab#130" in membership_t["owner_basis"]
    membership_t_alias = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == "learning.agency-acquisition-reuse-closure-membership-t")
    assert membership_t_alias["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#130" in membership_t_alias["basis"]
    assert "manifest-specific alias" in membership_t_alias["resolution_method"]
    membership_tm = by_id.pop("learning.agency-acquisition-reuse-closure-membership-tm")
    assert membership_tm["study_protocol_disposition"] == "DEFER"
    assert membership_tm["source_implementation_TARGET_disposition"] == "DEFER"
    assert "5a89784af6358cc6e9921288b5d9359e0ae08dc9" in membership_tm["protocol_paths_and_blobs"]
    assert "22767c97f6a9c15bf4adbbebf47ba2ec4eb831c7" in membership_tm["protocol_paths_and_blobs"]
    assert "biopeia/lab#131" in membership_tm["owner_basis"]
    assert "Closure trigger:" in membership_tm["TARGET_action"]
    assert "no run/result artifact" in membership_tm["experiment_artifacts_and_digests"]
    for source_ref in (
        *membership_tm["protocol_paths_and_blobs"].split(";"),
        membership_tm["implementation_path_and_blob"],
        membership_tm["source_test_path_and_blob"].split(" ", maxsplit=1)[0],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    membership_tm_alias = next(
        row
        for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.agency-acquisition-reuse-closure-membership-tm"
    )
    assert membership_tm_alias["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#131" in membership_tm_alias["basis"]
    assert "manifest-specific alias" in membership_tm_alias["resolution_method"]
    agency_closure = by_id.pop("learning.agency-acquisition-reuse-closure")
    assert agency_closure["study_protocol_disposition"] == "DEFER"
    assert agency_closure["source_implementation_TARGET_disposition"] == "DEFER"
    assert "92e26a2181b1cc99fa8f16f51fad67b1b931fb8c" in agency_closure["protocol_paths_and_blobs"]
    assert "8ba1043e5784c2e97df2dfc515617cc4f0b0277f" in agency_closure["protocol_paths_and_blobs"]
    assert "biopeia/lab#132" in agency_closure["owner_basis"]
    assert "Closure trigger:" in agency_closure["TARGET_action"]
    assert "no run/result artifact" in agency_closure["experiment_artifacts_and_digests"]
    for source_ref in (
        *agency_closure["protocol_paths_and_blobs"].split(";"),
        agency_closure["implementation_path_and_blob"],
        agency_closure["source_test_path_and_blob"].split(" ", maxsplit=1)[0],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    agency_closure_alias = next(
        row
        for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.agency-acquisition-reuse-closure"
    )
    assert agency_closure_alias["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#132" in agency_closure_alias["basis"]
    assert "nine distinct manifests" in agency_closure_alias["basis"]
    # FP-1 is a family-level row plus individually owner-dispositioned arms.
    for arm, issue, manifest_blob in (
        ("m", 156, "f9b76e34c13fc660f63dd1216191a50892e8743f"),
        ("r", 157, "22112aeb27c58f48b44775265f9481cf4c18a5a5"),
        ("t", 158, "3a04f0acc9cf0fdd9385c190872c8abe2098979d"),
        ("tm", 159, "c846f15b49e2cf055bfa01eb5c29af3d19533915"),
    ):
        unit_id = f"learning.footprint-precision-fp1-{arm}"
        unit = by_id.pop(unit_id)
        assert unit["study_protocol_disposition"] == "DEFER"
        assert unit["source_implementation_TARGET_disposition"] == "DEFER"
        assert manifest_blob in unit["protocol_paths_and_blobs"]
        assert f"biopeia/lab#{issue}" in unit["owner_basis"]
        assert "Closure trigger:" in unit["TARGET_action"]
        assert "no execution/result artifact" in unit["experiment_artifacts_and_digests"]
        for source_ref in (
            *unit["protocol_paths_and_blobs"].split(";"),
            unit["implementation_path_and_blob"],
            unit["source_test_path_and_blob"],
        ):
            path, expected_blob = source_ref.split("@", maxsplit=1)
            assert source[path]["source_blob_at_pinned_commit"] == expected_blob
        alias = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == unit_id)
        assert alias["candidate_disposition"] == "DEFER"
        assert f"biopeia/lab#{issue}" in alias["resolution_method"]
        assert "manifest-specific alias" in alias["resolution_method"]

    footprint_fp0 = by_id.pop("learning.footprint-precision-fp0")
    assert footprint_fp0["study_protocol_disposition"] == "DEFER"
    assert footprint_fp0["source_implementation_TARGET_disposition"] == "DEFER"
    assert "711727e5dc63bfb45a62828a77db3bb88862c64f" in footprint_fp0["protocol_paths_and_blobs"]
    assert "90f2cb64b9c442d79475251f62eef1f623edb2c5" in footprint_fp0["protocol_paths_and_blobs"]
    assert "biopeia/lab#166" in footprint_fp0["owner_basis"]
    assert "Closure trigger:" in footprint_fp0["TARGET_action"]
    assert "no execution/result artifact" in footprint_fp0["experiment_artifacts_and_digests"]
    footprint_alias = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == "learning.footprint-precision-fp0")
    assert footprint_alias["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#166" in footprint_alias["resolution_method"]
    assert "manifest-specific alias" in footprint_alias["resolution_method"]

    generative_gates = by_id.pop("learning.generative-cognition-consolidation-gates")
    assert generative_gates["study_protocol_disposition"] == "DEFER"
    assert generative_gates["source_implementation_TARGET_disposition"] == "DEFER"
    assert "98d5e49d108a6b0eba2c3f1db8eb69e6d96768ef" in generative_gates["protocol_paths_and_blobs"]
    assert "a48ca568a1b03a5339f4eb774c73a50058ce1514" in generative_gates["protocol_paths_and_blobs"]
    assert "biopeia/lab#167" in generative_gates["owner_basis"]
    assert "Closure trigger:" in generative_gates["TARGET_action"]
    assert "no execution/result artifact" in generative_gates["experiment_artifacts_and_digests"]
    for source_ref in (
        *generative_gates["protocol_paths_and_blobs"].split(";"),
        generative_gates["implementation_path_and_blob"],
        generative_gates["source_test_path_and_blob"].split(" ", maxsplit=1)[0],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    generative_alias = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == "learning.generative-cognition-consolidation-gates")
    assert generative_alias["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#167" in generative_alias["resolution_method"]
    assert "biopeia/lab#167" in generative_alias["basis"]
    fp2_bh = by_id.pop("learning.footprint-precision-fp2-bh")
    assert fp2_bh["study_protocol_disposition"] == "DEFER"
    assert fp2_bh["source_implementation_TARGET_disposition"] == "DEFER"
    assert "b46ff4d09033862aa8309d3f49e23fc785270111" in fp2_bh["protocol_paths_and_blobs"]
    assert "biopeia/lab#160" in fp2_bh["owner_basis"]
    assert "no execution/result artifact" in fp2_bh["experiment_artifacts_and_digests"]
    for source_ref in (*fp2_bh["protocol_paths_and_blobs"].split(";"), fp2_bh["implementation_path_and_blob"], fp2_bh["source_test_path_and_blob"]):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    fp2_bh_alias = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == "learning.footprint-precision-fp2-bh")
    assert fp2_bh_alias["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#160" in fp2_bh_alias["resolution_method"]
    assert "manifest-specific alias" in fp2_bh_alias["resolution_method"]
    assert len(units) == 92
    fp2_m = by_id.pop("learning.footprint-precision-fp2-m")
    assert fp2_m["study_protocol_disposition"] == "DEFER"
    assert fp2_m["source_implementation_TARGET_disposition"] == "DEFER"
    assert "6f1c75f4b79df440db86a45c2f6bd7cbcc6f7637" in fp2_m["protocol_paths_and_blobs"]
    assert "biopeia/lab#161" in fp2_m["owner_basis"]
    assert "no execution/result artifact" in fp2_m["experiment_artifacts_and_digests"]
    for source_ref in (*fp2_m["protocol_paths_and_blobs"].split(";"), fp2_m["implementation_path_and_blob"], fp2_m["source_test_path_and_blob"]):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    fp2_m_alias = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == "learning.footprint-precision-fp2-m")
    assert fp2_m_alias["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#161" in fp2_m_alias["resolution_method"]
    assert "manifest-specific alias" in fp2_m_alias["resolution_method"]
    assert len(units) == 92
    fp2_r = by_id.pop("learning.footprint-precision-fp2-r")
    assert fp2_r["study_protocol_disposition"] == "DEFER"
    assert fp2_r["source_implementation_TARGET_disposition"] == "DEFER"
    assert "0ae00533489a8ef3c5f347b7b5829fcb89cc5b8b" in fp2_r["protocol_paths_and_blobs"]
    assert "biopeia/lab#162" in fp2_r["owner_basis"]
    assert "no execution/result artifact" in fp2_r["experiment_artifacts_and_digests"]
    for source_ref in (
        *fp2_r["protocol_paths_and_blobs"].split(";"),
        fp2_r["implementation_path_and_blob"],
        fp2_r["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    fp2_r_alias = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.footprint-precision-fp2-r"
    )
    assert fp2_r_alias["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#162" in fp2_r_alias["resolution_method"]
    assert "manifest-specific alias" in fp2_r_alias["resolution_method"]
    assert len(units) == 92
    fp3_bh = by_id.pop("learning.footprint-precision-fp3-bh")
    assert fp3_bh["study_protocol_disposition"] == "DEFER"
    assert fp3_bh["source_implementation_TARGET_disposition"] == "DEFER"
    assert "b80a5108ba8aabced1ad9fc478dd40c3d85c3ae1" in fp3_bh["protocol_paths_and_blobs"]
    assert "biopeia/lab#163" in fp3_bh["owner_basis"]
    assert "no execution/result artifact" in fp3_bh["experiment_artifacts_and_digests"]
    for source_ref in (
        *fp3_bh["protocol_paths_and_blobs"].split(";"),
        fp3_bh["implementation_path_and_blob"],
        fp3_bh["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    fp3_bh_alias = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.footprint-precision-fp3-bh"
    )
    assert fp3_bh_alias["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#163" in fp3_bh_alias["resolution_method"]
    assert "manifest-specific alias" in fp3_bh_alias["resolution_method"]
    assert len(units) == 92

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

    intentional_causal = by_id.pop("learning.agency-intentional-causal-advantage")
    assert intentional_causal["study_protocol_disposition"] == "DEFER"
    assert intentional_causal["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#138" in intentional_causal["owner_basis"]
    assert "Closure trigger:" in intentional_causal["TARGET_action"]
    assert "No run/result artifact" in intentional_causal["experiment_artifacts_and_digests"]
    assert "No claim of scientific validity" in intentional_causal["limitations_and_nonclaims"]
    for source_ref in (
        *intentional_causal["protocol_paths_and_blobs"].split(";"),
        intentional_causal["implementation_path_and_blob"],
        intentional_causal["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    intentional_crosswalk = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.agency-intentional-causal-advantage"
    )
    assert intentional_crosswalk["candidate_disposition"] == "DEFER"
    assert "Lab #138" in intentional_crosswalk["basis"]

    autonomous = by_id.pop("learning.autonomous-cultural-agency")
    assert autonomous["study_protocol_disposition"] == "DEFER"
    assert autonomous["source_implementation_TARGET_disposition"] == "DROP"
    assert "biopeia/lab#139" in autonomous["owner_basis"]
    assert "audit-reported" in autonomous["source_evidence_basis"]
    assert "No explicit run ID" in autonomous["real_run_identity"]
    assert "NOT_ADMITTED" in autonomous["custody_ledger_state"]
    for source_ref in (
        *autonomous["protocol_paths_and_blobs"].split(";"),
        autonomous["implementation_path_and_blob"],
        autonomous["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    autonomous_crosswalk = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.autonomous-cultural-agency"
    )
    assert autonomous_crosswalk["candidate_disposition"] == "DEFER"
    assert "Lab #139" in autonomous_crosswalk["basis"]

    replay_stopping = by_id.pop("learning.autonomous-replay-stopping")
    assert replay_stopping["study_protocol_disposition"] == "DEFER"
    assert replay_stopping["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#140" in replay_stopping["owner_basis"]
    assert "no result/run artifact" in replay_stopping["experiment_artifacts_and_digests"]
    assert "NOT_ESTABLISHED" in replay_stopping["real_run_identity"]
    assert "NOT_ADMITTED" in replay_stopping["custody_ledger_state"]
    for source_ref in (
        *replay_stopping["protocol_paths_and_blobs"].split(";"),
        replay_stopping["implementation_path_and_blob"],
        replay_stopping["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    replay_crosswalk = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.autonomous-replay-stopping"
    )
    assert replay_crosswalk["candidate_disposition"] == "DEFER"
    assert "Lab #140" in replay_crosswalk["basis"]

    binding_hist = by_id.pop("learning.binding-degradation-hist")
    assert binding_hist["study_protocol_disposition"] == "DEFER"
    assert binding_hist["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#141" in binding_hist["owner_basis"]
    assert "0/79" in binding_hist["source_evidence_basis"]
    assert "not implemented" in binding_hist["source_evidence_basis"]
    assert "NOT_ADMITTED" in binding_hist["custody_ledger_state"]
    for source_ref in (
        *binding_hist["protocol_paths_and_blobs"].split(";"),
        binding_hist["implementation_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    hist_crosswalk = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.binding-degradation-hist"
    )
    assert hist_crosswalk["candidate_disposition"] == "DEFER"
    assert "Lab #141" in hist_crosswalk["basis"]
    grouped_binding = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.binding-degradation"
    )
    assert "distinct HIST and OFF arm manifests" in grouped_binding["basis"]

    binding_off = by_id.pop("learning.binding-degradation-off")
    assert binding_off["study_protocol_disposition"] == "DEFER"
    assert "biopeia/lab#142" in binding_off["owner_basis"]
    assert "0/197" in binding_off["source_evidence_basis"]
    assert "true detections 0/79 is not applicable" in binding_off["source_evidence_basis"]
    assert "NOT_ADMITTED" in binding_off["custody_ledger_state"]
    off_crosswalk = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.binding-degradation-off"
    )
    assert off_crosswalk["candidate_disposition"] == "DEFER"
    assert "Lab #142" in off_crosswalk["basis"]

    adaptation = by_id.pop("learning.canonical-sensorimotor-adaptation")
    assert adaptation["study_protocol_disposition"] == "DEFER"
    assert "biopeia/lab#143" in adaptation["owner_basis"]
    assert "validated=true" in adaptation["source_evidence_basis"]
    assert "NOT_ADMITTED" in adaptation["custody_ledger_state"]
    adaptation_crosswalk = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.canonical-sensorimotor-adaptation"
    )
    assert adaptation_crosswalk["candidate_disposition"] == "DEFER"
    assert "Lab #143" in adaptation_crosswalk["basis"]

    agency = by_id.pop("learning.canonical-sensorimotor-agency")
    assert agency["study_protocol_disposition"] == "DEFER"
    assert "biopeia/lab#144" in agency["owner_basis"]
    assert "3/3 trials" in agency["source_evidence_basis"]
    assert "NOT_ADMITTED" in agency["custody_ledger_state"]
    assert "DEFER" in agency["custody_ledger_state"]
    agency_crosswalk = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.canonical-sensorimotor-agency"
    )
    assert agency_crosswalk["candidate_disposition"] == "DEFER"
    assert "Lab #144" in agency_crosswalk["basis"]

    counterfactual = by_id.pop("learning.canonical-sensorimotor-counterfactual")
    assert counterfactual["study_protocol_disposition"] == "DEFER"
    assert "biopeia/lab#145" in counterfactual["owner_basis"]
    assert "3/3 trials" in counterfactual["source_evidence_basis"]
    assert "NOT_ADMITTED" in counterfactual["custody_ledger_state"]
    counterfactual_crosswalk = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.canonical-sensorimotor-counterfactual"
    )
    assert counterfactual_crosswalk["candidate_disposition"] == "DEFER"
    assert "Lab #145" in counterfactual_crosswalk["basis"]

    ecology = by_id.pop("learning.cognitive-ecology-embodiment")
    assert ecology["study_protocol_disposition"] == "DEFER"
    assert "biopeia/lab#146" in ecology["owner_basis"]
    assert "WORKING_ARTIFACT" in ecology["source_evidence_basis"]
    assert "NOT_ADMITTED" in ecology["custody_ledger_state"]
    ecology_crosswalk = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.cognitive-ecology-embodiment"
    )
    assert ecology_crosswalk["candidate_disposition"] == "DEFER"
    assert "Lab #146" in ecology_crosswalk["basis"]

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

    emergent_grounding = by_id.pop("learning.emergent-symbol-grounding")
    assert emergent_grounding["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert emergent_grounding["source_implementation_TARGET_disposition"] == "DROP"
    assert "biopeia/lab#154" in emergent_grounding["owner_basis"]
    assert "archival/unverified and not admitted" in emergent_grounding["owner_basis"]
    assert "a880b008470a8823447b3b7177b8315310f8c3467bb125fbe9ff9ecb67577e3f" in emergent_grounding["experiment_artifacts_and_digests"]
    assert "no run_id" in emergent_grounding["real_run_identity"]
    grounding_crosswalk = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.emergent-symbol-grounding"
    )
    assert grounding_crosswalk["candidate_disposition"] == "HISTORICAL_PROTOCOL"
    assert "biopeia/lab#154" in grounding_crosswalk["basis"]

    internal_learning_progress = by_id.pop("learning.internal-learning-progress")
    assert internal_learning_progress["study_protocol_disposition"] == "DEFER"
    assert internal_learning_progress["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#177" in internal_learning_progress["owner_basis"]
    assert "NOT_ESTABLISHED" in internal_learning_progress["real_run_identity"]
    internal_crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == "learning.internal-learning-progress")
    assert internal_crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#177" in internal_crosswalk["basis"]

    independent_grounding = by_id.pop("learning.independent-symbol-grounding")
    assert independent_grounding["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert independent_grounding["source_implementation_TARGET_disposition"] == "DROP"
    assert "biopeia/lab#176" in independent_grounding["owner_basis"]
    assert "non-admission" in independent_grounding["owner_basis"]
    assert "5f4a6600d943cc92bed0e499b63ef1ed6c883037c45fee84846fa4ab474ac14d" in independent_grounding["experiment_artifacts_and_digests"]
    assert "no run_id" in independent_grounding["real_run_identity"]
    independent_crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == "learning.independent-symbol-grounding")
    assert independent_crosswalk["candidate_disposition"] == "HISTORICAL_PROTOCOL"
    assert "biopeia/lab#176" in independent_crosswalk["basis"]

    predictive_discovery = by_id.pop("learning.predictive-discovery")
    assert predictive_discovery["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert predictive_discovery["source_implementation_TARGET_disposition"] == "DROP"
    assert "biopeia/lab#178" in predictive_discovery["owner_basis"]
    assert "comment #6223818659" in predictive_discovery["owner_basis"]
    assert "all_gates_pass=true" in predictive_discovery["source_evidence_basis"]
    assert "fa127d703b3fea5f3b0c31095076c22d3488467d" in predictive_discovery["experiment_artifacts_and_digests"]
    assert "NOT_ESTABLISHED" in predictive_discovery["real_run_identity"]
    assert "not evidence-admitted" in predictive_discovery["limitations_and_nonclaims"]
    predictive_crosswalk = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.predictive-discovery"
    )
    assert predictive_crosswalk["candidate_disposition"] == "HISTORICAL_PROTOCOL"
    assert "biopeia/lab#178" in predictive_crosswalk["basis"]
    assert "comment #6223818659" in predictive_crosswalk["basis"]
    assert "not autonomously wired to an input edge" in predictive_crosswalk["basis"]

    predictive_utility_ablation = by_id.pop("learning.predictive-utility")
    assert predictive_utility_ablation["study_protocol_disposition"] == "DEFER"
    assert predictive_utility_ablation["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#179" in predictive_utility_ablation["owner_basis"]
    assert "comment #6223821954" in predictive_utility_ablation["owner_basis"]
    assert "NOT_ESTABLISHED" in predictive_utility_ablation["real_run_identity"]
    assert "no run/results artifact" in predictive_utility_ablation["experiment_artifacts_and_digests"]
    predictive_utility_crosswalk = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.predictive-utility"
    )
    assert predictive_utility_crosswalk["candidate_disposition"] == "DEFER"
    assert "comment #6223821954" in predictive_utility_crosswalk["basis"]
    assert "no run/results artifact" in predictive_utility_crosswalk["basis"]

    episodic_utility = by_id.pop("learning.episodic-memory-utility")
    assert episodic_utility["study_protocol_disposition"] == "DEFER"
    assert episodic_utility["source_implementation_TARGET_disposition"] == "DROP"
    assert "biopeia/lab#155" in episodic_utility["owner_basis"]
    assert "no execution/result artifact" in episodic_utility["experiment_artifacts_and_digests"].lower()
    assert "current TARGET relevance remains unconfirmed" in episodic_utility["owner_basis"]
    episodic_crosswalk = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.episodic-memory-utility"
    )
    assert episodic_crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#155" in episodic_crosswalk["basis"]

    fp3_r = by_id.pop("learning.footprint-precision-fp3-r")
    assert fp3_r["study_protocol_disposition"] == "DEFER"
    assert fp3_r["source_implementation_TARGET_disposition"] == "DEFER"
    assert "c322486873ce1f63b6ccd4aebea9eb66a609c2d1" in fp3_r["protocol_paths_and_blobs"]
    assert "biopeia/lab#165" in fp3_r["owner_basis"]
    assert "no execution/result artifact" in fp3_r["experiment_artifacts_and_digests"]
    for source_ref in (
        *fp3_r["protocol_paths_and_blobs"].split(";"),
        fp3_r["implementation_path_and_blob"],
        fp3_r["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    fp3_r_alias = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.footprint-precision-fp3-r"
    )
    assert fp3_r_alias["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#165" in fp3_r_alias["resolution_method"]
    assert "manifest-specific alias" in fp3_r_alias["resolution_method"]


    fp3_bhb = by_id.pop("learning.footprint-precision-fp3-bhb")
    assert fp3_bhb["study_protocol_disposition"] == "DEFER"
    assert fp3_bhb["source_implementation_TARGET_disposition"] == "DEFER"
    assert "58a0c36629995e3bd7fbe93e81b966c2b90d90d3" in fp3_bhb["protocol_paths_and_blobs"]
    assert "biopeia/lab#164" in fp3_bhb["owner_basis"]
    assert "no execution/result artifact" in fp3_bhb["experiment_artifacts_and_digests"]
    for source_ref in (
        *fp3_bhb["protocol_paths_and_blobs"].split(";"),
        fp3_bhb["implementation_path_and_blob"],
        fp3_bhb["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    fp3_bhb_alias = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.footprint-precision-fp3-bhb"
    )
    assert fp3_bhb_alias["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#164" in fp3_bhb_alias["resolution_method"]
    assert "manifest-specific alias" in fp3_bhb_alias["resolution_method"]

    cognitive_graph = by_id.pop("learning.cognitive-graph-causal-composition")
    assert cognitive_graph["study_protocol_disposition"] == "DEFER"
    assert cognitive_graph["source_implementation_TARGET_disposition"] == "DEFER"

    temporal_controls = by_id.pop("learning.continuous-temporal-controls")
    assert temporal_controls["study_protocol_disposition"] == "DEFER"
    assert temporal_controls["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#149" in temporal_controls["owner_basis"]
    assert "NOT_ESTABLISHED" in temporal_controls["real_run_identity"]
    for source_ref in (
        *temporal_controls["protocol_paths_and_blobs"].split(";"),
        temporal_controls["implementation_path_and_blob"],
        temporal_controls["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob

    cultural_foundation = by_id.pop("learning.cultural-foundation")
    assert cultural_foundation["study_protocol_disposition"] == "DEFER"
    assert cultural_foundation["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#150" in cultural_foundation["owner_basis"]
    assert "NOT_ESTABLISHED" in cultural_foundation["real_run_identity"]
    for source_ref in (
        *cultural_foundation["protocol_paths_and_blobs"].split(";"),
        cultural_foundation["implementation_path_and_blob"],
        cultural_foundation["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob

    cumulative_culture = by_id.pop("learning.cumulative-culture")
    assert cumulative_culture["study_protocol_disposition"] == "DEFER"
    assert cumulative_culture["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#151" in cumulative_culture["owner_basis"]
    assert "NOT_ESTABLISHED" in cumulative_culture["real_run_identity"]
    for source_ref in (
        *cumulative_culture["protocol_paths_and_blobs"].split(";"),
        cumulative_culture["implementation_path_and_blob"],
        cumulative_culture["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob

    emergent_communication = by_id.pop("learning.emergent-structured-communication")
    assert emergent_communication["study_protocol_disposition"] == "DEFER"
    assert emergent_communication["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#153" in emergent_communication["owner_basis"]
    assert "NOT_IDENTIFIED" in emergent_communication["real_run_identity"]
    assert "all_gates_pass" in emergent_communication["source_evidence_basis"]
    assert "esc6_productive_generalization" in emergent_communication["source_evidence_basis"]
    for source_ref in (
        *emergent_communication["protocol_paths_and_blobs"].split(";"),
        emergent_communication["implementation_path_and_blob"],
        emergent_communication["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob

    embodied_ablation = by_id.pop("learning.embodied-behavioral-ablation")
    assert embodied_ablation["study_protocol_disposition"] == "DEFER"
    assert embodied_ablation["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#152" in embodied_ablation["owner_basis"]
    assert "NOT_ADMITTED" in embodied_ablation["custody_ledger_state"]
    assert "zero causally testable" in embodied_ablation["source_evidence_basis"]
    counterfactual_utility = by_id.pop(
        "learning.generative-cognition-counterfactual-utility"
    )
    assert counterfactual_utility["study_protocol_disposition"] == "DEFER"
    assert counterfactual_utility["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#168" in counterfactual_utility["owner_basis"]
    assert "NOT_ESTABLISHED" in counterfactual_utility["real_run_identity"]
    depth_calibration = by_id.pop("learning.generative-cognition-depth-calibration")
    assert depth_calibration["study_protocol_disposition"] == "DEFER"
    assert depth_calibration["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#169" in depth_calibration["owner_basis"]
    assert "NOT_ESTABLISHED" in depth_calibration["real_run_identity"]
    model_correction = by_id.pop("learning.generative-cognition-model-correction")
    planning_utility = by_id.pop("learning.generative-cognition-planning-utility")
    predictive_utility = by_id.pop("learning.generative-cognition-predictive-utility")
    recombination_construction = by_id.pop("learning.generative-cognition-recombination-construction")
    release_gates = by_id.pop("learning.generative-cognition-release-gates")
    replay_utility = by_id.pop("learning.generative-cognition-replay-utility")
    assert replay_utility["study_protocol_disposition"] == "DEFER"
    assert replay_utility["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#175" in replay_utility["owner_basis"]
    assert "NOT_ESTABLISHED" in replay_utility["real_run_identity"]
    assert release_gates["study_protocol_disposition"] == "DEFER"
    assert release_gates["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#174" in release_gates["owner_basis"]
    assert "NOT_ESTABLISHED" in release_gates["real_run_identity"]
    assert recombination_construction["study_protocol_disposition"] == "DEFER"
    assert recombination_construction["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#173" in recombination_construction["owner_basis"]
    assert "NOT_ESTABLISHED" in recombination_construction["real_run_identity"]
    assert predictive_utility["study_protocol_disposition"] == "DEFER"
    assert predictive_utility["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#172" in predictive_utility["owner_basis"]
    assert "NOT_ESTABLISHED" in predictive_utility["real_run_identity"]
    assert planning_utility["study_protocol_disposition"] == "DEFER"
    assert planning_utility["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#171" in planning_utility["owner_basis"]
    assert "NOT_ESTABLISHED" in planning_utility["real_run_identity"]
    assert model_correction["study_protocol_disposition"] == "DEFER"
    assert model_correction["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#170" in model_correction["owner_basis"]
    regime_symmetric = by_id.pop("learning.private-model-regime-symmetric")
    assert regime_symmetric["study_protocol_disposition"] == "DEFER"
    assert regime_symmetric["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#183" in regime_symmetric["owner_basis"]
    assert "NOT_ESTABLISHED" in regime_symmetric["real_run_identity"]
    assert "test_private_model_regime_shift_protocol.py@7afb947c044b8141981c8430d974ac6c6bb483c3" in regime_symmetric["source_test_path_and_blob"]
    assert "do not measure outcomes" in regime_symmetric["limitations_and_nonclaims"]
    regime_crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == "learning.private-model-regime-symmetric")
    assert regime_crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#183" in regime_crosswalk["basis"]
    private_learnability = by_id.pop("learning.private-model-learnability")
    assert private_learnability["study_protocol_disposition"] == "DEFER"
    assert private_learnability["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#182" in private_learnability["owner_basis"]
    assert "NOT_ESTABLISHED" in private_learnability["real_run_identity"]
    assert "test_private_model_learnability.py@9100fba97e542ac381ff53a83a66dd4a284e7b6d" in private_learnability["source_test_path_and_blob"]
    assert "not outcome evidence" in private_learnability["source_evidence_basis"]
    learnability_crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == "learning.private-model-learnability")
    assert learnability_crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#182" in learnability_crosswalk["basis"]
    assert learnability_crosswalk["study_test_path_candidates"] == "lab/tests/integration/test_private_model_learnability.py"
    assert "not outcome evidence" in learnability_crosswalk["basis"]
    private_controls = by_id.pop("learning.private-model-controls")
    assert private_controls["study_protocol_disposition"] == "DEFER"
    assert private_controls["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#181" in private_controls["owner_basis"]
    assert "NOT_ESTABLISHED" in private_controls["real_run_identity"]
    controls_crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == "learning.private-model-controls")
    assert controls_crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#181" in controls_crosswalk["basis"]
    private_adaptation = by_id.pop("learning.private-model-adaptation")
    assert private_adaptation["study_protocol_disposition"] == "DEFER"
    assert private_adaptation["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#180" in private_adaptation["owner_basis"]
    assert "NOT_ESTABLISHED" in private_adaptation["real_run_identity"]
    private_crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == "learning.private-model-adaptation")
    assert private_crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#180" in private_crosswalk["basis"]
    private_utility = by_id.pop("learning.private-model-utility")
    assert private_utility["study_protocol_disposition"] == "DEFER"
    assert private_utility["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#184" in private_utility["owner_basis"]
    assert "NOT_ESTABLISHED" in private_utility["real_run_identity"]
    assert "mocked model-family results" in private_utility["source_evidence_basis"]
    utility_crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == "learning.private-model-utility")
    assert utility_crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#184" in utility_crosswalk["basis"]
    assert "mocked model-family results" in utility_crosswalk["basis"]
    adaptive_delta = by_id.pop("perception.adaptive-delta-discovery")
    assert adaptive_delta["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert adaptive_delta["source_implementation_TARGET_disposition"] == "DEFER"
    assert "shared sensory_specialisation.py module" in adaptive_delta["TARGET_action"]
    replay_efficiency = by_id.pop("learning.replay-efficiency")
    assert replay_efficiency["study_protocol_disposition"] == "DEFER"
    assert "biopeia/lab#185" in replay_efficiency["owner_basis"]
    replay_pressure = by_id.pop("learning.replay-pressure-curve")
    assert replay_pressure["study_protocol_disposition"] == "DEFER"
    assert "biopeia/lab#186" in replay_pressure["owner_basis"]
    fairness = by_id.pop("learning.structural-producer-fairness")
    assert fairness["study_protocol_disposition"] == "DEFER"
    assert fairness["source_implementation_TARGET_disposition"] == "DROP"
    assert "biopeia/lab#187" in fairness["owner_basis"]
    structured = by_id.pop("learning.structured-causal-experience")
    assert structured["study_protocol_disposition"] == "DEFER"
    assert "biopeia/lab#188" in structured["owner_basis"]
    generalization = by_id.pop("learning.structured-causal-generalization")
    assert generalization["study_protocol_disposition"] == "DEFER"
    assert "biopeia/lab#189" in generalization["owner_basis"]
    temporal_controls = by_id.pop("learning.temporal-private-model-controls")
    assert temporal_controls["study_protocol_disposition"] == "DEFER"
    assert temporal_controls["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#191" in temporal_controls["owner_basis"]
    assert "no result/run artifact" in temporal_controls["experiment_artifacts_and_digests"]
    assert "No experiment" in temporal_controls["limitations_and_nonclaims"]
    for source_ref in (
        *temporal_controls["protocol_paths_and_blobs"].split(";"),
        temporal_controls["implementation_path_and_blob"],
        temporal_controls["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    temporal_crosswalk = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.temporal-private-model-controls"
    )
    assert temporal_crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#191" in temporal_crosswalk["basis"]

    visual_dev = by_id.pop("learning.visual-acquisition-v1-d1-v2-development")
    assert visual_dev["study_protocol_disposition"] == "DEFER"
    assert visual_dev["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#192" in visual_dev["owner_basis"]
    assert "no run/results artifact" in visual_dev["experiment_artifacts_and_digests"]
    assert "not be described as learning" in visual_dev["source_evidence_basis"]
    for source_ref in (
        *visual_dev["protocol_paths_and_blobs"].split(";"),
        visual_dev["implementation_path_and_blob"],
        visual_dev["source_test_path_and_blob"].split(" (")[0],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    visual_dev_alias = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.visual-acquisition-v1-d1-v2-development"
    )
    assert visual_dev_alias["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#192" in visual_dev_alias["basis"]

    visual_d1 = by_id.pop("learning.visual-acquisition-v1-development")
    assert visual_d1["study_protocol_disposition"] == "DEFER"
    assert visual_d1["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#193" in visual_d1["owner_basis"]
    assert "no run/results artifact" in visual_d1["experiment_artifacts_and_digests"]
    assert "no hypothesis test" in visual_d1["source_evidence_basis"]
    for source_ref in (
        *visual_d1["protocol_paths_and_blobs"].split(";"),
        visual_d1["implementation_path_and_blob"],
        visual_d1["source_test_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    visual_d1_alias = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "learning.visual-acquisition-v1-development"
    )
    assert visual_d1_alias["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#193" in visual_d1_alias["basis"]

    population_comm = by_id.pop("observability.population-communication")
    assert population_comm["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert population_comm["source_implementation_TARGET_disposition"] == "DROP"
    assert "biopeia/lab#194" in population_comm["owner_basis"]
    assert "c2bf9cb777016bb2a70fc4327173f15fe819d608e102ca1672a0041d71689d29" in population_comm["experiment_artifacts_and_digests"]
    assert "NOT_ADMITTED" in population_comm["custody_ledger_state"]
    for source_ref in (
        *population_comm["protocol_paths_and_blobs"].split(";"),
        population_comm["implementation_path_and_blob"],
        population_comm["source_test_path_and_blob"].split(" (")[0],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    population_crosswalk = next(
        row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == "observability.population-communication"
    )
    assert population_crosswalk["candidate_disposition"] == "HISTORICAL_PROTOCOL"
    assert "biopeia/lab#194" in population_crosswalk["basis"]

    autonomous_sensory = by_id.pop("perception.autonomous-sensory-selection")
    assert autonomous_sensory["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert autonomous_sensory["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#196" in autonomous_sensory["owner_basis"]
    assert "NOT_ADMITTED" in autonomous_sensory["limitations_and_nonclaims"]
    for source_ref in (
        *autonomous_sensory["protocol_paths_and_blobs"].split(";"),
        autonomous_sensory["implementation_path_and_blob"],
        autonomous_sensory["source_test_path_and_blob"].split(" (")[0],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    sensory_crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == "perception.autonomous-sensory-selection")
    assert sensory_crosswalk["candidate_disposition"] == "HISTORICAL_PROTOCOL"
    assert "biopeia/lab#196" in sensory_crosswalk["basis"]

    experience_phenotype = by_id.pop("perception.experience-conditioned-phenotype")
    assert experience_phenotype["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert experience_phenotype["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#197" in experience_phenotype["owner_basis"]
    assert "NOT_ADMITTED" in experience_phenotype["limitations_and_nonclaims"]
    for source_ref in (
        *experience_phenotype["protocol_paths_and_blobs"].split(";"),
        experience_phenotype["implementation_path_and_blob"],
    ):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob

    identity_equivalence = by_id.pop("perception.identity-equivalence")
    assert identity_equivalence["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert identity_equivalence["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#198" in identity_equivalence["owner_basis"]
    assert "NOT_ADMITTED" in identity_equivalence["limitations_and_nonclaims"]
    for source_ref in (*identity_equivalence["protocol_paths_and_blobs"].split(";"), identity_equivalence["implementation_path_and_blob"]):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob
    identity_crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == "perception.identity-equivalence")
    assert identity_crosswalk["candidate_disposition"] == "HISTORICAL_PROTOCOL"
    assert "biopeia/lab#198" in identity_crosswalk["basis"]

    sensory_duplication = by_id.pop("perception.sensory-duplication-divergence")
    assert sensory_duplication["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert sensory_duplication["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#203" in sensory_duplication["owner_basis"]
    assert "NOT_ADMITTED" in sensory_duplication["limitations_and_nonclaims"]

    sensory_ablation = by_id.pop("perception.sensory-ablation")
    assert sensory_ablation["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert sensory_ablation["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#202" in sensory_ablation["owner_basis"]
    assert "NOT_ADMITTED" in sensory_ablation["limitations_and_nonclaims"]

    phenotype_divergence = by_id.pop("perception.same-world-phenotype-divergence")
    assert phenotype_divergence["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert phenotype_divergence["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#201" in phenotype_divergence["owner_basis"]
    assert "NOT_ADMITTED" in phenotype_divergence["limitations_and_nonclaims"]

    multisource_specialisation = by_id.pop("perception.multisource-specialisation")
    assert multisource_specialisation["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert multisource_specialisation["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#200" in multisource_specialisation["owner_basis"]
    assert "NOT_ADMITTED" in multisource_specialisation["limitations_and_nonclaims"]
    for source_ref in (*multisource_specialisation["protocol_paths_and_blobs"].split(";"), multisource_specialisation["implementation_path_and_blob"]):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob

    modality_specialisation = by_id.pop("perception.modality-specialisation")
    assert modality_specialisation["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert modality_specialisation["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#199" in modality_specialisation["owner_basis"]
    assert "NOT_ADMITTED" in modality_specialisation["limitations_and_nonclaims"]
    for source_ref in (*modality_specialisation["protocol_paths_and_blobs"].split(";"), modality_specialisation["implementation_path_and_blob"]):
        path, expected_blob = source_ref.split("@", maxsplit=1)
        assert source[path]["source_blob_at_pinned_commit"] == expected_blob

    characterization = by_id.pop("learning.structured-communication-characterization")
    assert characterization["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert "productive_generalization_observed=false" in characterization["source_evidence_basis"]
    assert "NOT_ADMITTED" in characterization["limitations_and_nonclaims"]
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
    cognitive = {row["unit_id"]: row for row in units}["learning.cognitive-graph-causal-composition"]
    assert cognitive["study_protocol_disposition"] == "DEFER"
    assert cognitive["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#147" in cognitive["owner_basis"]
    assert "Closure trigger:" in cognitive["TARGET_action"]
    assert "NOT_ESTABLISHED" in cognitive["real_run_identity"]
    assert "not independently reproduced" in cognitive["source_evidence_basis"]
    cognitive_alias = {row["protocol_id"]: row for row in crosswalk}["learning.cognitive-graph-causal-composition"]
    assert cognitive_alias["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#147" in cognitive_alias["resolution_method"]
    assert "manifest-specific alias" in cognitive_alias["resolution_method"]
    somatic_protocol = crosswalk_by_id["embodiment.somatic-correlation-trap"]
    assert somatic_protocol["candidate_disposition"] == "HISTORICAL_PROTOCOL"
    assert "biopeia/lab#61" in somatic_protocol["basis"]
    assert "does not claim scientific validity" in somatic_protocol["basis"]
    for unit in units:
        protocol = crosswalk_by_id[unit["unit_id"]]
        assert protocol["candidate_disposition"] == unit["study_protocol_disposition"]


def test_generative_counterfactual_utility_has_exact_manifest_defer() -> None:
    unit_id = "learning.generative-cognition-counterfactual-utility"
    disposition = next(
        row
        for row in read_tsv("study-disposition-register-80d372a.tsv")
        if row["unit_id"] == unit_id
    )
    crosswalk = next(
        row
        for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == unit_id
    )

    assert disposition["study_protocol_disposition"] == "DEFER"
    assert disposition["source_commit"] == "80d372a186513035f85a769db886e505cabba52d"
    assert "experiment.toml@c9031b6d6c65ddbbf8882b25725ae129157e8a72" in disposition[
        "protocol_paths_and_blobs"
    ]
    assert "README.md@f71438f4cb91938e64ab0417a55fb04fc3eab39f" in disposition[
        "protocol_paths_and_blobs"
    ]
    assert "no execution/result artifact" in disposition["experiment_artifacts_and_digests"]
    assert "biopeia/lab#168" in disposition["owner_basis"]
    assert "authorized current TARGET" in disposition["TARGET_action"]
    assert crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#168" in crosswalk["basis"]


def test_adaptive_delta_discovery_is_historical_protocol_only() -> None:
    units = read_tsv("study-disposition-register-80d372a.tsv")
    unit = next(row for row in units if row["unit_id"] == "perception.adaptive-delta-discovery")
    assert unit["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert unit["source_commit"] == "80d372a186513035f85a769db886e505cabba52d"
    assert "b652d66049708aaf39560ca4352d553887f5ec78" in unit["protocol_paths_and_blobs"]
    assert "df9f0738658a7f09388f234641a10c6a3257a579" in unit["experiment_artifacts_and_digests"]
    assert "biopeia/lab#195" in unit["owner_basis"]
    assert unit["source_implementation_TARGET_disposition"] == "DEFER"
    assert "NOT_ADMITTED" in unit["custody_ledger_state"]


def test_generative_depth_calibration_has_exact_manifest_defer() -> None:
    unit_id = "learning.generative-cognition-depth-calibration"
    disposition = next(
        row
        for row in read_tsv("study-disposition-register-80d372a.tsv")
        if row["unit_id"] == unit_id
    )
    crosswalk = next(
        row
        for row in read_tsv("study-protocol-crosswalk-80d372a.tsv")
        if row["protocol_id"] == unit_id
    )

    assert disposition["study_protocol_disposition"] == "DEFER"
    assert disposition["source_commit"] == "80d372a186513035f85a769db886e505cabba52d"
    assert "experiment.toml@4494f110256173e860313180ee58de4b15cbce17" in disposition[
        "protocol_paths_and_blobs"
    ]
    assert "README.md@cacec9d7ac80cd540e8ee73f461f66ea836d686a" in disposition[
        "protocol_paths_and_blobs"
    ]
    assert "no execution/result artifact" in disposition["experiment_artifacts_and_digests"]
    assert "biopeia/lab#169" in disposition["owner_basis"]
    assert "authorized current TARGET" in disposition["TARGET_action"]
    assert crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#169" in crosswalk["basis"]


def test_generative_release_gates_has_exact_manifest_defer() -> None:
    unit_id = "learning.generative-cognition-release-gates"
    disposition = next(row for row in read_tsv("study-disposition-register-80d372a.tsv") if row["unit_id"] == unit_id)
    crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == unit_id)
    assert disposition["study_protocol_disposition"] == "DEFER"
    assert disposition["source_commit"] == "80d372a186513035f85a769db886e505cabba52d"
    assert "experiment.toml@38e47a1ad15331890bc8fbea499e76409afd75bf" in disposition["protocol_paths_and_blobs"]
    assert "README.md@eb88a494b9a7fa85d5d3ea09c78d03aacc7f88d8" in disposition["protocol_paths_and_blobs"]
    assert "no execution/result artifact" in disposition["experiment_artifacts_and_digests"]
    assert "biopeia/lab#174" in disposition["owner_basis"]
    assert crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#174" in crosswalk["basis"]


def test_generative_replay_utility_has_exact_manifest_defer() -> None:
    unit_id = "learning.generative-cognition-replay-utility"
    disposition = next(row for row in read_tsv("study-disposition-register-80d372a.tsv") if row["unit_id"] == unit_id)
    crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == unit_id)
    assert disposition["study_protocol_disposition"] == "DEFER"
    assert "experiment.toml@027a7ec141c69e40b8e777432a525f856d8ed690" in disposition["protocol_paths_and_blobs"]
    assert "README.md@5307fdafd22d9d63f5edc0c66fa6d6aedfd1a57d" in disposition["protocol_paths_and_blobs"]
    assert "no execution/result artifact" in disposition["experiment_artifacts_and_digests"]
    assert "biopeia/lab#175" in disposition["owner_basis"]
    assert crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#175" in crosswalk["basis"]


def test_generative_recombination_construction_has_exact_manifest_defer() -> None:
    unit_id = "learning.generative-cognition-recombination-construction"
    disposition = next(row for row in read_tsv("study-disposition-register-80d372a.tsv") if row["unit_id"] == unit_id)
    crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == unit_id)
    assert disposition["study_protocol_disposition"] == "DEFER"
    assert disposition["source_commit"] == "80d372a186513035f85a769db886e505cabba52d"
    assert "experiment.toml@d05364be0e32605b479bf685be2b089085bfcef1" in disposition["protocol_paths_and_blobs"]
    assert "README.md@fa3e7140120ef40b97d309486cffb535ed7eb2fe" in disposition["protocol_paths_and_blobs"]
    assert "no execution/result artifact" in disposition["experiment_artifacts_and_digests"]
    assert "biopeia/lab#173" in disposition["owner_basis"]
    assert crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#173" in crosswalk["basis"]


def test_generative_predictive_utility_has_exact_manifest_defer() -> None:
    unit_id = "learning.generative-cognition-predictive-utility"
    disposition = next(row for row in read_tsv("study-disposition-register-80d372a.tsv") if row["unit_id"] == unit_id)
    crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == unit_id)
    assert disposition["study_protocol_disposition"] == "DEFER"
    assert disposition["source_commit"] == "80d372a186513035f85a769db886e505cabba52d"
    assert "experiment.toml@ebb5affc2a9f6c828a87aa74fcc2950bd58ba1e9" in disposition["protocol_paths_and_blobs"]
    assert "README.md@70feac596a5fb971004bb3f1052e69d864bc904f" in disposition["protocol_paths_and_blobs"]
    assert "no execution/result artifact" in disposition["experiment_artifacts_and_digests"]
    assert "biopeia/lab#172" in disposition["owner_basis"]
    assert crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#172" in crosswalk["basis"]


def test_generative_planning_utility_has_exact_manifest_defer() -> None:
    unit_id = "learning.generative-cognition-planning-utility"
    disposition = next(row for row in read_tsv("study-disposition-register-80d372a.tsv") if row["unit_id"] == unit_id)
    crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == unit_id)
    assert disposition["study_protocol_disposition"] == "DEFER"
    assert disposition["source_commit"] == "80d372a186513035f85a769db886e505cabba52d"
    assert "experiment.toml@fb4ddc8dc6a7e24ca4882c36d28a8438cf7ffc05" in disposition["protocol_paths_and_blobs"]
    assert "README.md@639544aa2b6761d4b055b27bd6dd54271d8e35f7" in disposition["protocol_paths_and_blobs"]
    assert "no execution/result artifact" in disposition["experiment_artifacts_and_digests"]
    assert "biopeia/lab#171" in disposition["owner_basis"]
    assert crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#171" in crosswalk["basis"]


def test_generative_model_correction_has_exact_manifest_defer() -> None:
    unit_id = "learning.generative-cognition-model-correction"
    disposition = next(row for row in read_tsv("study-disposition-register-80d372a.tsv") if row["unit_id"] == unit_id)
    crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == unit_id)
    assert disposition["study_protocol_disposition"] == "DEFER"
    assert disposition["source_commit"] == "80d372a186513035f85a769db886e505cabba52d"
    assert "experiment.toml@88625378421a0ae53e08c7e47ab66047dd087085" in disposition["protocol_paths_and_blobs"]
    assert "README.md@e9f576683d04d8f55bfcd7494ae3d89eb9eb3b20" in disposition["protocol_paths_and_blobs"]
    assert "no result/run artifact" in disposition["experiment_artifacts_and_digests"]
    assert "biopeia/lab#170" in disposition["owner_basis"]
    assert crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#170" in crosswalk["basis"]



def test_private_model_utility_owner_defer_is_bounded() -> None:
    units = {row["unit_id"]: row for row in read_tsv("study-disposition-register-80d372a.tsv")}
    utility = units["learning.private-model-utility"]
    assert utility["study_protocol_disposition"] == "DEFER"
    assert utility["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#184" in utility["owner_basis"]
    assert "NOT_ESTABLISHED" in utility["real_run_identity"]
    assert "mocked model-family results" in utility["source_evidence_basis"]
    assert "does not establish training outcomes" in utility["limitations_and_nonclaims"]
    crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == "learning.private-model-utility")
    assert crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#184" in crosswalk["basis"]
    assert "mocked model-family results" in crosswalk["basis"]


def test_replay_efficiency_owner_defer_preserves_report_without_admission() -> None:
    units = read_tsv("study-disposition-register-80d372a.tsv")
    disposition = next(row for row in units if row["unit_id"] == "learning.replay-efficiency")
    assert disposition["study_protocol_disposition"] == "DEFER"
    assert disposition["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#185" in disposition["owner_basis"]
    assert "20260921T230526Z-learning-replay-efficiency-fd9292c-8c5b" in disposition["real_run_identity"]
    assert "fd9292c6776df0448c0336f85f09adb0253736a8" in disposition["real_run_identity"]
    assert "1/3" in disposition["source_evidence_basis"]
    assert "NOT_ADMITTED" in disposition["limitations_and_nonclaims"]
    assert "b5166649a4d0e61896d98ffbc6b023123f54f1f2" in disposition["experiment_artifacts_and_digests"]
    evidence = next(row for row in read_tsv("study-evidence-map-80d372a.tsv") if row["record_key"] == "learning.replay-efficiency")
    assert "20260921T230526Z-learning-replay-efficiency-fd9292c-8c5b" in evidence["protocol_or_run_identity_evidence"]
    assert "NOT_ADMITTED" in evidence["artifact_custody_refs"]
    crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == "learning.replay-efficiency")
    assert crosswalk["candidate_disposition"] == "DEFER"
    assert "biopeia/lab#185" in crosswalk["basis"]


def test_replay_pressure_curve_owner_defer_preserves_report_without_admission() -> None:
    units = read_tsv("study-disposition-register-80d372a.tsv")
    disposition = next(row for row in units if row["unit_id"] == "learning.replay-pressure-curve")
    assert disposition["study_protocol_disposition"] == "DEFER"
    assert disposition["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#186" in disposition["owner_basis"]
    assert "20260921T230220Z-learning-replay-pressure-curve-206a7b4-e02f" in disposition["real_run_identity"]
    assert "206a7b430817c0940029adc47aeac43e9be8c5cb" in disposition["real_run_identity"]
    assert "3/3" in disposition["source_evidence_basis"]
    assert "NOT_ADMITTED" in disposition["limitations_and_nonclaims"]
    assert "7fc7d0cf93479e4194540b1c437caeff1f6cc555" in disposition["experiment_artifacts_and_digests"]
    evidence = next(row for row in read_tsv("study-evidence-map-80d372a.tsv") if row["record_key"] == "learning.replay-pressure-curve")
    assert "20260921T230220Z-learning-replay-pressure-curve-206a7b4-e02f" in evidence["protocol_or_run_identity_evidence"]
    assert "NOT_ADMITTED" in evidence["artifact_custody_refs"]
    assert "REGISTRY_LOOKUP_AND_PROTOCOL_MECHANICS" == evidence["test_link_status"]
    assert "test_pressure_requests_keep_everything_except_replay_budget" in evidence["test_symbol_refs"]
    crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == "learning.replay-pressure-curve")
    assert crosswalk["candidate_disposition"] == "DEFER"
    assert "test_replay_pressure_curve.py" in crosswalk["study_test_path_candidates"]
    assert "biopeia/lab#186" in crosswalk["basis"]


def test_autonomous_sensory_selection_owner_historical_protocol_is_custody_only() -> None:
    unit = "perception.autonomous-sensory-selection"
    disposition = next(row for row in read_tsv("study-disposition-register-80d372a.tsv") if row["unit_id"] == unit)
    assert disposition["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert disposition["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#196" in disposition["owner_basis"]
    assert "NOT_ADMITTED" in disposition["limitations_and_nonclaims"]
    assert "73e559c8113145aa1062fd3e0e9b5692976d397be1e59d109526da7cc842c073" in disposition["experiment_artifacts_and_digests"]
    evidence = next(row for row in read_tsv("study-evidence-map-80d372a.tsv") if row["record_key"] == unit)
    assert "NOT_ADMITTED" in evidence["artifact_custody_refs"]
    assert evidence["protocol_or_run_identity_status"] == "NOT_VALIDATED_FROM_CONTENT"
    crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == unit)
    assert crosswalk["candidate_disposition"] == "HISTORICAL_PROTOCOL"
    assert "biopeia/lab#196" in crosswalk["basis"]


def test_experience_conditioned_phenotype_owner_historical_protocol_is_unadmitted() -> None:
    unit = "perception.experience-conditioned-phenotype"
    disposition = next(row for row in read_tsv("study-disposition-register-80d372a.tsv") if row["unit_id"] == unit)
    assert disposition["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert disposition["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#197" in disposition["owner_basis"]
    assert "NOT_ADMITTED" in disposition["limitations_and_nonclaims"]
    assert "integrate" in disposition["source_evidence_basis"]
    evidence = next(row for row in read_tsv("study-evidence-map-80d372a.tsv") if row["record_key"] == unit)
    assert "NOT_ADMITTED" in evidence["artifact_custody_refs"]
    assert evidence["protocol_or_run_identity_status"] == "NOT_ESTABLISHED"
    crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == unit)
    assert crosswalk["candidate_disposition"] == "HISTORICAL_PROTOCOL"
    assert "biopeia/lab#197" in crosswalk["basis"]

def test_identity_equivalence_owner_preserves_unresolved_artifact_discrepancy() -> None:
    unit = "perception.identity-equivalence"
    disposition = next(row for row in read_tsv("study-disposition-register-80d372a.tsv") if row["unit_id"] == unit)
    assert disposition["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert disposition["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#198" in disposition["owner_basis"]
    assert "NOT_ADMITTED" in disposition["limitations_and_nonclaims"]
    assert "contradiction" in disposition["source_evidence_basis"]
    evidence = next(row for row in read_tsv("study-evidence-map-80d372a.tsv") if row["record_key"] == unit)
    assert "NOT_ADMITTED" in evidence["artifact_custody_refs"]
    assert "discrepancy" in evidence["protocol_or_run_identity_evidence"]
    crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == unit)
    assert crosswalk["candidate_disposition"] == "HISTORICAL_PROTOCOL"
    assert "biopeia/lab#198" in crosswalk["basis"]


def test_modality_specialisation_owner_preserves_unverified_result_custody() -> None:
    unit = "perception.modality-specialisation"
    disposition = next(row for row in read_tsv("study-disposition-register-80d372a.tsv") if row["unit_id"] == unit)
    assert disposition["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert disposition["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#199" in disposition["owner_basis"]
    assert "NOT_ADMITTED" in disposition["limitations_and_nonclaims"]
    assert "all_three_niches=true" in disposition["source_evidence_basis"]
    evidence = next(row for row in read_tsv("study-evidence-map-80d372a.tsv") if row["record_key"] == unit)
    assert "NOT_ADMITTED" in evidence["artifact_custody_refs"]
    assert evidence["protocol_or_run_identity_status"] == "NOT_ESTABLISHED"
    crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == unit)
    assert crosswalk["candidate_disposition"] == "HISTORICAL_PROTOCOL"
    assert "biopeia/lab#199" in crosswalk["basis"]


def test_multisource_specialisation_owner_preserves_limited_result_claim() -> None:
    unit = "perception.multisource-specialisation"
    disposition = next(row for row in read_tsv("study-disposition-register-80d372a.tsv") if row["unit_id"] == unit)
    assert disposition["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert disposition["source_implementation_TARGET_disposition"] == "DEFER"
    assert "biopeia/lab#200" in disposition["owner_basis"]
    assert "ties the frozen control" in disposition["source_evidence_basis"]
    assert "NOT_ADMITTED" in disposition["limitations_and_nonclaims"]
    evidence = next(row for row in read_tsv("study-evidence-map-80d372a.tsv") if row["record_key"] == unit)
    assert evidence["protocol_or_run_identity_status"] == "NOT_ESTABLISHED"
    crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == unit)
    assert crosswalk["candidate_disposition"] == "HISTORICAL_PROTOCOL"
    assert "zero gain" in crosswalk["basis"]


def test_same_world_phenotype_divergence_preserves_unverified_archive_only() -> None:
    unit = "perception.same-world-phenotype-divergence"
    disposition = next(row for row in read_tsv("study-disposition-register-80d372a.tsv") if row["unit_id"] == unit)
    assert disposition["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert "biopeia/lab#201" in disposition["owner_basis"]
    assert "NOT_ADMITTED" in disposition["limitations_and_nonclaims"]
    assert "not establish adaptive causation" in disposition["source_evidence_basis"]
    crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == unit)
    assert crosswalk["candidate_disposition"] == "HISTORICAL_PROTOCOL"


def test_sensory_ablation_result_is_archival_not_causal_evidence() -> None:
    unit = "perception.sensory-ablation"
    row = next(row for row in read_tsv("study-disposition-register-80d372a.tsv") if row["unit_id"] == unit)
    assert row["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert "causal_support=true" in row["source_evidence_basis"]
    assert "NOT_ADMITTED" in row["limitations_and_nonclaims"]
    crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == unit)
    assert crosswalk["candidate_disposition"] == "HISTORICAL_PROTOCOL"
    assert "independent reproduction" in crosswalk["basis"]


def test_sensory_duplication_divergence_is_preserved_without_evolutionary_claim() -> None:
    unit = "perception.sensory-duplication-divergence"
    row = next(row for row in read_tsv("study-disposition-register-80d372a.tsv") if row["unit_id"] == unit)
    assert row["study_protocol_disposition"] == "HISTORICAL_PROTOCOL"
    assert "two variants" in row["source_evidence_basis"]
    assert "NOT_ADMITTED" in row["limitations_and_nonclaims"]
    crosswalk = next(row for row in read_tsv("study-protocol-crosswalk-80d372a.tsv") if row["protocol_id"] == unit)
    assert crosswalk["candidate_disposition"] == "HISTORICAL_PROTOCOL"
