from __future__ import annotations

import json
from hashlib import sha256
from typing import Any, Iterable


def compute_world_digest(events: Iterable[Any]) -> str:
    """Compute a deterministic SHA-256 hash of a supported event stream.

    Includes the full exogenous event: step, host, truth label, threat flag,
    phase, drift state and the agent's observation vector (roadmap safety
    finding A01). Earlier this hashed only step/host_index/truth_label/
    is_threat — two worlds that differed only in their observations (e.g.
    different drift magnitude) produced the *same* digest despite the
    agent seeing materially different data every step. Never includes
    anything the agent itself decided — this stays evaluator/world-side.

    Event objects must expose the fields used below. Plain strings are also
    accepted as deterministic opaque events. Other shapes are rejected rather
    than hashed through ``str()``, whose default object representation may
    include process-specific memory addresses.
    """
    h = sha256()
    for ev in events:
        has_event_fields = all(
            hasattr(ev, field)
            for field in ("step", "host_index", "truth_label", "is_threat")
        )
        if has_event_fields:
            step = ev.step
            host_index = ev.host_index
            truth_label = ev.truth_label
            is_threat = ev.is_threat
            if (
                type(step) is not int
                or type(host_index) is not int
                or type(truth_label) is not str
                or type(is_threat) is not bool
            ):
                raise TypeError("event fields must use deterministic scalar types")
            observation = getattr(ev, "observation", None)
            vector = (
                observation.vector()
                if observation is not None and hasattr(observation, "vector")
                else ()
            )
            if any(type(value) not in (int, float) for value in vector):
                raise TypeError("observation vector values must be int or float")
            values = ",".join(repr(float(value)) for value in vector)
            phase = getattr(ev, "phase", "")
            drift_state = getattr(ev, "drift_state", "")
            if type(phase) is not str or type(drift_state) is not str:
                raise TypeError("event phase and drift_state must be strings")
            chunk = (
                f"event:{step}:{host_index}:{truth_label}:{is_threat}:{phase}:{drift_state}:{values}\n"
            ).encode("utf-8")
        elif isinstance(ev, str):
            chunk = f"str:{ev}\n".encode("utf-8")
        else:
            raise TypeError(
                "unsupported event type for deterministic world digest: "
                f"{type(ev).__module__}.{type(ev).__qualname__}"
            )
        h.update(chunk)
    return h.hexdigest()


def compute_config_digest(config: dict[str, Any]) -> str:
    """Compute deterministic SHA-256 hash of configuration dictionary."""
    payload = json.dumps(config, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(payload).hexdigest()
