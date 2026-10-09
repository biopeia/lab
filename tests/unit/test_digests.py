from __future__ import annotations

from dataclasses import dataclass

import pytest

from lab.studies.common.digests import compute_config_digest, compute_world_digest


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


def test_digest_frames_strings_and_event_fields_without_separator_collisions():
    first = _event(1, (), phase="b:c", drift_state="d")
    second = _event(1, (), phase="b", drift_state="c:d")
    assert compute_world_digest([first]) != compute_world_digest([second])
    assert compute_world_digest(["a\nstr:b"]) != compute_world_digest(["a", "b"])


def test_digest_preserves_numeric_type_and_observation_availability():
    integer = _event(1, (1,))
    floating = _event(1, (1.0,))
    missing = _event(1, ())
    unavailable = _Event(
        step=missing.step,
        host_index=missing.host_index,
        truth_label=missing.truth_label,
        is_threat=missing.is_threat,
        phase=missing.phase,
        drift_state=missing.drift_state,
        observation=None,
    )

    assert compute_world_digest([integer]) != compute_world_digest([floating])
    assert compute_world_digest([missing]) != compute_world_digest([unavailable])


def test_config_digest_preserves_json_number_types_and_rejects_coercions():
    assert compute_config_digest({"value": 1}) != compute_config_digest({"value": 1.0})
    with pytest.raises(TypeError, match="keys must be strings"):
        compute_config_digest({1: "value"})  # type: ignore[dict-item]
    with pytest.raises(ValueError, match="non-finite"):
        compute_config_digest({"value": float("nan")})
