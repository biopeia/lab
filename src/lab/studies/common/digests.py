from __future__ import annotations

import json
import math
import struct
from hashlib import sha256
from typing import Any, Iterable


_WORLD_DIGEST_PREFIX = b"biopeia.lab.world-digest.v2\0"
_CONFIG_DIGEST_PREFIX = b"biopeia.lab.config-digest.v2\0"


def _canonical_json(value: Any) -> bytes:
    """Encode a JSON-shaped value without coercion or non-finite numbers."""
    _validate_json_value(value)
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _validate_json_value(value: Any) -> None:
    if value is None or type(value) in (bool, int, str):
        return
    if type(value) is float:
        if not math.isfinite(value):
            raise ValueError("digest values must not contain non-finite numbers")
        return
    if type(value) is list:
        for item in value:
            _validate_json_value(item)
        return
    if type(value) is dict:
        if any(type(key) is not str for key in value):
            raise TypeError("digest object keys must be strings")
        for item in value.values():
            _validate_json_value(item)
        return
    raise TypeError(
        "unsupported value for deterministic digest: "
        f"{type(value).__module__}.{type(value).__qualname__}"
    )


def _update_framed(hasher, payload: bytes) -> None:
    hasher.update(struct.pack(">Q", len(payload)))
    hasher.update(payload)


def compute_world_digest(events: Iterable[Any]) -> str:
    """Compute a versioned deterministic SHA-256 hash of an event stream.

    Includes the full exogenous event: step, host, truth label, threat flag,
    phase, drift state and the agent's observation vector (roadmap safety
    finding A01). Earlier this hashed only step/host_index/truth_label/
    is_threat — two worlds that differed only in their observations (e.g.
    different drift magnitude) produced the *same* digest despite the
    agent seeing materially different data every step. Never includes
    anything the agent itself decided — this stays evaluator/world-side.

    Event objects must expose the fields used below. Plain strings are also
    accepted as deterministic opaque events. Each event is encoded as canonical
    JSON and length-prefixed under a v2 domain separator, so field/event
    boundaries and JSON scalar types remain distinguishable. This changes the
    digest values from the previous delimiter-based encoding. Other shapes are
    rejected rather than hashed through ``str()``, whose default object
    representation may include process-specific memory addresses.
    """
    h = sha256(_WORLD_DIGEST_PREFIX)
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
            if hasattr(ev, "observation"):
                observation = ev.observation
                if observation is None:
                    observation_data = None
                elif callable(getattr(observation, "vector", None)):
                    vector = tuple(observation.vector())
                    if any(type(value) not in (int, float) for value in vector):
                        raise TypeError("observation vector values must be int or float")
                    observation_data = list(vector)
                else:
                    raise TypeError("event observation must be None or expose vector()")
            else:
                observation_data = {"absent": True}
            phase = ev.phase if hasattr(ev, "phase") else {"absent": True}
            drift_state = ev.drift_state if hasattr(ev, "drift_state") else {"absent": True}
            if (hasattr(ev, "phase") and type(phase) is not str) or (
                hasattr(ev, "drift_state") and type(drift_state) is not str
            ):
                raise TypeError("event phase and drift_state must be strings")
            payload = _canonical_json([
                "event",
                step,
                host_index,
                truth_label,
                is_threat,
                phase,
                drift_state,
                observation_data,
            ])
        elif isinstance(ev, str):
            payload = _canonical_json(["str", ev])
        else:
            raise TypeError(
                "unsupported event type for deterministic world digest: "
                f"{type(ev).__module__}.{type(ev).__qualname__}"
            )
        _update_framed(h, payload)
    return h.hexdigest()


def compute_config_digest(config: dict[str, Any]) -> str:
    """Compute deterministic SHA-256 hash of configuration dictionary."""
    if type(config) is not dict:
        raise TypeError("configuration digest requires a dictionary")
    return sha256(_CONFIG_DIGEST_PREFIX + _canonical_json(config)).hexdigest()
