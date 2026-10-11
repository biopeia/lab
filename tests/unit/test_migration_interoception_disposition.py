"""Keep the bounded interoception migration rows source-pinned and actionable."""

from __future__ import annotations

import ast
import csv
from pathlib import Path

ROOT = Path(__file__).parents[2]
MIGRATION = ROOT / "migration"
SOURCE_COMMIT = "80d372a186513035f85a769db886e505cabba52d"


def read_inventory() -> dict[str, dict[str, str]]:
    with (MIGRATION / "source-inventory-80d372a.tsv").open(
        encoding="utf-8", newline=""
    ) as stream:
        rows = list(csv.DictReader(stream, delimiter="\t"))
    return {row["source_path"]: row for row in rows}


def declared_symbols(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
    }


def test_interoception_source_symbols_have_bounded_rewrite_and_drop_dispositions() -> None:
    rows = read_inventory()
    row = rows["lab/src/lab/integration/physics3d/apparatus.py"]
    symbols = set(row["top_level_python_symbols"].split(";"))
    retained = {"OpaqueBodyInteroception"}
    dropped = {
        "_running_version",
        "physics3d_sensory_system",
        "physics3d_cognition",
        "physics3d_actuator_surface",
        "PhysicsDiscoveryProvider",
        "PhysicsReadingProvider",
        "actuator_to_effector_map",
        "actuator_exclusion_groups",
        "body_schema_summary",
    }

    assert row["source_blob_at_pinned_commit"] == "8de1f29fe87321fcab0cb051e79fadcf0f833cd6"
    assert row["disposition"] == "SPLIT"
    assert row["source_path"] == "lab/src/lab/integration/physics3d/apparatus.py"
    assert row["target_owner"].startswith("Lab (transducer only; Embodiment retains authority")
    assert symbols == retained | dropped
    assert "src/lab/apparatus/interoception.py::OpaqueBodyInteroception" in row["target_path_or_status"]
    assert all(name in row["target_path_or_status"] for name in dropped)
    assert "claims no semantic equivalence" in row["rationale_and_caveat"]
    assert SOURCE_COMMIT in (ROOT / "MIGRATION.md").read_text(encoding="utf-8")

    target = ROOT / "src/lab/apparatus/interoception.py"
    assert "OpaqueBodyInteroception" in declared_symbols(target)


def test_interoception_test_symbols_map_only_selected_assertions_and_drop_the_rest() -> None:
    rows = read_inventory()
    row = rows["lab/tests/unit/lab/physics3d/test_contract.py"]
    source_symbols = set(row["top_level_python_symbols"].split(";"))
    target_tests = {
        "test_interoception_projects_four_bounded_opaque_values",
        "test_interoception_permutation_changes_slots_not_source_state",
        "test_interoception_checkpoint_round_trip_keeps_only_ordinal_mapping",
    }
    mapped_source_tests = {
        "test_l3_receptors_remain_opaque_ordinals",
        "test_l3_interoception_mapping_is_label_invariant_under_permutation",
        "test_l3_checkpoint_preserves_only_opaque_ordinal_mapping",
    }
    explicitly_dropped_source_tests = {
        "test_l3_interoceptive_channels_are_independent",
        "test_l3_local_contact_loads_are_independent_physical_channels",
    }

    assert row["source_blob_at_pinned_commit"] == "f23d0122a7ab649f7142b0138c50b0cb6f1a57b6"
    assert row["disposition"] == "SPLIT"
    assert source_symbols >= mapped_source_tests | explicitly_dropped_source_tests
    assert "tests/unit/test_interoception.py" in row["target_path_or_status"]
    assert all(name in row["target_path_or_status"] for name in target_tests)
    assert all(name in row["target_path_or_status"] for name in explicitly_dropped_source_tests)
    assert "all other source tests/helpers listed in top_level_python_symbols" in row["target_path_or_status"]
    assert "no label-invariance scientific claim" in row["rationale_and_caveat"]
    assert "does not duplicate the separate somatic-correlation protocol disposition in Lab#61" in row["rationale_and_caveat"]

    target = ROOT / "tests/unit/test_interoception.py"
    assert target_tests <= declared_symbols(target)
    assert mapped_source_tests <= source_symbols
    assert explicitly_dropped_source_tests <= source_symbols
