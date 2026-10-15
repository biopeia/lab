"""Legacy broad Observation wire format is not a TARGET transport contract."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_PATH = "lab/src/lab/observation/wire.py"
SOURCE_BLOB = "160df024ef608db2ee97603e8d4a326c53718fae"
SYMBOLS = "SEMANTIC_WIRE_CONTRACT;_json_value;_actor;_identity;semantic_observation_payload;plane_message_payload"


def test_legacy_observation_wire_contract_is_dropped() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "4895"
    assert row["top_level_python_symbols"] == SYMBOLS
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "No TARGET owner for legacy wire schema"
    assert row["target_path_or_status"] == "No TARGET wire-contract path"
    assert "not this broad wire schema" in row["rationale_and_caveat"]
    assert "No semantic authority" in row["rationale_and_caveat"]
    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 28, "REWRITE": 3, "DROP": 949, "DEFER": 184}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "Historical Observation wire serializer disposition (Lab #246)" in migration
