from __future__ import annotations

from dataclasses import dataclass
from queue import Queue
from types import SimpleNamespace

import pytest

from lab.observation_consumer import (
    LabObservationAssociation,
    LabObservationReadStatus,
    associate_current_messages,
    associate_stream_messages,
)


@dataclass(frozen=True)
class _OwnerReference:
    owner: str
    owner_identity: str
    sha256: str


@dataclass(frozen=True)
class _CommittedCut:
    world_id: str = "world-1"
    causal_tick: int = 7
    commit_id: str = "commit-7"
    owner_checkpoint_references: tuple[_OwnerReference, ...] = (
        _OwnerReference("environment", "env-1", "a" * 64),
    )


def _message(
    *,
    authority: str = "environment",
    world_id: str = "world-1",
    tick: int = 7,
    sequence: int = 3,
):
    observation = SimpleNamespace(
        claim=SimpleNamespace(authority=SimpleNamespace(value=authority)),
        family=SimpleNamespace(authority=authority),
        lineage=SimpleNamespace(
            parents=(SimpleNamespace(reference="a" * 64),),
            transformation=SimpleNamespace(effective_configuration=(("world_id", world_id),)),
        ),
        context_time=(
            SimpleNamespace(
                domain=SimpleNamespace(value="world"),
                kind="world_target_causal_tick",
                value=tick,
            ),
        ),
    )
    return SimpleNamespace(sequence=sequence, observation=observation)


class _Plane:
    def __init__(self, messages=()):
        self.messages = tuple(messages)

    def current_messages(self, *, family=None):
        return self.messages


def _association(cut: _CommittedCut | None = None) -> LabObservationAssociation:
    return LabObservationAssociation.for_committed_cut(
        experiment_id="experiment-1",
        run_id="run-1",
        committed_cut=cut or _CommittedCut(),
    )


def test_current_read_associates_exact_committed_message_without_rewriting_it():
    message = _message()
    result = associate_current_messages(
        _Plane((message,)),
        association=_association(),
        committed_cut=_CommittedCut(),
    )

    assert result.status is LabObservationReadStatus.ASSOCIATED
    assert result.messages == (message,)
    assert result.messages[0] is message
    assert result.messages[0].observation.claim.authority.value == "environment"


def test_empty_current_view_is_not_reported_as_source_absence():
    result = associate_current_messages(
        _Plane(), association=_association(), committed_cut=_CommittedCut()
    )

    assert result.status is LabObservationReadStatus.UNASSOCIATED
    assert "not source absence" in result.reason


@pytest.mark.parametrize(
    "message",
    (
        _message(authority="world"),
        _message(world_id="world-other"),
        _message(tick=6),
        _message(tick=8),
    ),
)
def test_mismatched_authority_world_or_causal_tick_is_not_associated(message):
    result = associate_current_messages(
        _Plane((message,)), association=_association(), committed_cut=_CommittedCut()
    )

    assert result.status is LabObservationReadStatus.UNASSOCIATED
    assert result.messages == ()


def test_lab_association_cannot_be_reused_for_another_committed_cut():
    cut = _CommittedCut()
    mismatched_cut = _CommittedCut(causal_tick=8, commit_id="commit-8")
    result = associate_current_messages(
        _Plane((_message(),)),
        association=_association(cut),
        committed_cut=mismatched_cut,
    )

    assert result.status is LabObservationReadStatus.UNASSOCIATED
    assert result.reason == "lab_context_does_not_match_committed_cut"


def test_message_without_exact_owner_checkpoint_parent_is_not_associated():
    message = _message()
    message.observation.lineage.parents = (SimpleNamespace(reference="b" * 64),)

    result = associate_current_messages(
        _Plane((message,)), association=_association(), committed_cut=_CommittedCut()
    )

    assert result.status is LabObservationReadStatus.UNASSOCIATED
    assert result.reason == "observation_does_not_reference_committed_owner_checkpoint"


def test_stream_surfaces_rebase_without_claiming_absence_and_caller_closes():
    item = SimpleNamespace(reason="replay_expired", sequence=12)
    subscription = SimpleNamespace(queue=Queue())
    subscription.queue.put_nowait(item)

    result = associate_stream_messages(
        subscription,
        association=_association(),
        committed_cut=_CommittedCut(),
    )

    assert result.status is LabObservationReadStatus.REBASE_REQUIRED
    assert result.reason == "replay_expired"
    assert result.sequence == 12


def test_stream_batch_limit_requires_rebase_instead_of_returning_partial_batch():
    subscription = SimpleNamespace(queue=Queue())
    subscription.queue.put_nowait(_message())
    subscription.queue.put_nowait(_message(tick=6))

    result = associate_stream_messages(
        subscription,
        association=_association(),
        committed_cut=_CommittedCut(),
        max_messages=1,
    )

    assert result.status is LabObservationReadStatus.REBASE_REQUIRED
    assert result.reason == "consumer_batch_limit_exceeded"
    assert result.sequence == 3


@pytest.mark.parametrize(
    ("sequences", "expected_sequence"),
    (((3, 3), 3), ((4, 2), 2)),
)
def test_stream_duplicate_or_out_of_order_sequence_requires_rebase(
    sequences, expected_sequence
):
    subscription = SimpleNamespace(queue=Queue())
    for sequence in sequences:
        subscription.queue.put_nowait(_message(sequence=sequence))

    result = associate_stream_messages(
        subscription,
        association=_association(),
        committed_cut=_CommittedCut(),
    )

    assert result.status is LabObservationReadStatus.REBASE_REQUIRED
    assert result.reason == "stream_sequence_duplicate_or_out_of_order"
    assert result.sequence == expected_sequence


def test_stream_sequence_gaps_are_allowed_and_not_world_time():
    subscription = SimpleNamespace(queue=Queue())
    subscription.queue.put_nowait(_message(sequence=3))
    subscription.queue.put_nowait(_message(sequence=9))

    result = associate_stream_messages(
        subscription,
        association=_association(),
        committed_cut=_CommittedCut(),
    )

    assert result.status is LabObservationReadStatus.ASSOCIATED
    assert tuple(message.sequence for message in result.messages) == (3, 9)


def test_stream_invalid_sequence_requires_rebase():
    subscription = SimpleNamespace(queue=Queue())
    subscription.queue.put_nowait(_message(sequence=0))

    result = associate_stream_messages(
        subscription,
        association=_association(),
        committed_cut=_CommittedCut(),
    )

    assert result.status is LabObservationReadStatus.REBASE_REQUIRED
    assert result.reason == "stream_message_sequence_invalid"
    assert result.sequence == 0


@pytest.mark.parametrize("value", (0, -1, True, 1.0))
def test_stream_bound_must_be_a_positive_integer(value):
    with pytest.raises(ValueError, match="positive integer"):
        associate_stream_messages(
            SimpleNamespace(queue=Queue()),
            association=_association(),
            committed_cut=_CommittedCut(),
            max_messages=value,
        )
