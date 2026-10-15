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
    assert row["disposition"] == "SPLIT"  # mixed owners remain independently assigned
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



def test_physics3d_apparatus_symbols_have_explicit_owner_or_drop_dispositions() -> None:
    row = read_inventory()["lab/src/lab/integration/physics3d/apparatus.py"]
    status = row["target_path_or_status"]
    symbols = set(row["top_level_python_symbols"].split(";"))
    source = "lab/src/lab/integration/physics3d/apparatus.py::"
    explicit = {
        "_running_version": f"DROP: {source}_running_version;",
        "physics3d_sensory_system": f"DROP: {source}physics3d_sensory_system;",
        "physics3d_cognition": f"DROP historical Lab wrapper: {source}physics3d_cognition;",
        "physics3d_actuator_surface": f"DROP historical Lab wrapper: {source}physics3d_actuator_surface;",
        "OpaqueBodyInteroception": f"DROP: {source}OpaqueBodyInteroception;",
        "PhysicsDiscoveryProvider": f"DROP: {source}PhysicsDiscoveryProvider and",
        "PhysicsReadingProvider": f"`PhysicsReadingProvider`; no TARGET Lab adapter path.",
        "actuator_to_effector_map": f"DROP: {source}actuator_to_effector_map;",
        "actuator_exclusion_groups": f"DROP historical Lab projection: {source}actuator_exclusion_groups;",
        "body_schema_summary": f"DROP: {source}body_schema_summary;",
    }
    references = {
        "physics3d_cognition": "src/organism/cognition/birth.py::load_base_cognition",
        "physics3d_actuator_surface": "src/organism/actuation/surface.py::derive_actuator_constitution",
        "actuator_exclusion_groups": (
            "src/organism/actuation/sensorimotor.py::"
            "CompetenceDevelopmentEngine.exclusive_actuator_groups"
        ),
    }

    assert row["source_blob_at_pinned_commit"] == APPARATUS_BLOB
    assert row["disposition"] == "SPLIT"
    assert set(explicit) == symbols
    for symbol, marker in explicit.items():
        assert status.count(marker) == 1, f"missing or duplicate disposition for {symbol}"
    for symbol, target in references.items():
        assert status.count(target) == 1
        assert "independent" in status
    assert "no TARGET Lab adapter path" in status
    assert "not migrated" in status

    migration = (ROOT / "MIGRATION.md").read_text(encoding="utf-8")
    rationale = row["rationale_and_caveat"]
    section_start = migration.index("### Historical Physics3D apparatus wrapper dispositions")
    section_end = migration.find("\n### ", section_start + 1)
    section = migration[section_start : section_end if section_end >= 0 else len(migration)]
    assert "not migrated implementations or semantic equivalence" in section
    for symbol in symbols:
        assert section.count(f"`{symbol}`") == 1, f"missing or duplicate documentation row for {symbol}"
    assert SOURCE_COMMIT in section
    assert APPARATUS_BLOB in migration
    assert "Other source symbols in this mixed file are not disposed" not in rationale
    assert "Exact symbol-level dispositions for every source symbol" in rationale


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
    assert "`SPLIT` | 104 |" in migration
    assert "`DROP` | 900 |" in migration
    assert "`DEFER` | 160 |" in migration
    assert "test_contract.py` is `DROP` as a whole" in migration
    assert "DROP as TARGET code" in migration
    assert "DROP as TARGET tests" in migration
    assert APPARATUS_BLOB in migration
    assert TEST_BLOB in migration
    assert "does not include a body-interoception transducer" in readme
    assert "lab.apparatus.interoception" not in readme
