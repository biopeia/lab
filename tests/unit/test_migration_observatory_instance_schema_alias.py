"""Keep this legacy schema-path alias deferred until its sibling is dispositioned."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
ALIAS_PATH = "lab/src/lab/observatory/instance.schema.json"
SCHEMA_PATH = "lab/src/lab/observatory/schemas/instance.schema.json"


def test_instance_schema_alias_is_bounded_defer_linked_to_sibling_issue() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    by_path = {row["source_path"]: row for row in rows}

    alias = by_path[ALIAS_PATH]
    assert alias["source_blob_at_pinned_commit"] == (
        "705273ce14b8dad75fd3d087ee28dfddd2c6e389"
    )
    assert alias["git_mode"] == "120000"
    assert alias["bytes"] == "28"
    assert alias["top_level_python_symbols"] == ""
    assert alias["disposition"] == "DEFER"
    assert "Lab #255 coordinator" in alias["target_owner"]
    assert "Observation #38" in alias["target_owner"]
    assert "Lab #266" in alias["target_path_or_status"]
    assert "schemas/instance.schema.json" in alias["rationale_and_caveat"]
    assert SOURCE_COMMIT in alias["rationale_and_caveat"]
    assert "competent-owner disposition" in alias["rationale_and_caveat"]
    assert "outside the bounded runtime-transfer profile" in alias["rationale_and_caveat"]
    assert "unresolved #78/#45 worklist" in alias["rationale_and_caveat"]

    assert not (ROOT / "src/lab/observatory/instance.schema.json").exists()
    assert not (ROOT / "src/lab/observatory/schemas/instance.schema.json").exists()

    sibling = by_path[SCHEMA_PATH]
    assert sibling["source_blob_at_pinned_commit"] == (
        "7a2d29bb3dc576c2b984d85bbcfc8746fc7adb44"
    )
    # The alias cannot be finally dropped or retained independently of the schema row.
    assert sibling["disposition"] == "DEFER"
    assert "Observation #38" in sibling["target_path_or_status"]
    assert "bounded runtime-transfer profile" in sibling["rationale_and_caveat"]

    counts = Counter(row["disposition"] for row in rows)
    assert counts == {"MOVE": 8, "SPLIT": 54, "REWRITE": 3, "DROP": 941, "DEFER": 166}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Observatory instance schema path alias (Lab #255; linked to Observation #38 and Lab #266)" in migration
    assert "Keep this alias as `DEFER`, linked to Observation #38" in migration
    assert "classify this alias as DROP" in migration
    assert "scientific validity/equivalence/admission" in migration.lower()
    assert "Lab #266 recorded that schema as a bounded `DEFER`" in migration
    assert "competent Observation/Lab owners record whether" in migration
    assert "linked to Observation #38" in migration
