from __future__ import annotations

from dataclasses import dataclass

import pytest

from lab.studies.common.digests import compute_world_digest


@dataclass(slots=True, frozen=True)
class _Observation:
    values: tuple[float, ...]

    def vector(self) -> tuple[float, ...]:
        return self.values


@dataclass(slots=True, frozen=True)
class _Event:
    step: int
    host_index: int
    truth_label: str
    is_threat: bool
    phase: str
    drift_state: str
    observation: _Observation


def _event(
    step: int,
    observation_values: tuple[float, ...],
    *,
    phase: str = "steady",
    drift_state: str = "none",
) -> _Event:
    return _Event(
        step=step,
        host_index=0,
        truth_label="benign",
        is_threat=False,
        phase=phase,
        drift_state=drift_state,
        observation=_Observation(observation_values),
    )


def test_digest_differs_when_only_the_observation_vector_differs():
    """Roadmap safety finding A01: two otherwise-identical event streams
    whose actual observations differ must never hash identically."""
    events_a = [_event(1, (1.0, 2.0, 3.0))]
    events_b = [_event(1, (1.0, 2.0, 999.0))]

    assert compute_world_digest(events_a) != compute_world_digest(events_b)


def test_digest_differs_when_phase_differs():
    events_a = [_event(1, (1.0,), phase="steady")]
    events_b = [_event(1, (1.0,), phase="drifting")]

    assert compute_world_digest(events_a) != compute_world_digest(events_b)


def test_digest_differs_when_drift_state_differs():
    events_a = [_event(1, (1.0,), drift_state="none")]
    events_b = [_event(1, (1.0,), drift_state="active")]

    assert compute_world_digest(events_a) != compute_world_digest(events_b)


def test_digest_is_stable_for_identical_event_streams():
    events_a = [_event(1, (1.0, 2.0, 3.0)), _event(2, (4.0, 5.0, 6.0))]
    events_b = [_event(1, (1.0, 2.0, 3.0)), _event(2, (4.0, 5.0, 6.0))]

    assert compute_world_digest(events_a) == compute_world_digest(events_b)


def test_digest_accepts_deterministic_plain_string_events():
    assert compute_world_digest(["plain-string-event"]) == compute_world_digest(
        ["plain-string-event"]
    )


def test_digest_rejects_objects_with_process_specific_default_repr():
    class UnsupportedEvent:
        pass

    first = UnsupportedEvent()
    second = UnsupportedEvent()

    # The default repr embeds each instance's address, so str() is not a
    # deterministic event encoding even for otherwise identical objects.
    assert repr(first) != repr(second)
    with pytest.raises(TypeError, match="unsupported event type"):
        compute_world_digest([first])
