from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from embodiment.checkpoint import EmbodimentCheckpoint
from embodiment.metabolism import MetabolicLedger
from embodiment.physiology import LivingBodyState
from environment.identified_resource import IdentifiedFiniteResource
from environment.resource import FiniteResourceState
from world.durable_runtime import DurableJournalSnapshotStore, DurableWorldRuntime, WorldGenesisSpec
from world.manifest import CheckpointReference, WorldCausalManifestStore
from world.runtime import WorldId

from lab.interventions import (
    InterventionKind,
    InterventionRequest,
    MaterialTransferCheckpointStore,
    apply_material_transfer,
)
from lab.interventions.material_transfer import (
    EMBODIMENT_OWNER,
    EMBODIMENT_SCHEMA,
    ENVIRONMENT_OWNER,
    ENVIRONMENT_SCHEMA,
    LAB_EVIDENCE_OWNER,
)


def _owners(tmp_path, *, remaining: float = 3.0, energy: float = 0.5, maximum: float = 2.0):
    resource = IdentifiedFiniteResource(
        "resource-1",
        FiniteResourceState(remaining=remaining, transfer_per_tick=2.0),
    )
    body_state = LivingBodyState(energy_reserve=energy, max_energy=maximum)
    body = EmbodimentCheckpoint(
        body_id="body-1",
        episode_id="episode-1",
        body_state=body_state,
        metabolic_ledger=MetabolicLedger(body_state=body_state),
    )
    store = MaterialTransferCheckpointStore(tmp_path / "owner-checkpoints")
    environment_key = (ENVIRONMENT_OWNER, resource.resource_id)
    embodiment_key = (EMBODIMENT_OWNER, body.body_id)
    environment_ref = store.write(
        owner=ENVIRONMENT_OWNER,
        owner_identity=resource.resource_id,
        checkpoint_id="tick-0",
        schema_version=ENVIRONMENT_SCHEMA,
        encoded=resource.checkpoint_bytes(),
    )
    embodiment_ref = store.write(
        owner=EMBODIMENT_OWNER,
        owner_identity=body.body_id,
        checkpoint_id="tick-0",
        schema_version=EMBODIMENT_SCHEMA,
        encoded=body.to_bytes(),
    )
    contracts = {
        environment_key: store.environment_contract(resource.resource_id),
        embodiment_key: store.embodiment_contract(body.body_id),
    }
    owner_references = (environment_ref, embodiment_ref)

    def verify_files(references: tuple[CheckpointReference, ...]) -> bool:
        try:
            return all(
                hashlib.sha256(Path(ref.locator).read_bytes()).hexdigest()
                == ref.sha256
                for ref in references
            )
        except OSError:
            return False

    world_id = WorldId("lab-operator-world")
    manifest_store = WorldCausalManifestStore(tmp_path / "world" / "manifest.json")
    journal_store = DurableJournalSnapshotStore(tmp_path / "world" / "journal", world_id)
    genesis = WorldGenesisSpec(
        world_id=world_id,
        initial_presence_ids=(body.body_id,),
        registered_owner_ids=tuple(sorted((environment_key, embodiment_key))),
        initial_owner_references=owner_references,
        owner_checkpoint_contracts=contracts,
    )
    world = DurableWorldRuntime.initialize(
        genesis,
        body.body_id,
        manifest_store,
        journal_store,
        owner_checkpoint_verifier=verify_files,
    )
    request = InterventionRequest(
        "operator-7",
        "intervention-12",
        resource.resource_id,
        body.body_id,
        2.5,
        InterventionKind.NON_EXPERIMENTAL,
    )
    return world, resource, body, request, store


def _apply(world, resource, body, request, store, *, requested_material: float = 2.5):
    return apply_material_transfer(
        world=world,
        resource=resource,
        body=body,
        request=request,
        checkpoint_store=store,
        transition_id="world-transition-1",
        requested_material=requested_material,
    )


def test_intervention_commits_durable_owner_cut_and_lab_evidence(tmp_path) -> None:
    world, resource, body, request, store = _owners(tmp_path)
    initial_resource = resource.checkpoint_bytes()
    initial_body = body.to_bytes()

    result = _apply(world, resource, body, request, store)

    assert world.causal_tick == 1
    assert world.manifest.status.value == "COMMITTED"
    assert resource.checkpoint_bytes() == initial_resource
    assert body.to_bytes() == initial_body
    assert result.record is world.records[0]
    owner_refs = {
        (ref.owner, ref.owner_identity): ref for ref in world.manifest.checkpoint_references
    }
    assert set(owner_refs) == {
        (ENVIRONMENT_OWNER, resource.resource_id),
        (EMBODIMENT_OWNER, body.body_id),
        (LAB_EVIDENCE_OWNER, request.intervention_id),
        ("world-journal", world.world_id.value),
    }
    evidence = json.loads(Path(result.evidence_reference.locator).read_bytes())
    assert evidence == {
        "accepted_material": 1.5,
        "applicability": "NON_EXPERIMENTAL_INTERVENTION",
        "causal_tick": 1,
        "debited_material": 1.5,
        "intervention_id": "intervention-12",
        "offered_material": 2.0,
        "operator_id": "operator-7",
        "quantity_semantics": "unspecified_scalar_material",
        "requested_material": 2.5,
        "schema_version": 1,
        "source_id": "resource-1",
        "target_body_id": "body-1",
        "transition_id": "world-transition-1",
        "world_id": "lab-operator-world",
    }
    assert result.resource_candidate.state.remaining == 1.5
    assert result.body_candidate.body_state.energy_reserve == 2.0
    assert [event["type"] for event in result.observations] == ["body", "cognition", "vitals"]
    assert all("run_id" not in event for event in result.observations)


def test_real_run_context_is_explicit_in_committed_evidence(tmp_path) -> None:
    world, resource, body, _, store = _owners(tmp_path)
    request = InterventionRequest(
        "operator-7",
        "intervention-12",
        resource.resource_id,
        body.body_id,
        2.5,
        InterventionKind.EXPERIMENTAL_RUN,
        run_id="run-42",
        study_id="study-3",
    )
    result = _apply(world, resource, body, request, store, requested_material=1.0)
    evidence = json.loads(Path(result.evidence_reference.locator).read_bytes())
    assert evidence["run_id"] == "run-42"
    assert evidence["study_id"] == "study-3"
    assert evidence["intervention_id"] == "intervention-12"
    assert result.evidence_reference.owner_identity != evidence["run_id"]


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


def test_transition_id_is_distinct_from_intervention_id(tmp_path) -> None:
    world, resource, body, request, store = _owners(tmp_path)
    with pytest.raises(ValueError, match="distinct from intervention_id"):
        apply_material_transfer(
            world=world,
            checkpoint_store=store,
            resource=resource,
            body=body,
            request=request,
            transition_id=request.intervention_id,
            requested_material=1.0,
        )
    assert world.causal_tick == 0
    assert world.manifest.status.value == "COMMITTED"


def test_short_body_acceptance_debits_only_accepted_material(tmp_path) -> None:
    world, resource, body, request, store = _owners(tmp_path, remaining=0.4, energy=0.9, maximum=1.0)
    result = _apply(world, resource, body, request, store, requested_material=0.8)
    evidence = json.loads(Path(result.evidence_reference.locator).read_bytes())
    assert evidence["offered_material"] == 0.4
    assert evidence["accepted_material"] == pytest.approx(0.1)
    assert evidence["debited_material"] == evidence["accepted_material"]
    assert result.resource_candidate.state.remaining == pytest.approx(0.3)
    assert result.body_candidate.body_state.energy_reserve == 1.0


def test_request_identity_mismatch_fails_before_world_preparing(tmp_path) -> None:
    world, resource, body, request, store = _owners(tmp_path)
    mismatch = InterventionRequest(
        request.operator_id,
        request.intervention_id,
        "other-resource",
        request.target_body_id,
        request.maximum_material,
        request.kind,
    )
    with pytest.raises(ValueError, match="Environment owner identity"):
        _apply(world, resource, body, mismatch, store)
    assert world.causal_tick == 0
    assert world.manifest.status.value == "COMMITTED"


def test_world_genesis_checkpoint_identity_mismatch_fails_closed(tmp_path) -> None:
    world, resource, body, request, store = _owners(tmp_path)
    resource.state.remaining -= 0.1
    with pytest.raises(ValueError, match="does not match its committed owner checkpoint"):
        _apply(world, resource, body, request, store)
    assert world.causal_tick == 0
    assert world.manifest.status.value == "COMMITTED"


def test_owner_checkpoint_failure_leaves_no_committed_next_cut(tmp_path, monkeypatch) -> None:
    world, resource, body, request, store = _owners(tmp_path)
    initial_resource = resource.checkpoint_bytes()
    initial_body = body.to_bytes()
    original_write = store.write

    def fail_lab_evidence(**kwargs):
        if kwargs["owner"] == LAB_EVIDENCE_OWNER:
            raise OSError("evidence checkpoint failure")
        return original_write(**kwargs)

    monkeypatch.setattr(store, "write", fail_lab_evidence)
    with pytest.raises(OSError, match="evidence checkpoint failure"):
        _apply(world, resource, body, request, store)

    assert world.causal_tick == 0
    assert world.manifest.pending_tick == 1
    assert world.manifest.status.value == "RECOVERY_REQUIRED"
    assert resource.checkpoint_bytes() == initial_resource
    assert body.to_bytes() == initial_body
