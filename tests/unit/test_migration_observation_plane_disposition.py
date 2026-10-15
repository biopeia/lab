"""Keep the historical semantic plane responsibility with Observation."""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/observation/plane.py"
SOURCE_BLOB = "a971a49857a562021da909a00a4efd53a0f7e637"
SYMBOLS = "ObservationKey;PlaneMessage;PlaneRebaseRequired;PlaneStreamSubscription;observation_key;ObservationPlane"


def test_observation_plane_responsibility_moves_to_concrete_observation_owner() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]

    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "10805"
    assert row["top_level_python_symbols"] == SYMBOLS
    assert row["disposition"] == "MOVE"
    assert row["target_owner"] == "Observation"
    assert row["target_path_or_status"] == "repos/observation/src/observation/plane.py::ObservationPlane"
    rationale = row["rationale_and_caveat"]
    assert "bounded current-state materialization, live fan-out, replay" in rationale
    assert "does not admit scientific evidence" in rationale
    assert "not source-code identity, behavioral or scientific equivalence" in rationale

    assert not (ROOT / "src/lab/observation/plane.py").exists()
    assert (ROOT / "src/lab/observation_consumer.py").exists()

    counts = Counter(item["disposition"] for item in rows)
    assert counts == {"MOVE": 8, "SPLIT": 64, "REWRITE": 3, "DROP": 934, "DEFER": 163}

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert SOURCE_BLOB in migration
    assert "Historical Observation plane disposition (Lab #240)" in migration
    assert "`MOVE` | 8 |" in migration
    assert "`SPLIT` | 64 |" in migration
