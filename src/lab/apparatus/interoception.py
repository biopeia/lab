"""Opaque body-interoception transducer used by the Physics3D apparatus.

This adapter exposes bounded anonymous slots only. It does not assign labels,
valence, or action meaning to the underlying body-state scalars.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence

from embodiment.physiology import LivingBodyState


class OpaqueBodyInteroception:
    """Transduce selected body-state scalars into anonymous receptor slots."""

    SOURCE_COUNT = 4

    def __init__(
        self,
        *,
        receptor_ids: Sequence[str] | None = None,
        source_ordinals_by_slot: Sequence[int] | None = None,
    ) -> None:
        ids = tuple(
            () if receptor_ids is None else (str(item) for item in receptor_ids)
        )
        if len(ids) != self.SOURCE_COUNT or len(set(ids)) != self.SOURCE_COUNT:
            raise ValueError("body interoception requires four explicit unique opaque receptor ids")
        permutation = (
            tuple(range(self.SOURCE_COUNT))
            if source_ordinals_by_slot is None
            else tuple(int(item) for item in source_ordinals_by_slot)
        )
        if sorted(permutation) != list(range(self.SOURCE_COUNT)):
            raise ValueError("interoception mapping must be a permutation of source ordinals")
        self.receptor_ids = ids
        self._source_ordinals_by_slot = permutation

    @property
    def source_ordinals_by_slot(self) -> tuple[int, ...]:
        return self._source_ordinals_by_slot

    def sample(self, state: LivingBodyState) -> dict[str, float]:
        source_values = (
            max(0.0, min(1.0, state.energy_reserve / max(state.max_energy, 1e-12))),
            max(0.0, min(1.0, state.structural_integrity)),
            max(0.0, min(1.0, state.temperature)),
            max(0.0, min(1.0, state.fatigue)),
        )
        return {
            receptor_id: float(source_values[source_ordinal])
            for receptor_id, source_ordinal in zip(self.receptor_ids, self._source_ordinals_by_slot)
        }

    def checkpoint(self) -> dict[str, object]:
        """Persist only the slot permutation, never physiology labels."""
        return {
            "schema_version": 1,
            "source_ordinals_by_slot": list(self._source_ordinals_by_slot),
        }

    @classmethod
    def from_checkpoint(
        cls,
        payload: Mapping[str, object],
        *,
        receptor_ids: Sequence[str] | None = None,
    ) -> "OpaqueBodyInteroception":
        if payload.get("schema_version") != 1:
            raise ValueError("unsupported opaque body interoception checkpoint")
        raw = payload.get("source_ordinals_by_slot")
        if not isinstance(raw, (list, tuple)):
            raise ValueError("opaque body interoception mapping is missing")
        return cls(receptor_ids=receptor_ids, source_ordinals_by_slot=raw)
