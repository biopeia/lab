"""Passive association of retained Observation messages with Lab execution context.

This module adds no producer, persistence, transport, authorization, or scientific
evidence-admission behavior. A caller must provide the Lab-owned execution
context and the World-issued committed-cut receipt that were explicitly
correlated by the operation that produced the cut.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from queue import Empty
from typing import Protocol, Sequence


class _OwnerReference(Protocol):
    owner: str
    owner_identity: str
    sha256: str


class _CommittedWorldCut(Protocol):
    world_id: str
    causal_tick: int
    commit_id: str
    owner_checkpoint_references: Sequence[_OwnerReference]


class _ObservationPlane(Protocol):
    def current_messages(self, *, family: str | None = None) -> tuple[object, ...]: ...


@dataclass(frozen=True, slots=True)
class LabObservationAssociation:
    """Explicit Lab execution-to-cut association; not source authentication."""

    experiment_id: str
    run_id: str
    world_id: str
    causal_tick: int
    commit_id: str

    def __post_init__(self) -> None:
        for name in ("experiment_id", "run_id", "world_id", "commit_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")
        if type(self.causal_tick) is not int or self.causal_tick < 0:
            raise ValueError("causal_tick must be a non-negative integer")

    @classmethod
    def for_committed_cut(
        cls,
        *,
        experiment_id: str,
        run_id: str,
        committed_cut: _CommittedWorldCut,
    ) -> LabObservationAssociation:
        """Bind explicit Lab execution identity to the exact World receipt."""
        return cls(
            experiment_id=experiment_id,
            run_id=run_id,
            world_id=committed_cut.world_id,
            causal_tick=committed_cut.causal_tick,
            commit_id=committed_cut.commit_id,
        )


class LabObservationReadStatus(StrEnum):
    ASSOCIATED = "associated"
    UNASSOCIATED = "unassociated"
    REBASE_REQUIRED = "rebase_required"


@dataclass(frozen=True, slots=True)
class LabObservationRead:
    """Read result preserving original PlaneMessage/claim objects and limits."""

    status: LabObservationReadStatus
    association: LabObservationAssociation
    messages: tuple[object, ...] = ()
    reason: str | None = None
    sequence: int | None = None


def _context_matches(
    observation: object,
    association: LabObservationAssociation,
    committed_cut: _CommittedWorldCut,
) -> tuple[bool, str | None]:
    if (
        association.world_id != committed_cut.world_id
        or association.causal_tick != committed_cut.causal_tick
        or association.commit_id != committed_cut.commit_id
    ):
        return False, "lab_context_does_not_match_committed_cut"

    claim = getattr(observation, "claim", None)
    authority = getattr(getattr(claim, "authority", None), "value", None)
    family_authority = getattr(getattr(observation, "family", None), "authority", None)
    family_authority = getattr(family_authority, "value", family_authority)
    if not isinstance(authority, str) or family_authority != authority:
        return False, "observation_authority_is_missing_or_inconsistent"

    owner_references = tuple(
        reference
        for reference in committed_cut.owner_checkpoint_references
        if reference.owner == authority
    )
    lineage = getattr(observation, "lineage", None)
    parents = getattr(lineage, "parents", ())
    parent_references = {
        getattr(parent, "reference", None)
        for parent in parents
        if isinstance(getattr(parent, "reference", None), str)
    }
    matching_references = tuple(
        reference for reference in owner_references
        if reference.sha256 in parent_references
    )
    if not matching_references:
        return False, "observation_does_not_reference_committed_owner_checkpoint"
    if len(matching_references) != 1:
        return False, "observation_owner_reference_is_ambiguous_within_committed_cut"

    context_time = getattr(observation, "context_time", ())
    if not any(
        getattr(getattr(reference, "domain", None), "value", None) == "world"
        and getattr(reference, "kind", None)
        in {"world_target_causal_tick", "world_causal_tick"}
        and getattr(reference, "value", None) == committed_cut.causal_tick
        for reference in context_time
    ):
        return False, "observation_world_causal_tick_does_not_match"

    transformation = getattr(lineage, "transformation", None)
    configuration = dict(getattr(transformation, "effective_configuration", ()))
    if configuration.get("world_id") != committed_cut.world_id:
        return False, "observation_world_identity_does_not_match"

    return True, None


def _associate_messages(
    messages: Sequence[object],
    *,
    association: LabObservationAssociation,
    committed_cut: _CommittedWorldCut,
) -> LabObservationRead:
    matching: list[object] = []
    mismatch_reasons: list[str] = []
    for message in messages:
        observation = getattr(message, "observation", None)
        if observation is None:
            mismatch_reasons.append("plane_message_has_no_observation")
            continue
        matches, reason = _context_matches(observation, association, committed_cut)
        if matches:
            matching.append(message)
        elif reason:
            mismatch_reasons.append(reason)

    if matching:
        return LabObservationRead(
            LabObservationReadStatus.ASSOCIATED,
            association,
            tuple(matching),
            reason="matched_exact_committed_cut; source authority and claim are unchanged",
        )
    return LabObservationRead(
        LabObservationReadStatus.UNASSOCIATED,
        association,
        reason=(
            ";".join(sorted(set(mismatch_reasons)))
            if mismatch_reasons
            else "no matching message in current volatile view; not source absence"
        ),
    )


def associate_current_messages(
    plane: _ObservationPlane,
    *,
    association: LabObservationAssociation,
    committed_cut: _CommittedWorldCut,
    family: str | None = None,
) -> LabObservationRead:
    """Associate only currently retained messages matching one committed cut.

    The current view is bounded and volatile. An empty result says only that no
    matching message is in this view; it is not a census or evidence of source
    absence.
    """
    return _associate_messages(
        plane.current_messages(family=family),
        association=association,
        committed_cut=committed_cut,
    )


def associate_stream_messages(
    subscription: object,
    *,
    association: LabObservationAssociation,
    committed_cut: _CommittedWorldCut,
    max_messages: int = 512,
) -> LabObservationRead:
    """Drain currently delivered stream items; surface any required rebase.

    A rebase/overflow/expiry is returned as an incomplete read, never as an
    empty-source conclusion. The caller remains responsible for closing the
    Observation subscription and deciding how/when to rebase.
    """
    if type(max_messages) is not int or max_messages < 1:
        raise ValueError("max_messages must be a positive integer")
    consumer_queue = getattr(subscription, "queue", None)
    if consumer_queue is None or not hasattr(consumer_queue, "get_nowait"):
        raise TypeError("subscription must be an Observation Plane stream subscription")

    messages: list[object] = []
    previous_sequence: int | None = None
    for _ in range(max_messages):
        try:
            item = consumer_queue.get_nowait()
        except Empty:
            break
        if hasattr(item, "reason") and hasattr(item, "sequence"):
            return LabObservationRead(
                LabObservationReadStatus.REBASE_REQUIRED,
                association,
                reason=str(item.reason),
                sequence=item.sequence,
            )
        sequence = getattr(item, "sequence", None)
        if type(sequence) is not int or sequence < 1:
            return LabObservationRead(
                LabObservationReadStatus.REBASE_REQUIRED,
                association,
                reason="stream_message_sequence_invalid",
                sequence=sequence if type(sequence) is int else None,
            )
        if previous_sequence is not None and sequence <= previous_sequence:
            return LabObservationRead(
                LabObservationReadStatus.REBASE_REQUIRED,
                association,
                reason="stream_sequence_duplicate_or_out_of_order",
                sequence=sequence,
            )
        previous_sequence = sequence
        messages.append(item)
    if not consumer_queue.empty():
        # A bounded drain cannot claim to have observed a complete available
        # batch. Require the caller to rebase rather than silently treating a
        # truncated prefix as the whole current delivery window.
        return LabObservationRead(
            LabObservationReadStatus.REBASE_REQUIRED,
            association,
            reason="consumer_batch_limit_exceeded",
            sequence=getattr(messages[-1], "sequence", None) if messages else None,
        )
    return _associate_messages(
        messages,
        association=association,
        committed_cut=committed_cut,
    )


__all__ = [
    "LabObservationAssociation",
    "LabObservationRead",
    "LabObservationReadStatus",
    "associate_current_messages",
    "associate_stream_messages",
]
