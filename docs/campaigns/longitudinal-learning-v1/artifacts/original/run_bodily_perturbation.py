"""Phase 2: E3 Bodily Perturbation Experiment.

Compares standard embodiment mechanics (scale 0.5) against perturbed mechanics
(scale 0.2, damped mechanical response) to verify that CompetenceDevelopmentEngine
and somatic feedback reflect true physical dynamics rather than fictitious projections.
"""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys

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


def run_e3_mechanical_comparison(base_dir: Path):
    def run_with_scale(name: str, motor_scale: float, cycles: int = 15):
        run_dir = base_dir / name
        shutil.rmtree(run_dir, ignore_errors=True)
        run_dir.mkdir(parents=True, exist_ok=True)

        manifest_store = WorldCausalManifestStore(run_dir / "manifest.json")
        journal_store = DurableJournalSnapshotStore(run_dir / "journal", WorldId(acc.WORLD_ID))
        owner_dir = run_dir / "owners"
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
                    scale=motor_scale,
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

        inputs = ScalarSensorimotorCycleInputs(
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
            enable_somatic_feedback=True,
            somatic_transduction=KinematicSomaticTransductionV1(),
        )

        res = run_scalar_sensorimotor_session(
            world,
            acc.ObservationPlane(),
            run_id=f"session-E3-{name}",
            source_revisions={"world": "pilot-commit"},
            cycle_inputs=inputs,
            max_cycles=cycles,
            retain_cycle_results=True,
        )
        engine_chk = inputs.action_composer.engine.checkpoint()
        frames = engine_chk["frame_history"]
        avg_abs_vel = sum(abs(f["body_state"]["joint.hinge:vel"]) for f in frames) / len(frames)
        max_abs_pos = max(abs(f["body_state"]["joint.hinge:pos"]) for f in frames)

        return {
            "name": name,
            "motor_scale": motor_scale,
            "completed_cycles": res.completed_cycle_count,
            "mean_joint_speed_rad_per_s": avg_abs_vel,
            "max_joint_displacement_rad": max_abs_pos,
            "primitives_discovered": len(engine_chk["primitives"]),
            "horizon_counts": engine_chk["horizon_counts"],
        }

    res_standard = run_with_scale("standard_mechanics", motor_scale=0.5)
    res_perturbed = run_with_scale("damped_mechanics", motor_scale=0.2)

    return {
        "scenario": "E3_BODILY_PERTURBATION",
        "standard": res_standard,
        "perturbed": res_perturbed,
        "speed_reduction_ratio": res_perturbed["mean_joint_speed_rad_per_s"] / res_standard["mean_joint_speed_rad_per_s"],
    }


def main():
    pilot_dir = Path("/tmp/biopeia_e3_pilot")
    pilot_dir.mkdir(parents=True, exist_ok=True)

    print("Running E3 (Bodily Perturbation: Standard vs Damped Mechanics)...")
    res_e3 = run_e3_mechanical_comparison(pilot_dir)

    print("\n=== E3 BODILY PERTURBATION RESULTS ===")
    print(json.dumps(res_e3, indent=2))

    out_file = Path("/home/alessbarb/.gemini/antigravity-cli/brain/a1bbe301-b17c-40db-b33c-7f92d7b9541d/scratch/e3_results.json")
    out_file.write_text(json.dumps(res_e3, indent=2))
    print(f"\nWrote results to {out_file}")


if __name__ == "__main__":
    main()
