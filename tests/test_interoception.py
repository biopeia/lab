import pytest

from embodiment.physiology import LivingBodyState
from lab.apparatus.interoception import OpaqueBodyInteroception

RECEPTORS = ("slot.a", "slot.b", "slot.c", "slot.d")


def _state(**changes: float) -> LivingBodyState:
    values = dict(
        energy_reserve=1.0,
        max_energy=2.0,
        structural_integrity=0.8,
        temperature=0.4,
        fatigue=0.2,
    )
    values.update(changes)
    return LivingBodyState(**values)


def test_interoception_projects_four_bounded_opaque_values() -> None:
    surface = OpaqueBodyInteroception(receptor_ids=RECEPTORS)
    sample = surface.sample(_state())
    assert tuple(sample) == surface.receptor_ids
    assert tuple(sample.values()) == (0.5, 0.8, 0.4, 0.2)
    assert all(0.0 <= value <= 1.0 for value in sample.values())


def test_interoception_permutation_changes_slots_not_source_state() -> None:
    state = _state()
    canonical = OpaqueBodyInteroception(receptor_ids=RECEPTORS).sample(state)
    permuted = OpaqueBodyInteroception(
        receptor_ids=RECEPTORS, source_ordinals_by_slot=(2, 0, 3, 1)
    ).sample(state)
    assert tuple(permuted.values()) == (
        canonical[RECEPTORS[2]],
        canonical[RECEPTORS[0]],
        canonical[RECEPTORS[3]],
        canonical[RECEPTORS[1]],
    )
    assert state == _state()


def test_interoception_checkpoint_round_trip_keeps_only_ordinal_mapping() -> None:
    surface = OpaqueBodyInteroception(
        receptor_ids=RECEPTORS, source_ordinals_by_slot=(2, 0, 3, 1)
    )
    restored = OpaqueBodyInteroception.from_checkpoint(
        surface.checkpoint(), receptor_ids=RECEPTORS
    )
    assert restored.receptor_ids == surface.receptor_ids
    assert restored.source_ordinals_by_slot == (2, 0, 3, 1)
    assert "temperature" not in str(surface.checkpoint())


@pytest.mark.parametrize("mapping", [(0, 0, 1, 2), (0, 1, 2)])
def test_interoception_rejects_non_permutations(mapping: tuple[int, ...]) -> None:
    with pytest.raises(ValueError, match="permutation"):
        OpaqueBodyInteroception(receptor_ids=RECEPTORS, source_ordinals_by_slot=mapping)
