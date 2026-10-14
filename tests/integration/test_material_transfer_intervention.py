from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from embodiment.checkpoint import EmbodimentCheckpoint
from embodiment.metabolism import MetabolicLedger
from embodiment.physiology import LivingBodyState
from environment.identified_resource import IdentifiedFiniteResource
from environment.resource import FiniteResourceState
from observation.plane import ObservationPlane
from world.durable_runtime import DurableJournalSnapshotStore, DurableWorldRuntime, WorldGenesisSpec
from world.manifest import CheckpointReference, WorldCausalManifestStore
from world.runtime import PresenceId, WorldId
from world.durable_runtime import PresenceOwnerLink

from lab.interventions import (
    InterventionKind,
    InterventionRequest,
    MaterialTransferCheckpointStore,
    MaterialTransferOwnerRestoration,
    apply_material_transfer,
    publish_material_transfer_observations,
)
from lab.interventions.material_transfer import (
    EMBODIMENT_OWNER,
    EMBODIMENT_SCHEMA,
    ENVIRONMENT_OWNER,
    ENVIRONMENT_SCHEMA,
    LAB_EVIDENCE_OWNER,
    LabInterventionEvidenceCodec,
)
import lab.interventions.material_transfer as material_transfer_module


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
        environment_key: IdentifiedFiniteResource,
        embodiment_key: EmbodimentCheckpoint,
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
    presence_id = PresenceId("presence-1")
    manifest_store = WorldCausalManifestStore(tmp_path / "world" / "manifest.json")
    journal_store = DurableJournalSnapshotStore(tmp_path / "world" / "journal", world_id)
    genesis = WorldGenesisSpec(
        world_id=world_id,
        initial_presence_ids=(presence_id.value,),
        registered_owner_ids=tuple(sorted((environment_key, embodiment_key))),
        initial_owner_references=owner_references,
        owner_checkpoint_contracts=contracts,
        presence_owner_links=(
            PresenceOwnerLink(presence_id, EMBODIMENT_OWNER, body.body_id),
        ),
    )
    world = DurableWorldRuntime.initialize(
        genesis,
        presence_id.value,
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


def _apply(
    world,
    resource,
    body,
    request,
    store,
    *,
    intervention_action_id: str = "action-1",
    transition_id: str = "world-transition-1",
    requested_material: float = 2.5,
):
    return apply_material_transfer(
        world=world,
        resource=resource,
        body=body,
        request=request,
        checkpoint_store=store,
        transition_id=transition_id,
        intervention_action_id=intervention_action_id,
        requested_material=requested_material,
    )


def test_environment_checkpoint_schema_matches_current_owner_contract() -> None:
    resource = IdentifiedFiniteResource(
        "resource-1",
        FiniteResourceState(remaining=3.0, transfer_per_tick=2.0),
    )
    encoded = resource.checkpoint_bytes()

    assert ENVIRONMENT_SCHEMA == IdentifiedFiniteResource.OWNER_SCHEMA
    assert IdentifiedFiniteResource.validate_checkpoint(
        encoded, resource.resource_id, ENVIRONMENT_SCHEMA
    )
    assert not IdentifiedFiniteResource.validate_checkpoint(
        encoded, resource.resource_id, "environment-identified-resource-v1"
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
    assert result.record in world.records
    assert result.record.causal_tick == 1
    owner_record = next(
        record
        for record in world.records
        if record.record_type == "world.owner_record.committed"
    )
    assert owner_record.payload["owner_id"] == LAB_EVIDENCE_OWNER
    assert owner_record.payload["owner_identity"] == request.intervention_id
    assert owner_record.payload["owner_record_id"] == "action-1"
    evidence_pointer = owner_record.payload["data"]["evidence_checkpoint"]
    assert evidence_pointer["sha256"] == result.evidence_reference.sha256
    assert Path(evidence_pointer["locator"]).read_bytes() == Path(
        result.evidence_reference.locator
    ).read_bytes()
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
        "intervention_action_id": "action-1",
        "offered_material": 2.0,
        "operator_id": "operator-7",
        "quantity_semantics": "unspecified_scalar_material",
        "requested_material": 2.5,
        "schema_version": 2,
        "source_id": "resource-1",
        "target_body_id": "body-1",
        "transition_id": "world-transition-1",
        "world_id": "lab-operator-world",
    }
    assert result.resource_candidate.state.remaining == 1.5
    assert result.body_candidate.body_state.energy_reserve == 2.0
    assert result.committed_cut.causal_tick == result.record.causal_tick == 1
    assert result.committed_cut.commit_id == "world-transition-1"


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


def test_experimental_material_transfer_publishes_real_owner_snapshots_after_commit(tmp_path) -> None:
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
        experiment_id="experiment-5",
    )
    result = _apply(world, resource, body, request, store, requested_material=1.0)
    plane = ObservationPlane()

    published = publish_material_transfer_observations(
        world=world,
        plane=plane,
        result=result,
    )

    assert world.causal_tick == 1  # publication did not re-execute the transition
    assert published.committed_cut == result.committed_cut
    assert published.publication.delivery_sequences == (1, 2)
    assert published.association.experiment_id == "experiment-5"
    assert published.association.run_id == "run-42"
    assert published.read.status.value == "associated"
    assert len(published.read.messages) == 2
    env_observation, body_observation = tuple(
        message.observation for message in published.read.messages
    )
    assert env_observation.claim.authority.value == "environment"
    assert env_observation.claim.value == {"remaining": 2.0}
    assert body_observation.claim.authority.value == "embodiment"
    assert body_observation.claim.value == {
        "amount": {"value": 1.5, "quantity_kind": "model_amount"},
        "capacity": {"value": 2.0, "quantity_kind": "model_amount"},
        "fraction": {"value": 0.75, "unit": "1"},
    }
    for observation in (env_observation, body_observation):
        assert observation.context_time[-1].value == 1
        assert dict(observation.lineage.transformation.effective_configuration)["commit_id"] == "world-transition-1"
    assert env_observation.lineage.parents[0].reference == next(
        ref.sha256 for ref in result.committed_cut.owner_checkpoint_references
        if ref.owner == ENVIRONMENT_OWNER
    )
    assert body_observation.lineage.parents[0].reference == next(
        ref.sha256 for ref in result.committed_cut.owner_checkpoint_references
        if ref.owner == EMBODIMENT_OWNER
    )


@pytest.mark.parametrize(
    ("field", "forged_value"),
    (("run_id", "run-claimed"), ("experiment_id", "experiment-claimed")),
)
def test_publication_rejects_experiment_association_not_bound_to_committed_evidence(
    tmp_path, field, forged_value
) -> None:
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
        experiment_id="experiment-5",
    )
    result = _apply(world, resource, body, request, store, requested_material=1.0)
    plane = ObservationPlane()
    forged_result = replace(result, **{field: forged_value})

    with pytest.raises(ValueError, match="does not match committed Lab evidence"):
        publish_material_transfer_observations(
            world=world,
            plane=plane,
            result=forged_result,
        )

    assert plane.current_messages() == ()
    assert world.causal_tick == result.record.causal_tick == 1


def test_publication_rejects_evidence_reference_not_bound_to_committed_cut(tmp_path) -> None:
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
        experiment_id="experiment-5",
    )
    result = _apply(world, resource, body, request, store, requested_material=1.0)
    plane = ObservationPlane()
    forged_reference = replace(result.evidence_reference, sha256="0" * 64)

    with pytest.raises(ValueError, match="evidence reference does not match committed World cut"):
        publish_material_transfer_observations(
            world=world,
            plane=plane,
            result=replace(result, evidence_reference=forged_reference),
        )

    assert plane.current_messages() == ()
    assert world.causal_tick == result.record.causal_tick == 1


def test_publication_rejects_modified_lab_evidence_bytes_before_observation(tmp_path) -> None:
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
        experiment_id="experiment-5",
    )
    result = _apply(world, resource, body, request, store, requested_material=1.0)
    Path(result.evidence_reference.locator).write_bytes(b"corrupted evidence")
    plane = ObservationPlane()

    with pytest.raises(ValueError, match="evidence digest does not match its reference"):
        publish_material_transfer_observations(
            world=world,
            plane=plane,
            result=result,
        )

    assert plane.current_messages() == ()
    assert world.causal_tick == result.record.causal_tick == 1


def test_observation_publication_failure_does_not_repeat_committed_world_transition(
    tmp_path, monkeypatch
) -> None:
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
        experiment_id="experiment-5",
    )
    result = _apply(world, resource, body, request, store, requested_material=1.0)
    plane = ObservationPlane()
    committed_tick = world.causal_tick
    committed_cut = result.committed_cut

    def fail_publication(*args, **kwargs):
        raise OSError("observation publication unavailable")

    monkeypatch.setattr(
        material_transfer_module,
        "publish_committed_owner_observations",
        fail_publication,
    )
    with pytest.raises(OSError, match="observation publication unavailable"):
        publish_material_transfer_observations(world=world, plane=plane, result=result)

    assert world.causal_tick == committed_tick == 1
    assert world.manifest.status.value == "COMMITTED"
    assert world.committed_cut_for(
        world_id=committed_cut.world_id,
        causal_tick=committed_tick,
        commit_id=committed_cut.commit_id,
    ) == committed_cut
    assert plane.current_messages() == ()


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
            intervention_action_id="action-1",
            transition_id=request.intervention_id,
            requested_material=1.0,
        )
    assert world.causal_tick == 0
    assert world.manifest.status.value == "COMMITTED"


def test_one_intervention_can_commit_distinct_actions_and_preserve_evidence_after_restart(tmp_path) -> None:
    world, resource, body, request, store = _owners(tmp_path)
    first = _apply(world, resource, body, request, store, intervention_action_id="transfer-1")
    second = _apply(
        world,
        first.resource_candidate,
        first.body_candidate,
        request,
        store,
        intervention_action_id="transfer-2",
        transition_id="world-transition-2",
        requested_material=0.5,
    )

    assert second.record.causal_tick == 2
    action_records = [
        record
        for record in world.records
        if record.record_type == "world.owner_record.committed"
        and record.payload["owner_id"] == LAB_EVIDENCE_OWNER
        and record.payload["owner_identity"] == request.intervention_id
    ]
    assert [record.payload["owner_record_id"] for record in action_records] == [
        "transfer-1",
        "transfer-2",
    ]
    first_pointer = action_records[0].payload["data"]["evidence_checkpoint"]
    assert Path(first_pointer["locator"]).is_file()
    assert hashlib.sha256(Path(first_pointer["locator"]).read_bytes()).hexdigest() == first_pointer[
        "sha256"
    ]
    first_evidence = json.loads(Path(first_pointer["locator"]).read_bytes())
    assert first_evidence["intervention_id"] == request.intervention_id
    assert first_evidence["intervention_action_id"] == action_records[0].payload["owner_record_id"]
    assert first_evidence["causal_tick"] == action_records[0].causal_tick
    assert second.evidence_reference.locator == action_records[1].payload["data"]["evidence_checkpoint"]["locator"]

    owner_restoration = MaterialTransferOwnerRestoration()
    restored = DurableWorldRuntime.restore(
        world.world_id,
        world.presence_id,
        world._manifest_store,
        world._journal_store,
        owner_checkpoint_verifier=world._owner_checkpoint_verifier,
        owner_checkpoint_contracts={
            **owner_restoration.contracts(
                resource_id=resource.resource_id, body_id=body.body_id
            ),
            (LAB_EVIDENCE_OWNER, request.intervention_id): LabInterventionEvidenceCodec,
        },
        owner_checkpoint_restorer=owner_restoration.restore,
    )
    assert owner_restoration.resource is not None
    assert owner_restoration.body is not None
    assert owner_restoration.resource.state.remaining == pytest.approx(1.5)
    assert owner_restoration.body.body_state.energy_reserve == pytest.approx(2.0)
    restored_first = next(
        record
        for record in restored.records
        if record.record_type == "world.owner_record.committed"
        and record.payload["owner_record_id"] == "transfer-1"
    )
    restored_pointer = restored_first.payload["data"]["evidence_checkpoint"]
    assert restored_pointer == first_pointer
    assert hashlib.sha256(Path(restored_pointer["locator"]).read_bytes()).hexdigest() == restored_pointer[
        "sha256"
    ]
    with pytest.raises(ValueError, match="action id was already committed"):
        _apply(
            restored,
            second.resource_candidate,
            second.body_candidate,
            request,
            store,
            intervention_action_id="transfer-1",
            transition_id="world-transition-3",
            requested_material=0.1,
        )
    assert restored.causal_tick == 2


def test_duplicate_intervention_action_id_is_rejected_without_new_commit(tmp_path) -> None:
    world, resource, body, request, store = _owners(tmp_path)
    first = _apply(world, resource, body, request, store, intervention_action_id="transfer-1")

    with pytest.raises(ValueError, match="action id was already committed"):
        _apply(
            world,
            first.resource_candidate,
            first.body_candidate,
            request,
            store,
            intervention_action_id="transfer-1",
            transition_id="world-transition-2",
            requested_material=0.5,
        )

    assert world.causal_tick == 1
    assert world.manifest.status.value == "COMMITTED"


def test_same_intervention_id_cannot_change_immutable_context(tmp_path) -> None:
    world, resource, body, request, store = _owners(tmp_path)
    first = _apply(world, resource, body, request, store, intervention_action_id="transfer-1")
    changed_context = InterventionRequest(
        "different-operator",
        request.intervention_id,
        request.source_id,
        request.target_body_id,
        request.maximum_material,
        request.kind,
    )

    with pytest.raises(ValueError, match="immutable intervention context"):
        _apply(
            world,
            first.resource_candidate,
            first.body_candidate,
            changed_context,
            store,
            intervention_action_id="transfer-2",
            transition_id="world-transition-2",
            requested_material=0.5,
        )

    assert world.causal_tick == 1
    assert world.manifest.status.value == "COMMITTED"


def test_actions_in_one_intervention_can_have_distinct_action_scoped_limits(tmp_path) -> None:
    world, resource, body, request, store = _owners(tmp_path)
    first = _apply(world, resource, body, request, store, intervention_action_id="transfer-1")
    second_request = InterventionRequest(
        request.operator_id,
        request.intervention_id,
        request.source_id,
        request.target_body_id,
        0.75,
        request.kind,
    )

    result = _apply(
        world,
        first.resource_candidate,
        first.body_candidate,
        second_request,
        store,
        intervention_action_id="transfer-2",
        transition_id="world-transition-2",
        requested_material=0.5,
    )

    evidence = json.loads(Path(result.evidence_reference.locator).read_bytes())
    assert evidence["requested_material"] == 0.5
    assert result.record.causal_tick == 2


def test_action_id_uniqueness_is_scoped_to_logical_intervention(tmp_path) -> None:
    world, resource, body, request, store = _owners(tmp_path)
    first = _apply(world, resource, body, request, store, intervention_action_id="transfer-1")
    other_intervention = InterventionRequest(
        request.operator_id,
        "intervention-other",
        request.source_id,
        request.target_body_id,
        request.maximum_material,
        request.kind,
    )

    result = _apply(
        world,
        first.resource_candidate,
        first.body_candidate,
        other_intervention,
        store,
        intervention_action_id="transfer-1",
        transition_id="world-transition-2",
        requested_material=0.5,
    )

    assert result.record.causal_tick == 2


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
    # Owner candidate files may already exist, but only manifest references in
    # a committed World cut make them part of accepted causal state.
    assert all(
        ref.checkpoint_id != "tick-1"
        for ref in world.manifest.checkpoint_references
        if ref.owner != "world-journal"
    )


def test_evidence_file_written_before_journal_failure_is_not_a_committed_action(
    tmp_path, monkeypatch
) -> None:
    world, resource, body, request, store = _owners(tmp_path)
    original_write = store.write
    staged_evidence = []

    def capture_evidence(**kwargs):
        reference = original_write(**kwargs)
        if kwargs["owner"] == LAB_EVIDENCE_OWNER:
            staged_evidence.append(reference)
        return reference

    monkeypatch.setattr(store, "write", capture_evidence)

    def fail_journal(_journal, *, causal_tick, previous_reference):
        assert causal_tick == 1
        assert previous_reference in world.manifest.checkpoint_references
        raise OSError("journal snapshot failure")

    monkeypatch.setattr(world._journal_store, "write", fail_journal)
    with pytest.raises(OSError, match="journal snapshot failure"):
        _apply(world, resource, body, request, store)

    assert len(staged_evidence) == 1
    evidence_ref = staged_evidence[0]
    assert Path(evidence_ref.locator).is_file()
    evidence = json.loads(Path(evidence_ref.locator).read_bytes())
    assert evidence["intervention_action_id"] == "action-1"
    assert evidence["causal_tick"] == 1
    assert world.causal_tick == 0
    assert world.status.value == "RECOVERY_REQUIRED"
    assert all(
        (reference.owner, reference.owner_identity)
        != (LAB_EVIDENCE_OWNER, request.intervention_id)
        for reference in world.manifest.checkpoint_references
    )
    assert not any(
        record.record_type == "world.owner_record.committed"
        for record in world.records
    )


def test_candidate_journal_and_evidence_are_not_committed_if_manifest_publication_fails(
    tmp_path, monkeypatch
) -> None:
    world, resource, body, request, store = _owners(tmp_path)
    original_write = store.write
    staged_evidence = []

    def capture_evidence(**kwargs):
        reference = original_write(**kwargs)
        if kwargs["owner"] == LAB_EVIDENCE_OWNER:
            staged_evidence.append(reference)
        return reference

    monkeypatch.setattr(store, "write", capture_evidence)

    def fail_manifest_publication(*args, **kwargs):
        raise OSError("manifest publication failure")

    monkeypatch.setattr(world._manifest_store, "_commit_transition", fail_manifest_publication)
    with pytest.raises(OSError, match="manifest publication failure"):
        _apply(world, resource, body, request, store)

    assert world.causal_tick == 0
    assert world.manifest.pending_tick == 1
    assert world.manifest.status.value == "RECOVERY_REQUIRED"
    assert len(staged_evidence) == 1
    evidence_ref = staged_evidence[0]
    assert Path(evidence_ref.locator).is_file()
    evidence = json.loads(Path(evidence_ref.locator).read_bytes())
    assert evidence["intervention_action_id"] == "action-1"

    candidate_journal = world._journal_store.directory / "world-causal-journal-v3.jsonl"
    assert candidate_journal.is_file()
    candidate_records = [
        json.loads(line) for line in candidate_journal.read_text().splitlines()
    ]
    assert any(
        record.get("record_type") == "world.owner_record.committed"
        and record.get("payload", {}).get("owner_record_id") == "action-1"
        for record in (item.get("record", {}) for item in candidate_records)
    )

    # The pending manifest still identifies the previous cut, not the
    # candidate journal. Recovery must select that previous cut, leaving both
    # staged artifacts as uncommitted evidence/debug artifacts.
    assert world.manifest.causal_tick == 0
    owner_restoration = MaterialTransferOwnerRestoration()
    recovered = DurableWorldRuntime.recover_previous_cut(
        world.world_id,
        world.presence_id,
        world._manifest_store,
        world._journal_store,
        owner_checkpoint_verifier=world._owner_checkpoint_verifier,
        owner_checkpoint_contracts=owner_restoration.contracts(
            resource_id=resource.resource_id, body_id=body.body_id
        ),
        owner_checkpoint_restorer=owner_restoration.restore,
    )
    assert recovered.causal_tick == 0
    assert recovered.manifest.status.value == "COMMITTED"
    assert not any(
        record.record_type == "world.owner_record.committed"
        and record.payload.get("owner_record_id") == "action-1"
        for record in recovered.records
    )
    assert Path(evidence_ref.locator).is_file()
    assert candidate_journal.is_file()
    assert all(
        (reference.owner, reference.owner_identity)
        != (LAB_EVIDENCE_OWNER, request.intervention_id)
        for reference in world.manifest.checkpoint_references
    )
    assert not any(
        record.record_type == "world.owner_record.committed"
        for record in world.records
    )
