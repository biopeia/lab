from __future__ import annotations

import pytest

from embodiment.physiology import LivingBodyState
from environment.resource import FiniteResourceState
from world.runtime import RuntimeStatus, WorldId, WorldRuntime

from lab.interventions import (
    InterventionRequest,
    InterventionKind,
    apply_material_transfer,
)


def _owners(*, remaining: float = 3.0, energy: float = 0.5, maximum: float = 2.0):
    return (
        WorldRuntime(WorldId("lab-operator-world"), presence_id="body-1"),
        FiniteResourceState(remaining=remaining, transfer_per_tick=2.0),
        LivingBodyState(energy_reserve=energy, max_energy=maximum),
        InterventionRequest(
            "operator-7",
            "intervention-12",
            "resource-1",
            "body-1",
            2.5,
            InterventionKind.NON_EXPERIMENTAL,
        ),
    )


def test_operator_intervention_commits_before_returning_candidates_or_projection() -> None:
    world, resource, body, authorization = _owners()
    initial_resource = resource.checkpoint()
    initial_body = body.checkpoint()

    result = apply_material_transfer(
        world=world,
        resource=resource,
        body=body,
        request=authorization,
        body_id="body-1",
        source_id="resource-1",
        requested_material=2.5,
    )

    assert resource.checkpoint() == initial_resource
    assert body.checkpoint() == initial_body
    assert result.record is world.records[0]
    assert result.record.payload["event_payload"] == {
        "kind": "operator.material_transfer",
        "operator_id": "operator-7",
        "intervention_id": "intervention-12",
        "intervention_kind": "NON_EXPERIMENTAL_INTERVENTION",
        "source_id": "resource-1",
        "target_body_id": "body-1",
        "requested_material": 2.5,
        "offered_material": 2.0,
        "accepted_material": 1.5,
        "debited_material": 1.5,
    }
    assert result.resource_candidate.remaining == 1.5
    assert result.body_candidate.energy_reserve == 2.0
    assert [event["type"] for event in result.observations] == [
        "body",
        "cognition",
        "vitals",
    ]
    assert all("run_id" not in event for event in result.observations)


def test_real_run_context_is_explicit_and_not_aliased_from_intervention_id() -> None:
    world, resource, body, _ = _owners()
    authorization = InterventionRequest(
        "operator-7",
        "intervention-12",
        "resource-1",
        "body-1",
        2.5,
        InterventionKind.EXPERIMENTAL_RUN,
        run_id="run-42",
        study_id="study-3",
    )
    result = apply_material_transfer(
        world=world,
        resource=resource,
        body=body,
        request=authorization,
        body_id="body-1",
        source_id="resource-1",
        requested_material=1.0,
    )
    payload = result.record.payload["event_payload"]
    assert payload["run_id"] == "run-42"
    assert payload["study_id"] == "study-3"
    assert payload["intervention_id"] == "intervention-12"


def test_experimental_intervention_requires_real_run_context() -> None:
    with pytest.raises(ValueError, match="requires a real run_id"):
        InterventionRequest(
            "operator-7",
            "intervention-12",
            "resource-1",
            "body-1",
            2.5,
            InterventionKind.EXPERIMENTAL_RUN,
        )


def test_rejected_or_short_body_acceptance_only_debits_accepted_material() -> None:
    world, resource, body, authorization = _owners(
        remaining=0.4, energy=0.9, maximum=1.0
    )
    result = apply_material_transfer(
        world=world,
        resource=resource,
        body=body,
        request=authorization,
        body_id="body-1",
        source_id="resource-1",
        requested_material=0.8,
    )

    payload = result.record.payload["event_payload"]
    assert payload["offered_material"] == 0.4
    assert payload["accepted_material"] == pytest.approx(0.1)
    assert payload["debited_material"] == payload["accepted_material"]
    assert result.resource_candidate.remaining == pytest.approx(0.3)
    assert result.body_candidate.energy_reserve == 1.0


def test_authorization_limit_rejects_before_world_transition() -> None:
    world, resource, body, authorization = _owners()
    with pytest.raises(ValueError, match="caller-declared material limit"):
        apply_material_transfer(
            world=world,
            resource=resource,
            body=body,
            request=authorization,
            body_id="body-1",
            source_id="resource-1",
            requested_material=2.51,
        )

    assert world.causal_tick == 0
    assert world.records == ()


@pytest.mark.parametrize(
    ("body_id", "source_id"),
    [("other-body", "resource-1"), ("body-1", "other-resource")],
)
def test_authorization_is_bound_to_one_source_and_body(body_id: str, source_id: str) -> None:
    world, resource, body, authorization = _owners()
    with pytest.raises(ValueError, match="caller-declared request"):
        apply_material_transfer(
            world=world,
            resource=resource,
            body=body,
            request=authorization,
            body_id=body_id,
            source_id=source_id,
            requested_material=1.0,
        )

    assert world.causal_tick == 0
    assert world.records == ()


def test_failed_world_publication_exposes_no_candidates_or_observation(monkeypatch) -> None:
    world, resource, body, authorization = _owners()
    initial_resource = resource.checkpoint()
    initial_body = body.checkpoint()
    projected = False

    def fail_publication(_record):
        raise RuntimeError("simulated publication failure")

    def unexpected_projection(_payload):
        nonlocal projected
        projected = True
        raise AssertionError("projection ran before successful World return")

    monkeypatch.setattr(world._journal, "append", fail_publication)
    monkeypatch.setattr(
        "lab.interventions.material_transfer.runtime_tick_events", unexpected_projection
    )

    with pytest.raises(RuntimeError, match="publication failure"):
        apply_material_transfer(
            world=world,
            resource=resource,
            body=body,
            request=authorization,
            body_id="body-1",
            source_id="resource-1",
            requested_material=1.0,
        )

    assert not projected
    assert resource.checkpoint() == initial_resource
    assert body.checkpoint() == initial_body
    assert world.status is RuntimeStatus.RECOVERY_REQUIRED
    assert world.records == ()
