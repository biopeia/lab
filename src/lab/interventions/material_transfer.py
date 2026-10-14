"""Material-transfer intervention contracts and gated publication helpers.

The current runtime has no verified authorization source for material transfer,
so the operation is explicitly unsupported. No caller-declared identifier or
constraint grants permission to enter the World causal path.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import tempfile
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any, Mapping

from embodiment.checkpoint import (
    EmbodimentCheckpoint,
    project_committed_reserve_state,
)
from embodiment.intake import MaterialTransfer, absorb_material_transfer
from environment.identified_resource import (
    IdentifiedFiniteResource,
    project_committed_resource_state,
)
from observation import (
    ObservationPlane,
    embodiment_reserve_state_observation,
    environment_resource_state_observation,
)
from lab.observation_consumer import (
    LabObservationAssociation,
    LabObservationRead,
    associate_current_messages,
)
from world.durable_runtime import (
    CommittedWorldCut,
    DurableWorldRuntime,
    OwnerCausalRecord,
    PresenceOwnerLink,
)
from world.journal import CausalRecord
from world.manifest import CheckpointReference, ManifestError
from world.runtime import PresenceId
from world.observation_publication import (
    ObservationPublication,
    OwnerObservation,
    publish_committed_owner_observations,
)


ENVIRONMENT_OWNER = "environment"
EMBODIMENT_OWNER = "embodiment"
LAB_EVIDENCE_OWNER = "lab-intervention-evidence"
ENVIRONMENT_SCHEMA = IdentifiedFiniteResource.OWNER_SCHEMA
EMBODIMENT_SCHEMA = "embodiment-checkpoint-v2"
EVIDENCE_SCHEMA = "lab-intervention-evidence-v2"
OWNER_RECORD_TYPE = "world.owner_record.committed"


class MaterialTransferAuthorizationUnsupported(RuntimeError):
    """The current Lab runtime has no verified authority for this operation."""


class InterventionKind(StrEnum):
    """Declared scientific applicability of an operator action."""

    NON_EXPERIMENTAL = "NON_EXPERIMENTAL_INTERVENTION"
    EXPERIMENTAL_RUN = "EXPERIMENTAL_RUN_INTERVENTION"


@dataclass(frozen=True, slots=True)
class InterventionRequest:
    """Caller-declared request and constraints; not authentication or permission."""

    operator_id: str
    intervention_id: str
    source_id: str
    target_body_id: str
    maximum_material: float
    kind: InterventionKind
    run_id: str | None = None
    study_id: str | None = None
    experiment_id: str | None = None
    protocol_id: str | None = None

    def __post_init__(self) -> None:
        for name in ("operator_id", "intervention_id", "source_id", "target_body_id"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must not be empty")
        if (
            isinstance(self.maximum_material, bool)
            or not isinstance(self.maximum_material, (int, float))
            or not math.isfinite(float(self.maximum_material))
            or self.maximum_material < 0.0
        ):
            raise ValueError("maximum_material must be finite and non-negative")
        if not isinstance(self.kind, InterventionKind):
            raise ValueError("intervention kind must be explicit")
        if self.kind is InterventionKind.EXPERIMENTAL_RUN and not self.run_id:
            raise ValueError("experimental run intervention requires a real run_id")
        if self.kind is InterventionKind.NON_EXPERIMENTAL and self.run_id is not None:
            raise ValueError("non-experimental intervention cannot claim a run_id")
        for name in ("run_id", "study_id", "experiment_id", "protocol_id"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(f"{name} must be non-empty when supplied")


class LabInterventionEvidenceCodec:
    """Lab-owned validation of intervention evidence checkpoint identity."""

    @classmethod
    def validate_checkpoint(cls, encoded: bytes, owner_identity: str, schema_version: str) -> bool:
        if schema_version != EVIDENCE_SCHEMA:
            return False
        try:
            payload: Any = json.loads(encoded)
        except (TypeError, UnicodeDecodeError, json.JSONDecodeError):
            return False
        return (
            isinstance(payload, dict)
            and payload.get("schema_version") == 2
            and payload.get("intervention_id") == owner_identity
            and isinstance(payload.get("intervention_action_id"), str)
            and bool(payload["intervention_action_id"].strip())
        )

    @classmethod
    def verify_restoration(cls, reference: CheckpointReference) -> bool:
        if reference.owner != LAB_EVIDENCE_OWNER:
            return False
        try:
            encoded = Path(reference.locator).read_bytes()
        except OSError:
            return False
        if hashlib.sha256(encoded).hexdigest() != reference.sha256:
            return False
        return cls.validate_checkpoint(
            encoded, reference.owner_identity, reference.schema_version
        )


class MaterialTransferCheckpointStore:
    """Write immutable, content-addressed owner and intervention checkpoints."""

    def __init__(self, directory: str | Path) -> None:
        self.directory = Path(directory)

    def write(
        self,
        *,
        owner: str,
        owner_identity: str,
        checkpoint_id: str,
        schema_version: str,
        encoded: bytes,
    ) -> CheckpointReference:
        if not all(isinstance(value, str) and value.strip() for value in (owner, owner_identity, checkpoint_id, schema_version)):
            raise ValueError("checkpoint identity fields must be non-empty")
        digest = hashlib.sha256(encoded).hexdigest()
        self.directory.mkdir(parents=True, exist_ok=True)
        path = self.directory / f"{hashlib.sha256(owner_identity.encode()).hexdigest()[:16]}-{checkpoint_id}-{digest}.bin"
        if path.exists():
            if path.read_bytes() != encoded:
                raise ManifestError("immutable checkpoint path collision")
        else:
            fd, temporary = tempfile.mkstemp(prefix=".owner-checkpoint-", dir=self.directory)
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(encoded)
                    stream.flush()
                    os.fsync(stream.fileno())
                try:
                    os.link(temporary, path)
                except FileExistsError:
                    if path.read_bytes() != encoded:
                        raise ManifestError("immutable checkpoint path collision")
                directory_fd = os.open(self.directory, os.O_RDONLY)
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
            finally:
                try:
                    os.unlink(temporary)
                except FileNotFoundError:
                    pass
        return CheckpointReference(
            owner=owner,
            owner_identity=owner_identity,
            checkpoint_id=checkpoint_id,
            schema_version=schema_version,
            locator=str(path),
            sha256=digest,
        )

    @staticmethod
    def evidence_contract() -> type[LabInterventionEvidenceCodec]:
        return LabInterventionEvidenceCodec


@dataclass(frozen=True, slots=True)
class MaterialTransferResult:
    """Committed World record and owner candidates from an adopted cut.

    Observation is deliberately a separate post-commit operation. The result
    does not invent a sensory or causal event when no owner projection has
    actually been published.
    """

    record: CausalRecord
    intervention_action_id: str
    evidence_reference: CheckpointReference
    committed_cut: CommittedWorldCut
    experiment_id: str | None
    run_id: str | None
    resource_candidate: IdentifiedFiniteResource
    body_candidate: EmbodimentCheckpoint


@dataclass(frozen=True, slots=True)
class MaterialTransferObservationPublication:
    """Two independently owned state claims published against one World cut."""

    committed_cut: CommittedWorldCut
    observations: tuple[object, ...]
    publication: ObservationPublication
    association: LabObservationAssociation
    read: LabObservationRead


def apply_material_transfer(
    *,
    world: DurableWorldRuntime,
    checkpoint_store: MaterialTransferCheckpointStore,
    resource: IdentifiedFiniteResource,
    body: EmbodimentCheckpoint,
    request: InterventionRequest,
    intervention_action_id: str,
    transition_id: str,
    requested_material: float,
) -> MaterialTransferResult:
    """Reject material transfer until a verified authorization source exists.

    ``InterventionRequest`` contains caller-declared identifiers and constraints;
    it is not an authorization credential. Lab #330 classifies verified
    authorization as unsupported for the current implementation. Fail before
    inspecting owner state, writing checkpoints, or entering World.
    """
    raise MaterialTransferAuthorizationUnsupported(
        "material transfer is unsupported: no verified authorization source is configured"
    )


def publish_material_transfer_observations(
    *,
    world: DurableWorldRuntime,
    plane: ObservationPlane,
    result: MaterialTransferResult,
) -> MaterialTransferObservationPublication:
    """Publish exact owner snapshots for an experimental committed transfer.

    The emitted Environment and Embodiment claims are independent state
    snapshots. Their shared World cut does not assert conservation, absorption,
    physical transfer, or causation. Publication is process-local and
    non-transactional across messages; this function never retries the causal
    transition or publication automatically.
    """
    if not isinstance(plane, ObservationPlane):
        raise TypeError("publication requires the accepted in-process ObservationPlane")
    if not isinstance(result, MaterialTransferResult):
        raise TypeError("publication requires a committed MaterialTransferResult")
    if not result.experiment_id or not result.run_id:
        raise ValueError("experimental publication requires explicit experiment_id and run_id")
    cut = result.committed_cut
    if cut.world_id != result.record.world_id or cut.causal_tick != result.record.causal_tick:
        raise ValueError("World receipt does not match the committed intervention record")

    # Bind Lab's experiment association to the exact World transition record
    # and Lab evidence that World committed. Result objects are caller-owned
    # values; matching a World/tick pair or membership in that tick's journal
    # does not establish which record represents the transition.
    journal_records = world.records
    transition_records = tuple(
        record
        for record in journal_records
        if record.world_id == cut.world_id
        and record.causal_tick == cut.causal_tick
        and record.record_type == "world.causal_tick.committed"
    )
    if len(transition_records) != 1:
        raise ValueError(
            "exact committed World transition record is missing or ambiguous"
        )
    if result.record != transition_records[0]:
        raise ValueError(
            "result does not identify the exact committed World transition record"
        )
    try:
        verified_cut = world.committed_cut_for(
            world_id=cut.world_id,
            causal_tick=cut.causal_tick,
            commit_id=cut.commit_id,
            expected_owner_references=cut.owner_checkpoint_references,
        )
    except (ManifestError, OSError) as exc:
        raise ValueError("World receipt is not the current verified committed cut") from exc
    if verified_cut != cut:
        raise ValueError("World receipt does not equal the verified committed cut")

    evidence_refs = tuple(
        reference
        for reference in cut.owner_checkpoint_references
        if reference.owner == LAB_EVIDENCE_OWNER
        and reference.owner_identity == result.evidence_reference.owner_identity
    )
    if len(evidence_refs) != 1 or evidence_refs[0] != result.evidence_reference:
        raise ValueError("evidence reference does not match committed World cut")

    action_records = tuple(
        journal_record
        for journal_record in journal_records
        if journal_record.world_id == cut.world_id
        and journal_record.causal_tick == cut.causal_tick
        and journal_record.record_type == OWNER_RECORD_TYPE
        and journal_record.payload.get("owner_id") == LAB_EVIDENCE_OWNER
        and journal_record.payload.get("owner_identity") == result.evidence_reference.owner_identity
        and journal_record.payload.get("owner_record_id") == result.intervention_action_id
    )
    if len(action_records) != 1:
        raise ValueError("committed Lab action record is missing or ambiguous")
    action_record = action_records[0]
    action_data = action_record.payload.get("data")
    if not isinstance(action_data, Mapping):
        raise ValueError("committed Lab action record has no evidence data")
    evidence_pointer = action_data.get("evidence_checkpoint")
    if not isinstance(evidence_pointer, Mapping):
        raise ValueError("committed Lab action record has no evidence checkpoint reference")
    expected_pointer = {
        "owner": result.evidence_reference.owner,
        "owner_identity": result.evidence_reference.owner_identity,
        "checkpoint_id": result.evidence_reference.checkpoint_id,
        "schema_version": result.evidence_reference.schema_version,
        "locator": result.evidence_reference.locator,
        "sha256": result.evidence_reference.sha256,
    }
    if dict(evidence_pointer) != expected_pointer:
        raise ValueError("evidence reference does not match committed Lab action record")

    try:
        evidence_bytes = Path(result.evidence_reference.locator).read_bytes()
    except OSError as exc:
        raise ValueError("committed Lab evidence bytes are unavailable") from exc
    if hashlib.sha256(evidence_bytes).hexdigest() != result.evidence_reference.sha256:
        raise ValueError("committed Lab evidence digest does not match its reference")
    if not LabInterventionEvidenceCodec.validate_checkpoint(
        evidence_bytes,
        result.evidence_reference.owner_identity,
        result.evidence_reference.schema_version,
    ):
        raise ValueError("committed Lab evidence checkpoint is invalid")
    evidence = json.loads(evidence_bytes)
    intervention_context = action_data.get("intervention_context")
    if not isinstance(intervention_context, Mapping):
        raise ValueError("committed Lab action record has no intervention context")
    expected_evidence = {
        "intervention_id": action_data.get("intervention_id"),
        "intervention_action_id": result.intervention_action_id,
        "transition_id": action_data.get("transition_id"),
        "world_id": cut.world_id,
        "causal_tick": cut.causal_tick,
        "run_id": result.run_id,
        "experiment_id": result.experiment_id,
        "operator_id": intervention_context.get("operator_id"),
        "applicability": intervention_context.get("applicability"),
    }
    for field, expected in expected_evidence.items():
        if evidence.get(field) != expected:
            raise ValueError("result association does not match committed Lab evidence")
    if (
        intervention_context.get("run_id") != result.run_id
        or intervention_context.get("experiment_id") != result.experiment_id
    ):
        raise ValueError("result association does not match committed Lab action context")
    if action_data.get("intervention_id") != result.evidence_reference.owner_identity:
        raise ValueError("committed Lab action identity does not match evidence owner identity")
    if (
        action_data.get("world_id") != cut.world_id
        or action_data.get("causal_tick") != cut.causal_tick
        or action_data.get("transition_id") != cut.commit_id
    ):
        raise ValueError("committed Lab action record does not match the World cut")

    by_owner = {(ref.owner, ref.owner_identity): ref for ref in cut.owner_checkpoint_references}
    environment_ref = by_owner.get((ENVIRONMENT_OWNER, result.resource_candidate.resource_id))
    embodiment_ref = by_owner.get((EMBODIMENT_OWNER, result.body_candidate.body_id))
    if environment_ref is None or embodiment_ref is None:
        raise ValueError("committed World cut lacks required Environment/Embodiment owner references")
    try:
        environment_bytes = Path(environment_ref.locator).read_bytes()
        embodiment_bytes = Path(embodiment_ref.locator).read_bytes()
    except OSError as exc:
        raise ValueError("committed owner checkpoint bytes are unavailable for projection") from exc

    environment_projection = project_committed_resource_state(
        environment_bytes,
        committed_cut=cut,
        owner_reference=environment_ref,
    )
    embodiment_projection = project_committed_reserve_state(
        embodiment_bytes,
        committed_cut=cut,
        owner_reference=embodiment_ref,
    )
    observations = (
        environment_resource_state_observation(environment_projection),
        embodiment_reserve_state_observation(embodiment_projection),
    )
    publication = publish_committed_owner_observations(
        world,
        plane,
        committed_cut=cut,
        owner_observations=(
            OwnerObservation(environment_ref, observations[0]),
            OwnerObservation(embodiment_ref, observations[1]),
        ),
    )
    association = LabObservationAssociation.for_committed_cut(
        experiment_id=result.experiment_id,
        run_id=result.run_id,
        committed_cut=cut,
    )
    read = associate_current_messages(
        plane,
        association=association,
        committed_cut=cut,
    )
    return MaterialTransferObservationPublication(
        committed_cut=cut,
        observations=observations,
        publication=publication,
        association=association,
        read=read,
    )


__all__ = [
    "InterventionKind",
    "InterventionRequest",
    "MaterialTransferCheckpointStore",
    "MaterialTransferObservationPublication",
    "MaterialTransferResult",
    "apply_material_transfer",
    "publish_material_transfer_observations",
]
