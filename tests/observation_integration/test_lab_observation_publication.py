"""Lab consumes a real owner publication made after a committed World cut.

The fixture uses deterministic World storage and an Environment-owned scalar
field. It does not execute a scientific experiment or claim biological
meaning; it exercises the production World commit/publication APIs and the
existing in-process Observation plane.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from environment import (
    EnvironmentObservationContext,
    FiniteResourceState,
    FrameDescriptor,
    IdentifiedFiniteScalarField,
)
from observation.environment import environment_finite_scalar_field_observation
from observation.plane import ObservationPlane
from world.durable_runtime import (
    DurableJournalSnapshotStore,
    DurableWorldRuntime,
    PresenceOwnerLink,
    WorldGenesisSpec,
)
from world.manifest import CheckpointReference, WorldCausalManifestStore
from world.observation_publication import (
    OwnerObservation,
    publish_committed_owner_observations,
)
from world.runtime import PresenceId, WorldId

from lab.observation_consumer import (
    LabObservationAssociation,
    LabObservationReadStatus,
    associate_current_messages,
    associate_stream_messages,
)

WORLD_ID = "world.lab-observation-consumer"
RESOURCE_ID = "resource.scalar-field"
ENVIRONMENT_ID = "environment.scalar-field"
ENVIRONMENT_REVISION = "environment-r1"
FIELD_REVISION = "field-r1"
FRAME_ID = "environment-frame"


class _FieldCheckpointContract:
    def validate_checkpoint(self, encoded: bytes, owner_identity: str, schema_version: str) -> bool:
        return IdentifiedFiniteScalarField.validate_checkpoint(
            encoded, owner_identity, schema_version
        )

    def verify_restoration(self, reference: CheckpointReference) -> bool:
        return Path(reference.locator).is_file()


def _frame() -> FrameDescriptor:
    return FrameDescriptor(
        frame_id=FRAME_ID,
        parent_frame_id="world-frame",
        origin_m=(0.0, 0.0, 0.0),
        x_axis_in_parent=(1.0, 0.0, 0.0),
        y_axis_in_parent=(0.0, 1.0, 0.0),
        z_axis_in_parent=(0.0, 0.0, 1.0),
        handedness="RIGHT_HANDED",
        up_axis="Z",
    )


def _field() -> IdentifiedFiniteScalarField:
    return IdentifiedFiniteScalarField(
        resource_id=RESOURCE_ID,
        field_revision=FIELD_REVISION,
        environment_id=ENVIRONMENT_ID,
        environment_revision=ENVIRONMENT_REVISION,
        frame_id=FRAME_ID,
        state=FiniteResourceState(
            position=(1.0, 0.0, 0.0),
            radius=0.1,
            field_radius=2.0,
            remaining=10.0,
            transfer_per_tick=1.0,
        ),
    )


def _reference(path: Path, *, tick: int, encoded: bytes) -> CheckpointReference:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(encoded)
    return CheckpointReference(
        owner="environment",
        owner_identity=RESOURCE_ID,
        checkpoint_id=f"environment-cut-{tick}",
        schema_version=IdentifiedFiniteScalarField.OWNER_SCHEMA,
        locator=str(path),
        sha256=hashlib.sha256(encoded).hexdigest(),
    )


def _committed_publication(tmp_path: Path, plane: ObservationPlane):
    field = _field()
    owners_dir = tmp_path / "owner-checkpoints"
    initial_ref = _reference(
        owners_dir / "environment-0.json",
        tick=0,
        encoded=field.checkpoint_bytes(),
    )
    contract = _FieldCheckpointContract()
    world_id = WorldId(WORLD_ID)
    world = DurableWorldRuntime.initialize(
        WorldGenesisSpec(
            world_id=world_id,
            initial_presence_ids=("presence.environment",),
            registered_owner_ids=(("environment", RESOURCE_ID),),
            initial_owner_references=(initial_ref,),
            owner_checkpoint_contracts={("environment", RESOURCE_ID): contract},
            presence_owner_links=(
                PresenceOwnerLink(
                    PresenceId("presence.environment"), "environment", RESOURCE_ID
                ),
            ),
        ),
        "presence.environment",
        WorldCausalManifestStore(tmp_path / "manifest.json"),
        DurableJournalSnapshotStore(tmp_path / "journal", world_id),
        owner_checkpoint_verifier=lambda refs: all(
            contract.validate_checkpoint(
                Path(reference.locator).read_bytes(),
                reference.owner_identity,
                reference.schema_version,
            )
            for reference in refs
        ),
    )

    world.tick(
        "commit-1",
        lambda tick: (
            _reference(
                owners_dir / f"environment-{tick}.json",
                tick=tick,
                encoded=field.checkpoint_bytes(),
            ),
        ),
    )
    cut = world.committed_cut_for(
        world_id=WORLD_ID,
        causal_tick=1,
        commit_id="commit-1",
    )

    projection = field.project_observation(
        (0.0, 0.0, 0.0),
        frame=_frame(),
        context=EnvironmentObservationContext(
            world_id=WORLD_ID,
            source_causal_tick=0,
            target_causal_tick=1,
            physical_step_id="physical-step-fixture-1",
            environment_id=ENVIRONMENT_ID,
            environment_revision=ENVIRONMENT_REVISION,
            resource_id=RESOURCE_ID,
            field_revision=FIELD_REVISION,
        ),
    )
    observation = environment_finite_scalar_field_observation(projection)
    owner_reference = next(
        reference
        for reference in cut.owner_checkpoint_references
        if reference.owner == "environment"
        and reference.owner_identity == RESOURCE_ID
    )
    publication = publish_committed_owner_observations(
        world,
        plane,
        committed_cut=cut,
        owner_observations=(OwnerObservation(owner_reference, observation),),
    )
    return world, cut, observation, publication


def test_lab_associates_authentic_environment_publication_after_world_commit(tmp_path):
    plane = ObservationPlane()
    world, cut, source_observation, publication = _committed_publication(tmp_path, plane)
    association = LabObservationAssociation.for_committed_cut(
        experiment_id="lab-study-1",
        run_id="run-1",
        committed_cut=cut,
    )

    result = associate_current_messages(
        plane,
        association=association,
        committed_cut=cut,
    )

    assert world.causal_tick == 1
    assert publication.committed_cut == cut
    assert publication.delivery_sequences == (1,)
    assert result.status is LabObservationReadStatus.ASSOCIATED
    assert len(result.messages) == 1
    assert result.messages[0].observation == source_observation
    assert result.messages[0].observation.claim.authority.value == "environment"
    assert result.messages[0].observation.context_time[-1].value == 1
    assert result.association.experiment_id == "lab-study-1"
    assert result.association.run_id == "run-1"


def test_lab_stream_consumes_committed_publication_and_requires_explicit_close(tmp_path):
    plane = ObservationPlane()
    subscription = plane.open_stream(after_sequence=0)
    try:
        _world, cut, _observation, publication = _committed_publication(tmp_path, plane)
        association = LabObservationAssociation.for_committed_cut(
            experiment_id="lab-study-2",
            run_id="run-2",
            committed_cut=cut,
        )

        result = associate_stream_messages(
            subscription,
            association=association,
            committed_cut=cut,
        )

        assert publication.delivery_sequences == (1,)
        assert result.status is LabObservationReadStatus.ASSOCIATED
        assert tuple(message.sequence for message in result.messages) == (1,)
    finally:
        plane.close_stream(subscription)


def test_world_commit_without_observation_message_is_unassociated_not_source_absence(
    tmp_path,
):
    plane = ObservationPlane()
    world, cut, _observation, _publication = _committed_publication(
        tmp_path, ObservationPlane()
    )
    association = LabObservationAssociation.for_committed_cut(
        experiment_id="lab-study-3",
        run_id="run-3",
        committed_cut=cut,
    )

    result = associate_current_messages(
        plane,
        association=association,
        committed_cut=cut,
    )

    assert world.causal_tick == 1
    assert result.status is LabObservationReadStatus.UNASSOCIATED
    assert "not source absence" in result.reason
