"""Keep historical Physics3D observer labels deferred pending owner contracts."""

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/physics3d/observer_semantics.py"
SOURCE_BLOB = "ea458b9ffba761a94426c436ed347f947c282ba0"

def test_observer_semantics_remains_bounded_defer() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "7776"
    assert row["disposition"] == "DEFER"
    assert row["target_owner"] == "Embodiment physical-state/actuator owner; Observation projection owner; Lab observer/evidence custodian"
    assert row["target_path_or_status"] == "No authorized TARGET evaluator-only semantics projection contract or consumer"
    rationale = row["rationale_and_caveat"]
    for evidence in (SOURCE_COMMIT, "ground truth for evaluation only", "never enter organism discovery", "evidence-custody policy", "No source/labels are copied/deleted"):
        assert evidence in rationale
    counts = Counter(entry["disposition"] for entry in rows)
    assert counts == {"MOVE": 8, "SPLIT": 22, "REWRITE": 3, "DROP": 949, "DEFER": 190}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical Physics3D observer-semantics disposition (Lab #300)" in migration
    assert SOURCE_BLOB in migration
