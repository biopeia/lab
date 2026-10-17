"""Exploratory Instrumentation Pilot: 2x2 Factorial Matrix & Multicut Restore.

Runs G1 (Control Inert), G2 (Control Somatic), G3 (Control Plastic), and G4 (Experimental Full)
for 20 cycles each in the real World causal runtime with MuJoCo physics, plus G4 cold restore
at cut 10 -> 20 cycles.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys

# Add world repository to sys.path so we can import world and harness
repo_root = Path("/home/alessbarb/workspace/repos/active/biopeia-workspace/repos/world")
sys.path.insert(0, str(repo_root))
sys.path.insert(0, str(repo_root / "src"))

import importlib.util
_spec = importlib.util.spec_from_file_location(
    "m3_acceptance_harness",
    repo_root / "tests/integration/test_end_to_end_causal_cycle_acceptance.py",
)
acc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(acc)

from modality.kinematics import KinematicSomaticTransductionV1
from organism import (
    EmbodimentContextRef,
    OrganismCheckpoint,
    OrganismIdentity,
    OrganismLifecycle,
    OrganismTransitionState,
)
from organism.actuation import (
    ActuatorEvidenceContext,
    ActuatorSurface,
    CompetenceDevelopmentEngine,
    OrganismExplorationComposer,
)
from organism.cognition import (
    CognitiveRuntimeCheckpoint,
    CognitiveTransitionState,
    EdgeLearningInstruction,
    SenseChannelBinding,
)
from organism.cognition.graph import CognitiveGraph, PlasticEdge, PlasticNode
from organism.cognition.limits import KernelLimits
from organism.cognition.types import EdgeKind, NodeKind
from organism.memory import ExperienceRecordingPolicy

from embodiment.physics3d.articulated_state import (
    ARTICULATED_PHYSICAL_CHECKPOINT_SCHEMA,
)
from world.adapters.articulated_mujoco import (
    ArticulatedMujocoConfiguration,
)
from world.causal_cycle import (
    ScalarSensorimotorCycleInputs,
    restore_scalar_sensorimotor_runtime,
    run_scalar_sensorimotor_session,
)
from world.durable_runtime import (
    DurableJournalSnapshotStore,
    DurableWorldRuntime,
    PresenceOwnerLink,
    WorldGenesisSpec,
)
from world.manifest import WorldCausalManifestStore
from world.owner_checkpoint_store import FileOwnerCheckpointStore
from world.runtime import PresenceId, WorldId


def build_environment(runtime_dir: Path, with_plasticity: bool, with_somatic: bool):
    shutil.rmtree(runtime_dir, ignore_errors=True)
    runtime_dir.mkdir(parents=True, exist_ok=True)
    manifest_store = WorldCausalManifestStore(runtime_dir / "manifest.json")
    journal_store = DurableJournalSnapshotStore(runtime_dir / "journal", WorldId(acc.WORLD_ID))
    owner_dir = runtime_dir / "owners"
    owner_dir.mkdir(parents=True, exist_ok=True)
    owner_store = FileOwnerCheckpointStore(owner_dir / "committed")

    morphology = acc.ActiveArticulatedMorphology.from_spec(
        body_id=acc.BODY_ID,
        embodiment_episode_id=acc.EPISODE_ID,
        morphology_revision=acc.MORPHOLOGY_REVISION,
        spec=acc._spec(),
    )
    kernel_limits = KernelLimits()

    surface = ActuatorSurface.from_effector_ids(
        ("actuator.hinge.positive", "actuator.hinge.negative"),
        fingerprint_material=acc.SURFACE_FINGERPRINT,
    )
    actuator_context = ActuatorEvidenceContext(
        acc.BODY_ID, acc.EPISODE_ID, acc.MORPHOLOGY_REVISION, surface.contract_fingerprint
    )

    graph = CognitiveGraph(
        nodes=(
            PlasticNode("opaque.scalar.signal", NodeKind.SENSE),
            PlasticNode("concept.resource", NodeKind.CONCEPT),
        ),
        edges=(
            PlasticEdge(
                "opaque.scalar.signal", "concept.resource", EdgeKind.EXCITATORY,
                0.20, 0.0, 0,
            ),
        ),
        kernel_limits=kernel_limits,
    )
    cognition = CognitiveRuntimeCheckpoint(
        state=CognitiveTransitionState.initial(acc.ORGANISM_ID),
        graph=graph,
    )
    organism = OrganismTransitionState(
        owner_checkpoint=cognition.to_organism_checkpoint(),
        organism_step=0,
        embodiment=EmbodimentContextRef(acc.BODY_ID, acc.EPISODE_ID, acc.MORPHOLOGY_REVISION),
        lifecycle=OrganismLifecycle.ACTIVE,
    )

    pose = acc.BodyPoseSample(
        body_id=acc.BODY_ID,
        reference_frame=acc.FRAME_ID,
        body_frame="body.root",
        position_m=(0.0, 0.0, 0.0),
        orientation_xyzw=(0.0, 0.0, 0.0, 1.0),
        sample_kind="genesis",
        sample_value=0,
    )
    root = acc.EmbodimentPhysicalState(
        world_id=acc.WORLD_ID,
        causal_tick=0,
        body_id=acc.BODY_ID,
        embodiment_episode_id=acc.EPISODE_ID,
        morphology_revision=acc.MORPHOLOGY_REVISION,
        pose=pose,
        linear_velocity_m_per_s=(0.0, 0.0, 0.0),
        angular_velocity_rad_per_s=(0.0, 0.0, 0.0),
    )
    body = acc.ArticulatedEmbodimentPhysicalState(
        root=root,
        morphology=morphology,
        joints=(acc.JointKinematicState("joint.hinge", 0.0, 0.0),),
    )
    env_owner = acc.StaticEnvironmentOwner(
        acc.StaticPhysicalScene(
            environment_id=acc.ENVIRONMENT_ID,
            environment_revision=acc.ENVIRONMENT_REVISION,
            frame=acc._frame(),
            gravity_m_s2=(0.0, 0.0, 0.0),
            objects=(),
        ),
        owner_id=acc.ENVIRONMENT_OWNER_ID,
        world_id=acc.WORLD_ID,
    )
    field = acc.IdentifiedFiniteScalarField(
        resource_id=acc.RESOURCE_ID,
        field_revision=acc.FIELD_REVISION,
        environment_id=acc.ENVIRONMENT_ID,
        environment_revision=acc.ENVIRONMENT_REVISION,
        frame_id=acc.FRAME_ID,
        state=acc.FiniteResourceState(
            position=(1.0, 0.0, 0.0), radius=0.1, field_radius=2.0,
            remaining=10.0, transfer_per_tick=1.0,
        ),
    )

    engine = CompetenceDevelopmentEngine(
        surface.actuator_ids,
        organism_id=str(acc.ORGANISM_ID),
        embodiment_fingerprint=actuator_context.fingerprint,
        exclusive_actuator_groups=(("actuator.hinge.positive", "actuator.hinge.negative"),),
    )
    composer = OrganismExplorationComposer(
        organism_id=str(acc.ORGANISM_ID),
        engine=engine,
    )

    contracts = {
        ("organism", str(acc.ORGANISM_ID)): acc.OrganismCheckpointContract(kernel_limits=kernel_limits),
        ("embodiment", acc.BODY_ID): acc._Contract(
            acc.BODY_ID, {ARTICULATED_PHYSICAL_CHECKPOINT_SCHEMA: lambda data: acc._valid_body_checkpoint(data, morphology)},
        ),
        ("environment", acc.ENVIRONMENT_OWNER_ID): acc._Contract(
            acc.ENVIRONMENT_OWNER_ID, {acc.StaticEnvironmentOwner.CHECKPOINT_SCHEMA: lambda data: acc.StaticEnvironmentOwner.validate_checkpoint(
                data, acc.ENVIRONMENT_OWNER_ID, acc.StaticEnvironmentOwner.CHECKPOINT_SCHEMA
            )},
        ),
        ("environment", acc.RESOURCE_ID): acc._Contract(
            acc.RESOURCE_ID, {acc.IdentifiedFiniteScalarField.OWNER_SCHEMA: lambda data: acc.IdentifiedFiniteScalarField.validate_checkpoint(
                data, acc.RESOURCE_ID, acc.IdentifiedFiniteScalarField.OWNER_SCHEMA
            )},
        ),
    }

    initial_refs = (
        acc._reference(owner_dir, "organism", str(acc.ORGANISM_ID), "organism-transition-v2", 0, organism.to_bytes()),
        acc._reference(owner_dir, "embodiment", acc.BODY_ID, ARTICULATED_PHYSICAL_CHECKPOINT_SCHEMA, 0, body.checkpoint_bytes()),
        acc._reference(owner_dir, "environment", acc.ENVIRONMENT_OWNER_ID, acc.StaticEnvironmentOwner.CHECKPOINT_SCHEMA, 0, env_owner.checkpoint_bytes()),
        acc._reference(owner_dir, "environment", acc.RESOURCE_ID, acc.IdentifiedFiniteScalarField.OWNER_SCHEMA, 0, field.checkpoint_bytes()),
    )
    world = DurableWorldRuntime.initialize(
        WorldGenesisSpec(
            world_id=WorldId(acc.WORLD_ID),
            initial_presence_ids=(acc.PRESENCE_ID,),
            registered_owner_ids=tuple(sorted(contracts)),
            initial_owner_references=initial_refs,
            owner_checkpoint_contracts=contracts,
            presence_owner_links=(PresenceOwnerLink(PresenceId(acc.PRESENCE_ID), "organism", str(acc.ORGANISM_ID)),),
        ),
        acc.PRESENCE_ID,
        manifest_store,
        journal_store,
        owner_checkpoint_verifier=lambda refs: all(
            contracts[(ref.owner, ref.owner_identity)].validate_checkpoint(
                Path(ref.locator).read_bytes(), ref.owner_identity, ref.schema_version
            ) for ref in refs if ref.owner != "world-journal"
        ),
    )

    learning = (
        (
            EdgeLearningInstruction(
                source_id="opaque.scalar.signal",
                target_id="concept.resource",
                kind=EdgeKind.EXCITATORY,
                learning_rate=0.15,
                modulation=1.0,
                eligibility_decay=0.90,
                eligible=True,
            ),
        )
        if with_plasticity
        else ()
    )

    receptor = acc.EmbodimentReceptor(
        receptor_id=acc.RECEPTOR_ID,
        body_id=acc.BODY_ID,
        embodiment_episode_id=acc.EPISODE_ID,
        morphology_revision=acc.MORPHOLOGY_REVISION,
        body_frame="body.root",
        position_in_body_frame_m=(0.0, 0.0, 0.0),
    )
    differential_binding = acc.EmbodimentDifferentialMotorBinding(
        binding_id="binding.differential-r1",
        body_id=acc.BODY_ID,
        embodiment_episode_id=acc.EPISODE_ID,
        morphology_revision=acc.MORPHOLOGY_REVISION,
        source_surface_fingerprint=surface.contract_fingerprint,
        pairs=(
            acc.DifferentialMotorPair(
                joint_id="joint.hinge",
                positive_actuator_id="actuator.hinge.positive",
                negative_actuator_id="actuator.hinge.negative",
                scale=0.5,
            ),
        ),
    )
    torque_binding = acc.EmbodimentJointTorqueBinding(
        binding_id="binding.torque-r1",
        body_id=acc.BODY_ID,
        embodiment_episode_id=acc.EPISODE_ID,
        morphology_revision=acc.MORPHOLOGY_REVISION,
        source_surface_fingerprint=surface.contract_fingerprint,
        channels=(acc.JointTorqueChannelBinding("actuator.hinge", "joint.hinge", (0.0, 1.0, 0.0)),),
    )
    solver = ArticulatedMujocoConfiguration(
        revision=acc.SOLVER_REVISION,
        timestep_s=0.01,
        iterations=50,
        tolerance=1e-10,
        solref=(0.02, 1.0),
        solimp=(0.9, 0.95, 0.001, 0.5, 2.0),
        contact_policy="max-sliding-body-torsion-rolling/no-self-collision-v1",
        velocity_regulation_policy="m1-fixed-single-hinge-grid-v2",
    )

    cycle_inputs = ScalarSensorimotorCycleInputs(
        environment_revision=acc.ENVIRONMENT_REVISION,
        solver_configuration=solver,
        current_organism=organism,
        action_composer=composer,
        receptor=receptor,
        embodiment_state=body.root,
        environment_field=field,
        sampling_frame=acc._frame(),
        transduction=acc.DimensionlessScalarFieldIdentityV1(),
        sense_binding=SenseChannelBinding("channel.scalar", acc.RECEPTOR_ID, "opaque.scalar.signal"),
        kernel_limits=kernel_limits,
        actuator_context=actuator_context,
        actuator_surface=surface,
        articulated_body=body,
        active_morphology=morphology,
        differential_binding=differential_binding,
        torque_binding=torque_binding,
        environment_owner=env_owner,
        owner_checkpoint_store=owner_store,
        embodiment_geometry_revision="geo.r1",
        learning=learning,
        experience_policy=ExperienceRecordingPolicy(record_reception=True, max_records=64),
        enable_somatic_feedback=with_somatic,
        somatic_transduction=KinematicSomaticTransductionV1() if with_somatic else None,
    )
    return world, cycle_inputs, manifest_store, journal_store, surface, actuator_context, morphology, contracts


def run_group(name: str, base_dir: Path, with_plasticity: bool, with_somatic: bool, cycles: int = 20):
    group_dir = base_dir / name
    world, inputs, manifest_store, journal_store, surface, act_ctx, morphology, contracts = build_environment(
        group_dir, with_plasticity=with_plasticity, with_somatic=with_somatic
    )
    res = run_scalar_sensorimotor_session(
        world,
        acc.ObservationPlane(),
        run_id=f"session-{name}",
        source_revisions={"world": "pilot-commit"},
        cycle_inputs=inputs,
        max_cycles=cycles,
        retain_cycle_results=True,
    )
    last_sensory = res.cycles[-1].sensory_input.state
    chk = CognitiveRuntimeCheckpoint.from_organism_checkpoint(last_sensory.owner_checkpoint, kernel_limits=KernelLimits())
    edge = next(e for e in chk.graph.edges if e.source_id == "opaque.scalar.signal")
    engine_chk = inputs.action_composer.engine.checkpoint()

    return {
        "group": name,
        "plasticity": with_plasticity,
        "somatic": with_somatic,
        "completed_cycles": res.completed_cycle_count,
        "last_cut_tick": res.last_committed_cut.causal_tick if res.last_committed_cut else None,
        "initial_weight": 0.20,
        "final_weight": edge.weight,
        "weight_delta": edge.weight - 0.20,
        "experience_records_count": len(chk.experience_records),
        "frame_history_count": len(engine_chk["frame_history"]),
        "primitives_discovered": len(engine_chk["primitives"]),
        "horizon_counts": engine_chk["horizon_counts"],
    }


def run_g4_multicut_restore(base_dir: Path):
    """Run G4 with interruption at cut 10 and restore to cycle 20."""
    g4_dir = base_dir / "G4_multicut"
    world, inputs, manifest_store, journal_store, surface, act_ctx, morphology, contracts = build_environment(
        g4_dir, with_plasticity=True, with_somatic=True
    )
    # Part 1: 10 cycles
    res_part1 = run_scalar_sensorimotor_session(
        world,
        acc.ObservationPlane(),
        run_id="session-G4-cut10",
        source_revisions={"world": "pilot-commit"},
        cycle_inputs=inputs,
        max_cycles=10,
        retain_cycle_results=True,
    )
    cut10 = res_part1.last_committed_cut
    assert cut10.causal_tick == 10

    # Cold restore from cut 10
    restored = restore_scalar_sensorimotor_runtime(
        WorldId(acc.WORLD_ID),
        acc.PRESENCE_ID,
        manifest_store,
        journal_store,
        owner_checkpoint_verifier=lambda refs: True,
        owner_checkpoint_contracts=contracts,
        active_morphology=morphology,
        expected_organism_id=str(acc.ORGANISM_ID),
        expected_physical_step_id="session-G4-cut10:physical-step:10",
        expected_environment_owner_id=acc.ENVIRONMENT_OWNER_ID,
        expected_environment_id=acc.ENVIRONMENT_ID,
        expected_environment_revision=acc.ENVIRONMENT_REVISION,
        expected_field_id=acc.RESOURCE_ID,
        expected_field_revision=acc.FIELD_REVISION,
        kernel_limits=KernelLimits(),
        actuator_context=act_ctx,
        actuator_surface=surface,
    )
    restored_frames = restored.organism.action_composer.engine.checkpoint()["frame_history"]
    assert len(restored_frames) == 10
    assert [f["tick"] for f in restored_frames] == list(range(1, 11))

    # Part 2: Resume 10 more cycles (11 to 20)
    inputs_resumed = ScalarSensorimotorCycleInputs(
        environment_revision=acc.ENVIRONMENT_REVISION,
        solver_configuration=inputs.solver_configuration,
        current_organism=restored.organism.transition_state,
        action_composer=restored.organism.action_composer,
        receptor=inputs.receptor,
        embodiment_state=restored.articulated_body.root,
        environment_field=restored.environment_field,
        sampling_frame=acc._frame(),
        transduction=acc.DimensionlessScalarFieldIdentityV1(),
        sense_binding=inputs.sense_binding,
        kernel_limits=KernelLimits(),
        actuator_context=act_ctx,
        actuator_surface=surface,
        articulated_body=restored.articulated_body,
        active_morphology=morphology,
        differential_binding=inputs.differential_binding,
        torque_binding=inputs.torque_binding,
        environment_owner=restored.environment_owner,
        owner_checkpoint_store=FileOwnerCheckpointStore(g4_dir / "owners" / "committed"),
        embodiment_geometry_revision="geo.r1",
        learning=inputs.learning,
        experience_policy=inputs.experience_policy,
        enable_somatic_feedback=True,
        somatic_transduction=KinematicSomaticTransductionV1(),
    )

    res_part2 = run_scalar_sensorimotor_session(
        restored.world,
        acc.ObservationPlane(),
        run_id="session-G4-resumed",
        source_revisions={"world": "pilot-commit"},
        cycle_inputs=inputs_resumed,
        max_cycles=10,
        retain_cycle_results=True,
    )
    print("res_part2:", res_part2.status, res_part2.error, res_part2.failure_kind, "completed:", res_part2.completed_cycle_count)
    assert res_part2.completed_cycle_count == 10
    assert res_part2.last_committed_cut.causal_tick == 20

    resumed_engine = restored.organism.action_composer.engine.checkpoint()
    last_sensory = res_part2.cycles[-1].sensory_input.state
    chk = CognitiveRuntimeCheckpoint.from_organism_checkpoint(last_sensory.owner_checkpoint, kernel_limits=KernelLimits())
    edge = next(e for e in chk.graph.edges if e.source_id == "opaque.scalar.signal")

    return {
        "group": "G4_RESTORED",
        "interruption_tick": 10,
        "completed_cycles": 20,
        "last_cut_tick": 20,
        "final_weight": edge.weight,
        "experience_records_count": len(chk.experience_records),
        "frame_history_count": len(resumed_engine["frame_history"]),
        "primitives_discovered": len(resumed_engine["primitives"]),
        "horizon_counts": resumed_engine["horizon_counts"],
    }


def main():
    pilot_dir = Path("/tmp/biopeia_longitudinal_pilot")
    pilot_dir.mkdir(parents=True, exist_ok=True)

    print("Running G1 (Control Inert: P=0, S=0)...")
    res_g1 = run_group("G1_CONTROL_INERT", pilot_dir, with_plasticity=False, with_somatic=False, cycles=20)

    print("Running G2 (Control Somatic: P=0, S=1)...")
    res_g2 = run_group("G2_CONTROL_SOMATIC", pilot_dir, with_plasticity=False, with_somatic=True, cycles=20)

    print("Running G3 (Control Plastic: P=1, S=0)...")
    res_g3 = run_group("G3_CONTROL_PLASTIC", pilot_dir, with_plasticity=True, with_somatic=False, cycles=20)

    print("Running G4 (Experimental Full: P=1, S=1)...")
    res_g4 = run_group("G4_EXPERIMENTAL_FULL", pilot_dir, with_plasticity=True, with_somatic=True, cycles=20)

    print("Running G4 Restored (Interrupted at cut 10 -> restored -> 20)...")
    res_g4_restored = run_g4_multicut_restore(pilot_dir)

    results = {
        "pilot_id": "PILOT-FACTORIAL-20261017",
        "status": "COMPLETED",
        "groups": [res_g1, res_g2, res_g3, res_g4, res_g4_restored],
    }

    print("\n=== PILOT RESULTS SUMMARY ===")
    print(json.dumps(results, indent=2))

    out_file = Path("/home/alessbarb/.gemini/antigravity-cli/brain/a1bbe301-b17c-40db-b33c-7f92d7b9541d/scratch/pilot_results.json")
    out_file.write_text(json.dumps(results, indent=2))
    print(f"\nWrote results to {out_file}")


if __name__ == "__main__":
    main()
