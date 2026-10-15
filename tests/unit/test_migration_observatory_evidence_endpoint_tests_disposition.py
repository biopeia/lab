"""Keep unresolved evidence-endpoint authority visible in the migration ledger."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/observatory/tests/test_evidence_endpoints.py"
SOURCE_BLOB = "2029ddd95201008a1e16c237411b835fa0e11d31"


def test_evidence_endpoint_tests_are_deferred_with_owner_closure_trigger() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "4461"
    assert row["top_level_python_symbols"] == "EvidenceEndpointTests"
    assert row["disposition"] == "DEFER"
    assert "Lab #278 coordinator" in row["target_owner"]
    assert "Lab evidence-custody owner" in row["target_owner"]
    assert all(link in row["target_owner"] for link in ("#257", "#260", "#256", "Observation #38"))
    assert "no authorized TARGET endpoint/response contract" in row["target_path_or_status"]
    rationale = row["rationale_and_caveat"]
    assert SOURCE_COMMIT in rationale
    assert "Closure trigger" in rationale
    assert "does not block bounded runtime-transfer profile" in rationale
    assert "no scientific validity/equivalence/evidence-admission claim" in rationale

    counts = Counter(row["disposition"] for row in rows)
    assert counts == {"MOVE": 8, "SPLIT": 42, "REWRITE": 3, "DROP": 948, "DEFER": 171}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 42 |" in migration
    assert "`DEFER` | 171 |" in migration
    assert "### Historical Observatory evidence-endpoint tests (Lab #278)" in migration
