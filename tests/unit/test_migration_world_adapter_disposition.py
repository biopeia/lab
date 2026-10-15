"""Keep Lab #208's pinned historical-adapter disposition auditable."""
from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).parents[2]
SOURCE = "lab/src/lab/integration/world/adapter.py"
COMMIT = "80d372a186513035f85a769db886e505cabba52d"
BLOB = "1e8c7b50d658ac2fc06db98868c713a517bc27b7"
SYMBOLS = {
    "LONGITUDINAL_CONTRACT", "physical_receptor_ids", "WorldDiscoveryProvider",
    "WorldReadingProvider", "local_substrate_signals", "_capabilities_for",
    "_unit_interval", "_mix_weight", "physical_receptor_signals",
    "clean_world_observation", "_load_base_genome", "ActuationBinding",
    "ActuationBindingConstitution", "ActuationAdapter",
    "default_world_actuation_binding", "ActionExecutionResult", "WorldTickRecord",
    "_OrganismRig", "_construct_organism", "_act",
}


def test_world_adapter_row_and_every_recorded_symbol_have_bounded_drop_disposition() -> None:
    with (ROOT / "migration/source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    row = next(item for item in rows if item["source_path"] == SOURCE)

    assert row["source_blob_at_pinned_commit"] == BLOB
    assert row["disposition"] == "DROP"
    assert row["target_owner"] == "Historical Lab integration composition; no TARGET owner"
    assert set(row["top_level_python_symbols"].split(";")) == SYMBOLS
    assert "no consumer" in row["rationale_and_caveat"]
    assert COMMIT in row["rationale_and_caveat"]
    assert BLOB in row["rationale_and_caveat"]

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    section_start = migration.index("### Historical World integration adapter (Lab #208)")
    section_end = migration.index("### Historical Observatory snapshot schemas", section_start)
    section = migration[section_start:section_end]
    assert "not asserted to replace or be equivalent" in section
    for symbol in SYMBOLS:
        assert section.count(f"`{symbol}`") == 1, f"missing or duplicate disposition: {symbol}"
    assert COMMIT in section
    assert BLOB in section
