"""Track the ownership split for the pinned historical persistence facade."""

import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
SOURCE_PATH = "lab/src/lab/physics3d/persistence.py"
SOURCE_BLOB = "2658c40c11d52a162d573d5b7bd4c319bae0f665"
SYMBOLS = (
    "_atomic_write_json;_read_json;validate_bundle_export_invariants;build_symbiont_bundle_manifest;"
    "sync_organism_metadata;save_symbiont_bundle;read_symbiont_bundle_manifest;_read_bundle_manifest;"
    "read_symbiont_bundle_runtime;_bundle_models;load_symbiont_bundle;save_runtime_state_file;"
    "load_runtime_state_file;save_body_state_file;load_body_state_file;TelemetryWriter;"
    "load_telemetry_records;load_telemetry_transitions"
)

def test_persistence_facade_is_split_by_owner_and_unmatched_helpers_are_excluded() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    matches = [row for row in rows if row["source_path"] == SOURCE_PATH]
    assert len(matches) == 1
    row = matches[0]
    assert row["source_blob_at_pinned_commit"] == SOURCE_BLOB
    assert row["git_mode"] == "100644"
    assert row["bytes"] == "23500"
    assert row["top_level_python_symbols"] == SYMBOLS
    assert row["disposition"] == "SPLIT"
    for owner_path in ("organism/src/organism/checkpoint.py", "embodiment/src/embodiment/checkpoint.py", "world/src/world/owner_checkpoint_store.py"):
        assert owner_path in row["target_path_or_status"]
    rationale = row["rationale_and_caveat"]
    for evidence in (SOURCE_COMMIT, "no single authorized TARGET bundle", "Lab evidence custody alone", "No source files or artifacts are copied or deleted"):
        assert evidence in rationale
    counts = Counter(entry["disposition"] for entry in rows)
    assert counts == {"MOVE": 8, "SPLIT": 21, "REWRITE": 3, "DROP": 950, "DEFER": 190}
    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    assert "### Historical Physics3D persistence facade disposition (Lab #301)" in migration
    assert SOURCE_BLOB in migration
