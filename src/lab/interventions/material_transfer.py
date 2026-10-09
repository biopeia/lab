"""Explicit caller-declared scalar transfer across Biopeia owners.

This is a Lab/application intervention, not autonomous Organism agency or a
physical contact model. Owner candidates are private until World returns its
committed causal record. The scalar has no established material/energy
equivalence.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping

from embodiment.intake import MaterialTransfer, absorb_material_transfer
from embodiment.physiology import LivingBodyState
from environment.resource import FiniteResourceState
from observation.projection import runtime_tick_events
from world.journal import CausalRecord
from world.runtime import WorldRuntime


class InterventionKind(StrEnum):
    """Declared scientific applicability of an operator action."""

    NON_EXPERIMENTAL = "NON_EXPERIMENTAL_INTERVENTION"
    EXPERIMENTAL_RUN = "EXPERIMENTAL_RUN_INTERVENTION"


@dataclass(frozen=True, slots=True)
class InterventionRequest:
    """Caller-declared request and constraints; not authentication or permission."""

    operator_id: str
    intervention_id: str
    source_id: str
    target_body_id: str
    maximum_material: float
    kind: InterventionKind
    run_id: str | None = None
    study_id: str | None = None
    experiment_id: str | None = None
    protocol_id: str | None = None

    def __post_init__(self) -> None:
        if not self.operator_id or not self.operator_id.strip():
            raise ValueError("operator_id must not be empty")
        if not self.intervention_id or not self.intervention_id.strip():
            raise ValueError("intervention_id must not be empty")
        if not self.source_id or not self.source_id.strip():
            raise ValueError("requested source_id must not be empty")
        if not self.target_body_id or not self.target_body_id.strip():
            raise ValueError("requested target_body_id must not be empty")
        if (
            isinstance(self.maximum_material, bool)
            or not isinstance(self.maximum_material, (int, float))
            or not math.isfinite(float(self.maximum_material))
            or self.maximum_material < 0.0
        ):
            raise ValueError("maximum_material must be finite and non-negative")
        if not isinstance(self.kind, InterventionKind):
            raise ValueError("intervention kind must be explicit")
        if self.kind is InterventionKind.EXPERIMENTAL_RUN and not self.run_id:
            raise ValueError("experimental run intervention requires a real run_id")
        if self.kind is InterventionKind.NON_EXPERIMENTAL and self.run_id is not None:
            raise ValueError("non-experimental intervention cannot claim a run_id")
        for name in ("run_id", "study_id", "experiment_id", "protocol_id"):
            value = getattr(self, name)
            if value is not None and not value.strip():
                raise ValueError(f"{name} must be non-empty when supplied")


@dataclass(frozen=True, slots=True)
class MaterialTransferResult:
    """Committed record, passive projection, and owner candidates to adopt."""

    record: CausalRecord
    observations: tuple[dict[str, object], ...]
    resource_candidate: FiniteResourceState
    body_candidate: LivingBodyState


def apply_material_transfer(
    *,
    world: WorldRuntime,
    resource: FiniteResourceState,
    body: LivingBodyState,
    request: InterventionRequest,
    body_id: str,
    source_id: str,
    requested_material: float,
) -> MaterialTransferResult:
    """Run one scalar transfer under caller-declared constraints.

    The caller must adopt the returned owner candidates after success. Inputs
    are not mutated. Any callback or World journal failure raises before a
    result (including its observation projection) is returned. World owns the
    causal commit, but not durable storage, distributed rollback, or runtime
    recovery; callers must respect ``RECOVERY_REQUIRED`` after failure.
    """
    if not body_id or not body_id.strip():
        raise ValueError("body_id must not be empty")
    if not source_id or not source_id.strip():
        raise ValueError("source_id must not be empty")
    if source_id != request.source_id:
        raise ValueError("source_id does not match caller-declared request")
    if body_id != request.target_body_id:
        raise ValueError("body_id does not match caller-declared request")
    if (
        isinstance(requested_material, bool)
        or not isinstance(requested_material, (int, float))
        or not math.isfinite(float(requested_material))
        or requested_material < 0.0
        or requested_material > request.maximum_material
    ):
        raise ValueError("request exceeds caller-declared material limit")

    staged: dict[str, object] = {}

    def transition(_tick: int) -> Mapping[str, object]:
        candidate_resource = FiniteResourceState.from_checkpoint(resource.checkpoint())
        candidate_body = LivingBodyState.from_checkpoint(body.checkpoint())
        offered = min(float(requested_material), candidate_resource.offered_material())
        transfer = MaterialTransfer(
            source_id=source_id,
            target_body_id=body_id,
            amount=offered,
            composition="unspecified-scalar-material",
        )
        accepted = absorb_material_transfer(
            body_id=body_id,
            body_state=candidate_body,
            transfer=transfer,
        )
        debited = candidate_resource.consume_absorbed(accepted)
        if debited != accepted:
            raise RuntimeError("environment debit did not equal body acceptance")

        payload: dict[str, object] = {
            "kind": "operator.material_transfer",
            "operator_id": request.operator_id,
            "intervention_id": request.intervention_id,
            "intervention_kind": request.kind.value,
            "source_id": source_id,
            "target_body_id": body_id,
            "requested_material": float(requested_material),
            "offered_material": offered,
            "accepted_material": accepted,
            "debited_material": debited,
        }
        for key in ("run_id", "study_id", "experiment_id", "protocol_id"):
            value = getattr(request, key)
            if value is not None:
                payload[key] = value
        # Staging stays local to this call; owner state is not mutated/exposed.
        staged.update(
            candidate_resource=candidate_resource,
            candidate_body=candidate_body,
        )
        return payload

    record = world.tick(transition)
    candidate_resource = staged.get("candidate_resource")
    candidate_body = staged.get("candidate_body")
    if not isinstance(candidate_resource, FiniteResourceState) or not isinstance(
        candidate_body, LivingBodyState
    ):
        # Defensive fail-closed guard against a nonconforming World callback API.
        raise RuntimeError("World committed without complete intervention candidates")

    # Projection is deliberately after World returns the successful record.
    observations = runtime_tick_events(
        {
            "source": "biopeia.lab.operator_material_transfer",
            "instance_id": body_id,
            "sequence": record.causal_tick,
            "tick": record.causal_tick,
            "body_kind": "operator-intervention",
            "metabolic_reserve_ratio": (
                candidate_body.energy_reserve / candidate_body.max_energy
            ),
            "resource_remaining": candidate_resource.remaining,
        }
    )
    return MaterialTransferResult(
        record=record,
        observations=observations,
        resource_candidate=candidate_resource,
        body_candidate=candidate_body,
    )


__all__ = [
    "InterventionKind",
    "InterventionRequest",
    "MaterialTransferResult",
    "apply_material_transfer",
]
