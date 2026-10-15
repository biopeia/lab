"""Keep the historical adversarial-hardening tests out of TARGET tests."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/observatory/tests/test_adversarial_hardening.py"
SOURCE_BLOB = "00262cc40b18a8de57910e192d799f0063b21a07"


def test_historical_adversarial_hardening_test_is_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "4748"
    assert row["top_level_python_symbols"] == (
        "ROOT;_next_sse_payload;ObservatoryAdversarialHardeningTests"
    )
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET test owner"
    assert row["target_path_or_status"] == "No TARGET test destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "synthetic" in row["rationale_and_caveat"]
    assert "not scientific results" in row["rationale_and_caveat"]
    assert not (ROOT / "src/lab/observatory/tests/test_adversarial_hardening.py").exists()

    counts = Counter(row["disposition"] for row in rows)
    assert counts == {"MOVE": 8, "SPLIT": 20, "REWRITE": 3, "DROP": 950, "DEFER": 191}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 20 |" in migration
    assert "`DROP` | 950 |" in migration
    assert "### Historical Observatory adversarial hardening tests (Lab #275)" in migration
