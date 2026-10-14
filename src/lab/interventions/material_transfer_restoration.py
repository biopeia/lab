"""Lab composition for restoring material-transfer owner checkpoints.

The adapters translate World's opaque checkpoint reference into each owner's
existing validation boundary. They do not alter owner state or confer semantic
authority on Lab.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Mapping

from embodiment.checkpoint import EmbodimentCheckpoint
from environment.identified_resource import IdentifiedFiniteResource
from environment.restoration import OwnerRestorationReference
from world.durable_runtime import OwnerCheckpointContract
from world.manifest import CheckpointReference


class MaterialTransferOwnerRestoration:
    """Restore and validate the Environment/Embodiment owners in one cut."""

    def __init__(self) -> None:
        self.resource: IdentifiedFiniteResource | None = None
        self.body: EmbodimentCheckpoint | None = None

    def restore(self, references: tuple[CheckpointReference, ...]) -> None:
        environment_refs = [ref for ref in references if ref.owner == "environment"]
        embodiment_refs = [ref for ref in references if ref.owner == "embodiment"]
        if len(environment_refs) != 1 or len(embodiment_refs) != 1:
            raise ValueError("material transfer restore requires Environment and Embodiment owners")

        environment_ref = environment_refs[0]
        embodiment_ref = embodiment_refs[0]
        environment_bytes = _read_verified_bytes(environment_ref)
        embodiment_bytes = _read_verified_bytes(embodiment_ref)
        if not IdentifiedFiniteResource.validate_checkpoint(
            environment_bytes, environment_ref.owner_identity, environment_ref.schema_version
        ):
            raise ValueError("Environment checkpoint does not satisfy its owner contract")
        if not EmbodimentCheckpoint.validate_checkpoint(
            embodiment_bytes, embodiment_ref.owner_identity, embodiment_ref.schema_version
        ):
            raise ValueError("Embodiment checkpoint does not satisfy its owner contract")

        self.resource = IdentifiedFiniteResource.from_checkpoint_bytes(environment_bytes)
        self.body = EmbodimentCheckpoint.from_bytes(embodiment_bytes)

    def contracts(
        self, *, resource_id: str, body_id: str
    ) -> Mapping[tuple[str, str], OwnerCheckpointContract]:
        return {
            ("environment", resource_id): _EnvironmentRestoreContract(self),
            ("embodiment", body_id): _EmbodimentRestoreContract(self),
        }


class _EnvironmentRestoreContract:
    def __init__(self, restoration: MaterialTransferOwnerRestoration) -> None:
        self._restoration = restoration

    def validate_checkpoint(self, encoded: bytes, owner_identity: str, schema_version: str) -> bool:
        return IdentifiedFiniteResource.validate_checkpoint(encoded, owner_identity, schema_version)

    def verify_restoration(self, reference: CheckpointReference) -> bool:
        owner = self._restoration.resource
        if owner is None or reference.owner != "environment":
            return False
        try:
            owner.verify_restoration(
                OwnerRestorationReference(
                    owner_identity=reference.owner_identity,
                    schema_version=reference.schema_version,
                    checkpoint_sha256=reference.sha256,
                )
            )
        except (TypeError, ValueError):
            return False
        return True


class _EmbodimentRestoreContract:
    def __init__(self, restoration: MaterialTransferOwnerRestoration) -> None:
        self._restoration = restoration

    def validate_checkpoint(self, encoded: bytes, owner_identity: str, schema_version: str) -> bool:
        return EmbodimentCheckpoint.validate_checkpoint(encoded, owner_identity, schema_version)

    def verify_restoration(self, reference: CheckpointReference) -> bool:
        owner = self._restoration.body
        if owner is None or reference.owner != "embodiment":
            return False
        encoded = owner.to_bytes()
        if hashlib.sha256(encoded).hexdigest() != reference.sha256:
            return False
        return EmbodimentCheckpoint.verify_restoration(
            encoded, reference.owner_identity, reference.schema_version
        )


def _read_verified_bytes(reference: CheckpointReference) -> bytes:
    encoded = Path(reference.locator).read_bytes()
    if hashlib.sha256(encoded).hexdigest() != reference.sha256:
        raise ValueError("owner checkpoint bytes differ from World's committed reference")
    return encoded


__all__ = ["MaterialTransferOwnerRestoration"]
