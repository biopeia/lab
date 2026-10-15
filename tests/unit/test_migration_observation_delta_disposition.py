"""Keep the historical Observation delta transport disposition bounded."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_PATH = "lab/src/lab/observation/delta.py"
SOURCE_BLOB = "b4573fd49979fd8eee088f3dfa98fe5b0f147c44"
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"


def test_historical_observation_delta_transport_is_dropped() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "9259"
    assert row["top_level_python_symbols"] == (
        "DELTA_CONTRACT;DEFAULT_ANCHOR_INTERVAL;COMPRESSIBLE_TYPES;"
        "_canonical_bytes;state_hash;_join;_equal;_diff;ObservationDeltaEncoder;"
        "_split;_apply;ObservationDeltaDecoder"
    )
    assert row["disposition"] == "DROP"
    assert row["target_path_or_status"] == "No target delta encoder/decoder or wire schema"
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert "authorized delivery contract" in row["rationale_and_caveat"]
    assert "not deletes protected source" not in row["rationale_and_caveat"]
    assert "does not delete protected source" in row["rationale_and_caveat"]

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 45, "REWRITE": 3, "DROP": 947, "DEFER": 169}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "### Historical Observation delta transport disposition (Lab #234)" in migration
    assert "`SPLIT` | 45 |" in migration
    assert "`DROP` | 947 |" in migration
    assert "not a replacement for this JSON delta format" in migration
