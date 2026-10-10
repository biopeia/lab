"""Lab integration check for durable operator intervention."""

from __future__ import annotations

import hashlib
from pathlib import Path

from embodiment.checkpoint import EmbodimentCheckpoint
from embodiment.metabolism import MetabolicLedger
from embodiment.physiology import LivingBodyState
from environment.identified_resource import IdentifiedFiniteResource
from environment.resource import FiniteResourceState
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
from world.durable_runtime import DurableJournalSnapshotStore, DurableWorldRuntime, WorldGenesisSpec
from world.manifest import CheckpointReference, WorldCausalManifestStore
from world.runtime import WorldId
from world.runtime import PresenceId
from world.durable_runtime import PresenceOwnerLink


def test_lab_intervention_commits_owner_states_and_evidence_in_durable_cut(tmp_path) -> None:
    resource = IdentifiedFiniteResource(
        "resource-1", FiniteResourceState(remaining=3.0, transfer_per_tick=2.0)
    )
    body_state = LivingBodyState(energy_reserve=0.5, max_energy=2.0)
    body = EmbodimentCheckpoint(
        "body-1", "episode-1", body_state, MetabolicLedger(body_state=body_state)
    )
    store = MaterialTransferCheckpointStore(tmp_path / "owners")
    env_key = (ENVIRONMENT_OWNER, resource.resource_id)
    body_key = (EMBODIMENT_OWNER, body.body_id)
    refs = (
        store.write(
            owner=ENVIRONMENT_OWNER,
            owner_identity=resource.resource_id,
            checkpoint_id="tick-0",
            schema_version=ENVIRONMENT_SCHEMA,
            encoded=resource.checkpoint_bytes(),
        ),
        store.write(
            owner=EMBODIMENT_OWNER,
            owner_identity=body.body_id,
            checkpoint_id="tick-0",
            schema_version=EMBODIMENT_SCHEMA,
            encoded=body.to_bytes(),
        ),
    )
    contracts = {env_key: IdentifiedFiniteResource, body_key: EmbodimentCheckpoint}
    presence_id = PresenceId("presence-1")
    world_id = WorldId("operator-transfer-workspace")

    def verify_files(checkpoints: tuple[CheckpointReference, ...]) -> bool:
        try:
            return all(
                hashlib.sha256(Path(reference.locator).read_bytes()).hexdigest() == reference.sha256
                for reference in checkpoints
            )
        except OSError:
            return False

    world = DurableWorldRuntime.initialize(
        WorldGenesisSpec(
            world_id=world_id,
            initial_presence_ids=(presence_id.value,),
            registered_owner_ids=tuple(sorted((env_key, body_key))),
            initial_owner_references=refs,
            owner_checkpoint_contracts=contracts,
            presence_owner_links=(PresenceOwnerLink(presence_id, EMBODIMENT_OWNER, body.body_id),),
        ),
        presence_id.value,
        WorldCausalManifestStore(tmp_path / "world" / "manifest.json"),
        DurableJournalSnapshotStore(tmp_path / "world" / "journal", world_id),
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

    result = apply_material_transfer(
        world=world,
        checkpoint_store=store,
        resource=resource,
        body=body,
        request=request,
        intervention_action_id="action-1",
        transition_id="transition-1",
        requested_material=2.5,
    )

    assert world.causal_tick == result.record.causal_tick == 1
    assert world.manifest.status.value == "COMMITTED"
    assert result.resource_candidate.state.remaining == 1.5
    assert result.body_candidate.body_state.energy_reserve == 2.0
    assert resource.state.remaining == 3.0
    assert body.body_state.energy_reserve == 0.5
    assert result.evidence_reference.owner == LAB_EVIDENCE_OWNER
    assert {(ref.owner, ref.owner_identity) for ref in world.manifest.checkpoint_references} == {
        env_key,
        body_key,
        (LAB_EVIDENCE_OWNER, request.intervention_id),
        ("world-journal", world_id.value),
    }
