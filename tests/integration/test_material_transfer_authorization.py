from __future__ import annotations

import pytest

from lab.interventions import (
    InterventionKind,
    InterventionRequest,
    MaterialTransferAuthorizationUnsupported,
    apply_material_transfer,
)


def test_material_transfer_fails_before_touching_world_or_owner_state() -> None:
    class WorldSpy:
        tick_called = False

        def tick(self, *_args, **_kwargs):
            self.tick_called = True
            raise AssertionError("unsupported material transfer must not call World.tick")

    class CheckpointStoreSpy:
        write_called = False

        def write(self, *_args, **_kwargs):
            self.write_called = True
            raise AssertionError("unsupported material transfer must not write checkpoints")

    world = WorldSpy()
    checkpoint_store = CheckpointStoreSpy()
    request = InterventionRequest(
        operator_id="caller-supplied-operator",
        intervention_id="caller-supplied-intervention",
        source_id="resource-1",
        target_body_id="body-1",
        maximum_material=1.0,
        kind=InterventionKind.NON_EXPERIMENTAL,
    )

    with pytest.raises(MaterialTransferAuthorizationUnsupported, match="no verified authorization source"):
        apply_material_transfer(
            world=world,
            checkpoint_store=checkpoint_store,
            resource=object(),
            body=object(),
            request=request,
            intervention_action_id="action-1",
            transition_id="transition-1",
            requested_material=1.0,
        )

    assert world.tick_called is False
    assert checkpoint_store.write_called is False
