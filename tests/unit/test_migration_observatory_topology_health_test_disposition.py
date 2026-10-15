"""Keep the historical topology-health test out of TARGET tests."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/observatory/tests/test_topology_health_contract.py"
SOURCE_BLOB = "9d24e5ebb1366a0228d81637b64610a11c1ff671"


def test_historical_topology_health_test_is_dropped_as_target_code() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "1240"
    assert row["top_level_python_symbols"] == (
        "ROOT;test_cognition_schema_declares_reversible_topology_health_states;"
        "test_adapter_projects_topology_health_without_raw_structural_state"
    )
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Lab historical test; no TARGET owner"
    assert row["target_path_or_status"] == "No TARGET code destination"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "not a scientific result or oracle" in row["rationale_and_caveat"]
    assert "future cognition-state observation is unnecessary" in row["rationale_and_caveat"]
    assert not (ROOT / "src/lab/observatory/tests/test_topology_health_contract.py").exists()

    counts = Counter(row["disposition"] for row in rows)
    assert counts == {"MOVE": 8, "SPLIT": 53, "REWRITE": 3, "DROP": 941, "DEFER": 167}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "`SPLIT` | 53 |" in migration
    assert "`DROP` | 941 |" in migration
    assert "### Historical Observatory topology-health contract test" in migration
