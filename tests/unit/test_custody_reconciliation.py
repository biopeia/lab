"""Guard the source-pinned Lab artifact custody proposal reconciliation."""

from __future__ import annotations

import csv
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


def read_tsv(name: str) -> list[dict[str, str]]:
    with (MIGRATION / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


def proposed_class(row: dict[str, str]) -> str:
    return row.get("proposed_review_class") or row.get("custody_classification", "")


def test_all_pinned_artifacts_have_one_identity_matched_proposal() -> None:
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
        assert row["proposal_review_status"] == (
            "INDEPENDENT_ADVISOR_REVIEWED_PROPOSAL; "
            "LAB_OWNER_DISPOSITION_PENDING; NOT_ADMITTED"
        )


def test_proposals_remain_separate_from_authoritative_custody_classes() -> None:
    ledger = read_tsv("scientific-custody-80d372a.tsv")
    assert Counter(row["custody_classification"] for row in ledger) == {
        "DEFER": 470,
        "HISTORICAL_RECORD": 3,
        "SCIENTIFIC_EVIDENCE": 3,
        "PROTOCOL": 1,
    }
    assert Counter(row["proposed_review_class"] for row in ledger) == {
        "PROTOCOL": 222,
        "HISTORICAL_RECORD": 95,
        "SCIENTIFIC_EVIDENCE": 75,
        "WORKING_ARTIFACT": 48,
        "DEFER": 37,
    }


def test_v024_results_and_replay_keep_their_explicit_proposal_boundaries() -> None:
    ledger = {row["source_path"]: row for row in read_tsv("scientific-custody-80d372a.tsv")}
    for name in ("baseline.json", "causal.json", "causal_validation.json"):
        path = f"lab/research/audits/historical/v024/{name}"
        row = ledger[path]
        assert row["custody_classification"] == row["proposed_review_class"] == "SCIENTIFIC_EVIDENCE"
        assert "no unique run_id is asserted" in row["protocol_or_run_linkage"]
        assert row["proposal_review_status"].endswith("NOT_ADMITTED")

    replay = ledger["lab/examples/replays/symbiont-replay.json"]
    assert replay["custody_classification"] == "DEFER"
    assert replay["proposed_review_class"] == "WORKING_ARTIFACT"
    replay_map = read_tsv("custody-review-replay-80d372a.tsv")[0]
    assert "not a protocol" in replay_map["known_limitations_and_rationale"].lower()
    assert replay["proposal_review_status"].endswith("NOT_ADMITTED")
