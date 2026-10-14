"""Keep the bounded historical interoception DROP disposition source-pinned."""

from __future__ import annotations

import csv
from pathlib import Path

ROOT = Path(__file__).parents[2]
MIGRATION = ROOT / "migration"
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"
APPARATUS_BLOB = "8de1f29fe87321fcab0cb051e79fadcf0f833cd6"
TEST_BLOB = "f23d0122a7ab649f7142b0138c50b0cb6f1a57b6"


def read_inventory() -> dict[str, dict[str, str]]:
    with (MIGRATION / "source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    return {row["source_path"]: row for row in rows}


def test_historical_interoception_symbol_is_dropped_without_target_mapping() -> None:
    rows = read_inventory()
    row = rows["lab/src/lab/integration/physics3d/apparatus.py"]
    symbols = set(row["top_level_python_symbols"].split(";"))
    source_symbol = "OpaqueBodyInteroception"

    assert row["source_blob_at_pinned_commit"] == APPARATUS_BLOB
    assert row["disposition"] == "SPLIT"  # the source file contains other symbols
    assert source_symbol in symbols
    assert "DROP: lab/src/lab/integration/physics3d/apparatus.py::OpaqueBodyInteroception" in row["target_path_or_status"]
    assert "no TARGET path" in row["target_path_or_status"]
    assert "no approved TARGET contract" in row["rationale_and_caveat"]
    assert "no production consumer" in row["rationale_and_caveat"]
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert APPARATUS_BLOB in row["rationale_and_caveat"]

    assert not (ROOT / "src/lab/apparatus/interoception.py").exists()
    assert not any(
        source_symbol in path.read_text(encoding="utf-8")
        for path in (ROOT / "src").rglob("*.py")
    )


def test_historical_interoception_assertions_are_dropped_without_target_tests() -> None:
    rows = read_inventory()
    row = rows["lab/tests/unit/lab/physics3d/test_contract.py"]
    source_tests = {
        "test_l3_receptors_remain_opaque_ordinals",
        "test_l3_interoceptive_channels_are_independent",
        "test_l3_interoception_mapping_is_label_invariant_under_permutation",
        "test_l3_local_contact_loads_are_independent_physical_channels",
        "test_l3_checkpoint_preserves_only_opaque_ordinal_mapping",
    }

    assert row["source_blob_at_pinned_commit"] == TEST_BLOB
    assert row["disposition"] == "DROP"  # whole source test file is excluded from TARGET
    assert source_tests <= set(row["top_level_python_symbols"].split(";"))
    all_source_tests = {
        name
        for name in row["top_level_python_symbols"].split(";")
        if name.startswith("test_")
    }
    assert len(all_source_tests) == 52
    assert row["target_path_or_status"] == (
        "DROP as TARGET tests: all 52 test functions; no Biopeia target destination"
    )
    assert SOURCE_COMMIT in row["rationale_and_caveat"]
    assert TEST_BLOB in row["rationale_and_caveat"]
    assert not (ROOT / "tests/unit/test_interoception.py").exists()

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "`SPLIT` | 107 |" in migration
    assert "`DROP` | 898 |" in migration
    assert "`DEFER` | 159 |" in migration
    assert "test_contract.py` is `DROP` as a whole" in migration
    assert "DROP as TARGET code" in migration
    assert "DROP as TARGET tests" in migration
    assert APPARATUS_BLOB in migration
    assert TEST_BLOB in migration
    assert "does not include a body-interoception transducer" in readme
    assert "lab.apparatus.interoception" not in readme
