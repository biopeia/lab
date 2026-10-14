"""Non-executing Lab experiment plan boundary.

A plan is not operator authorization, a World command, or scientific evidence.
Only domain-owned contracts may validate and execute real operations.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RequestedOperation(StrEnum):
    PREPARE = "prepare"
    RUN = "run"
    INTERVENE = "intervene"


@dataclass(frozen=True, slots=True)
class ExperimentIntent:
    """Declared intent suitable for review, never a capability token."""

    protocol_id: str
    experiment_id: str
    target_domain: str
    operation: RequestedOperation
    contract_ref: str
    requested_by: str

    def __post_init__(self) -> None:
        for field in ("protocol_id", "experiment_id", "contract_ref", "requested_by"):
            value = getattr(self, field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{field} must be non-empty")
        if not isinstance(self.target_domain, str) or self.target_domain not in {
            "organism", "embodiment", "environment", "world", "modality"
        }:
            raise ValueError("target_domain must name a permitted domain boundary")
        if not isinstance(self.operation, RequestedOperation):
            raise ValueError("operation must be an explicit RequestedOperation")


def describe_intent(intent: ExperimentIntent) -> dict[str, str]:
    """Return a detached audit description, never dispatch an intervention."""
    if not isinstance(intent, ExperimentIntent):
        raise TypeError("intent must be ExperimentIntent")
    return {
        "protocol_id": intent.protocol_id,
        "experiment_id": intent.experiment_id,
        "target_domain": intent.target_domain,
        "operation": intent.operation.value,
        "contract_ref": intent.contract_ref,
        "requested_by": intent.requested_by,
        "status": "unapproved_intent",
    }
