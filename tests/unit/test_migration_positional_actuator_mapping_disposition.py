"""Keep the historical positional actuator mapping out of TARGET."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/integration/physics3d/apparatus.py"
SOURCE_BLOB = "8de1f29fe87321fcab0cb051e79fadcf0f833cd6"
SOURCE_SYMBOL = "actuator_to_effector_map"


def test_historical_positional_mapping_is_dropped_without_disposing_siblings() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["disposition"] == "SPLIT"  # sibling source symbols remain unresolved
    assert SOURCE_SYMBOL in row["top_level_python_symbols"].split(";")
    assert f"DROP: {SOURCE_PATH}::{SOURCE_SYMBOL}; no TARGET path." in row[
        "target_path_or_status"
    ]
    assert "pairs actuator and effector identities by list index" in row["rationale_and_caveat"]
    assert "stable identity, never collection order" in row["rationale_and_caveat"]
    assert "DROP applies to this historical implementation only" in row["rationale_and_caveat"]
    assert "biopeia/embodiment@56e9a34a6a778a298493dabca9d15b0912066803" in row["rationale_and_caveat"]
    assert "src/embodiment/physics3d/actuator_binding.py" in row["rationale_and_caveat"]
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert SOURCE_BLOB in row["rationale_and_caveat"]


def test_disposition_does_not_reintroduce_the_historical_function() -> None:
    assert not any(
        SOURCE_SYMBOL in path.read_text(encoding="utf-8")
        for path in (ROOT / "src").rglob("*.py")
    )
