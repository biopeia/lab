"""Keep the historical composed-frame disposition evidence bounded."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_PATH = "lab/src/lab/observation/contracts.py"
SOURCE_BLOB = "14dd5186a187820d679d88b542c639cf84b57adc"
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"


def test_historical_observation_frame_contract_requires_rewrite() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "2822"
    assert row["top_level_python_symbols"] == (
        "PRESENTATION_PROJECTION;COMPLETED_FRAME_CONTRACT;"
        "OBSERVATION_IDENTITY_CONTRACT;ObservedFrame"
    )
    assert row["disposition"] == "REWRITE"
    assert "observation/src/observation/semantic.py" in row["target_path_or_status"]
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "not a stable target schema/API" in row["rationale_and_caveat"]
    assert "No scientific validity" in row["rationale_and_caveat"]

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 21, "REWRITE": 3, "DROP": 950, "DEFER": 190}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "### Historical Observation frame contract disposition (Lab #233)" in migration
    assert "`SPLIT` | 21 |" in migration
    assert "`REWRITE` | 3 |" in migration
    assert "not one semantic claim" in migration
