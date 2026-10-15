"""Keep the human-only Observatory provenance adapter disposition auditable."""

import csv
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/observatory/provenance.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "d928fa835da90a21d06c02976794b3b3396bccc7"


def test_observer_provenance_translator_is_dropped_without_science_claim() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["bytes"] == "5400"
    assert row["top_level_python_symbols"] == "_descriptor;build_observer_provenance"
    assert row["disposition"] == "DROP"
    assert "No TARGET owner" in row["target_owner"]
    assert COMMIT in row["rationale_and_caveat"]
    assert "does not enter RuntimeTickResult, checkpoint state, cognition, or learning" in row["rationale_and_caveat"]
    assert "do not infer that future observability is unnecessary" in row["rationale_and_caveat"]
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "Historical Observatory observer-provenance translator disposition (Lab #258)" in migration
    assert BLOB in migration
