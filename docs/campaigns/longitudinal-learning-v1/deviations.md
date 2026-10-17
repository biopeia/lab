# Campaign V1 — frozen protocol versus execution

The frozen text is `docs/protocols/protocol-lab-longitudinal-learning-v1.md`
(sha256 `e6b088a0…`). The executed scripts are preserved in
`artifacts/original/`. Line numbers refer to those copies. Nothing here
reinterprets a result; each row states what was planned and what was run.

**Classification: the results come from an experimental variant that does
not conform to the written protocol.** They may not be reported as outcomes
of `PROTOCOL-LAB-LONGITUDINAL-LEARNING-V1`.

## Factor P — plasticity (Oja)

| Item | Protocol | Executed | Source |
|---|---|---|---|
| Learning rate | η = 0.05 (§3, G3/G4) | `learning_rate=0.15` | `run_pilot_factorial.py` line 230; E2 script line 232; E3 script line 229 |
| Modulation | not stated | `modulation=1.0`, fixed by the script | same |
| Eligibility decay | not stated | `eligibility_decay=0.90` | same |
| Eligible edges | not stated | the single edge `opaque.scalar.signal → concept.resource`, chosen by the script | same |
| Initial graph | 2 nodes, w₀ = 0.20 (§3) | as planned | `build_environment` |

## Factor S — joint kinematic feedback

| Item | Protocol | Executed |
|---|---|---|
| Name | "retroalimentación somática interoceptiva" (§1), "somática" (§2–§3) | `KinematicSomaticTransductionV1`: joint position and velocity. This is **proprioception**, not interoception (see README) |
| Off condition | `somatic_transduction=None` | `enable_somatic_feedback=False`, `somatic_transduction=None` (as planned) |

## Shared configuration

| Item | Protocol | Executed |
|---|---|---|
| Solver | Euler, 0.01 s, 50 iterations (§3) | `timestep_s=0.01`, `iterations=50`. The integrator is not set in the scripts. The scripts add `velocity_regulation_policy="m1-fixed-single-hinge-grid-v2"`, which the protocol does not mention (see Execution history) |
| Kernel limits | identical across cells | `KernelLimits()` defaults in every cell (as planned) |
| Experience recording | not stated | `ExperienceRecordingPolicy(record_reception=True, max_records=64)` in every cell: 20 records per cell are logging, not an outcome |
| Seeds and replicates | not stated | none: one deterministic run per cell |

## Scenarios

| Scenario | Protocol (§4) | Executed |
|---|---|---|
| E1 stable field | 20–50 cycles, constant source at (1, 0, 0) | No separate E1 run. The four 20-cycle factorial runs use a static field with its source at (1, 0, 0) |
| E2 variable field | Phase A cycles 1–20 at I = 1.0; Phase B 21–40, I = 0.0; Phase C 41–60, reappearance in **inverted** orientation | 10 cycles active, then 10 cycles with the field replaced **by the script** with a field of `remaining=0.0` at the same position (`run_environmental_variability.py`, lines 322–332). No Phase C and no inversion, so **H5 was not tested** |
| E3 bodily perturbation | variable joint resistance (change in damping or load torque) under Embodiment's contracts | **motor gain** changed: the differential binding `scale` goes from 0.5 to 0.2 (`run_bodily_perturbation.py`, lines 255 and 329–330), labelled `damped_mechanics`. Joint damping and load are not changed; 15 cycles per condition |

## Continuity (§5, H4)

| Item | Protocol | Executed (`run_g4_multicut_restore`) |
|---|---|---|
| Session length | 30 cycles | 20 cycles |
| Interruptions | cuts 10 and 20, each with a process abort and a cold restore | one cut at 10; restored **in the same process**; no abort |
| Restore verification | World's owner-checkpoint contracts (§6.2 counts their failure as a fault) | `owner_checkpoint_verifier=lambda refs: True` (`run_pilot_factorial.py` line 371): verification disabled on the path under test |
| Comparison | strict identity of `frame_history`, `experience_records`, `graph.edges[0].weight`, `horizon_counts` and `horizon_stats`, against an uninterrupted 30-cycle run | final weight, record and frame counts, primitive count and `horizon_counts`, against the separate 20-cycle G4 run; restored frame ticks 1–10 checked after the restore |

## Hypotheses and metrics

| Item | Protocol | Executed |
|---|---|---|
| H1 monotonic, bounded | trajectory of w | only initial and final w recorded; monotonicity not measured |
| H2 functional difference | probe x_probe; "estadísticamente diferenciado"; Δ < 10⁻⁶ falsifies | **no probe in any script; $D_{func}$ (§6.1) never computed**; no statistical test |
| H3 frames and primitives | `frame_history` > 0 and primitives present | measured (counts) |
| H4 durability | see Continuity | see Continuity |
| H5 environment-dependent rate | inversion and extinction | extinction only (E2) |
| $R_{frames}$ | restored / committed frames ≡ 1.0 | frame count compared at the end; frame ticks 1–10 checked after restore |
| Primitive reuse (§6.2, Inconclusión) | needed to avoid "inconclusive" | not measured |

## Execution history

The agent's step log records about eight edit-and-run iterations of
`run_pilot_factorial.py` between 23:23:47Z and 23:26:34Z. Several failed; the
last failure was `ValueError: joint 'joint.hinge' velocity exceeds active
morphology limit` in the resumed G4 session. The last edit before the run that
wrote `pilot_results.json` (23:27:29Z) added
`velocity_regulation_policy="m1-fixed-single-hinge-grid-v2"`. The script was
therefore changed in response to failures during data collection, and the
discarded attempts wrote no result file.
