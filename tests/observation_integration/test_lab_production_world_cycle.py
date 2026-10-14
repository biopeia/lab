"""Lab reads owner projections from World’s production causal-cycle path.

The deterministic World acceptance fixture configures initial state and calls
the production composition. This test captures its real ObservationPlane; it
does not create or join post-commit claims itself.
"""

from __future__ import annotations

import os
import runpy
from dataclasses import replace
from pathlib import Path

from lab.observation_consumer import (
    LabObservationAssociation,
    LabObservationReadStatus,
    associate_current_messages,
)


def test_lab_associates_real_production_world_cycle_publications(
    tmp_path: Path,
) -> None:
    source = Path(os.environ["BIOPEIA_WORLD_ACCEPTANCE_TEST"])
    world_test = runpy.run_path(str(source))
    real_plane_type = world_test["ObservationPlane"]
    captured_planes = []

    class CapturedObservationPlane(real_plane_type):
        def __init__(self):
            super().__init__()
            captured_planes.append(self)

    # Retain the actual in-process plane used by World’s production path.
    # Behavior is unchanged; this only exposes the object for Lab’s consumer.
    world_test["_run"].__globals__["ObservationPlane"] = CapturedObservationPlane
    run, published_messages, resumed, _ = world_test["_run"](
        tmp_path / "world-cycle", stop_after_first=True
    )

    assert resumed is None
    assert len(captured_planes) == 1
    plane = captured_planes[0]
    cut = run.committed_cut
    assert run.observation_publication.committed_cut == cut
    assert cut.causal_tick == run.context.target_causal_tick == 1
    assert tuple(message.sequence for message in published_messages) == (
        run.observation_publication.delivery_sequences
    )
    assert len(published_messages) == 2

    association = LabObservationAssociation.for_committed_cut(
        experiment_id="lab-production-cycle",
        run_id="run-production-cycle-1",
        committed_cut=cut,
    )
    before_read_tick = run.committed_cut.causal_tick
    result = associate_current_messages(
        plane, association=association, committed_cut=cut
    )

    assert result.status is LabObservationReadStatus.ASSOCIATED
    assert result.association == association
    assert result.messages == published_messages
    assert run.committed_cut.causal_tick == before_read_tick
    assert {message.observation.claim.authority.value for message in result.messages} == {
        "embodiment",
        "environment",
    }

    owner_references = cut.owner_checkpoint_references
    assert {
        message.observation.claim.family.path
        for message in result.messages
    } == {("body_pose",), ("finite_scalar_field",)}

    for message in result.messages:
        observation = message.observation
        authority = observation.claim.authority.value
        assert observation.family.authority.value == authority
        configuration = dict(
            observation.lineage.transformation.effective_configuration
        )
        matching_refs = tuple(
            reference
            for reference in owner_references
            if reference.owner == authority
            and any(parent.reference == reference.sha256 for parent in observation.lineage.parents)
        )
        assert len(matching_refs) == 1
        assert matching_refs[0].owner_identity == (
            "body.acceptance.sensorimotor-v1"
            if authority == "embodiment"
            else "resource.acceptance.scalar-field-v1"
        )
        assert configuration["world_id"] == cut.world_id
        if authority == "embodiment":
            assert configuration["causal_tick"] == str(cut.causal_tick)
            assert (
                configuration["embodiment_episode_id"]
                == "episode.acceptance.sensorimotor-v1"
            )
            assert (
                configuration["morphology_revision"]
                == "morphology.acceptance.sensorimotor-r1"
            )
            assert configuration["environment_revision"] == "environment.acceptance.r1"
        else:
            assert (
                configuration["physical_step_id"]
                == "physical-step.acceptance.sensorimotor.tick-1"
            )
            assert configuration["environment_revision"] == "environment.acceptance.r1"
            assert configuration["field_revision"] == "field.acceptance.r1"
        assert any(
            reference.domain.value == "world"
            and reference.kind in {"world_target_causal_tick", "world_causal_tick"}
            and reference.value == cut.causal_tick
            for reference in observation.context_time
        )

    # A caller cannot reuse the Lab association against a different cut.
    mismatched_cut = replace(cut, causal_tick=cut.causal_tick + 1)
    rejected = associate_current_messages(
        plane, association=association, committed_cut=mismatched_cut
    )
    assert rejected.status is LabObservationReadStatus.UNASSOCIATED
    assert rejected.reason == "lab_context_does_not_match_committed_cut"
    assert run.committed_cut.causal_tick == before_read_tick
