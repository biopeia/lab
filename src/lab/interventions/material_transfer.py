"""Durable Lab intervention over Environment and Embodiment owners.

This is a caller-requested scalar transfer, not an autonomous action, physical
contact model, or demonstrated material/energy equivalence. World publishes the
causal cut; Lab contributes a step-scoped evidence checkpoint to that cut.
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
    """Commit an intervention and owner checkpoints as one durable World cut.

    Body identity is derived from Embodiment's checkpoint boundary; source
    identity is carried by Environment's identified resource checkpoint. The
    request envelope alone cannot establish either identity. Inputs are cloned
    through owner checkpoint codecs and never mutated in place.
    """
    if not isinstance(world, DurableWorldRuntime):
        raise TypeError("material transfer requires DurableWorldRuntime")
    if not isinstance(resource, IdentifiedFiniteResource):
        raise TypeError("resource must be an Environment-owned identified resource")
    if not isinstance(body, EmbodimentCheckpoint):
        raise TypeError("body must be an EmbodimentCheckpoint")
    if not isinstance(transition_id, str) or not transition_id.strip():
        raise ValueError("transition_id must be non-empty")
    if transition_id == request.intervention_id:
        raise ValueError("transition_id must be distinct from intervention_id")
    if not isinstance(intervention_action_id, str) or not intervention_action_id.strip():
        raise ValueError("intervention_action_id must be non-empty")
    if intervention_action_id in {request.intervention_id, transition_id}:
        raise ValueError("intervention_action_id must be distinct from intervention_id and transition_id")
    source_id = resource.resource_id
    body_id = body.body_id
    if source_id != request.source_id:
        raise ValueError("requested source_id differs from Environment owner identity")
    if body_id != request.target_body_id:
        raise ValueError("requested target_body_id differs from Embodiment owner identity")
    if (
        isinstance(requested_material, bool)
        or not isinstance(requested_material, (int, float))
        or not math.isfinite(float(requested_material))
        or requested_material < 0.0
        or requested_material > request.maximum_material
    ):
        raise ValueError("request exceeds caller-declared material limit")

    environment_key = (ENVIRONMENT_OWNER, source_id)
    embodiment_key = (EMBODIMENT_OWNER, body_id)
    if set(world.manifest.registered_owner_ids) != {environment_key, embodiment_key}:
        raise ValueError("World genesis owner roster must exactly match the Environment and Embodiment owners")

    # These fields identify the logical request/provenance and therefore stay
    # fixed across its causal actions. Resource/body targets and quantities
    # below describe each action, not the logical intervention as a whole.
    intervention_context: dict[str, object] = {
        "operator_id": request.operator_id,
        "applicability": request.kind.value,
        "run_id": request.run_id,
        "study_id": request.study_id,
        "experiment_id": request.experiment_id,
        "protocol_id": request.protocol_id,
    }

    def validate_intervention_history() -> None:
        for journal_record in world.records:
            if journal_record.record_type != OWNER_RECORD_TYPE:
                continue
            envelope = journal_record.payload
            if (
                envelope.get("owner_id") != LAB_EVIDENCE_OWNER
                or envelope.get("owner_identity") != request.intervention_id
            ):
                continue
            if envelope.get("owner_record_id") == intervention_action_id:
                raise ValueError("intervention action id was already committed in this World")
            data = envelope.get("data")
            if not isinstance(data, Mapping) or data.get("intervention_context") != intervention_context:
                raise ValueError("intervention_id cannot be reused with a different immutable intervention context")

    # Fail user errors before World enters PREPARING. World independently
    # enforces stable action-record uniqueness at commit, including after restore.
    validate_intervention_history()

    # Verify the accepted World cut references the exact owner identities and
    # that its checkpoint values still represent the supplied owner objects.
    reference_by_owner = {
        (ref.owner, ref.owner_identity): ref for ref in world.manifest.checkpoint_references
    }
    try:
        environment_ref = reference_by_owner[environment_key]
        embodiment_ref = reference_by_owner[embodiment_key]
        if Path(environment_ref.locator).read_bytes() != resource.checkpoint_bytes():
            raise ValueError("Environment state does not match its committed owner checkpoint")
        if Path(embodiment_ref.locator).read_bytes() != body.to_bytes():
            raise ValueError("Embodiment state does not match its committed owner checkpoint")
    except (KeyError, OSError) as exc:
        raise ValueError("World cut is missing a readable authoritative owner checkpoint") from exc

    candidate_resource = IdentifiedFiniteResource.from_checkpoint_bytes(resource.checkpoint_bytes())
    candidate_body = EmbodimentCheckpoint.from_bytes(body.to_bytes())
    offered = min(float(requested_material), candidate_resource.state.offered_material())
    transfer = MaterialTransfer(
        source_id=source_id,
        target_body_id=body_id,
        amount=offered,
        composition="unspecified-scalar-material",
    )
    accepted = absorb_material_transfer(
        body_id=body_id,
        body_state=candidate_body.body_state,
        transfer=transfer,
    )
    debited = candidate_resource.state.consume_absorbed(accepted)
    if debited != accepted:
        raise RuntimeError("Environment debit did not equal Embodiment acceptance")

    staged: dict[str, object] = {}

    def write_owner_checkpoints(causal_tick: int) -> tuple[CheckpointReference, ...]:
        evidence: dict[str, object] = {
            "schema_version": 2,
            "intervention_id": request.intervention_id,
            "intervention_action_id": intervention_action_id,
            "operator_id": request.operator_id,
            "applicability": request.kind.value,
            "transition_id": transition_id,
            "world_id": world.world_id.value,
            "causal_tick": causal_tick,
            "source_id": source_id,
            "target_body_id": body_id,
            "requested_material": float(requested_material),
            "offered_material": offered,
            "accepted_material": accepted,
            "debited_material": debited,
            "quantity_semantics": "unspecified_scalar_material",
        }
        for key in ("run_id", "study_id", "experiment_id", "protocol_id"):
            value = getattr(request, key)
            if value is not None:
                evidence[key] = value
        evidence_bytes = json.dumps(
            evidence, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode()
        refs = (
            checkpoint_store.write(
                owner=ENVIRONMENT_OWNER,
                owner_identity=source_id,
                checkpoint_id=f"tick-{causal_tick}",
                schema_version=ENVIRONMENT_SCHEMA,
                encoded=candidate_resource.checkpoint_bytes(),
            ),
            checkpoint_store.write(
                owner=EMBODIMENT_OWNER,
                owner_identity=body_id,
                checkpoint_id=f"tick-{causal_tick}",
                schema_version=EMBODIMENT_SCHEMA,
                encoded=candidate_body.to_bytes(),
            ),
            checkpoint_store.write(
                owner=LAB_EVIDENCE_OWNER,
                owner_identity=request.intervention_id,
                checkpoint_id=f"action-{hashlib.sha256(intervention_action_id.encode()).hexdigest()}",
                schema_version=EVIDENCE_SCHEMA,
                encoded=evidence_bytes,
            ),
        )
        staged["evidence"] = evidence
        evidence_refs = tuple(
            ref
            for ref in refs
            if ref.owner == LAB_EVIDENCE_OWNER
            and ref.owner_identity == request.intervention_id
        )
        if len(evidence_refs) != 1:
            raise RuntimeError("Lab evidence checkpoint writer must return exactly one matching reference")
        staged["evidence_ref"] = evidence_refs[0]
        return refs

    def write_owner_records(
        causal_tick: int,
        owner_references: tuple[CheckpointReference, ...],
    ) -> tuple[OwnerCausalRecord, ...]:
        # Recheck while World owns its single-writer tick guard. The World
        # journal is the durable index; Lab remains the semantic/evidence owner.
        validate_intervention_history()
        evidence_refs = tuple(
            ref
            for ref in owner_references
            if ref.owner == LAB_EVIDENCE_OWNER
            and ref.owner_identity == request.intervention_id
        )
        if len(evidence_refs) != 1:
            raise RuntimeError("World candidate cut must contain exactly one Lab evidence checkpoint")
        evidence_ref = evidence_refs[0]
        return (
            OwnerCausalRecord(
                owner_id=LAB_EVIDENCE_OWNER,
                owner_identity=request.intervention_id,
                owner_record_id=intervention_action_id,
                payload={
                    "schema_version": 1,
                    "intervention_id": request.intervention_id,
                    "intervention_action_id": intervention_action_id,
                    "intervention_context": intervention_context,
                    "transition_id": transition_id,
                    "world_id": world.world_id.value,
                    "causal_tick": causal_tick,
                    "evidence_checkpoint": {
                        "owner": evidence_ref.owner,
                        "owner_identity": evidence_ref.owner_identity,
                        "checkpoint_id": evidence_ref.checkpoint_id,
                        "schema_version": evidence_ref.schema_version,
                        "locator": evidence_ref.locator,
                        "sha256": evidence_ref.sha256,
                    },
                },
            ),
        )

    evidence_contract = checkpoint_store.evidence_contract()
    record = world.tick(
        transition_id,
        write_owner_checkpoints,
        write_owner_records=write_owner_records,
        step_participants=((LAB_EVIDENCE_OWNER, request.intervention_id),),
        register_owner_contracts={
            (LAB_EVIDENCE_OWNER, request.intervention_id): evidence_contract
        },
    )
    evidence_reference = staged.get("evidence_ref")
    evidence_payload = staged.get("evidence")
    if not isinstance(evidence_reference, CheckpointReference) or not isinstance(evidence_payload, dict):
        raise RuntimeError("World committed without the staged Lab intervention evidence checkpoint")

    # Obtain a World-issued receipt for exactly the committed candidate.
    # This is correlation evidence only; it does not infer a transfer claim.
    committed_cut = world.committed_cut_for(
        world_id=world.world_id.value,
        causal_tick=record.causal_tick,
        commit_id=transition_id,
    )
    return MaterialTransferResult(
        record=record,
        intervention_action_id=intervention_action_id,
        evidence_reference=evidence_reference,
        committed_cut=committed_cut,
        experiment_id=request.experiment_id,
        run_id=request.run_id,
        resource_candidate=candidate_resource,
        body_candidate=candidate_body,
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

    # Bind Lab's experiment association to the exact Lab evidence and owner
    # record that World committed. Result objects are caller-owned values; their
    # run/experiment fields are not authoritative merely because they accompany
    # a valid World receipt.
    journal_records = world.records
    if result.record not in journal_records:
        raise ValueError("committed intervention record is absent from the World journal")
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
