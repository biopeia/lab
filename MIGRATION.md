# Migration record

## Source baseline

- Source repository: local `symbiont-lab` monorepo
- Source SHA: `80d372a186513035f85a769db886e505cabba52d`
- Architecture audit baseline: `cef998a55aae32ed8b2f7373079c11667b01e915`

## Initial slice dispositions

| Source path | Disposition | Target path | Notes |
| --- | --- | --- | --- |
| `lab/src/lab/studies/common/statistics.py` | MOVE (copy-first rehearsal) | `src/lab/studies/common/statistics.py` | Pure descriptive/paired scalar summaries; source-path commit `13720935595fedabec2c376dc933629b0deae5aa`; copied bytes verified identical. |
| `lab/src/lab/studies/common/pairing.py` | MOVE (copy-first rehearsal) | `src/lab/studies/common/pairing.py` | Enforces seed pairing and disjointness for study design; source-path commit `13720935595fedabec2c376dc933629b0deae5aa`; copied bytes verified identical. |
| `lab/tests/unit/lab/test_common_stats.py` | MOVE (copy-first rehearsal) | `tests/test_statistics.py` | Existing focused unit tests; source-path commit `282c44eea894faedb57763c3545a1401cf032a86`; copied bytes identical. |
| `lab/tests/experimental_integrity/test_pairing.py` | MOVE (copy-first rehearsal) | `tests/test_pairing.py` | Existing focused seed-pairing checks; source-path commit `282c44eea894faedb57763c3545a1401cf032a86`; copied bytes identical. |

No new Git history is claimed for copied modules. Provenance is the pinned source
SHA and paths above. Source repository remains unchanged.

## Deferred / excluded

| Source area | Disposition | Reason |
| --- | --- | --- |
| `lab/studies/**` beyond the three extracted common utilities | DEFER pending study/protocol-level disposition | Lab is the designated scientific custodian. No blanket transfer or discard follows from that designation; the source modules remain deferred until their study/protocol disposition is recorded. No source implementation is retained for compatibility. |
| `lab/experiments/**` | DEFER | Runner, registry, manifests and workspace interact with source layout, runtime composition and persistence/provenance. |
| `lab/physics3d/**`, `lab/integration/**`, `lab/world/**` | DEFER | Mixed physical substrate, semantic authorities and runtime orchestration; not safe for bulk transfer. |
| `lab/observation/**`, `lab/observatory/**`, `lab/server/**`, `lab/app/**` | DEFER | Observation, transport, evidence custody and UI boundaries require separate extraction. |
| CLI and reproduction code | DEFER | Entrypoints and reproduction callers are mixed with CURRENT runtime authorities/interventions. |
| Scientific assets, manifests and run/checkpoint payloads | Excluded from runtime-package transfer; custody disposition remains DEFER | Lab is the designated scientific custodian. This scope exclusion does not mean disposal: source artifacts remain untouched until a group/item-specific preservation and target-location decision is recorded. |

## Known rewrites

- Copied module bytes are unchanged.
- Test files are rewritten to exercise the extracted package namespace (`lab`).
- Distribution/import name is `lab`; no `biopeia_*` prefix is used.
- This narrow utility slice is an extraction rehearsal, not a complete Lab repo migration or authority claim.

## Validation

Build/install/test results are recorded in the migration PR and checks. No
experiments were executed and no scientific assets were moved.

## Additional evidence-handling slice

| Source path | Disposition | Target path | Provenance |
| --- | --- | --- | --- |
| `lab/src/lab/studies/common/digests.py` | MOVE (copy-first extraction) | `src/lab/studies/common/digests.py` | Source repository `alessbarb/symbiont-lab`, source SHA `80d372a186513035f85a769db886e505cabba52d`; source-path commit `13720935595fedabec2c376dc933629b0deae5aa`; blob `64ba8a0d417ef64c0d7429c0ad6289007f673290`; byte-identical copy SHA-256 `544b0a8ec525bc5589692dd2692d4af05eff36806463484c96fba6d7a2e5b588`. Also present at audit baseline `cef998a55aae32ed8b2f7373079c11667b01e915`. |
| `lab/tests/unit/lab/test_digests.py` | MOVE (test path adaptation only) | `tests/test_digests.py` | Same source repository/SHA; source-path commit `282c44eea894faedb57763c3545a1401cf032a86`; source blob `065d75478b633c469b715fa2a4d1c4b9093ec374`. Import remains `lab.studies.common.digests`; assertions and fixtures are unchanged. |

This bounded utility computes deterministic digests for experiment event streams and
configuration records. The pinned source `ExperimentRunner` is its only tracked
runtime caller. The extracted helper contains no runtime dependency and is Lab-owned
as experiment/evidence apparatus; it does not acquire World state ownership or assert
causal equivalence beyond the supplied event representation. The source package and
all scientific artifacts remain untouched. No historical results were regenerated.

### Deterministic event-shape hardening

The copied source helper's fallback to `str(event)` was narrowed in Biopeia: the
target accepts the documented event-field shape and plain strings, and raises
`TypeError` for other objects rather than hashing a default representation that may
contain a process-specific address. A regression test uses two otherwise identical
instances with distinct default representations. This is a target-side rewrite, not
a source change; the source provenance above remains unchanged.

Source caller review at the recorded source SHA found `ExperimentRunner.run` as the
only tracked caller. It collects events only for `protocol == "simulate"`. That
protocol is not present in the pinned `PROTOCOLS` registry, so no concrete runtime
producer/event class is reachable in the tracked registry to further narrow the
accepted event contract. The source tests define the expected event shape (`step`,
`host_index`, `truth_label`, `is_threat`, optional `phase`/`drift_state`, and optional
observation vector); this is test-fixture evidence, not proof of a production event
class. CLI progress handling also reads `ev.step`. No source implementation was
changed.

### Historical Physics3D apparatus wrapper dispositions

The pinned mixed adapter composes several concerns. The ledger remains `SPLIT` because its owner responsibilities do not collapse to one target, but each listed symbol is now dispositioned; owner references below identify current independent APIs, not migrated implementations or semantic equivalence.

| Pinned source symbol | Disposition / owner reference | Boundary |
| --- | --- | --- |
| `_running_version` | DROP as TARGET helper | No Lab target consumer or owner contract. |
| `physics3d_sensory_system` | DROP as TARGET Lab wrapper | No TARGET path for this helper; this does not prohibit future sensory capability. |
| `physics3d_cognition` | DROP historical Lab wrapper; Organism capability reference: `src/organism/cognition/birth.py::load_base_cognition` | The reference identifies an independently owned API, not a retained Lab wrapper, migrated implementation, or equivalence claim. |
| `physics3d_actuator_surface` | DROP historical Lab wrapper; Organism capability reference: `src/organism/actuation/surface.py::derive_actuator_constitution` | The reference identifies an independently owned API, not a retained Lab wrapper, migrated implementation, or equivalence claim. |
| `OpaqueBodyInteroception` | DROP as TARGET code | No approved TARGET contract or current Lab consumer; see bounded interoception disposition above. |
| `PhysicsDiscoveryProvider`, `PhysicsReadingProvider` | DROP as TARGET Lab adapters | No current TARGET Lab adapter path; no compatibility surface is retained. |
| `actuator_to_effector_map` | DROP as TARGET implementation | Historical positional mapping conflicts with stable-identity binding; see its specific rationale below. |
| `actuator_exclusion_groups` | DROP historical Lab projection; Organism capability reference: `src/organism/actuation/sensorimotor.py::CompetenceDevelopmentEngine.exclusive_actuator_groups` | Distinct owner contract. No claim of semantic or behavioral equivalence with the historical projection; the reference does not retain the Lab projection. |
| `body_schema_summary` | DROP as TARGET evaluator helper | No TARGET path or production consumer established. |

All references were checked against Organism `7b9f738efdcd8cc27efe99c201ce3d88e487fcb2`, Embodiment `5a23e1fbeaa31109647aec4d4dc36eddbe0a6321`, Modality `93a4c3a4ea71dcf65269ce730aab736238fd3ea7`, and Lab base `35759fc2794cd0944fe3d77a07925cef8f3f937e`. Historical provenance remains `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob `8de1f29fe87321fcab0cb051e79fadcf0f833cd6`. This is a migration inventory disposition only: no code transfer, compatibility, scientific validation, evidence admission, or permanent capability prohibition is implied.

### Historical body-interoception behavior disposition

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/integration/physics3d/apparatus.py::OpaqueBodyInteroception` | DROP as TARGET code | No TARGET path | Source repository `alessbarb/symbiont-lab`, pinned source SHA `80d372a186513035f85a769db886e505cabba52d`, blob `8de1f29fe87321fcab0cb051e79fadcf0f833cd6`. Independent review found no approved TARGET contract and no production consumer on Biopeia Lab main. This is a migration disposition, not a scientific validity judgment or a permanent ban on future sensing under a separately approved contract. |
| Five interoception assertions in `lab/tests/unit/lab/physics3d/test_contract.py` | DROP as TARGET tests | No TARGET test mapping | Pinned source blob `f23d0122a7ab649f7142b0138c50b0cb6f1a57b6`; exact source test names and bounded disposition are recorded in `migration/source-inventory-80d372a.tsv`. Other assertions/helpers in this mixed source test file are outside this slice. |

The former target-only `OpaqueBodyInteroception` implementation and its tests
were removed because they had no production consumers and no independent TARGET
contract. No historical source code or tests were copied or modified. This
bounded disposition does not classify other symbols/assertions in the mixed
source files and makes no claim that an analogous future capability is
unwanted; any future implementation requires its own approved contract.

### Explicit operator material-transfer application entry point

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `symbiont/src/symbiont/core/orchestration/runtime.py::OrganismRuntime.request_resource_intake` | SPLIT + REWRITE | `src/lab/interventions/material_transfer.py::apply_material_transfer` plus Environment/Embodiment owner APIs | Source baseline SHA `80d372a186513035f85a769db886e505cabba52d`, source blob `c436087ec1d1f4bfab6bfa7c4e4d801514c69708`; the source method conflates resource acquisition and metabolism. The target Lab function is a new application-side composition, not a byte migration. Environment owns available quantity; Embodiment owns somatic acceptance; World commits an opaque record; the caller supplies a requested intervention envelope. |
| `lab/integration/**` operator/resource exchange paths | DEFER except this bounded slice | `src/lab/interventions/material_transfer.py` | No legacy adapter, physical contact model, action inference, or autonomous Organism authority was carried over. |

The application entry point requires `EmbodimentCheckpoint` and Environment's
`IdentifiedFiniteResource`, deriving body/source identities from those owner
boundaries rather than trusting identity values in the request. It verifies
the accepted World genesis roster and exact initial checkpoint bytes, stages
cloned owner candidates, and durably writes candidate Environment,
Embodiment, and Lab intervention-evidence checkpoints before World publishes
the next causal cut through `DurableWorldRuntime`. The evidence checkpoint is
a staged candidate until World publishes the committed cut; an orphaned file
after a failed preparation is not accepted state or evidence. World invokes
each registered owner codec on the exact digest-checked bytes and issues its
own recovery receipt only after successful validation; Lab does not validate
or certify Embodiment/Environment checkpoints. The evidence checkpoint is a
step-scoped Lab participant and records `intervention_id`, distinct
`transition_id`, World/tick, source/body owner identities, applicability/run
context, and requested/offered/accepted/debited amounts. World requires the
prepared participant set and owner recoverability receipts before commit.
Observation projection and returning candidates occur only after that commit.

The operation does not mutate caller-held owner objects; callers must adopt
the returned candidates after success. A failure while persisting any
checkpoint leaves the previous committed tick intact and the World manifest
`RECOVERY_REQUIRED`; callers must not continue ordinary causal execution.
The local checkpoint store uses immutable content-addressed files and syncs
file/directory writes, but staged files alone are not a committed cut and this
slice is not a general crash/power-loss
recovery implementation, distributed transaction, or multi-writer protocol.

The transfer is deliberately an unspecified scalar. Current Embodiment intake
maps accepted material amount into its energy-reserve scalar, but no conversion
unit, physical energy equivalence, contact condition, or efficacy is claimed.
No Organism intention/readout authorizes this intervention.

#### Scientific-apparatus and intervention-identity boundary

Lab remains the scientific apparatus/application layer for this operation. It
composes Environment and Embodiment owner APIs and stages explicit requested
intervention evidence; it does not own resource quantity, somatic acceptance,
causal commit, or scientific interpretation. The evidence checkpoint is Lab
provenance, not authority over Environment or Embodiment state. The bounded API
carries `intervention_id`, caller-provided `operator_id`, owner-derived
`source_id` and `target_body_id`, and requested/offered/accepted/debited scalar
values. Those support traceable provenance but do not constitute an
authenticated principal reference, approved protocol, or scientific result.
The intervention contract
requires an explicit applicability kind: `NON_EXPERIMENTAL_INTERVENTION` or
`EXPERIMENTAL_RUN_INTERVENTION`. The latter requires a separately supplied
real `run_id`; optional study, experiment, and protocol identities remain
distinct. A non-experimental action cannot carry a synthetic `run_id`. Neither
the causal event nor passive observation projection aliases `intervention_id`
as `run_id`.

`operator_id` and `InterventionRequest` are caller-supplied assertions,
not authentication, authorization enforcement, or proof of operator authority.
Authentication, permission checks, and principal-reference semantics belong
to the control plane/application security boundary and are outside this API.
The `requested_material` field records the requested action; the Environment
and Embodiment APIs retain authority over offered quantity and accepted amount.
The operation carries two distinct identities: `intervention_id` identifies
the logical intervention, while required `intervention_action_id` identifies
each causal action it produces. A single intervention may produce multiple
actions and commits; a repeated action ID for the same World/intervention is
rejected. Neither identity aliases the World `transition_id` or `run_id`.
The operator and declared study/run applicability identify the logical
intervention and remain stable across its actions. Source resource, target
body, requested quantity, and the request's maximum quantity are per-action
inputs, not logical-intervention identity. This bounded function currently
requires a World roster with exactly one Environment resource and one
Embodiment body, so it does not yet support changing source/body identities
between actions. The fixture exercises multiple actions against that same
registered pair.
World's generic causal-tick record does not contain the intervention payload.
Instead, Lab supplies an opaque `OwnerCausalRecord` to the World journal, with
the stable action identity and an exact content-addressed reference to the Lab
evidence checkpoint. The World journal therefore retains the committed
evidence pointer across later ticks and restart, while Lab remains the
scientific/evidence custodian and World does not interpret the payload.

Evidence files staged for a failed causal step may remain as uncommitted
orphans. They are not accepted actions unless a matching committed owner record
exists in the durable World journal. This linkage identifies commit status; it
does not prove long-term external archival, production crash/power-loss
durability, or scientific admissibility.
Each causal cut applies to exactly one committed transfer action. A logical
intervention may correlate multiple such cuts, but that does not establish
experimental causality, efficacy, repeatability, or physical interaction.
This API is bounded to controlled experimental transfer under caller-supplied conditions;
it makes no claim of physical material equivalence, energy equivalence, or
general resource-exchange equivalence.

#### Bounded CURRENT-oracle comparison

At the pinned source SHA, the closest executable CURRENT oracle is
`lab/src/lab/world/population.py`'s material-exchange path, exercised by
`lab/tests/unit/lab/world/test_adapter.py::test_clean_material_exchange_conserves_mass_with_scarce_resources`.
That path requests a bounded amount across positive resources, withdraws
pro-rata shares, lets the body absorb up to capacity, refunds unabsorbed matter,
and asserts that environmental stock lost equals body absorption. This is a
behavioral reference for conservation and capacity handling, not a semantic
equivalence target for the new Lab intervention.

Disposition of that oracle path is **SPLIT + REWRITE; remaining contact/world
coupling DEFERRED**. The target implements only the bounded single-source,
single-body scalar subcase: the offer is capped by the Environment state, body
acceptance caps the debit, and tests assert `debited_material ==
accepted_material` including short acceptance. It does not reproduce source
resource mixtures, pro-rata withdrawal/refund, spatial contact, world-population
scheduling, or the source's energy-cost accounting. Those behaviors have no
target-side equivalence claim and remain deferred. The target tests are local
contract tests, not a run of the source oracle; no cross-repository differential
or scientific equivalence test has been performed. Source and its frozen tests
remain unchanged.

Reproducible package coupling is declared in `pyproject.toml` using immutable
commit references: Embodiment `028e2f912eccbe554a9d7f8543fe9dfe2bb94218`,
Environment `a979688e90b279ccfe003d77eddb787272fd5ebf`, Observation
`be82907d1d677b2362e369d15eb1e8e964d893aa`, and World
`4d264b24d0501a51d8b56b9cbe762aff3402da7b`. World main provides durable
owner-closed cuts, step-participant checkpoints, and opaque owner causal
records; the intervention payload remains in Lab's evidence checkpoint and
the World journal stores its stable pointer. Lab CI
therefore uses Python 3.12,
matching World/Environment. The operator id is caller-supplied provenance, not
authenticated authorization. Quantity remains a scalar with no established
physical material-energy equivalence. No experiments or scientific assets were
moved or run.

### Lab CI boundary for cross-repository dependencies

The material-transfer contract tests in `tests/integration` exercise the
actual Embodiment, Environment, World, and Observation APIs; they are not
replaced by mocks. The domain repositories are public, and their immutable
commit references are declared by the `integration` extra in `pyproject.toml`.
The required Lab CI workflow installs that extra on Python 3.12 and explicitly
runs `tests/integration`; dependency or setup failures fail the job. It also
runs unit tests on Python 3.11 and 3.12 and builds, installs, and imports the
wheel in an isolated Python 3.11 environment. These checks establish software
integration and package-distribution evidence only; they do not establish
scientific validity, efficacy, or historical equivalence.

The integration suite was locally verified against the exact immutable
dependency revisions in `pyproject.toml` (17 passed). An exploratory run
against the current moving `main` heads of all sibling repositories produced
15 passed and 2 failed: the current Environment main exposes
`validate_checkpoint`, while current World main requires
`verify_restoration` for the corresponding owner contract. This does not alter
the tested immutable integration set and must not be hidden by a skip or
fallback. Updating these pins requires resolving that owner-contract mismatch
in the relevant domain repositories first.

## Preliminary candidate source inventory — Lab runtime, studies, observation, and apparatus

**Superseded as a path inventory by the file-level accounting below.** This
section records the earlier grouped first pass. Its grouped candidate rows are
not final dispositions and do not authorize bulk copying, deletion,
scientific-result publication, or a backward-compatibility layer. The no-legacy
rule applies: any future transfer must implement a justified Biopeia contract
directly, not preserve old imports or behavior.

### Provenance and coverage

- Source repository: `/home/alessbarb/workspace/repos/active/symbiont-lab`
- Pinned source commit: `80d372a186513035f85a769db886e505cabba52d`
- Inventory paths below resolve at that commit, never at the moving source
  `main` tip. For any path, its exact Git blob ID is reproducibly obtained with
  `git -C <source> ls-tree <sha> -- <path>`; commits are not inferred from
  directory names. Existing exact blob/commit evidence for already-extracted
  files is preserved in earlier sections above.
- Read-only tree counts at the pin: 297 files under `lab/tests`, 364 files
  under `lab/experiments`, and 390 files under `lab/src/lab` (Python, schemas,
  web assets and package docs). The source also has examples, run receipts,
  result JSON, manifests and generated evidence under `lab/experiments/`.
- Biopeia target consumer scan covered `repos/lab/src` and `repos/lab/tests`.
  Current tracked target modules are `lab.interventions.material_transfer` and
  the three extracted common study utilities (`digests`, `pairing`,
  `statistics`). Target tests cover those APIs
  (`tests/unit/test_{digests,pairing,statistics}.py` and
  `tests/integration/test_material_transfer_intervention.py`). No target
  implementation or test imports source `lab.observatory`, `lab.observation`,
  `lab.server`, `lab.app`, `lab.workbench`, `lab.world`, `lab.physics3d`,
  `lab.integration`, `lab.experiments` or individual `lab.studies` modules.
  Workspace integration callers are separately inventoried in workspace tests;
  those consumers do not make the source package a dependency.
- No source file, test, study, result, receipt, model or web asset was copied or
  modified for this inventory. Source tests are consumer/evidence leads, not
  proof that a historical scientific claim remains valid under Biopeia.

### Candidate module dispositions

All rows use `CANDIDATE` to distinguish this inventory from final inventory
closure. A row's source paths are relative to the source repository and its blob
provenance is the pinned commit plus exact path (the blob object is
content-addressed and queryable using the command above). Source test paths are
at the same pin; target paths are present consumers, not proposed destinations.

| Source path(s), symbols / module responsibility | Source tests or consumers observed | Candidate disposition | Evidence, reason, caveat |
| --- | --- | --- | --- |
| `lab/src/lab/studies/common/{statistics,pairing,digests}.py`; `conditions.py`, `rng.py`, `summaries.py`, `causal_selection.py`, `actuator_probing_calendar.py` | `lab/tests/unit/lab/test_common_stats.py`, `test_pairing.py`, `test_digests.py`; `ExperimentRunner` is the tracked digest caller. Biopeia directly consumes only the three already-extracted utilities. | Existing three: `MOVE` (bounded extraction, see prior records); `summaries.py::format_markdown_table`: `DROP`; other remaining common modules: `DEFER` pending per-utility caller/API review | `summaries.py` is a generic Markdown table formatter at pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob `3ba4a1f396fd7888cb67651d069af01c55b01582`. A repository-wide search of package source and tests found no consumer at these Biopeia main heads: organism `ba0011797a6a3b4d48c7731651e50560c4043f18`, embodiment `b5714f985d0aa970d3a412a7d29e43fa0bcb89d6`, environment `caa885a11ec0170717bb4b71d271ab171807197e`, world `a4d04928a82fb0f53f6a1ca7e6362686d4c894d5`, modality `79b779152d4bff2ab4191dc6601c8f1640e4cae3`, observation `6aac3c76684834722440f53c9d8604ac4c16b138`, and Lab `f5dc75d6a94b13b9c650f64d0f94e33e6db2e425`. This makes the source helper unjustified as a migration input at those heads; any future reporting requirement needs a separately justified TARGET implementation. This does not say the formatter is generally useless. Other deferred utilities remain independently unresolved; do not infer target demand from a source test or study. |
| `lab/src/lab/studies/**` (132 source files across ablations, continuity, embodiment, genetics, learning, observability, perception, physics3d, world and root-level studies); symbols include `run_*_study`, study/result dataclasses, condition and metric helpers | `lab/tests/integration/studies/**` (50), protocol/runner tests, and `lab/experiments/**` manifests/README files; source `lab/experiments/registry.py::get_protocol` dispatches selected runners. No target study imports. | `DEFER` pending study/protocol-level disposition; `SPLIT` or `REWRITE` only when separately justified | Lab is designated scientific custodian. The source-module count is not a count of independently resolved studies. Keep these rows deferred until their study/protocol dispositions are recorded; any successor must be newly justified Biopeia code, never a source-compatibility layer. |
| `lab/src/lab/experiments/{execution_workspace,generations,loader,manifest,registry,resource_guard,runner,snapshot_archive,spec,verified_child}.py`; symbols include `ExperimentRunner`, `ExperimentSpec`, `RunManifest`, `GenerationStore`, `pinned_worktree`, `run_verified`, `get_protocol` | Source `lab/experiments/**`, `lab/tests/experiments/{protocols,runners}/**`, CLI study/experiment entry points; no Biopeia target caller. | `SPLIT` / `REWRITE` candidate; `DEFER` pending Lab experiment/run contract | Study orchestration, run identity, manifests, resource controls, provenance and controlled execution belong in Lab, but source registry/runtime is monorepo- and protocol-coupled. Do not carry implicit source defaults, process-global registry or runner semantics forward. |
| `lab/src/lab/observation/{semantic,contracts,projection,plane,bus,wire,delta,provenance_journal,world_scene,environment_resource,body_pose,body_physiology,joint_kinematics,physics3d,atlas,development_history,symbiont_affordance,subsystem_status,cadence,observatory}.py` | Source observation unit/smoke/integration suites; referenced by `observatory`, `physics3d`, `workbench`, `server` and source runtime adapters. Current Biopeia Observation repository owns its own semantic-model work; Lab has no implementation consumer. | `SPLIT` / `REWRITE` candidate; transport/UI-specific pieces `DROP` or `DEFER` after consumer audit | Ratified architecture keeps Observation a passive projection, distinct from scientific evidence custody. Its approved conceptual model does not authorize copying this source schema/API/transport. Lab may admit claims into evidence but must not become primary authority for Embodiment, Environment, Organism or World claims. |
| `lab/src/lab/physics3d/__init__.py` | DROP as TARGET code | No TARGET Lab package or consumer | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`, blob `18a8d568dfb995653b5d6e838b62591889412e6a` (259 bytes). This file only re-exports `HumanoidPhysics`, `Physics3DEmbodimentRuntime`, and `Tick3D`; it has no independent behavior. Drop only the obsolete package facade. Separately inventoried physical/runtime modules are not disposed by this row; no source compatibility namespace is retained. This says nothing about scientific value or future Biopeia physical-simulation needs. |
| `lab/src/lab/observatory/{adapter,config,history_summary,journal,manifest,provenance,publisher,registry,schema_validate,server}.py`, schemas, `world.html`, and nested tests | 47 non-marker source files plus source `lab/tests/smoke/test_observatory_source_adapter.py`, server/runtime projection tests, source Workbench/app. No target consumers. | `SPLIT` candidate for Lab evidence/provenance custody; `DROP` candidate for domain-state adapters/schemas/UI that duplicate domain or Observation contracts; otherwise `DEFER` | The zero-byte `lab/src/lab/observatory/__init__.py` package marker is separately dispositioned `DROP` in the canonical TSV (blob `e69de29bb2d1d6434b8b29ae775ad8c2e48c5391`); this does not decide any sibling module. Distinguish experiment evidence records from passive Observation claims, source state and delivery. Existing JSON shapes (`instance`, `snapshot`, `topology`) are not approved Biopeia records. Determine custody, retention, replay and integrity requirements before implementing any successor. |
| `lab/src/lab/physics3d/{engine,runtime,effects,equivalence*,persistence,settling,observer_semantics,private_model_training,telemetry/**}.py`; examples include physics runtime/engine, telemetry readers/writers and effect characterization | `lab/tests/unit/lab/physics3d/**`, integration/equivalence tests, Physics3D runs and CLI; no target Lab runtime consumer. | `SPLIT` / `REWRITE` candidate for scientific apparatus, analysis and retained telemetry evidence; `DROP` candidate for stale adapters/obsolete schemas only after per-path proof; core runtime `DEFER`; `world_observation.py` individually `DROP` as TARGET code (Lab #316) | Biopeia ratifies solver as numerical substrate, not semantic authority; Environment and Embodiment own adoption and World commits. Do not transfer a source runtime as a solver authority. Preserve raw scientific outputs where governance requires; this candidate code disposition does not dispose of records. |
| `lab/src/lab/integration/{integrated_habitat.py,organism/**,physics3d/**,world/**}` including `OpaqueBodyInteroception` and source adapters; `lab/src/lab/world/{population,runtime,transaction,persistence,cli_view}.py` | Source integrated-habitat/world/physics tests; current target uses `lab.interventions.material_transfer`; workspace suite has `tests/integration/test_operator_material_transfer.py` and `test_first_biopeia_physical_causal_step.py`. | Interoception symbol: `DROP` as TARGET code (see bounded disposition above). Other extracted items and remaining adapters/runtime retain their separately recorded dispositions. | World/Environment/Embodiment split is ratified; source World/hex/population assumptions do not transfer by name. New integrations must call current owner APIs and preserve causal commit order; no old namespace bridge. Determine each behavior against Biopeia contracts, not source file location. |
| `lab/src/lab/app/physics3d/**`, `lab/src/lab/server/{api,server,sse}.py`, `lab/src/lab/cli/**` | Source unified server/app/CLI smoke tests and source users; no target consumer. | `DROP` candidate for old monolith/UI/commands; `REWRITE` candidate only for independently justified operator tooling or Lab application endpoints; otherwise `DEFER` | Do not preserve old HTTP/SSE, command syntax, browser assets or launch flow by compatibility. Any future operator tooling must not turn caller identity into authentication/authorization and must keep Lab out of causal ownership. |
| `lab/src/lab/workbench/{coordinator.py,web/**}` | Source Workbench/browser tests; source `observatory`/`server` integration; no target consumer. | `DROP` candidate for source-coupled presentation; possible `REWRITE` candidate as a new Lab UI after requirements | Frontend and static assets are implementation-specific, not scientific evidence or semantic contracts. This candidate is not a ruling to delete historical screenshots/assets from protected evidence stores. |
| `lab/src/lab/evaluation/**`, `evolution/**`, `experience/**`, `reproduction/**`, `modeling/**`, `kernel_characterization/**` | Corresponding source unit/integration tests and study/experiment callers; no target Lab consumer. | `SPLIT` / `REWRITE` / `DEFER` by module; a package-level facade may be `DROP` when separately dispositioned | Some can be Lab methods, analysis, model/evaluator apparatus; some source modules may encode Organism or lifecycle semantics. Keep longitudinal private state and cognition out of Lab. Establish owner for every persistent state and claim before any broad MOVE. |
| `lab/experiments/**` (364 source files at pin: experiment definitions, protocols, README, result summaries, frozen reports, manifests, receipts, seeds, selection outputs and snapshots) | Referenced by source registry/studies/CLI; no target path consumes the source tree. | Executable definitions: `DEFER`/`REWRITE`; scientific results, receipts, manifests, snapshots: `DEFER` evidence-custody review; unsupported/stale test artifacts: candidate `DROP` only with evidence-owner approval | Distinguish executable code from scientific evidence. Do not migrate or regenerate recorded results as if source code. Preserve source/provenance and obtain owner decision before any destructive disposition. |
| `lab/tests/**` (297 source test files) | Grouped under unit, integration/studies, experiments, smoke, workbench, Observatory and physics; exercise source implementation and source-coupled fixtures. | `DROP` as source tests from Biopeia package; selected assertions may be `REWRITE` as contract tests once target behavior exists; scientific evidence suites `DEFER` | Tests are not production API and must not be bulk copied. A rewritten test must state invariant and whether it is contract, validation or scientific experiment; no source experiment run is claimed. |
| `lab/examples/**`, manifests, saved run/checkpoint payloads and model assets referenced by package | Source CLI/reproduction/Workbench or individual experiments; no target package consumer. | `DEFER` evidence/preservation inventory; then `DROP` from runtime distribution or `MOVE` to governed evidence archive only by explicit authorization | Code inventory does not authorize moving, deleting, exposing or reinterpreting evidence/artifacts. No data/evidence disposition is final in this PR. |

### Registered study-protocol crosswalk (candidate links only)

[`migration/study-protocol-crosswalk-80d372a.md`](migration/study-protocol-crosswalk-80d372a.md)
and its TSV enumerate the 76 protocol IDs registered at the pinned source SHA
`80d372a186513035f85a769db886e505cabba52d`, with statically resolved
registry-callable and implementation-module candidates plus candidate spec,
test and artifact paths. [`migration/study-protocol-test-links-80d372a.tsv`](migration/study-protocol-test-links-80d372a.tsv)
records pinned implementation blobs and test-symbol links established by
static source inspection. It distinguishes direct calls to the registered
implementation callable, registry-ID lookup tests, and explicit
`NO_DIRECT_TEST_LINK` rows.

The companion [`migration/study-disposition-register-80d372a.tsv`](migration/study-disposition-register-80d372a.tsv)
records four resolved owner-directed `HISTORICAL_PROTOCOL` units:
`continuity.recurrent-restoration`,
`embodiment.causal-revision-sequence`,
`embodiment.heredity-leakage-challenge`, and
`world.genesis-viability-characterization`. The protocol crosswalk retains the
other 72 candidate IDs as `DEFER`. All four historical implementations are `DROP`
as TARGET code. This disposition does not copy or move protocol/result bytes;
the historical source remains read-only at the recorded source paths. The
genesis-viability unit's linked result/config has an unresolved population-size
discrepancy and is not treated as conformant, scientifically validated, or
admitted by this disposition. No run/result artifact is present in the recurrent-restoration protocol
directory at the pinned source commit. Links establish source-code traceability only,
not scientific provenance, test validity, method preservation, or disposition
closure. This is not a reconciliation of the historical “129” count, a
crosswalk of all study capabilities, or a claim that every historical artifact
has been classified. Unregistered study modules and artifact-level custody
decisions remain open.

### Target consumer and test evidence (bounded)

The existing Biopeia Lab implementation has no target-side `observatory`,
`observation`, `server`, `app`, `workbench`, `world`, `physics3d`, `integration`,
`experiments` or individual study modules. Its consumers are limited to the
current unit/integration paths listed above. Workspace tests exercise integrated
Biopeia contracts, not source Lab modules. This is a search result over the
current target checkout, not proof that no future contract will need an apparatus
capability. In particular, a no-current-consumer result alone does not establish
that code or evidence should be deleted.

### Inventory limitations

This earlier table is not symbol-by-symbol closure. It groups cohesive path
families and gives representative symbols. The file-level manifest below
supersedes it for path/blob coverage; it does not eliminate the need for
symbol-level responsibility review, source consumer/test linkage, evidence
custody decisions, or approval of scientific protocol successors.

## Pinned source file-level accounting

**Status: complete path/blob accounting snapshot; Lab is designated scientific
custodian, while item-level evidence disposition and most semantic dispositions
remain open.** This is not migration completion, cut-over,
authorization to transfer assets, or a claim that each historical behavior has
been independently reviewed. It replaces grouped-path accounting as the index
for all files in `lab/` at the pinned source commit.

The machine-readable manifest is [`migration/source-inventory-80d372a.tsv`](migration/source-inventory-80d372a.tsv). Each row records the exact source-relative path, blob object ID at the pinned commit, Git mode, byte size, top-level Python symbols where parseable, a disposition, target-owner/path status, and the reason/caveat. The source commit for every row is
`80d372a186513035f85a769db886e505cabba52d` in `alessbarb/symbiont-lab`; the
manifest is not derived from the moving source checkout. The committed source
tree is the provenance anchor; blob IDs identify file contents within it.

Snapshot coverage is **1,172 tracked files**: 394 under `lab/src/lab/` (390
Python modules plus non-Python package assets), 297 under `lab/tests/`, 364
under `lab/experiments/`, 112 under `lab/research/`, and five package-root or
example files (`lab/README.md`, `lab/pyproject.toml`, and three examples). The
manifest disposition counts are:

| Disposition | Files | Interpretation in this snapshot |
| --- | ---: | --- |
| `MOVE` | 8 | Three already-extracted utility modules and their three focused test files; this records existing target state, not a new transfer in this change. |
| `SPLIT` | 15 | Mixed responsibility or authority; target owner(s) are named, but unresolved target path means no source implementation is approved to move. |
| `REWRITE` | 3 | Target package/document root is independently authored; old package roots are not compatibility surfaces. |
| `DROP` | 950 | Excluded from Biopeia migration input; **not** deletion of the protected historical source. This includes 81 source test-tree files excluded as TARGET test/code, subject to separate evidence admission where warranted. Future functionality, if required, must be newly justified and target-authored. |
| `DEFER` | 196 | Open disposition, not final. Must be revisited before migration completion. |

### Historical Observatory read adapter disposition (Lab #238)

At source baseline `80d372a186513035f85a769db886e505cabba52d`,
`lab/src/lab/observation/observatory.py` is blob
`47c42c8ffa09828989342f7b7f95d6382aefe66c` (mode `100644`, 7,710 bytes).
The inventory's seven recorded symbols were checked against the pinned file:
`observatory_package_root`, `valid_instance_id`, `_read_json_object`,
`_registry_api`, `parse_journal_line`, `read_journal`, and `ObservatorySource`.

The module is a read-only adapter to the historical Lab Observatory package:
it resolves that package, reads its registry and topology/manifests, filters
registry records by legacy liveness rules, incrementally parses old NDJSON or
gzip run journals, and reads run summaries. It does not implement a generic
Observation consumer contract or scientific evidence admission. Current Lab
has no consumer of this API. Observation #38's product direction makes Lab a
read-only consumer of owner-authorized Observation data and keeps Lab's
scientific evidence custody distinct; #38 does not authorize preserving this
historical filesystem API, schemas, or ingestion path. Therefore the source
adapter and its legacy interface are `DROP` as TARGET code, with no target
path. A future Lab reader, if needed, must be newly designed against an
approved Observation contract. DROP applies only to the pinned implementation;
the historical source remains read-only and no scientific artifact, validity,
or equivalence is dispositioned here. This row is non-blocking to the bounded
Lab utility extraction, while its disposition is recorded for the complete
source inventory.

### Historical semantic model disposition (Lab #243)

Pinned source: `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observation/semantic.py`, blob `125c906cd4a2d52d797f577172a33133534ef230` (12,321 bytes; mode `100644`). The verified top-level symbol list includes TypeVar `T`, token/text validators, authority/family/identity/subject/time/acquisition/transformation/lineage/condition/orchestration value types, semantic claims and observations. The responsibility is classified `MOVE` to the concrete owner `repos/observation/src/observation/semantic.py`; Observation's migration ledger records the copy-first extraction and target-native semantic model tests. This source file does not itself define Lab evidence custody or admission, so `SPLIT` incorrectly merged distinct authorities. These are capability primitives only: they do not grant semantic authority to Observation and do not choose wire/envelope, record schema, API, storage, transport, or evidence-admission policy. The TARGET implementation has evolved, including authority domains and validation; no source-code or behavioral equivalence is claimed. Historical source remains read-only.

### Historical provenance journal disposition (Lab #242)

Pinned source: `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observation/provenance_journal.py`, blob `e4eb2840dc63c52b95cbfce812dda4e9828b7c3f` (6,216 bytes; mode `100644`). Verified symbols: `ProvenanceJournal;ProvenanceIndex;render_tree`. The writer appends Organism `CausalEvent` payloads as JSONL; the index supports producer/ancestor/causal-tree queries over the append-only history. Current Organism `src/organism/provenance.py::ProvenanceLog` owns bounded event/frontier semantics and checkpoint state, not an all-history archive. Current World `src/world/journal.py` records committed causal-cycle records; that is not established as a replacement for this event archive. Observation's migration boundary excludes evidence archive/custody; its row remains deferred to Lab tooling pending custody/admissibility and artifact-retention decisions.

Disposition: `DEFER` pending the Lab owner's explicit decision on (1) whether all causal events are retained as experiment evidence, (2) their admissibility status, (3) retention, integrity and schema/version requirements, and (4) the authorized target artifact/query path. Dependency: Lab #45 umbrella and #78 worklist. Closure trigger: record that owner decision and target path, then re-review this row before migrating, replacing, or dropping archive/query behavior. This does not block the bounded runtime-package migration because the pinned source module and artifacts remain preserved and no target claim of complete historical provenance continuity is made; it does block any such continuity claim. No scientific validity, equivalence, or evidence admission is inferred.

### Historical runtime/Mind projection disposition (Lab #241)

Pinned source: `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observation/projection.py`, blob `9ee6e8ccd2ebdcd1896ebe17d035f42a0da48655` (36,067 bytes; mode `100644`). Verified symbols: `_identity;_copy_number;_copy_bool;runtime_tick_events;_prediction_class;mind_snapshot_from_rich_state`. This row is genuinely split: the bounded `runtime_tick_events` presentation projection has a concrete existing migration-stage counterpart at Observation `src/observation/projection.py::runtime_tick_events`, explicitly documented there as transitional and not a stable semantic-family contract; preserve only that bounded runtime projection responsibility, not source code/schema or semantic authority. `mind_snapshot_from_rich_state` maps a broad legacy rich-state/Mind view schema for which no TARGET schema/function/consumer was found; drop that legacy responsibility. The pinned module does not establish Lab evidence custody or admission. No scientific validity, semantic authority, code identity, behavioral equivalence, or transfer of the historical view schema is inferred; pinned source remains read-only.

### Historical Observation plane disposition (Lab #240)

The pinned source is `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observation/plane.py`, blob `a971a49857a562021da909a00a4efd53a0f7e637` (10,805 bytes, mode `100644`). Verified top-level symbols: `ObservationKey;PlaneMessage;PlaneRebaseRequired;PlaneStreamSubscription;observation_key;ObservationPlane`. The row is classified `MOVE` to the concrete semantic coordination owner `repos/observation/src/observation/plane.py::ObservationPlane`: bounded in-memory current-state materialization, fan-out, replay and rebase are generic Observation responsibilities. Lab consumers associate/consume owner plane messages; this source module itself does not define Lab-specific evidence custody or admission, so the former `SPLIT` classification overstated its responsibility split. The TARGET implementation adds value-shape validation and defensive snapshots and has evolved APIs; this ownership disposition makes no source-code, behavioral, scientific, or equivalence claim. The pinned historical file remains read-only. Existing TARGET clients (for example Lab `src/lab/observation_consumer.py` and World `src/world/observation_publication.py`) are integration context, not evidence of historical behavior equivalence.

### Historical Physics3D observation bridge disposition (Lab #239)

At source baseline `80d372a186513035f85a769db886e505cabba52d`,
`lab/src/lab/observation/physics3d.py` is blob
`116d19599724ddfb785e7e8ea4eaacfeb0c27a4a` (mode `100644`, 26,053 bytes).
The recorded top-level names were checked at the pinned blob:
`_body_descriptor_for_state`, `_optional_text`, `_topology_revision`,
`EventSink`, and `Physics3DObservationBridge`.

The class combines viewer-event formatting/delivery, Lab run identity fallback
and stop lifecycle, and optional calls into historical Lab observation helpers
for raw body-pose, joint-kinematics, physiology and affordance inputs. The
module has no Biopeia Lab Physics3D caller or target viewer/event sink. Current
Lab exposes only a read-only committed-Observation consumer at
`src/lab/observation_consumer.py`. TARGET Embodiment defines owner-side
`BodyPoseSample` and adopted `BodyPoseObservationProjection` in
`src/embodiment/observation.py`; Observation maps an approved Embodiment
projection in `src/observation/embodiment.py`. Those require owner state and
causal-step correlation; they are not equivalent to accepting arbitrary raw
Physics3D payloads from this legacy adapter. Embodiment's
`src/embodiment/physics3d/observation_contract.py` declares coordinate
conventions, not publication authority or a viewer bridge. Therefore drop the
legacy adapter, direct sink/event shapes, and implicit publication path as
TARGET code; no source implementation or compatibility API transfers. Any
future runtime visualization or publication must be target-authored under the
relevant owner/World boundary and an authorized Observation contract. The
historical source is preserved read-only. This code disposition makes no
physical, scientific-validity, results, or equivalence claim and does not
dispose of scientific artifacts. It does not block the bounded Lab utility
extraction.

### Historical Lab ObservationBus disposition (Lab #231)

| Source path | Disposition | Current target responsibility references | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observation/bus.py` | SPLIT: retain semantic plane/passive-consumer responsibilities; DROP the historical event bus and legacy presentation schemas | Observation `repos/observation/src/observation/plane.py::ObservationPlane` owns bounded semantic current state, live fan-out, replay and rebase; `repos/observation/src/observation/http_bridge.py` exposes a limited local read-only current snapshot; Lab `repos/lab/src/lab/observation_consumer.py::associate_stream_messages` passively associates plane stream messages with committed-cut context | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob `f270ded3e9963456eea3d18c94ba0b1d2bfb3e81` (15,539 bytes). The historical `ObservationBus` also materializes string-keyed legacy events and world scenes, compresses event deltas, manages run boundaries and serialized transport replay, and tracks client transport counters. The current target plane operates on semantic claims, not these legacy JSON event/schema contracts; the HTTP bridge is a narrow snapshot, not the old SSE bus. No source implementation, compatibility bus or UI schema is approved for transfer. No evidence-custody, scientific-validity or equivalence claim is made. |

### Historical Body Pose observation adapter disposition (Lab #230)

| Source path | Disposition | Current target responsibility references | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observation/body_pose.py` | SPLIT across owner projection, semantic mapping and passive Lab consumption; do not transfer this source adapter | Embodiment `repos/embodiment/src/embodiment/observation.py::BodyPoseSample` and `repos/embodiment/src/embodiment/physics3d/physical_transition.py::body_pose_observation_projection`; Observation `repos/observation/src/observation/embodiment.py::embodiment_body_pose_observation`; Lab `repos/lab/src/lab/observation_consumer.py` | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob `9eda624b2fcbcebaf5759faa9c4ec1b8e2f7cdcc` (3,069 bytes). The historical helper creates a `simulated_apparatus_sample` claim from an apparatus BodyPoseSample and attaches Lab producer/run context. Current Embodiment derives a validated projection from adopted owner state with checkpoint lineage; Observation maps it to an authoritative Embodiment claim; Lab passively associates plane messages. This mapping is not source API or semantic equivalence: the target observation is owner-state-derived rather than the source's raw simulated-apparatus sample. No historical helper, claim shape or compatibility behavior is transferred. No scientific measurement/validity, evidence admission or equivalence claim is made. |

### Historical Environment resource observation adapter disposition (Lab #236)

| Source path | Disposition | Current target responsibility references | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observation/environment_resource.py` | SPLIT responsibilities across owner projection, semantic mapping and passive Lab consumption; DROP this historical adapter and its legacy claim/schema semantics | Environment `repos/environment/src/environment/identified_resource.py::project_committed_resource_state`; Observation `repos/observation/src/observation/environment.py::environment_resource_state_observation`; Lab `repos/lab/src/lab/interventions/material_transfer.py` | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob `c849ed5be32744799949d0529a65e37965ace9e2` (2,295 bytes). The source turns a whole logical hex-cell `ResourcePoolObservation` into a legacy claim whose authority is Environment, producer is Lab world runtime, identity is scoped to a world runtime, and time is Environment `world_tick`. Current Environment projects identified resource state from its committed checkpoint; Observation validates and maps that projection to a narrower unitless `remaining` claim, carrying checkpoint lineage and World causal tick; Lab consumes this current projection. These are distinct current owner responsibilities, not evidence that source semantics were transferred or equivalent. No source helper, compatibility contract or legacy claim shape is approved to move. No scientific measurement/validity, evidence admission or equivalence claim is made. |

### Historical Joint Kinematics observation adapter disposition (Lab #237)

| Source path | Disposition | Current target responsibility references | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observation/joint_kinematics.py` | SPLIT responsibilities across Embodiment state, possible Observation mapping and Lab run orchestration; DROP this historical adapter/claim shape as migration input | Embodiment `repos/embodiment/src/embodiment/physics3d/physical_projection.py::BodyPhysicalInput` (solver input only); Observation `repos/observation/src/observation/semantic.py::SemanticObservation` (generic primitives only; no joint family adapter); owner-contract dependency [Embodiment #75](https://github.com/biopeia/embodiment/issues/75) | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, path commit `f9f641b9d26cb0b6db885a541141f029930c1ec2`, blob `6f69da7ae98e638455e85b2833a0ff50071a14b2` (2,920 bytes). The sole adapter turns an Embodiment `JointKinematicsSample` into an Embodiment-authority `simulated_apparatus_sample`, carries sample timing and optionally adds Lab run context. Current Embodiment `BodyPhysicalInput` carries stable joint identity, morphology revision and `rad`/`rad/s` units but is explicitly solver input, not a post-step observation; current Observation has generic semantic primitives but no joint-kinematics family adapter; current Lab has no corresponding consumer. Keep state meaning with Embodiment, any future passive family mapping with Observation, and any future run orchestration with Lab. Whether a post-step owner projection or Observation adapter is warranted is deferred to Embodiment #75; an approved mapping requires its own bounded Observation implementation issue. No source compatibility, measurement/calibration, scientific validity, evidence admission or equivalence claim is made. |

### Historical modeled body physiology observation adapter disposition (Lab #229)

| Source path | Disposition | Current target responsibility references | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observation/body_physiology.py` | SPLIT; do not transfer the historical adapter or schema | Embodiment `repos/embodiment/src/embodiment/physiology.py` owns `LivingBodyState` and `PhysiologyController`; Observation `repos/observation/src/observation/semantic.py` owns generic transport-independent semantic observation/claim types; Lab `repos/lab/src/lab/observation_consumer.py` consumes the plane | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob `a2f3bc375850779d9d07bfe768c056f106d3ec83` (2,950 bytes). `body_physiology_observation` wraps a source `BodyPhysiologySample` as a semantic observation, with an Embodiment-authority body-physiology family, modeled-state epistemic kind, body identity, body-local age, and optional Lab-run context. The referenced current target paths establish separate responsibility boundaries only: no target `BodyPhysiologySample` or body-physiology projection contract was found, so they do not authorize an adapter or source API compatibility. Keep historical adapter/schema out of transfer; any specific physiology claim family/projection requires an owner-authored contract and review. No scientific validity, measurement status, evidence admission, or equivalence claim is made. |

### Historical Cognitive Atlas v2 disposition (Lab #228)

| Source path | Disposition | Target mapping | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observation/atlas.py` | DROP as TARGET implementation and schema | None authorized | Pinned `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob `c75dfca22bfb153f759c04bb8fdfd730fc5f67b9` (38,627 bytes). The source builds a Cognitive Atlas v2 graph/metrics projection from private cognition, motor, agency, embodiment, prediction and knowledge structures. Observation `src/observation/semantic.py` defines a transport-independent semantic claim model; it is not this atlas schema or compatible graph projection. Observation `src/observation/projection.py` is explicitly a transitional runtime-telemetry view, not a stable semantic-family contract. Neither is a target mapping for this source schema, and no approved target contract or consumer establishes a retained responsibility. No source code, compatibility API or source tests are transferred. Future need must be specified and authored against an approved target contract. No claim of scientific validity, efficacy, evidence admission or permanent capability prohibition is made. |

### Historical habitat population and lineage authority disposition (Lab #317)

At source baseline `80d372a186513035f85a769db886e505cabba52d`,
`lab/src/lab/reproduction/authority.py` is blob
`090a4ea9da61f6e36ddf504b931ed1609a73e388` (8,155 bytes; path commit
`2caa8efa8a40a34e3b53045ca19416a3f6659126`). Its `BirthRecord`, `DeathRecord`,
and `HabitatBirthAuthority` implement one in-memory historical aggregate for
habitat capacity admission, identity allocation, live/dead membership, parent
and generation lineage, legacy Body-death observation, and checkpoint state.

| Responsibility | Current TARGET evidence | Disposition |
| --- | --- | --- |
| Identity and offspring lineage | Organism `src/organism/identity.py` accepts a caller-supplied UUID; it has no offspring identity or lineage operation. Organism #49 remains open on reproduction/inheritance contracts. | No equivalent authority or destination identified. |
| Habitat population capacity and membership | World `src/world/durable_runtime.py` records explicit active-presence and causal-owner transitions with trigger provenance. It does not own biological population capacity or parentage. **World presence lifecycle is not a biological birth/death authority.** | Do not reassign this responsibility to World by name or analogy. |
| Birth/death records and checkpointed authority state | No matching Environment contract or TARGET Lab reproduction package/consumer was found in the reviewed target revisions. | No component of this historical authority API or its source-coupled tests is retained as TARGET code. |

**Disposition: DROP as TARGET code.** This is a bounded migration decision, not
a claim that reproduction, lineage, habitat capacity, or birth/death
coordination is unnecessary, impossible, scientifically invalid, or
permanently prohibited. Any future capability requires newly specified,
owner-approved TARGET contracts. Historical implementation and tests remain
read-only evidence of historical software behavior, not proof of scientific
validity or TARGET equivalence. The separate Lab #318 runtime disposition and
Organism #49 remain independent records; this decision does not close either
question. Historical study/protocol/results continue under Lab #45 governance.

### Observatory instance schema path alias (Lab #255; linked to Observation #38 and Lab #266)

At pinned source commit `80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observatory/instance.schema.json` is a symlink (mode `120000`, blob `705273ce14b8dad75fd3d087ee28dfddd2c6e389`, 28 bytes) containing only `schemas/instance.schema.json`. It has no independent semantic responsibility; the target is the sibling source row `lab/src/lab/observatory/schemas/instance.schema.json` (blob `7a2d29bb3dc576c2b984d85bbcfc8746fc7adb44`). Lab #266 recorded that schema as a bounded `DEFER`, integrated by PR #351 at `82aabb39f63cded0bdc82c0927689c763fe60416`. That records the unresolved question; it does not supply a competent-owner schema disposition.

Keep this alias as `DEFER`, linked to Observation #38. The Lab #255 coordinator tracks the closure trigger: competent Observation/Lab owners record whether the instance identity/heartbeat/topology-revision record has a TARGET responsibility and, if retained, its owner/path; otherwise they explicitly determine DROP. If the schema is DROP, classify this alias as DROP because the link has no separate meaning. If responsibility is retained, preserve the alias as a DEFER until the owner/path decision is integrated. Current Lab main `82aabb39f63cded0bdc82c0927689c763fe60416` contains neither this legacy alias path nor an authorized replacement contract. This row is outside the bounded runtime-transfer profile and does not block that profile, but it remains part of the unresolved #78/#45 source-disposition worklist until the decision trigger is met. No code/schema is copied, historical source is untouched, and no scientific validity/equivalence/admission claim is made.

### Historical Hex World CLI visualization

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/world/cli_view.py` | DROP as TARGET implementation | No TARGET code destination | Pinned source commit `80d372a186513035f85a769db886e505cabba52d`; Git blob `0f0ed5fcb41253a05b37413de3f6cdd08f1297ab`, mode `100644`, 15,581 bytes. The module renders a read-only CLI view over historical `HexTopology`, `WorldState`, `WorldEnvironment`, `GroundTruth`, and private `population._rigs` state. These inputs and semantics are not Biopeia TARGET contracts, and no Lab TARGET consumer exists. Drop this implementation and its API rather than preserving a compatibility path. Any future visualization must be newly authored to consume passive Observation publications; this disposition does not claim that visualization is unnecessary. Historical source remains read-only. |


### Historical Observatory replay schema (Lab #267)

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/schemas/replay.schema.json` | DROP as TARGET schema artifact | No TARGET replay schema/compatibility contract | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `d1f6f042b4ac49d70a8f4debf665ea4c68f72885`, mode `100644`, 479 bytes; SHA-256 `1e916b2f4fde95b4ac62e78d91537a5bad0617399e3674df540a9f609530aae5`. This schema defines a version-1 envelope of up to 10,000 legacy Observatory snapshots via local `$ref`. The legacy snapshot schema and publisher are separately inventoried/dispositioned; no TARGET replay schema, consumer, or compatibility contract is authorized. Drop this historical envelope format only; historical replay records/data are not dispositioned by implication, and future replay is not ruled out. No scientific validity/equivalence/evidence-admission claim is made; historical source remains read-only. |

### Historical Observatory signal-knowledge schema (Lab #268)

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/schemas/signal_knowledge.schema.json` | DEFER as an unapproved historical wire schema | No TARGET signal-knowledge schema/path authorized; Organism owns any internal semantic state, while Lab custody applies only to separately dispositioned evidence artifacts | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`; blob `fe960b2b38ef3655a5aff6867b81a46fbf380a9e`, mode `100644`, 4,079 bytes; SHA-256 `100195ff2df5d7feb4e86eead7482858b5a1b2a88956e28efaa825ca67fe2c9d`. This schema describes a historical Observatory array of bounded per-signal claim summaries, including identity, claim kind/status, evidence/validation counters, performance/loss classes, epochs and age classes; its shape does not establish claim truth or scientific validity. Biopeia Organism migration already defers signal identity/knowledge components until a perception-source contract defines identity, provenance and epistemic basis. Keep this whole wire schema deferred rather than infer `SPLIT` from its historical location or field names. Closure trigger: Organism owner records the signal identity/source/provenance/epistemic contract and the publication/privacy disposition in Organism #169; Organism #45 tracks incomplete cognitive-checkpoint scope if any state is persisted. Lab then reclassifies this row: DROP the legacy wire artifact absent an accepted contract, or open a separate issue for a fresh target-authored schema under its authorized owner. This row does not block the bounded Lab runtime migration because no TARGET consumer/package dependency is identified. Historical source remains read-only; no schema is copied, no scientific validity/equivalence/admission or future-need claim is made. |

### Historical Observatory topology schema (Lab #270)

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/schemas/topology.schema.json` | DEFER as unapproved historical cognition-topology schema | Organism owns private cognition; no TARGET topology projection/checkpoint schema authorized. Dependencies: Organism #169, Organism #45, Observation #38. | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`; blob `6525f49ddf3271b0ff6f8fde7fe516da791f9059`, mode `100644`, 1,669 bytes; SHA-256 `4c735bd03d4a0f46306441a68ff4e0abcdbdbf86da50fdfd08d4005e56254441`. The structural-only schema serializes genome/kernel identity, topology revision, node kinds/bias/tau and typed edges while excluding weights, eligibility and readouts. Its fields still describe private cognitive structure; this does not establish a scientific interpretation. ADR-0095 assigns private cognition to Organism and bars semantic inspection except via an explicit owner contract. No Biopeia consumer or approved projection/persistence contract was identified. DEFER until the Organism owner decides whether any bounded projection may be published (Organism #169); if intended only for private persistence, resolve checkpoint completeness first (Organism #45). Observation #38 tracks the broader producer inventory. Closure trigger: owner-recorded identity, provenance, revision and privacy semantics. Lab then drops this historical wire schema absent an accepted contract or raises a separate target-authored schema issue. This does not block bounded Lab runtime migration (no TARGET consumer/package dependency). No schema copy or scientific validity/equivalence/admission/future-need claim; source remains read-only. |

### Historical Observatory server (Lab #271)

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/server.py` | DROP as TARGET implementation | No TARGET server/application implementation destination | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`; blob `4f656e71647dfa05a10eb9e017f573d1fc5506cf`, mode `100644`, 10,054 bytes; SHA-256 `34686bbad323801893321c95cdd00f3168db1c010bde2104ab996cc6c9865058`. Verified symbols `_valid_instance_id`, `_Handler`, `ObservatoryServer`, `main`. This loopback-only read-only HTTP/SSE server serves legacy Observatory files, static assets, historical fleet/instance streams, optional World state/events and a semantic-observation wire endpoint; it provides presentation/transport, not scientific evidence custody or semantic authority. Its pinned source tests exercise route/server implementation behavior only, not scientific validity. Current Biopeia Lab has no target Observatory/server/application consumer, and target Observation owns a passive semantic contract rather than this HTTP service. Drop this implementation as TARGET migration input only; any future Lab presentation/transport must be separately specified and newly authored against owner-authorized contracts. This does not rule out future UI/transport needs, dispose historical evidence, or claim scientific validity/equivalence/admission; source remains read-only. |

### Historical Observatory cognition-state schema (Lab #265)

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/schemas/cognition_state.schema.json` | DROP as TARGET schema artifact | No TARGET cognition-state schema path or authorized projection contract | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `4a64ef2467617deb58e466602319c0cc5939cb71`, mode `100644`, 11,259 bytes; SHA-256 `cb100c4d360a7411b62bc7b2a1cd795598fe2e1ee19b9dc921a27081f3cab64f`. This schema describes legacy per-tick Observatory telemetry, including topology status, quantized cognitive readouts/errors, edge deltas, graph mutations, safety and predictor/structural metrics. It is a display/wire shape over Organism-owned cognitive state, not a target semantic contract or scientific result. Organism owns its cognitive state/checkpoint internals; Observation's inherited frame remains explicitly transitional, with no authorized target schema/path for this legacy projection. Drop this historical schema format only; do not infer that cognitive concepts or future observation needs are invalid or unnecessary. Historical source remains read-only; no scientific validity/equivalence/evidence-admission claim is made. |

### Historical Observatory compatibility matrix (Lab #263)

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/schemas/CONTRACT_MATRIX.md` | DROP as TARGET artifact | No TARGET compatibility-matrix path | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `dfaed5b57aa8750b22665200e7badc063aef7179`, mode `100644`, 3,093 bytes; SHA-256 `95ae294d7e636c56ae869b834a67d9fb6904910caf415af3e02ec1a74e206c96`. This document summarizes version/field rules for the historical Observatory snapshot schemas, projection bounds, replay/UI limits, and social/resource/degradation projections. It is not itself a schema or executable consumer contract. No TARGET consumer or authorized Biopeia compatibility matrix/path establishes this legacy version policy. Drop the document as a TARGET artifact only; the independently inventoried schemas and any future Observation schema/version policy remain separate and undecided here. Historical source remains read-only; no scientific validity/equivalence or evidence-admission claim is made. |

### Historical Observatory signal-knowledge schema alias (Lab #272)

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/signal_knowledge.schema.json` | DROP as TARGET alias | No TARGET code/schema alias destination | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`; Git blob `012e142f6b6d3489adc6982ee01473e338b76477`, mode `120000`, 36 bytes. The blob content is exactly `schemas/signal_knowledge.schema.json` (target-text SHA-256 `ead3631c068819492a6a2e7f2fcfc980f6e84f3cbc89c9b52e33dc7d2553a741`), so this path has no independent schema semantics. Its destination is separately inventoried at `lab/src/lab/observatory/schemas/signal_knowledge.schema.json` (blob `fe960b2b38ef3655a5aff6867b81a46fbf380a9e`) and remains DEFER under Lab #268 pending the Organism owner signal identity/provenance/privacy decision (#169; checkpoint scope #45). Drop only this unsupported legacy alias; it does not resolve or alter the underlying schema disposition and does not authorize a TARGET schema. No Biopeia target consumer or alias destination is identified. Historical source remains read-only; no schema or data is copied/deleted and no scientific validity/equivalence/admission or future-need claim is made. |

### Historical Observatory topology schema alias

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/topology.schema.json` | DROP as TARGET alias | No TARGET code destination | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`; Git blob `d83405ac5e7eac3565e2ff88caf159e2a59f1f62`, mode `120000`, 28 bytes. The symlink target is `schemas/topology.schema.json` (target-text SHA-256 `4154ccaeafb3dd3692cbc8bec8a6278962a9c1a44b4de3ca9f8e88fdbbcece73`). The underlying schema is separately inventoried as `lab/src/lab/observatory/schemas/topology.schema.json` (blob `6525f49ddf3271b0ff6f8fde7fe516da791f9059`) and is `DEFER` under Lab #270; its owner/privacy decision is tracked there. No Biopeia TARGET consumer/import was found. This drops only an unsupported legacy alias path; it does not drop the underlying schema or make scientific claims. Historical source remains read-only. |

### Historical Observatory replay schema alias (Lab #261; sibling tracked by #267)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observatory/replay.schema.json` is a symlink (mode `120000`, blob `5f31831c1a9cd170f8384475e33c26e95742a3db`, 26 bytes) containing only `schemas/replay.schema.json` (target-text SHA-256 `88f0c6a4af97c62cf3d1bcb80767051014b64f0387c63c27393d76da346be155`). The JSON schema is separately inventoried at `lab/src/lab/observatory/schemas/replay.schema.json` (blob `d1f6f042b4ac49d70a8f4debf665ea4c68f72885`) and remains under the independent review in Lab #267. The symlink is only an alternate historical access path: it adds no independent schema, API, behavior, or contract, and no Biopeia TARGET import/consumer of the alias was found. Drop only this alias as a TARGET path under UC-0001; this does not disposition the underlying schema, historical evidence/records, or the read-only source. Lab #267 remains independent and unresolved. No scientific validity or equivalence claim is made; no evidence-admission or future-need claim is made.

### Historical Observatory world visualization

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/world.html` | DROP as TARGET implementation | No TARGET code destination | Pinned source commit `80d372a186513035f85a769db886e505cabba52d`; Git blob `725250dd6c5fbc1b657be88ddb0ccd0397edb31c`, mode `100644`, 66,976 bytes; content SHA-256 `d321d005540f0169edc9a3ee8301df52d19dfdf258ddd3bc250d17766fd8f70a` verified from the exact pinned blob. This single-file HTML embeds the historical hex-grid/organism observatory and polls `/world/state`, `/api/observations?family=environment.resource_state`, and `/world/events` using source-specific payloads. It renders Reality/Ground Truth, phenotype, cognition, and population views. These routes, payload assumptions, topology, and combined presentation are not a TARGET UI or Observation publication contract, and no approved Biopeia target design/path authorizes this implementation. Drop this historical UI implementation only; do not copy it or preserve its routes as compatibility. The future Biopeia Workbench/visualization remains separately tracked in Lab #63 and must be specified anew against authorized TARGET publications. This does not claim visualization is unnecessary, assess scientific validity, or disposition separate historical evidence; the source remains read-only. |

### Historical genome recombination implementation

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/evolution/recombination.py` | DROP as TARGET implementation | No TARGET code destination; any future operation requires a new Organism design | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `8ff4517f3f102688c6b9d9780128475418c7764a` (2,232 bytes). The module implements seeded gene/linkage-group recombination (`recombine_genomes`) over the historical Genome schema. Biopeia Organism #49 confirms there is no TARGET recombination operation and requires a new design and controlled-randomness contract before any future implementation. The historical algorithm is therefore excluded from TARGET code; this does not decide whether a future Biopeia scientific question will require recombination, nor make a claim about historical scientific validity. No source code or tests are copied, and the historical source remains read-only. |

This file performs one Organism-related genome operation; it does not itself
mix a Lab apparatus responsibility with an Organism responsibility. Its
previous `SPLIT` classification was therefore unsupported by the file's
responsibilities. The source implementation is `DROP`; future TARGET work, if
authorized, must be newly specified and implemented rather than adapted from
this function.

### Historical genome mutation and developmental-budget intervention

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/evolution/mutation.py` | DROP as TARGET implementation and API | No TARGET code destination; future Organism or Lab methods require fresh specifications | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `fcd57742df5bdec29de2801aa4b3d68bffb2f4dd` (5,019 bytes). The file contains internal path/family-scale helpers, seeded `mutate_genome`, the `mutate_continuous_fields` wrapper, `derive_child_genome`, and a separate one-variable `mutate_soft_budget` intervention. The historical source uses an explicit seed, but that alone does not establish a current TARGET randomness or inheritance contract. Organism main `022afcc9dad0d4edbafd70440afb712f5bee7bfc` has mutation-related schema/data shapes but no mutation operation; Organism #49 keeps the capability POST_MIGRATION and requires a new method, controlled randomness and inheritance semantics before implementation. Lab main `c9e558b68611477f8400f213badf6f32d8b04df2` has no consumer for these symbols. Exclude the historical implementation, wrapper and API from migration; this does not decide whether future Organism genetics or Lab study methods are needed. Related historical protocols/results remain under their independent Lab #45 disposition and scientific-custody process. No code or source tests are copied; the source remains read-only. |

The file combines historical organism-genome alteration with an experimental
developmental-budget intervention, but neither responsibility has a current
TARGET implementation consumer or authorization to reuse this implementation.
Both portions are explicitly dropped as source code; the old `SPLIT` label did
not justify carrying either implementation forward. This code disposition is
not a scientific assessment or a disposition of historical protocol/result
artifacts.

### Historical offspring-package implementation

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/evolution/reproduction.py` | DROP as TARGET implementation/API | No TARGET code destination; any future reproductive method requires fresh TARGET design and authorization | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `4f990ac460e0b4104b925730e5705aa9179b70ae` (2,085 bytes). The single exported `create_offspring_package` combines historical mutation/recombination, germline/epigenetic handling, and parent/generation records. Organism main `022afcc9dad0d4edbafd70440afb712f5bee7bfc` has an `InheritancePackage` value type but no offspring producer or reproductive transition; Organism #49 records reproduction/genetics implementation as POST_MIGRATION and requires a fresh TARGET method/contract if later authorized. Lab main `cebbdb149deac3bf74b6b33d1bae2da364ace6b9` has no target evolution/reproduction consumer. The historical function is used by a historical study and source tests, but those protocol/result artifacts remain separately governed by Lab #45; no scientific validity, method-equivalence, evidence-admission, or future-capability claim is made. No source implementation/tests are copied; the pinned source remains read-only. |

This row excludes the historical offspring-package implementation from TARGET
migration only. It does not dispose the associated study/protocol/results or
decide whether a future Biopeia Organism reproductive capability is needed.

### Historical Lab run-definition module

The pinned `lab/src/lab/experience/definition.py` source module is classified `DROP` as TARGET code/API. At source commit `80d372a186513035f85a769db886e505cabba52d`, blob `1bbf7ea86a90f44203024888a1cfa029c5419ebd` (6,593 bytes), it defines a Lab-specific run taxonomy, Physics3D exit-cause mapping, and a hard-coded run/situation catalog. The file contains no Organism-owned state and no responsibilities requiring a multi-owner `SPLIT`.

Biopeia Lab main at `acfb5c6c44eb8fec3eebdcaf236c2b94d3d355a4` has no current TARGET consumer or approved contract for this historical API. This disposition excludes the implementation from migration; it does not decide whether a future Biopeia run-definition capability is useful, classify related protocols/results, or make a scientific-validity claim. Historical protocols and evidence remain governed separately by Lab #45, and the pinned source remains read-only.

### Historical Lab experience safety/run-guard implementation

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/experience/safety.py` | DROP as TARGET implementation | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `6d8b084b3e212ad76d56a418e75dec4982180a8e` (2,530 bytes). The module defines Lab-side termination guards over historical `alive`/`vital_state` values and `RunKind`, including the fixed protected-state set `agonizing`/`dormant`. Biopeia Lab main `50d0b575d693bc2efd619520e6cc7456a6918964` has no consumer or approved TARGET contract for these rules. Exclude this implementation rather than port legacy physiology/run semantics. This does not claim scientific invalidity or dispose of related protocols/results; any future Lab apparatus policy must be specified afresh for a TARGET study. The historical source remains read-only. |

The source responsibility is confined to historical Lab run apparatus and does
not establish authority over Organism lifecycle or Embodiment somatic truth.
The prior `SPLIT` label had no concrete second responsibility or destination;
the implementation is therefore classified `DROP`, not transferred to another
domain. Protocol/result disposition remains separate under Lab #45.

### Historical kernel-characterization package facade

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/kernel_characterization/__init__.py` | DROP as TARGET code | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `072aea65d990b64db4936ead4e0fb0861cb46ca1` (343 bytes). The initializer contains a docstring and re-exports `BASELINE_KERNEL` and `KernelVariant` from the separately inventoried historical `config` module; it defines no independent behavior. The Biopeia Lab TARGET tree has no `kernel_characterization` package or tracked source/test consumer at candidate main `fcf678d85241842a7811e02c3e1b0d37b8895ade`. Drop this package facade only; the sibling config and characterization/study modules remain separate inventory items and are not classified here. This does not claim the historical method is scientifically invalid or future Lab analysis unnecessary. Do not retain the old import surface for compatibility. Historical source remains read-only. |

### Historical kernel-characterization config disposition (Lab #209)

At pinned historical source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`,
`lab/src/lab/kernel_characterization/config.py` is blob
`011e47d5527d3cc0844d97b187a047fd533356da` (4,182 bytes; path commit
`13720935595fedabec2c376dc933629b0deae5aa`). Its three recorded symbols are
`BASELINE_KERNEL`, `KernelVariant`, and `complete_kernel`. The baseline
instantiates the historical `KernelLimits`; the variant creates a
study-specific copy changing selected resource limits; `complete_kernel`
serializes all fields for the historical run manifest. The historical runner
and its source-coupled tests are the only tracked callers at the pinned source.

Biopeia Organism at `b674450dd6678d7a0a00a41591648511814709ba` already owns
`KernelLimits` at `src/organism/cognition/limits.py`. Its contract is an
Organism runtime ceiling type, and it differs from the older historical
parameter set; that relationship does not make the Lab experiment wrapper an
Organism API. Lab at `e45f94473f2ee49d9097a4fa817671a72fce2cb0` has no TARGET
`kernel_characterization` package or tracked consumer of these symbols.

**Disposition: DROP the entire historical config module as TARGET code, not
SPLIT.** The source row has one actual responsibility: experiment-local
configuration and serialization for the historical characterization runner.
`KernelLimits` is an input owned by the historical Organism layer and already
has a distinct TARGET owner; this file does not implement that limit contract.
No target Lab experiment configuration/consumer is present to retain, and the
old variant/manifest API is not carried forward by analogy. This decision
disposes only this code row; it does not disposition the separately inventoried
runner, protocols, studies, or results, and makes no scientific-validity,
result-admission, method-equivalence, or future-need claim. Historical source
remains read-only.

### Historical kernel-characterization protocol data (Lab #212)

At pinned historical source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`,
`lab/src/lab/kernel_characterization/protocols.py` is blob
`1d056c3cb86d36c0b9e36fcee507fb9da3671992` (727 bytes). The module defines
ten fixed seeds, a `Phase` value type, seven named phase durations, and a helper
that substitutes a positive uniform duration. The only tracked call sites at
the pinned source revision are in the historical `kernel_characterization`
runner, where those values structure a synthetic capacity probe. The source
contains no Organism state/behavior and no distinct responsibility assigned to
multiple TARGET owners. Biopeia Lab has no corresponding TARGET module or
tracked consumer.

**Disposition: DROP this historical code row from TARGET.** This does not delete
or disposition the historical source, protocol/results, or associated evidence;
they remain preserved under their separate governance and custody paths. It is
not a scientific-validity, result-admission, method-equivalence, or future-need
claim. No experiment was run and no protocol was changed.


### Historical kernel-characterization study runner (Lab #213)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`,
`lab/src/lab/kernel_characterization/runner.py` is blob
`ee911bbf77e8620281cd140a439ecef760afc5ff` (37,213 bytes). It orchestrates
historical K1-A/K1-B and K2-K12 characterization runs, invoking historical
cognition, structural-plasticity, consolidation, and weight-stability paths,
and emits manifests and run outputs. Its recorded function inventory matches
the pinned source. Biopeia Lab has no corresponding TARGET runner or tracked
consumer; the pinned callers are source-coupled tests and direct study-runner
entry points. This is a composite historical study runner, not an independent
Organism runtime implementation; its current TARGET owner/path is not established.

**Disposition: DROP this historical runner as TARGET code.** This excludes the
legacy implementation only; it does not dispose of its protocols, study outputs,
source, or evidence, which remain preserved and separately governed. This is not
a scientific-validity, result-admission, method-equivalence, or future-need
claim. No study or experiment was run.


### Historical private-model architectures (Lab #214)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`,
`lab/src/lab/modeling/architectures.py` is blob
`e35ff6df4dd2ef8649ca2d365c9d1947cc1a2aa2` (9,882 bytes). It defines bounded
GRU/Transformer specifications, parameter-budget selection, reconstruction from
model manifests, optional PyTorch builders, and parameter counting. Its imported
`ArchitectureId` and `ModelArtifactManifest` come from the separately inventoried
historical `symbiont.modeling.authority` module. Pinned callers are Lab's own
historical modeling gateway/trainer and source-coupled tests; Biopeia Lab has no
corresponding TARGET module or tracked consumer.

**Disposition: DROP this historical Lab implementation as TARGET code.** This
does not reassign or transfer the authority module, architecture/model artifacts,
studies, or evidence; those remain separately governed and preserved. No model
was trained or evaluated. This is not a scientific-validity, result-admission,
method-equivalence, or future-need claim.


### Historical private-model artifact/store implementation (Lab #215)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`,
`lab/src/lab/modeling/artifacts.py` is blob
`0f5330bee027421e7a58dc204c7e66dfee8babb3` (8,025 bytes). It defines a
manifest-validated artifact wrapper and a content-addressed file store for model
weights and manifest metadata. It depends on the separately inventoried
`symbiont.modeling.authority` contract and historical durable-write helper.
Pinned callers are the historical Lab model factory/gateway/trainer, private-model
training apparatus, observed-resident CLI, and source-coupled tests. Biopeia Lab
has no corresponding TARGET module or tracked consumer.

**Disposition: DROP this historical Lab implementation as TARGET code.** This
does not delete, transfer, admit, or reclassify model files, manifests, source,
or evidence; their custody/authority remains separately governed. No training
or artifact review occurred. This is not a scientific-validity, method-equivalence,
or future-need claim.


### Historical private-model baseline metrics (Lab #216)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`,
`lab/src/lab/modeling/baselines.py` is blob
`03d2e76bac1d507056861aa93ce55a50cfef569e` (3,193 bytes). It defines
uniform, persistence, and smoothed-frequency token-outcome baselines and
computes log-loss/accuracy/count summaries over historical `EncodedSplit`
records. Pinned callers are Lab's historical modeling evaluation and private-model
learnability study; Biopeia Lab has no corresponding TARGET implementation or
tracked consumer.

**Disposition: DROP this historical helper code as TARGET code.** This is not
validation, rejection, or replacement of the baseline methods, and does not
dispose of protocols, study results, or evidence; those remain separately
preserved and governed. No study was run. No scientific-validity, result-admission,
method-equivalence, or future-need claim is made.

### Historical private-model outcome metrics (Lab #223)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`,
`lab/src/lab/modeling/outcome_metrics.py` is blob
`6540b1d7ac18e3220ba5580184cfeacc259c9e4d` (2,300 bytes). It computes held-out
cross-entropy, accuracy, and count over explicitly indexed outcome-token
positions in the historical `EncodedSplit` representation. Pinned callers are
private-model evaluation/factory/training and learning-study code; Biopeia Lab
TARGET has no corresponding modeling package or tracked consumer.

**Disposition: DROP this historical helper code as TARGET code.** This is not
an assessment of metric validity, study outcomes, or scientific evidence; those
remain separately preserved and governed. No candidate evaluation or study was
run. No scientific-validity, outcome validity, admission, method-equivalence,
or future-need claim is made.

### Historical continuous temporal challenger model (Lab #224)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`,
`lab/src/lab/modeling/reservoir.py` is blob
`f901fa48f1744fec08dcef5a40a2eac825174150` (8,156 bytes). It implements a
fixed recurrent reservoir with an online normalized-LMS readout through the
historical temporal prediction/resource-usage interfaces. Pinned callers are
Lab continuous temporal challenge/control studies and tests; current Biopeia
Lab TARGET has no temporal challenger model package or tracked consumer.

**Disposition: DROP this historical model implementation as TARGET code.** The
study protocols, inputs, results, and evidence are separate governed assets and
are not disposed of by this code decision. No model run or scientific
comparison was performed. No scientific-validity, efficacy, equivalence,
evidence-admission, or future-need claim is made.

### Historical private-model and temporal study orchestration (Lab #225)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`,
`lab/src/lab/modeling/study.py` is blob
`203a1aace30839a5490db32fce9b15be7cfc9f91` (10,043 bytes). It composes
private-model training, held-out evaluation and promotion, cross-individual
comparison, token remapping for negative controls, regime-shift evaluation,
temporal challenger comparison, and responsibility summaries into historical
study utilities/results. These are study design and analysis orchestration,
not Organism behavior or a reusable TARGET contract. The pinned consumers are
historical Lab study modules/tests; no corresponding TARGET study/model API or
tracked consumer was found in the bounded current Biopeia repository search.

**Disposition: DROP this historical orchestration code as TARGET code.** Study
protocols, corpora, results, and evidence remain separately preserved and
governed. No study/evaluation was executed. No scientific validity, efficacy,
interpretation, evidence admission, equivalence, or future-need claim is made.

### Historical temporal challenger evaluation (Lab #226)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`,
`lab/src/lab/modeling/temporal_evaluation.py` is blob
`40cee786463b5161ba397686eebb357833b31137` (3,433 bytes). It fits the historical
decayed variable-order Markov challenger on encoded training sequences, then
computes held-out next-token loss, accuracy, and resource summaries without
updating learned counts with test tokens. Pinned callers are historical
private-model/temporal learning studies and tests; no current TARGET consumer
or temporal-challenger evaluation contract was found in the bounded repository
search.

**Disposition: DROP this historical evaluation code as TARGET code.** This
does not dispose of protocols, corpora, results, or evidence. No study or
evaluation was run. No metric/scientific validity, evidence admission,
equivalence, or future-need claim is made.

### Historical private-model training and adaptation (Lab #227)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`,
`lab/src/lab/modeling/trainer.py` is blob
`e4625c42267ab794a5bbc7f952ae0cb97a4d644c` (20,490 bytes). It defines optional
PyTorch training configuration/results/probes, batching and evaluation,
checkpoint serialization and parent-state/vocabulary adaptation, and private
next-token model training/adaptation loops. Historical consumers are Lab
factory/study orchestration; no matching trainer or private-model consumer was
found in the bounded current Biopeia TARGET search.

**Disposition: DROP this historical trainer implementation as TARGET code.**
This does not dispose of model artifacts, protocols, corpora, results, or
evidence. No training/adaptation was run. No scientific validity, efficacy,
evidence admission, equivalence, or future-need claim is made.

### Historical private-model inference gateway (Lab #222)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`,
`lab/src/lab/modeling/gateway.py` is blob
`93e8e65261450c5c56e77bef13d2f66a6c6264fd` (4,642 bytes). It loads optional
PyTorch models from stored private-model artifacts and serves cached token
inference. Pinned callers are historical learning studies, training tests, and
an observed-resident CLI path. Current Biopeia Lab and Organism targets have no
direct consumer or matching artifact-inference contract.

**Disposition: DROP this historical inference gateway as TARGET code.** This
does not dispose of models, artifacts, protocols, or evidence, nor assess their
utility. No model loading, inference, or study was performed. The source's legacy
`torch.load` compatibility fallback is noted only as provenance; this issue is
not a security assessment or endorsement. No scientific-validity, efficacy,
method-equivalence, or future-need claim is made.

### Historical private-model factory and adoption orchestration (Lab #221)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`,
`lab/src/lab/modeling/factory.py` is blob
`7fce0166b3659fefadbae72e7a83752f6a43d4d7` (8,645 bytes). It orchestrates
private-model training/adaptation, artifact storage, held-out evaluation, and
adoption/activation through the historical `ModeledOrganismRuntime` contract.
Pinned consumers are Lab learning studies and CLI apparatus. Biopeia Lab TARGET
has no equivalent factory; current Organism TARGET has no corresponding runtime
adoption/promotion contract or direct consumer.

**Disposition: DROP this historical orchestration code as TARGET code.** This
is not a statement that model training, adaptation, or organism-owned learning
is unnecessary; no code, model, protocol, result, or evidence is transferred or
disposed of. No training/evaluation/adoption/promotion was run. No scientific
validity, autonomy, method-equivalence, or result-admission claim is made.

### Historical private-model evaluation and promotion (Lab #220)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`,
`lab/src/lab/modeling/evaluation.py` is blob
`8860f21a4e9b76f324f60b07237229b646a64087` (5,285 bytes). It aggregates
held-out outcome metrics and applies configurable candidate-promotion thresholds
against trivial, recurrent, or cognitive references. Pinned callers are
historical private-model factories and studies; Biopeia Lab TARGET has no current
model-promotion consumer.

**Disposition: DROP this historical evaluation/promotion implementation as TARGET
code.** Its threshold values are not ratified scientific policy or evidence
admission. No candidate was evaluated or promoted; no protocols, results, or
evidence are disposed of. No validity, efficacy, result-admission,
method-equivalence, or future-need claim is made.

### Historical private-model determinism setup (Lab #219)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`,
`lab/src/lab/modeling/determinism.py` is blob
`e3b281b7f51a8a9216a478e754d2999a460038ce` (1,676 bytes). It configures
PyTorch training seeds, CPU/CUDA RNG state, thread settings, and deterministic
algorithm mode. Pinned callers are private-model training and an offline
physics3d equivalence-test helper; it is not Organism runtime behavior. Biopeia
Lab TARGET has no corresponding training/equivalence consumer.

**Disposition: DROP this historical configuration helper as TARGET code.** No
study or equivalence run was performed. This does not dispose of any separate
study results or evidence, and makes no reproducibility, scientific-validity,
method-equivalence, or future-need claim.

### Historical private-model corpus encoding (Lab #218)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`,
`lab/src/lab/modeling/dataset.py` is blob
`365fa2e2feec1187616c6616704593ba2d287ecb` (5,348 bytes). It defines encoded
split/corpus containers and converts historical training corpora into token-id
sequences while preserving causal outcome-target positions. Pinned callers are
private-model training/evaluation and learning-study code; Biopeia Lab TARGET
has no corresponding modeling package or tracked consumer.

**Disposition: DROP this historical encoding helper as TARGET code.** This does
not dispose of source corpora, protocols, study results, or evidence; these
remain separately preserved and governed. No study was run. No scientific or
outcome validity, result-admission, method-equivalence, or future-need claim is
made.

### Historical Physics3D physical-effects disposition (Lab #296)

The pinned `lab/src/lab/physics3d/effects.py`
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`843f12def33ae4aecc19afe36b2d8c10b1539d8d`, mode `100644`, 10,891 bytes)
parses observer-side physical payloads and computes kinematic deltas, rotations,
contact measures, path efficiency, mechanical work and metabolic cost. Its own
module contract excludes reward, utility, goals, action preference and runtime
feedback. It is a coupled metric contract, and the historical owner hint does
not establish several target authorities; correct `SPLIT` to bounded `DEFER`.

No accepted TARGET physical-state schema/path or World/Embodiment contract for
field identity, units, work/cost provenance or metric interpretation is
established. Lab has not established whether outputs are diagnostics or study
evidence, nor custodian/retention/admissibility policy. World must define
physical-state/kinematic semantics; Embodiment must decide body-specific
payload semantics; Lab must determine output status and custody. Closure
requires those contracts, metric provenance/units and a consumer/path, or
explicit owner-authorized DROP of portions. No code/data is copied or deleted;
no metric correctness, physical validity, competence, efficacy or evidence
admissibility is claimed. This does not block bounded runtime transfer.

### Historical variable-order Markov challenger (Lab #217)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`,
`lab/src/lab/modeling/context_tree.py` is blob
`6ee1533579f2d588b6a4422c3bd007a2f45c18ac` (5,859 bytes). It defines
`DecayedVariableOrderMarkov`: a discrete next-symbol challenger with decayed,
smoothed context counts, bounded context length, and resource accounting. The
pinned source callers are offline Lab temporal evaluation and private-model
controls/study code; this is not Organism runtime state or behavior. The Biopeia
Lab TARGET has no corresponding module or tracked consumer.

**Disposition: DROP this historical helper as TARGET code.** This does not
remove or classify its protocols, study results, or evidence; those remain
preserved and governed separately. No study was run. No scientific validity,
efficacy, method-equivalence, result-admission, or future-need claim is made.

### Historical modeling package facade

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/modeling/__init__.py` | DROP as TARGET code | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `3bf74d0ff1633c094853d49a1d5dcc637cbec7dc` (2,367 bytes; SHA-256 `7f2c443d947fa4b762cd990d125e0c5a473457efddd34db221c6c95f23d46d07`). This initializer is an aggregate import facade re-exporting names from separately inventoried modeling modules; it defines no independent model, training, or evaluation behavior. Biopeia Lab main `d58ff1fdeb6e4450a72d264fca4251311b2a0bdd` has no `src/lab/modeling` package or `lab.modeling` source/test import. Drop only this historical package-level import facade. The underlying modeling modules remain independent inventory rows and are not classified here. No scientific validity, utility, or irrelevance claim about models, studies, or results is made; no TARGET implementation is authorized. Historical source remains read-only and the old import surface is not retained for compatibility. |

### Historical evolution lineage implementation

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/evolution/lineage.py` | DROP as TARGET code | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `0a9566b08ad245706162c1f8c3b67f2a8132921e` (4,114 bytes). `LineageRecord`/`LineageArchive` and `GenomeLineageRecord` are historical Lab evolution records; the archive is an in-memory record/ancestor/export/restore helper. A tracked-source search across the inspected current Biopeia main heads found no TARGET consumer for these symbols; historical references are limited to the source module, its package re-export, and source tests. Exclude this implementation and API from migration rather than assigning it by historical location. Any future Organism reproduction/lineage capability must be newly specified against TARGET contracts if required. This is a code disposition only: it makes no scientific validity, evidence-admission, method-equivalence, or permanent capability claim. Historical source and records/artifacts remain preserved; source tests are not migrated. |

### Historical Observation package initializer

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observation/__init__.py` | DROP as TARGET code | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `7c68362376e3d177daf15d86eeed0e916d45702b` (207 bytes). The file contains only a package docstring and defines no symbols or executable behavior. Biopeia Observation owns its own TARGET semantic projection contracts; Lab has no corresponding source package or consumer. Drop this historical initializer only; sibling Observation source rows and Lab's scientific evidence custody are unaffected. This is not a decision to remove or weaken the Observation authority boundary, and it does not classify scientific artifacts. The historical source remains read-only; no compatibility namespace is retained. |

### Historical Physics3D integration package marker

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/integration/physics3d/__init__.py` | DROP as TARGET code | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `2c55cd785f6933fffd22f011447f38cc79d8e216` (81 bytes). The file contains only a package docstring; it defines no implementation or exports. Biopeia Lab has no corresponding integration package or consumer. Drop this historical package marker only. This does not disposition the separately inventoried integrated runtime, physics3d modules, domain semantics, protocols, or evidence; each remains subject to its own owner review. The source remains preserved read-only. |

### Historical World integration package marker

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/integration/world/__init__.py` | DROP as TARGET code | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `366e8f126df46bb6eda3cf0bff057c9d06c671cc` (54 bytes). The file contains only a package docstring and defines no symbols. No Biopeia TARGET package or consumer uses this historical namespace. Drop this package marker only; the separately inventoried historical integration/runtime files are not dispositioned here. The source remains preserved read-only. |

### Historical World integration adapter (Lab #208)

| Source path | Disposition | Target owner/path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/integration/world/adapter.py` | DROP as TARGET code (all recorded symbols) | No TARGET code destination; no historical namespace or compatibility adapter retained | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`; blob `1e8c7b50d658ac2fc06db98868c713a517bc27b7` (26,212 bytes). AST inspection at the pinned commit verifies the 20 names in the inventory row. Searches of tracked TARGET source and tests at Lab `ac618e10ba8fdd9ce11bd9d7dd5045ea5d1006cd`, World `00e6335740101acef0fd93610edfbb7e7cfe0fac`, Environment `d09e45c40633c9b2bf927c7aec3f6326318c2ea8`, Embodiment `5a23e1fbeaa31109647aec4d4dc36eddbe0a6321`, and Organism `b674450dd6678d7a0a00a41591648511814709ba` found no direct consumers of the historical API. World causal-cycle orchestration, Environment inputs, Embodiment receptor/actuator mechanics, and Organism birth/cognition mechanisms have their own TARGET contracts; they are not asserted to replace or be equivalent to this adapter. The historical module is an integrated Lab population harness, not one separable current owner API. This excludes only its historical implementation from TARGET; it does not assert scientific invalidity, lack of future need, or validity/equivalence of studies or results. The pinned source remains read-only. |

The issue-recorded symbols are individually dispositioned as follows; each DROP means exclusion of that historical symbol/API from TARGET, not a claim that its scientific question is invalid:

| Source symbol | Disposition and bounded reason |
| --- | --- |
| `LONGITUDINAL_CONTRACT` | DROP — historical subject-construction setting; no TARGET adapter consumes it. |
| `physical_receptor_ids` | DROP — historical apparatus identity generator; no TARGET consumer of this API. |
| `WorldDiscoveryProvider` | DROP — implements the historical Host discovery contract; no TARGET Lab host adapter uses it. |
| `WorldReadingProvider` | DROP — buffers legacy World observations into historical host readings; no TARGET Lab consumer. |
| `local_substrate_signals` | DROP — legacy apparatus projection helper; no TARGET contract consumes this mapping. |
| `_capabilities_for` | DROP — builds capabilities for the historical host API; no TARGET adapter consumer. |
| `_unit_interval` | DROP — source-local numeric transform, not a standalone TARGET domain contract. |
| `_mix_weight` | DROP — source-local physical-receptor transfer rule; no TARGET contract or consumer. |
| `physical_receptor_signals` | DROP — historical clean-study projection; no TARGET contract adopts its mixing semantics. |
| `clean_world_observation` | DROP — wrapper around that historical projection; no TARGET observation consumer. |
| `_load_base_genome` | DROP — historical version-parsing/factory wrapper; Organism birth APIs are independent, not mapped replacements. |
| `ActuationBinding` | DROP — historical World-effect binding record; no TARGET consumer of this type. |
| `ActuationBindingConstitution` | DROP — historical binding collection/fingerprint; no TARGET contract adopts this schema. |
| `ActuationAdapter` | DROP — translates historical opaque actuation into legacy WorldAction; no TARGET adapter consumer. |
| `default_world_actuation_binding` | DROP — historical apparatus default mapping; no TARGET contract authorizes this mapping. |
| `ActionExecutionResult` | DROP — module-local legacy step report; no TARGET consumer. |
| `WorldTickRecord` | DROP — module-local legacy tick record; World causal records are a distinct owner contract, not an equivalence mapping. |
| `_OrganismRig` | DROP — private state bundle for the historical integrated harness; no TARGET consumer. |
| `_construct_organism` | DROP — legacy/experimental population construction path; no TARGET consumer; no Organism equivalence claim. |
| `_act` | DROP — legacy harness action/intake driver; no TARGET consumer; no behavioral equivalence claim. |

The inventory row preserves the pinned path/blob and records this decision. No runtime code, source test suite, scientific result, or compatibility layer is copied. This is a migration classification only, not scientific review or admission.


### Historical Observatory body self-knowledge schema (Lab #264)

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/schemas/body_schema.schema.json` | DROP as TARGET schema artifact | No TARGET schema path or compatibility contract | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `4f393ed9161c3ba8e9672dc78edbb1bef9cd516d`, mode `100644`, 4,195 bytes; SHA-256 `d111d1bafaee791e9688f2a6a0e6aefb67a8775a09b1aec797f15b1cca498738`. This closed JSON Schema describes a historical Observatory projection of bounded body self-knowledge, including sensory/cognitive-region parts, confidence and state classes, dependencies, and global state. It is not an authoritative Embodiment physical-body schema. Current Embodiment BodyPose and Observation adapters describe distinct physical claims; no TARGET contract for this legacy self-model representation was identified. Drop this schema format only; do not infer that body self-knowledge or future target projections are unnecessary or invalid. No source is deleted and no scientific validity/equivalence/evidence-admission claim is made. Historical source remains read-only. |

### Historical Observatory snapshot schemas

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/snapshot.schema.json`; `lab/src/lab/observatory/schemas/snapshot.schema.json` | DROP as TARGET schema artifacts | No TARGET schema/code destination | Both paths resolve to the same pinned source blob `469eb56de0a1ce806eb4dfd693d06691cbf9f220` at `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d` (mode `100644`, 61,719 bytes; SHA-256 `3ffb739a06c7047d184b8c392d6916a0e5b6a71232472048be92d11a7c09e6f0`). The JSON Schema identifies itself as a bounded, display-only Symbiont Observatory snapshot and includes schema version/tick plus organism, population, observer and apparatus projections. No Biopeia TARGET consumer or authorized schema/wire contract was identified; Observation Semantic Model v1 is conceptual and does not authorize this historical schema. Drop both copies from TARGET migration input without copying or compatibility support. This does not claim future Observation semantic-family schemas are unnecessary and makes no scientific-validity, equivalence or evidence-admission claim. The historical source remains read-only. |

### Historical Observatory topology-health contract test

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/tests/test_topology_health_contract.py` | DROP as TARGET test | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `9d24e5ebb1366a0228d81637b64610a11c1ff671` (1,240 bytes). The two assertions exercise only the historical `cognition_state.schema.json` and private Lab Observatory `_cognition_state` adapter: an enum for `topology_health`, a `recovering` flag, and omission of raw graph/weight fields from that adapter's output. Biopeia has not authorized this source schema or adapter API as a TARGET contract. These assertions are not a scientific result or oracle. Drop this source test from TARGET code; do not migrate the historical test suite or infer that future cognition-state observation is unnecessary. No source bytes are deleted and no scientific validity, equivalence or evidence-admission claim is made. Historical source remains preserved read-only. |

### Historical Observatory test package marker

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/tests/__init__.py` | DROP as TARGET code/test | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `4e1fc67df6cac9182eac14d80d7c79420feb5709` (38 bytes). This file contains only the docstring `Observatory test suite package.`; it defines no test, implementation, API, or scientific result. Biopeia's own Lab tests live in its TARGET test tree and do not consume this historical source test namespace. Drop this package marker only; this neither reuses the source test suite nor disposes of any separate scientific evidence. Historical source remains preserved read-only. |

### Historical Observatory schema validator (Lab #262)

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/schema_validate.py` | DROP as TARGET implementation | No TARGET schema-validation helper path | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `762299aa594fc5209a0ca7b826340dc33f6f80b4` (mode `100644`, 8,048 bytes); verified symbols `_require;validate`. This custom helper validates the historical Observatory JSON schema subset and resolves local `$ref`; its module documentation expressly says it is a test helper, not runtime input sanitization. No Biopeia TARGET contract or consumer establishes this helper as an Observation or Lab responsibility or supplies a target path. Drop only this source implementation from TARGET migration. Its schemas are independently inventoried and not decided by this row; the historical validator tests are independently dispositioned under Lab #288. No source is deleted and no schema validity/equivalence, scientific validity, evidence-admission, or future-need claim is made. Historical source remains preserved read-only. |

### Historical Observatory schema-validation tests

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/tests/test_schema_validate.py` | DROP as TARGET test | No TARGET test destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `d6754edd98b6e26315ee2f95d13d7e4038642bba` (mode `100644`, 3,912 bytes). `SchemaValidateConditionalTests` checks the historical Observatory JSON-schema helper's `if/then/else`, `allOf`, `anyOf` and `not` behavior; `SignalKnowledgeSchemaTests` checks required/identity/unexpected-field structure in the historical `signal_knowledge.schema.json`. The inspected Biopeia TARGET repositories establish no matching schema/test contract or destination. These are structural test assertions, not scientific evidence. Exclude this historical test file from TARGET tests while preserving its source and provenance read-only. This does not claim future schema validation, signal-knowledge representation or Observation publication is unnecessary or scientifically invalid. |

### Historical Observatory adapter tests (Lab #274)

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/tests/test_adapter.py` | DROP as TARGET test | No TARGET test destination | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`; blob `b4a586f647bb22a6169863bbbe56312b4203ed5f`, mode `100644`, 22,130 bytes. Verified symbols `_minimal_genome_payload`, `AdapterTests`, `_test_generative_projection_fixture`, `test_projects_generative_cognition_as_separate_ephemeral_layer`. The suite imports the legacy Observatory adapter and checks historical snapshot fields, replay serialization, schema shapes, and synthetic bounded cognition/generative projection fixtures. Assertions on contamination counters concern constructed objects and implementation output; they are not observed biological outcomes or scientific evidence. No Biopeia TARGET consumer or authorized contract adopts these legacy test oracles, and the tested adapter/schemas are separately inventoried. Exclude this implementation-coupled source test from TARGET tests; retain historical source read-only. Future tests must target owner-approved contracts. This does not dispose of scientific assets/results or establish validity, equivalence, evidence admission, or future need. |

### Historical Observatory adversarial hardening tests (Lab #275)

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/tests/test_adversarial_hardening.py` | DROP as TARGET test | No TARGET test destination | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`; blob `00262cc40b18a8de57910e192d799f0063b21a07`, mode `100644`, 4,748 bytes; verified symbols `ROOT`, `_next_sse_payload`, `ObservatoryAdversarialHardeningTests`. The tests exercise legacy schema validation, malformed registry records, heartbeat timestamp parsing, run rollover and the historical HTTP/SSE server using synthetic temporary records. These are implementation-coupled software/security assertions, not a target API contract or scientific evidence. No Biopeia target Observatory server/registry consumer adopts these behaviors. Exclude only this historical test from TARGET tests; preserve its source read-only. Any future security requirements must be specified and tested against their owning TARGET contract; this disposition does not say safeguards are unnecessary. No evidence/assets are dispositioned and no scientific validity/equivalence/admission claim is made. |

### Historical reproduction package facade

| `lab/src/lab/reproduction/__init__.py` | DROP as TARGET code | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`, blob `302e1d96cd93da7dc7baaf3ff63c387bd9015d76` (313 bytes). The file only re-exports `BirthRecord`, `DeathRecord`, `HabitatBirthAuthority`, and `materialize_clonal_bud` from separately inventoried `authority.py` and `runtime.py`; it has no independent behavior. Drop this package facade only. The sibling modules remain independent inventory items and are not dispositioned here. No historical package import path is retained for compatibility. This does not make a claim about scientific validity, future reproductive capability, method equivalence or evidence admission; the historical source remains read-only. |

### Historical clonal-budding runtime disposition (Lab #318)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/reproduction/runtime.py` is blob `1f24d3c045f971f4e69c4df019da7da1b581aa72` (path commit `200e0e259a25c6acad7b4fa2d79a27c78500e0e8`, 6,956 bytes). The two inventoried symbols are `materialize_clonal_bud` and `_birth_surfaces_available`.

The code is a cross-boundary historical adapter, not separable Lab-only apparatus: it reads private Organism genome, reproductive-readiness, metabolism, physiology and runtime fields; asks `HabitatBirthAuthority` for a birth record; constructs a body state, metabolism and base cognitive graph; calls the Lab canonical organism factory; charges parental energy; and may join the child to social habitat. Its preflight checks historical habitat capacity. These operations together encode a reproduction transition and assumptions about who owns readiness, identity, somatic state, initialization, and habitat authority. The function depends on a private legacy runtime surface and cannot be retained as a Biopeia target operation merely by redirecting the factory call.

| Source responsibility | Current target evidence | Disposition |
| --- | --- | --- |
| Reproductive readiness, inherited genome and offspring transition | Organism #49 remains open and records that the target genetics data has no reproduction producer/consumer; no target operation is authorized by this disposition. | DROP this historical implementation; future work requires its own Organism-owned contract/design. |
| Habitat birth record and capacity authority | Separately inventoried in Lab #317, which remains open; this issue does not settle its disposition. | No part of this runtime row is retained as a target authority. |
| Child body/metabolism/cognition setup and parent energy debit | Historical code directly accesses private legacy runtime and composes several domain states; no target offspring initializer/path is established by this issue. | DROP the composite and source-coupled tests from target migration; no equivalent behavior is claimed. |
| Lab composition of the above | No current target contract/path for this legacy reproduction adapter. | No target code destination; do not preserve a compatibility API. |

This is a code-migration disposition only. Historical tests that call `materialize_clonal_bud` are evidence that the historical code is exercised by its test suite, not scientific validation or evidence of target equivalence. No claim is made that reproduction is unnecessary, impossible, scientifically invalid, or permanently prohibited. The pinned source remains read-only; historical protocols/results remain independently governed and are not dispositioned here. See the exact row in `migration/source-inventory-80d372a.tsv` and the related open issues [Lab #317](https://github.com/biopeia/lab/issues/317) and [Organism #49](https://github.com/biopeia/organism/issues/49).

### Historical Lab World aggregate facade

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/world/__init__.py` | DROP as TARGET code | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `73fb4a3b7f9c3380b6aa94f11f1bb62bbe494d02` (1,401 bytes). The initializer re-exports Environment genesis helpers and historical World adapter, population, checkpoint, runtime and transaction symbols from separately inventoried modules. It is an old aggregate import surface, not an independent implementation to migrate. Tracked source/test searches at candidate revisions found no Biopeia `lab.world` import or package; the only textual match was an unrelated `biopeia.lab.world-digest.v2` identifier in Lab. Drop the old facade and do not preserve its import path. This does not dispose of the re-exported modules or their symbols; each remains subject to its own inventory row and owner review. The source remains read-only. Search revisions: Lab `fccf2710e468b796298c66fdf99a9da0167a6828`, Organism `26778028c4058d96ba2f2b77199df7852a03def1`, Embodiment `a925c2f2f2694048e4ced4c00874dcfd2331bebe`, Environment `b71d5566c3a73774a088a41a7b99a03954e43a53`, Modality `79b779152d4bff2ab4191dc6601c8f1640e4cae3`, World `e231fa38c92360161847b71e7abd617a5c8691f0`, Observation `ef6321d2bab43b883238cdcf0ce33c08321d595c`. |

### `WorldStorage` and aggregate checkpoint source row disposition (Lab #319)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/world/persistence.py` is blob `0871079c908d2efb0329c3f0571a1d22671f12d7` (path commit `f7407d9b320caea839c637a8bb98324813584423`, 32,600 bytes). The inventory symbols were verified: `PERSISTENCE_SCHEMA_VERSION`, `_restore_rng_state`, `PersistentWorldCheckpoint`, `capture_checkpoint`, `restore_population_from_checkpoint`, and `WorldStorage`. This file crosses distinct state owners; it is not a single TARGET persistence contract:

| Source responsibility | TARGET owner/path reference | Disposition and limit |
| --- | --- | --- |
| Causal cut, commit record and recovery state | World `src/world/durable_runtime.py`, `src/world/manifest.py` | World records opaque checkpoint references and cut status; it does not decode the legacy aggregate payload. This is not the old checkpoint format or general transactional rollback. |
| Durable checkpoint bytes and atomic owner-store publication | World `src/world/owner_checkpoint_store.py` | File-backed owner checkpoint storage exists as a World infrastructure component. It does not establish parity with `WorldStorage` schema, event segmentation, retention, or restore rules. |
| Environment state capture/restoration | Environment `src/environment/restoration.py` and owner checkpoint contracts | Environment retains authority for its own state; historical direct reads of private fields/resource pools are dropped. |
| Organism and embodied state/checkpoint | Organism `src/organism/checkpoint.py`; Embodiment `src/embodiment/checkpoint.py` | Each owner controls its checkpoint schema and validation; no single `PersistentWorldCheckpoint` envelope spans these domains. |
| Legacy `PERSISTENCE_SCHEMA_VERSION`, RNG adapter, aggregate checkpoint/capture/restore functions, and `WorldStorage` interface | No Lab-owned aggregate persistence API | Explicit `DROP` as TARGET implementation/API; no compatibility namespace. |

The pinned source call sites and tests (including `lab/tests/unit/lab/world/test_persistence.py`) establish how the historical monolith was used, not TARGET requirements or validation. The old checkpoint serializes state from private population, Environment, and rig internals; its own checkpoint/replay assertions do not establish current cross-owner durability or equivalence. No checkpoint data is copied or migrated, no experiment runs, and no scientific validity, restore equivalence, crash-consistency, or cut-over claim is made. The canonical inventory row is covered by `tests/unit/test_migration_world_persistence_disposition.py`.

### `PopulationGenesisRuntime` source row disposition (Lab #320)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/world/population.py` is blob `bcb046937b036fad9264599a7832afd95e810d29` (path commit `0550aede453d213674bfeb916cd6e3975f26aa91`, 59,604 bytes). The inventory symbol list was verified: `founder_placement`, `PopulationTickRecord`, `PopulationGenesisRuntime`. The file is genuinely cross-responsibility, but the historical aggregate is not a TARGET class to preserve:

| Source responsibility | TARGET owner/path reference | Disposition and limit |
| --- | --- | --- |
| Shared world clock/state, founder placement, topology, ecology and causal event ordering | World `src/world/durable_runtime.py`, `src/world/causal_cycle.py`, `src/world/procedural_genesis.py` | Responsibility split to World; no claim that these APIs reproduce the old population runner. |
| Resource pools, fields, local availability and material transfer | Environment `src/environment/resource.py`, `src/environment/dynamic_state.py` | Ownership stays with Environment; old integration and automatic exchange behavior are not transferred. |
| Per-organism transition/construction and cognitive state | Organism `src/organism/transition.py`, `src/organism/checkpoint.py` | Responsibility split only; no TARGET population factory or `_rigs` aggregate is established. |
| Somatic/metabolic state and embodied consequences | Embodiment `src/embodiment/physiology.py`, `src/embodiment/metabolism.py`, `src/embodiment/checkpoint.py` | Owner APIs are references, not a complete behavioral replacement for the legacy composition. |
| Aggregate `PopulationTickRecord`, private rig map, legacy Hex-specific loop and source API | No Lab-owned population runtime/path | Explicit `DROP` as source implementation/API; no compatibility path. |

The source combines these responsibilities in `PopulationGenesisRuntime`, including private `_rigs` storage and source-specific ordering. `founder_placement` and `PopulationTickRecord` are likewise source helper/aggregate records; naming World paths above does not assert equivalent placement guarantees or record contracts. Historical callers/tests are evidence of source use only. Source remains read-only; no experiment, scientific result, method equivalence, or target completeness is inferred. The canonical row is in `migration/source-inventory-80d372a.tsv` and is covered by `tests/unit/test_migration_world_population_disposition.py`.

### `WorldRuntimeState` source row disposition (Lab #321)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/world/runtime.py` is blob `de62c2b2e56cb5c6a08fb431441ff3ecb8db9844` (path commit `17f56e5fa85dfdfd7c033bca18d073bcc9f1795f`). The class is a composite source implementation, not a Lab TARGET runtime. Its responsibilities divide by authority, but its implementation and API are dropped:

| Source responsibility | TARGET owner / evidence | Disposition and limit |
| --- | --- | --- |
| Causal progression, tick serialization and commit | World `src/world/runtime.py`, `src/world/durable_runtime.py`; World owns causal commit. | `SPLIT` responsibility; source thread loop and runtime API `DROP`. No source-vs-target behavioral equivalence is claimed. |
| Environment and body state creation/adoption through the legacy population | Environment and Embodiment owner contracts; source runtime directly builds/uses legacy `PopulationGenesisRuntime`. | `SPLIT` responsibility; old genesis/population composition and its assumptions `DROP` as a TARGET implementation. Owner modules retain authority; no Lab copy or default is carried forward. |
| Periodic `WorldStorage` checkpoint and host-time tick delay | World durable runtime has a separately owned checkpoint/commit boundary; host-time pacing is not causal progression. | Source scheduling, storage integration, and `tick_delay_s` semantics `DROP`; no compatibility or equivalence claim. |
| Resource observations and rendered snapshot/event/metric payloads | Observation publication is passive and requires its own authorized owner/cut contract; World owns commit. | Source direct publication adapter, private-population metrics, history accumulator and presentation payload `DROP`. No Lab TARGET consumer/path for this class was found. |

Pinned source caller: `lab/src/lab/cli/world.py`; source tests: `lab/tests/unit/observatory/test_world_integration.py`. These are historical consumer evidence, not TARGET requirements or validation. The source class also accesses private `population._rigs`, runs a daemon thread and uses host `time.sleep`; these details are not transferred. No experiment is executed, no source material is removed, and no scientific result or efficacy is inferred. The canonical row is in `migration/source-inventory-80d372a.tsv` and is covered by `tests/unit/test_migration_world_runtime_disposition.py`.

### Historical integrated World tick transaction (Lab #322)

| Source path | Disposition | Target owner/path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/world/transaction.py`: `IntegratedWorldTickTransaction` | REWRITE the causal-coordination responsibility; DROP the historical in-memory rollback implementation | World: `src/world/durable_runtime.py` and `src/world/causal_cycle.py` | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`; blob `0229a2b970246163e3ead08b5a8026ffd2066dc7`. The class snapshots mutable `WorldState`, `WorldEnvironment`, private Lab `_OrganismRig` values, deferred effects and staged events, then restores copies when its context exits with an exception. It is an in-process aggregate rollback helper, not a durable cross-owner transaction. The independently implemented World TARGET owns the causal commit/recovery boundary: it coordinates owner checkpoint references, durable cut publication and explicit recovery; callback/owner failure may require `RECOVERY_REQUIRED` and does not promise arbitrary in-memory rollback. World `MIGRATION.md` at `1f35e92611ed76f1863136916601f07fc2fd78c1` records the same source row and boundary. The pinned source regression suite is `lab/tests/unit/lab/world/test_transaction_integrity.py` (blob `04c54e80fbcd846573fdabb334d52fb77cd64999`); those assertions establish only its local rollback behavior, not durable recovery, crash consistency, multi-process guarantees, or semantic equivalence. Current World cycle restore/continuation coverage includes `tests/integration/test_end_to_end_causal_cycle_acceptance.py::test_committed_cycle_restores_and_continues_in_fresh_process`. No source code/test is copied, no old API or compatibility path is retained, and no claim of rollback equivalence is made. Any requirement for broader atomic rollback must be separately specified against owner authority and recovery contracts. |

### Historical canonical Organism factory and restore adapter

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/integration/organism/canonical.py` | DROP as TARGET code | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `9b2e8ee25199a9b1a69cb822c695257d1fbf9b2c` (5,110 bytes). The listed symbols form one historical application factory/restore adapter: it constructs legacy `symbiont.api.OrganismRuntime` instances, resolves source sense requirements, adapts `modality.host.*` providers to `symbiont.host.HostSenseSources`, and invokes legacy checkpoint/resident restore APIs. The exact composition is bound to removed source APIs and has no authorized Biopeia destination; it is not a separable implementation of World, Environment, Embodiment, Modality or Organism authority. The accepted Biopeia scalar-field sensing path is independently implemented through current owner contracts and is not claimed to replace host telemetry. Exclude this source implementation and do not retain its namespace/API; any future application composition must be newly authored against TARGET boundaries. This makes no claim that historical concepts are scientifically invalid or that future host sensing is unnecessary. Sibling rows, protocols, studies and evidence are not dispositioned here; pinned source remains read-only. |

### Historical evaluation package re-export

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/evaluation/__init__.py` | DROP as TARGET code | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `2ee39fcc87b2a48b2d1a5ca183c0369c4bc688b1`. The file only re-exports `DevelopmentPhase`, `FrozenEvaluationPhase`, and `SeedLedger` from the historical `holdout` module. No target consumer or approved Biopeia package API requires this historical namespace. Drop the wrapper rather than preserve import compatibility; this does not determine the disposition of the underlying holdout methods or scientific protocols. |

This is a file-level disposition of a package re-export only. Its disposition
does not itself classify `holdout.py`; the underlying historical module is
separately dispositioned below. Neither row transfers evaluation authority to
Organism or makes a scientific validity or method-equivalence claim. The
historical source remains read-only and preserved.

### Historical evaluation holdout guard

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/evaluation/holdout.py` | DROP as TARGET implementation | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `b9f230fb6ff5b3b33e99cd5be21c6a730d45d85d` (5,018 bytes). The module implements persisted seed-separation enforcement for the historical `predictive_discovery` study. Tracked Lab TARGET source at `34f7dd4504f425c6a262954aae7ee641b795a825` has no implementation/consumer for this source-specific API. Exclude the historical implementation and do not preserve its import/API. This does not disposition the study protocol/results, claim the guardrail is scientifically unnecessary, or preclude newly specified holdout controls for future Biopeia studies. Source and provenance remain preserved read-only. |

This disposition concerns the source implementation only. Any scientific question,
protocol, or result that uses a development/evaluation split remains subject to
its own Lab custody and scientific review.

### Historical advisory-evaluation utility

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/evaluation/advisory_evaluation.py` | DROP as TARGET code | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `e2d11c6420ea03b86f4de2fb072342d0fd94d864` (7,457 bytes). The cohesive module stores and summarizes operator judgments of advisories emitted by the historical Organism host advisory runtime. That producer/runtime is excluded from Biopeia TARGET (Organism `main` at `26778028c4058d96ba2f2b77199df7852a03def1`); tracked-source searches found no consumer in Lab `main` at `8febcad282e9c0ed0340dc255ae1c85b7cdd8992` or Organism `main`. Drop the source-specific implementation; do not retain an interface or create a replacement as part of this disposition. This says nothing about scientific validity or usefulness of the historical judgments. A future capability requires a newly specified TARGET source and workflow. The pinned source remains preserved read-only. |

This resolves only this source module. It does not disposition its source tests as scientific evidence, authorize an operator study, or make any claim about the historical advisory mechanism.

The source test file `lab/tests/unit/lab/physics3d/test_contract.py` is `DROP` as a whole from TARGET tests/code: its 52 test functions exercise historical implementation and do not constitute scientific result records or an independent scientific oracle. Its exact source commit/blob remain recorded in the inventory; this is not deletion of historical source or a claim that the tested concepts are scientifically invalid.

The file-level classifications are intentionally conservative. Four registered
study implementation rows are now `DROP` under their separately documented
unit dispositions; their protocols are retained as `HISTORICAL_PROTOCOL` in the
study disposition register. The file-level inventory and unit register are kept
consistent without claiming scientific validation or method equivalence. A `SPLIT` row
does not assert that a particular source symbol is worth preserving. A `DROP`
row means “do not migrate this source artifact or its legacy interface”; the
historical source copy remains untouched. A `DEFER` row is explicit migration
debt and cannot be counted as completed inventory.

### Historical evolution archive-evaluation module

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/evolution/evaluation.py` | DROP as TARGET code | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `749b84d3b66da594464a8dc6cd2d21da3460e86c` (1,279 bytes). The file defines `EvaluationResult` and `select_archive`; the latter selects a Pareto front using the historical Symbiont `LearningObjective`. At the pinned source, repository-wide references are limited to this definition, the package re-export and unit tests; there is no production caller. Biopeia Organism main `022afcc9dad0d4edbafd70440afb712f5bee7bfc` contains `LearningObjective`/`dominates` but no consumer of these symbols, and Lab main `4151e2fa5ec9835f02b43e25bcc789274ed56713` has no target evolution package or consumer. No currently authorized TARGET study/method requires this specific implementation, so it is excluded as migration input rather than assigned by historical package location. This code disposition does not assess scientific validity, utility or equivalence, and does not preclude a newly specified future Lab method. The pinned source remains read-only; its source tests are not migrated. |

This is a disposition of the source artifact only. It does not classify any scientific protocol or result that may have used related concepts, and it creates no TARGET implementation or compatibility surface.

### Historical evolution package re-export

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/evolution/__init__.py` | DROP as TARGET code | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `fd96fd72dd947913e2bc183c36b53c343cccae7f` (1,105 bytes). This file is a package-level convenience facade re-exporting lineage, mutation, recombination and reproduction symbols. Its docstring identifies the broader package as Lab scientific apparatus and distinguishes it from Organism reproduction. At candidate base `a8293ed7bf0af417a4c8fbf537f31772c7c2dcfa`, Biopeia Lab has no `src/lab/evolution/` TARGET package or production consumer. Drop only the legacy re-export facade; do not preserve import compatibility. This does not classify sibling implementation rows, declare the broader apparatus scientifically invalid/unnecessary, transfer ownership to Organism or preclude a newly specified future Lab method. The source remains read-only. |

This disposition covers only the initializer/facade. `evaluation.py`, `lineage.py`, `mutation.py`, `recombination.py`, and `reproduction.py` remain separate inventory rows and are not resolved by this change.

### Historical Organism host adapter

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/integration/organism/host_sources.py` | DROP as TARGET code | No TARGET implementation path | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `1ed9fb9bdb1325ffe219416ce473eaf2f9a13bf6` (2,868 bytes). `HostSource` adapts historical modality host discovery, readings and tick-observer protocols into legacy Organism records; it owns no authoritative state and is not a multi-owner composition. No authorized TARGET consumer for this historical adapter has been identified within the approved sensing path, and no compatibility code is authorized. This disposition covers only this file, not sibling modules or scientific records, and makes no claim about future integration needs or scientific validity. Historical source remains read-only. |

### Historical local host composition

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/integration/organism/local_host.py` | DROP as TARGET code | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; source-path commit `7a63ec3ce140514e085789f498e7c73a72eca3fc`; blob `c5841f9a91c42e4dd2ba702aa79371497f35eab0` (6,386 bytes; SHA-256 `4eacc161e68fb5b6a82c0d28d64d71984e84d8e63dea942727627a0c79a4ef99`). The convenience functions compose historical `modality.host` providers with `symbiont.host` discovery, sampling, perception, acclimation, lifecycle, rhythm, drift and second-look APIs; this is not a TARGET-owned contract or implementation. Current Biopeia TARGET source/tests have no consumer for these functions, and the accepted scalar-field sensing route is implemented separately. Exclude this source implementation/API and do not retain its namespace for compatibility. This is not a scientific-validity or permanent-capability claim and does not disposition related protocols/results. Source remains read-only. |

### Historical integrated-habitat package re-export

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/integration/__init__.py` | DROP as TARGET code | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `b19fae9ef159d30e7d3d7e614c804a986284c97f` (311 bytes). This initializer only re-exports `IntegratedHabitatConfig`, `IntegratedHabitatRuntime`, and `IntegratedTickSummary` from the separately inventoried historical `integrated_habitat.py` module. Lab main `a392a24f6767b711449df147ec328a77a5a0d35e` has no `src/lab/integration/` package or consumer for this facade. Drop the legacy package-level API rather than retain a compatibility namespace. This facade-only record does not itself disposition the implementation module or its historical study/protocol/results; the implementation module has its own record below. It does not transfer causal runtime ownership to Lab. The source remains read-only. |

### Historical integrated-habitat runtime

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/integration/integrated_habitat.py` | DROP as TARGET code | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `20b8de5348f05930cffc583efced5d72a3105ac7` (19,401 bytes). `IntegratedHabitatConfig`, `IntegratedTickSummary`, and `IntegratedHabitatRuntime` form one historical population-runtime implementation: configuration and summaries are local to that runtime, while execution directly composes legacy Symbiont Organism cognition, physiology, social habitat, reproduction, host lifecycle, communication, and checkpoint APIs. No separable TARGET responsibility in this file is retained; causal composition belongs to current domain-owned TARGET paths, not a Lab compatibility runtime. Lab main `39ea00694bba11e59f22fe50a8daf20521363cfc` contains no integration package or consumer for these symbols. Exclude this source-specific runtime as TARGET code; do not copy its implementation or source-coupled tests or preserve its namespace. The historical study/protocol/results and source artifacts are separate inventory/custody rows and are not dispositioned here. This makes no scientific-validity, method-equivalence, capability-unnecessity, or evidence-admission claim; the pinned source remains read-only. |
| `lab/src/lab/experience/__init__.py` | DROP as TARGET code | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `52329f0b9a413d88b1ec679be99d01708dcd7c41` (723 bytes). The initializer only re-exports run ontology and safety symbols from the separately inventoried `definition.py` and `safety.py`. Lab main `3ec119d28c054daa01fbd48f2e951a3c4d40033e` has no `src/lab/experience/` package or TARGET consumer. Drop only this historical package-level import facade rather than preserve import compatibility. This does not disposition the underlying modules or any study/protocol/results, transfer Organism authority to Lab, or claim the historical concepts are unnecessary. The source remains read-only. |
| `lab/src/lab/integration/organism/__init__.py` | DROP as TARGET code | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; blob `c6539413d645b0900d620a2835643d25966a5cac` (816 bytes). The initializer only re-exports canonical Organism composition/restore functions from separately inventoried `canonical.py`. Lab main `3a69a6021e6328b19b4c7347ef2f822fb1fb84de` has no target package or consumer for the old facade. Drop only the historical package-level import surface; do not preserve compatibility. This does not disposition `canonical.py`, transfer Organism/World authority to Lab, or claim the historical composition concepts are unnecessary. Source remains read-only. |

These rows concern only historical package initializers that re-export other
modules. Their underlying implementations, studies, protocols, and results remain
separately inventoried; dropping a facade is not a claim that historical work is
invalid or that any capability should be copied into Lab.

### Lab tests and scientific assets

All 297 pinned source test-tree files have a row. The current target test
coverage is selective: three focused utility test files are `MOVE`, one mixed
physics contract test file is `SPLIT` because it contains assertion groups with
distinct dispositions; its five interoception assertions are explicitly `DROP`
as TARGET tests in the bounded record above, and 293 files are `DROP` from the
Biopeia TARGET test/code plan (217 previously classified source-coupled files
plus 76 science/protocol/integrity-oriented source test files). The 76 are not
carried forward as compatibility tests. This code disposition does not delete source
history or automatically admit test code, assertions, fixtures or outputs as
scientific evidence. Lab, as designated scientific custodian, may separately
identify and admit evidence with its own provenance and admissibility record.

The machine-readable custody register is
[`migration/scientific-custody-80d372a.tsv`](migration/scientific-custody-80d372a.tsv).
It accounts for all 364 tracked files under `lab/experiments/`, all 112 under
`lab/research/`, and the historical replay example. Each row pins the source
repository revision, path, Git blob, byte count, and SHA-256 of the bytes at the
pinned revision. The separate `proposed_review_class`, `proposal_source_map`, and
`proposal_review_status` columns reconcile the six content-reviewed maps, while
leaving the authoritative `custody_classification` unchanged pending Lab owner
disposition. Proposal classes are not evidence admission, scientific validation,
or authority to transfer/delete. `DEFER` in the authoritative field means the
artifact remains preserved at source without a final owner custody class; it does
not mean discard. See the
[custody reconciliation](migration/custody-reconciliation-80d372a.md) for exact
scope, counts, limitations, and identity checks. No artifact bytes were copied,
regenerated, republished, or deleted by this update.

This bounded slice classifies only the historical v0.24 audit packet at
`lab/research/audits/historical/v024/`:

| Source item(s) | Custody classification | Basis and limits |
| --- | --- | --- |
| `PROTOCOL.md` | `PROTOCOL` | Dated protocol identifies Symbiont v0.24.0 and frozen engine commit `a352c93d889aa901e53903bae844b894d78adeb6`, specifies seeds/configuration and reproduction steps, and records interpretation limits. It is historical, not a Biopeia TARGET protocol. |
| `baseline.json`, `causal.json`, `causal_validation.json` | `SCIENTIFIC_EVIDENCE` | Immutable source-pinned data artifacts linked to the adjacent protocol; the JSON content exposes per-seed results or explicit seeds/configuration. This is custody classification only, not scientific validation, reproduction, acceptance of a conclusion, or TARGET applicability. |
| `ANALYSIS.md` | `HISTORICAL_RECORD` | Preserves the contemporaneous report and caveats; does not independently validate or endorse its conclusions. |
| `diagnostics.json`, `tests.txt` | `HISTORICAL_RECORD` | Preserves historical diagnostic/test output. These are not standalone scientific results; `tests.txt` is software-test evidence only. |

For the classified data records, no unique structured `run_id` is asserted;
linkage is to the adjacent historical protocol and the seed/configuration
information actually present. The protocol/report state the important limits,
including exploratory scope and known methodological/implementation caveats.
The protocol and analysis document authors are not identified in their source
content. The protocol names historical runner/diagnostic scripts, but those
scripts are not files at the pinned repository revision and it does not map
every output to a unique executable. The register records this limitation
instead of attributing the documents to the scripts or claiming per-output
executable hashes.
No scientific claim is made here. Lab is the designated custodian and the
source files remain the immutable originals; any later storage relocation must
preserve their identity, provenance, and hashes. The other 470 entries,
including all `lab/experiments/**`, the other 105 research artifacts and the
replay example, remain explicitly `DEFER` because this slice did not establish
their item-specific evidence/protocol provenance sufficiently for a defensible
classification. Their preservation at source continues; no deletion is
authorized. Every deferred item must be revisited before Lab migration can be
declared complete.

### Remaining closure work

The manifest establishes path/blob completeness at one pinned source tree, but
it is not a source consumer graph: references between individual symbols,
tests, protocols, runtime entry points, external users, and persisted records
have not all been resolved. Nor does path/blob coverage show that a study can be
reproduced or that a target replacement is scientifically admissible. Before
Lab migration can be declared complete, every `DEFER` must be revisited, every
`SPLIT` must receive a justified owner/path or a final `DROP`, scientific assets
must have an approved custody disposition without loss of provenance, and
external users/consumers must be accounted for. This accounting change alone
does not meet those conditions.

### Historical source-audit reconciliations

[`BAW-001 — EV-0356–EV-0361 and ADR tension reconciliation`](migration/baw-001-source-audit-reconciliation.md)
records the bounded Biopeia-side disposition of one sealed historical audit
dossier. It is a provenance/review record, not a new scientific-evidence item,
evidence admission, or rewrite of the source register. The source dossier
remains read-only and is identified by its pinned audit base and SHA-256 in the
record; no source bytes are copied into this repository.

## Integration test moved from the integration workspace

`tests/integration/test_operator_material_transfer.py` was copied unchanged from the unversioned local integration workspace by Architecture Owner decision of 2026-10-09. It imports Lab, so it belongs here and not with World: World must not depend on Lab. It is a new Biopeia test; no path of the historical source repository corresponds to it.

Verified on 2026-10-09 against the then-pinned revisions in the `integration` extra: `tests/integration` 9 passed. This is historical evidence; current validation is recorded below.

**Finding, not fixed here.** Against the `main` branches of the other repositories on the same day the integration suite does not pass: 7 of the 8 existing integration tests and this one fail with `ManifestError: initial causal cut checkpoint dependency closure is not verified`. Substituting one repository at a time isolates the cause to Environment: with World and Embodiment at `main` and Environment at the pinned `c14814a` the suite passes; with Environment at `main` (`f2ef8c2`) it fails. The pins were not moved. Default CI runs only the isolated unit suite, so it does not show this.


**Resolved later the same day.** The cause was Environment's change of its finite-resource checkpoint contract in `f2ef8c2` ("Define target-owned finite resource checkpoint contract"), the first Environment commit after the old pin with which the suite failed. Lab was aligned to that contract and its Environment pin moved to `f2ef8c2` in `e93401d` ("Record Lab custody and align Environment checkpoint schema"). With Lab at `3b84a25` and the revisions pinned in its `integration` extra, `tests/integration` passes: 10 passed. The finding above is kept as the record of what was observed before that change.

### Embodiment physiology-complete checkpoint consumer

Lab now requires Embodiment owner schema `embodiment-checkpoint-v2` for material-transfer checkpoint validation. Its integration dependency is pinned to the explicit Biopeia Embodiment revision that introduces this format; no v1 fallback is accepted. This is a consumer-contract update only: Lab does not interpret or own Embodiment physiology state. The change does not claim complete material-transfer durability or scientific equivalence.

### Historical PhysicsWorldObserver adapter disposition (Lab #316)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/physics3d/world_observation.py` is blob `76b380080757ad1a9819b5eb2664539d3febe818` (6,325 bytes; content SHA-256 `c552e7ab0cb0d9aae13356009c9139e9e1204202d963b4bb6ea9c68bcfbbd40a`; path commit `40adf60c42322c06b225e9169dbb77b126c04257`). The file defines only `PhysicsWorldObserver`. Its `capture` method reads private MuJoCo scene/runtime/apparatus state and builds one transient dictionary containing external entity geometry/material/field, receptor descriptors, contacts, environment recipe and observer provenance. Although the output spans multiple owner concerns, this is one cross-owner adapter, not a set of portable owner contracts.

**Disposition: DROP as TARGET code; no Lab target destination.** The current owner boundaries are independently authored and are not migration destinations or equivalence claims: Environment physical state (`environment/src/environment/static_scene.py`, `dynamic_state.py`), Embodiment receptor sampling (`embodiment/src/embodiment/physics3d/receptor.py`), and World causal composition/publication (`world/src/world/causal_cycle.py`, `observation_publication.py`). The historical source runtime consumer is `runtime.passive_world_observation`; source tests are `test_physics_world_observer.py` and `test_world_environments.py`. These establish only source use and local assertions, not scientific validity or TARGET behavior. The pinned source remains read-only; no implementation, compatibility surface, or experimental result is transferred. This disposition does not rule out a separately designed TARGET physical-observation composition. The exact row is recorded in `migration/source-inventory-80d372a.tsv`.

### Historical Physics3D package facade

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/physics3d/__init__.py` | DROP as TARGET code | No TARGET Lab package or consumer | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`, blob `18a8d568dfb995653b5d6e838b62591889412e6a` (259 bytes), content SHA-256 `b5aab993112c2c867257104d6e7dd4a3a83c8b2537637b361685c1f787b58982`. The source digest was verified from the read-only checkout. This file contains only a docstring and re-exports `HumanoidPhysics`, `Physics3DEmbodimentRuntime`, and `Tick3D`; it does not define independent behavior. Drop only the historical package facade. Separately inventoried runtime and owner responsibilities remain independent and are not disposed here. No historical import namespace is retained for compatibility. This makes no claim about scientific validity or future physical-simulation needs; historical source remains read-only. |

### Historical Physics3D telemetry package facade

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/physics3d/telemetry/__init__.py` | DROP as TARGET code | No TARGET code destination | Pinned source SHA `80d372a186513035f85a769db886e505cabba52d`, blob `d947446f8caf7b9c0a39bb91b61de8161b587dd7` (530 bytes), content SHA-256 `446644aaf51d1fde398269751e78a7d51d8a060a4fd38ae4dd3d41636cdccc58`. The source digest was verified from the read-only checkout. This file contains a package docstring and re-exports from separately inventoried `reader.py` and `v41.py`; it defines no independent behavior. Biopeia Lab TARGET main at `f3d5283302b4b71222820254fbecfc3f754d9fad` has no `physics3d/telemetry` package or tracked source/test consumer. Drop only this historical package facade; all sibling telemetry modules remain separate inventory rows and are not classified here. This is a TARGET migration disposition, not a scientific-validity claim or a decision that future telemetry capability is unnecessary. No historical import namespace is retained for compatibility; historical source remains read-only. |

### Historical Lab Physics3D body registry and vision composition

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/integration/physics3d/bodies.py` | DROP as TARGET code | No TARGET code destination | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`; blob `e7753adda5aeb2c302f7477f882af39c9cdbaba9` (1,201 bytes); symbols `ANTHROPOMORPHIC_V6_VISION`, `DEFAULT_BODY_REGISTRY`. The file composes Embodiment body presets and `VisionHumanoidPhysics` with Modality `VisualApparatus` into a Lab-owned historical registry. No approved current TARGET consumer or Lab-owned use for this catalog/composition is established. Drop this historical implementation and its old names/API; do not retain compatibility. This does not claim Biopeia has no future need for a body catalog, vision apparatus or study configuration. Any such capability must be newly specified for a concrete TARGET consumer under current owner contracts. The historical source remains read-only. This is a migration disposition only, not a scientific-validity or permanent capability-necessity claim. |

### Historical positional actuator-to-effector mapping

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/integration/physics3d/apparatus.py::actuator_to_effector_map` | DROP as TARGET implementation | No TARGET path | Source repository `alessbarb/symbiont-lab`, pinned source SHA `80d372a186513035f85a769db886e505cabba52d`, blob `8de1f29fe87321fcab0cb051e79fadcf0f833cd6`. The historical function pairs actuator and effector IDs by list index. TARGET requires stable identity and forbids collection order as authoritative correspondence. DROP applies only to the exact historical function. The separate Embodiment TARGET binding is revision-bound and records explicit actuator_id→effector_id identity at `biopeia/embodiment@56e9a34a6a778a298493dabca9d15b0912066803`, `src/embodiment/physics3d/actuator_binding.py`; this is not a migration/adaptation of the historical function. No compatibility adapter is authorized, and sibling symbols in this mixed source file remain independently unresolved. |

The source repository remains read-only. The mixed `apparatus.py` row remains `SPLIT` while its other symbols are reviewed independently.

### Historical kernel-characterization run-summary helper

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/kernel_characterization/metrics.py` | DROP as TARGET implementation | No TARGET code destination | Pinned source repository `alessbarb/symbiont-lab` at `80d372a186513035f85a769db886e505cabba52d`; source blob `3a5cd292c22fbfb8f5ec82ef83f267dc585e8e81`, mode `100644`, 1,747 bytes; symbols `_numeric`, `summarize`. The file validates numeric values and aggregates generic run-record counts and fields. At the pinned source revision, the only tracked callers are in `kernel_characterization/runner.py`. Biopeia Lab at `a96bfac3a9fa49ccf60d3d32d58535118b2df703` has no corresponding module or tracked consumer. This is a disposition of the historical implementation from TARGET, not a claim that its method or results are scientifically invalid, or that future Lab analysis is unnecessary. A concrete future consumer requires a new Lab-owned design; no compatibility API is retained. The historical source remains read-only and preserved. |

This record does not transfer or admit any historical study, protocol, result, or
scientific claim. It addresses this source file only; neighboring
kernel-characterization modules remain independently dispositioned.

### Historical kernel-characterization Pareto helper

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/kernel_characterization/pareto.py` | DROP as TARGET implementation | No TARGET code destination | Pinned source repository `alessbarb/symbiont-lab` at `80d372a186513035f85a769db886e505cabba52d`; source blob `e1dd23edf35487cf59df5642a549742387f80421`, mode `100644`, 1,365 bytes; symbols `_numeric`, `pareto_frontier`. The helper filters rows marked failed and computes a two-objective non-dominated set over a caller-selected benefit and cost, then sorts by `max_nodes`. At the pinned source revision its tracked call sites are in `kernel_characterization/runner.py`. Biopeia Lab has no corresponding TARGET implementation or tracked consumer. DROP applies to this historical helper as migration input; it does not claim the algorithm or any historical result is scientifically invalid, nor that future Lab analysis is unnecessary. A concrete future use requires a new Lab-owned design; no compatibility API is retained. Historical source remains read-only and preserved. |

This classification is not a review or admission of the studies/results whose rows may have been summarized by the historical runner.


### Historical Observatory architecture inventory

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/ARCHITECTURE.md` | DROP as TARGET documentation | No TARGET document destination | Pinned source commit `80d372a186513035f85a769db886e505cabba52d`; source blob `38def6dbfef9e01d6352d17c4d87ce6facbd7aaf`, mode `100644`, 3,759 bytes. This document inventories the historical Symbiont Observatory implementation and its old browser/server/launcher topology. It is not a scientific protocol, result, or evidence artifact and is not adopted as a TARGET design authority. The TARGET authority boundary is instead defined by Biopeia Docs at `ffe1503985bc815861d78efc5aa13b7e54928e01`, `technical/design/observability/observation-semantic-model-v1.md` and `technical/adr/ADR-0078-observation-is-causally-passive.md`; neither specifies or adopts the historical Observatory implementation topology. No portion of this historical inventory is required as a TARGET document. DROP applies only to migration into TARGET. The pinned historical source remains read-only and preserved; this does not claim that future visualization or Observation documentation is unnecessary. |

### Historical Observatory user and operator README

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/README.md` | DROP as TARGET documentation | No TARGET document destination | Pinned source commit `80d372a186513035f85a769db886e505cabba52d`; source blob `f4e3c4710ac5bc14f612c82a1c7ade809df8ee3c`, mode `100644`, 20,019 bytes. The README documents the historical Symbiont Observatory UI, launcher commands, local transports/replay, versioned snapshot schemas, and runtime-specific display projections. It is operational/product documentation, not a scientific protocol, result, or evidence artifact. Its routes, commands, schema versions, labels and display semantics are not Biopeia TARGET contracts and are not to be copied by analogy. The historical source remains read-only and preserved. This is only a migration disposition for this README; it does not claim that future Biopeia visualization, Observation publication, Lab tooling, or scientific value is unnecessary. |


### Observatory instance registry schema (Lab #266)

At source baseline `80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observatory/schemas/instance.schema.json` is blob `7a2d29bb3dc576c2b984d85bbcfc8746fc7adb44` (946 bytes). It describes instance/run/process/display identity, start and heartbeat timestamps, topology revision, and organism identity. The source inventory records this row as `DEFER`, not `SPLIT`: the `Observation / Lab` hint does not establish a competent TARGET owner, contract, or path. Observation #38 remains open with design/owner decisions unresolved.

Re-evaluate when Observation #38 and the competent Observation/Lab owners record whether this record has a TARGET responsibility and its owner/path, or explicitly determine DROP. Until then, preserve provenance and do not copy a schema or infer scientific validity/equivalence. This bounded ledger defer does not block the bounded runtime-transfer profile, but remains open and prevents declaring Lab #78/#45 source-disposition work complete. The sibling path alias remains separately deferred under the linked #255/#266 record.


### Observatory body-schema alias (Lab #251; underlying schema tracked by #264)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observatory/body_schema.schema.json` is a 31-byte symlink (blob `a8aac03965d0416b6e8849db4c582638cbfe6c2f`, mode `120000`) to `schemas/body_schema.schema.json`. Its target is schema blob `4f393ed9161c3ba8e9672dc78edbb1bef9cd516d`; the substantive schema is separately inventoried and reviewed in open Lab #264. The schema describes bounded organism-owned self-knowledge but provides no evidence of a target owner-authored schema or contract path.

The alias is `DEFER`, not an independent `SPLIT` or final `DROP`: the underlying schema decision belongs with the competent Organism/Observation owners and is linked through #264. Closure trigger: #264 records an owner-authored target owner/path or explicit `DROP`, then reconcile this duplicate historical alias. This bounded defer does not block runtime transfer. The pinned source remains read-only; no scientific validity, equivalence, or evidence-admission claim is made.


### Observatory cognition-state schema alias (Lab #252; underlying schema tracked by #265)

At pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observatory/cognition_state.schema.json` is a 35-byte symlink (blob `b22e40673ee98ac2d9c12039b685cc2aeb5ca16e`, mode `120000`) to `schemas/cognition_state.schema.json`. The target schema is blob `4a64ef2467617deb58e466602319c0cc5939cb71`, separately inventoried and under review in open Lab #265. It describes per-tick cognition telemetry including evidence-gated stranded-concept and shadow-prediction metrics, explicitly not raw weights. Its historical description does not create a TARGET contract or identify a competent owner/path.

The alias is `DEFER`, linked to #265, until the competent Organism/Observation owners disposition the underlying schema and its TARGET responsibility or explicitly DROP it. Closure trigger: record the schema owner/path or explicit DROP, then reconcile the alias. This bounded defer does not block runtime transfer. Source remains read-only; no scientific validity, equivalence, or evidence-admission claim is made.







### Historical Observatory publisher disposition (Lab #259)

Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observatory/publisher.py`, blob `16860fd39c55472f7b6f8f8df26a170ca1e91f4f` (mode `100644`, 2,100 bytes). Verified symbols: `Sink;StdoutSink;JournalSink;ReplayRecorder;SnapshotPublisher`. It fans legacy Observatory envelopes to stdout/journal and buffers snapshots for whole-file replay export through the legacy adapter. Current World publishes owner-authorized semantic observations after causal commit into Observation; this is a different contract, not evidence of replacement/equivalence. With no authorized TARGET legacy-envelope sink/replay contract or consumer identified, this pinned fan-out is `DROP` from migration input. Journal data custody remains a separate unresolved question under Lab #256. This does not claim future human transports/replay are unnecessary; no source/runtime behavior, scientific validity, equivalence, or admission is inferred.

### Historical Observatory observer-provenance translator disposition (Lab #258)

Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observatory/provenance.py`, blob `d928fa835da90a21d06c02976794b3b3396bccc7` (mode `100644`, 5,400 bytes). Verified symbols: `_descriptor;build_observer_provenance`. It maps opaque runtime capability readings into bounded human-observer rows (signal ID, label/category, scaled value/unit, quality); its source docstring explicitly states those labels do not enter the tick result, checkpoint state, cognition or learning. No TARGET descriptor schema, owner-authored contract, consumer or path was identified. The pinned apparatus translator is `DROP` from migration input. This does not assert future human observability is unnecessary or validate the labels as scientific constructs; any future viewer requires a target-authored contract and review by owners of the underlying fields. No scientific validity/equivalence/admission is inferred and the historical source remains read-only.

### Historical Observatory capture-manifest disposition (Lab #257)

Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observatory/manifest.py`, blob `e002f1a246b40317d9feea99083666b1e85fe143` (mode `100644`, 6,374 bytes; SHA-256 `0e26e07b05736f63e847865b66c82a8c251c8717920bffcf712b9f7f164105cc`). Verified symbols: `_file_sha256;_git_commit_sha;CaptureManifest;create_capture_manifest;write_capture_manifest;verify_capture_manifest`. It hashes checkpoint/topology files and records identity/run/sequence/tick/revision/config/timestamp/consistency metadata in an atomically written manifest. No authorized TARGET capture schema, field authority, custody/retention policy or path was identified. `DEFER` pending Lab owner decision on custody/admissibility/retention and competent Organism/World field authority; Observation must define any passive projection boundary. Linked but distinct unresolved custody work: Lab #242 and #256. Closure requires explicit owner-authorized `DROP` or a target-authored contract naming field authority, schema/version, consistency semantics, custody/retention and storage path. This is outside the bounded runtime-transfer profile; no artifact/source is copied or deleted and no scientific validity/equivalence/admission is inferred.

### Historical Observatory manifest-test disposition (Lab #281)

Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observatory/tests/test_manifest.py`, blob `22763bb6941654000d1bc7cf0941a6f7c71d5736` (mode `100644`, 8,115 bytes); verified class `ManifestTests`. Three tests exercise legacy capture-manifest writing and detection of checkpoint/topology digest mismatches; one checks a legacy heartbeat record against the historical instance schema; one checks the legacy canonical-organism adapter's identity/config/checkpoint round-trip. The manifest checks remain unresolved under #257 because no authorized TARGET capture-manifest contract, field authority, custody/retention policy or path exists. The heartbeat/schema check remains unresolved under #260, Observation #38 and Lab #266 because no TARGET instance registry/heartbeat contract/path is authorized. The adapter round-trip test covers only the legacy composition adapter already dispositioned `DROP`, not a TARGET Organism contract, and is not an independent retained TARGET responsibility. The file therefore does not establish a concrete split among TARGET owners; bounded `DEFER` is more accurate while the manifest and registry contracts remain undecided. Lab is accountable for evidence custody/admissibility/retention, domain owners for their represented fields, and Observation for any passive projection boundary. Closure trigger: competent owners record explicit `DROP` for these unresolved responsibilities, or author TARGET contracts naming field authority, schema/version, privacy, custody/retention and paths; then reconcile this row and create separately scoped TARGET tests only where justified. This does not block the bounded runtime-transfer profile. No source/state is copied or deleted, and no scientific validity/equivalence/admission or checkpoint compatibility is inferred.

### Historical Observatory journal disposition (Lab #256)

Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observatory/journal.py`, blob `bad69fb063b32a949ae50b765672b69f8f61dffa` (mode `100644`, 3,957 bytes); verified symbol `Journal`. It appends per-run snapshot envelopes to NDJSON, rotates segments, triggers the derived summary separately dispositioned `DROP` in Lab #254, and gzips closed segments while unlinking the uncompressed paths. `DEFER` pending the Lab owner's explicit decision whether this historical stream is evidence requiring custody/retention or an obsolete Observatory cache, and the Observation owner's boundary decision if semantic projection is proposed. No TARGET journal schema, retention policy, or authorized path exists in the evidence reviewed. Lab #242 is a related but distinct unresolved archive-custody question, not a substitute contract. Closure requires an explicit owner-authorized `DROP` or a target-authored custody/retention contract with schema/path. This defer is outside the bounded runtime-transfer profile; no source/data is copied or deleted and no scientific validity/equivalence/admission is asserted.

### Historical Observatory journal-test disposition (Lab #280)

Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observatory/tests/test_journal.py`, blob `7cddecc56a0dc102c134cb305a61de124826789a` (mode `100644`, 4,562 bytes). Verified class: `JournalTests`. Seven tests characterize per-run sequence/envelope generation, rotation, automatic summary generation, compaction/segment preservation, gzip output, segment naming and the configured size target not deleting segments across runs. These tests concern a single historical Lab journal implementation; they do not split separate Observation and Lab TARGET responsibilities. The implementation remains `DEFER` under Lab #256 because no owner has decided whether the snapshot stream is evidence requiring custody/retention or an obsolete cache, and no TARGET journal schema, integrity/retention policy or authorized path exists. Lab is accountable for custody/admissibility/retention; Observation must decide whether any passive projection responsibility remains. Lab #242 concerns a different provenance journal and is not a substitute decision. This test row therefore remains bounded `DEFER` rather than asserting the legacy tests as TARGET requirements or dropping potentially material retention/custody safeguards. Closure trigger: owner-authorized explicit `DROP` or a target-authored custody/retention contract naming schema, integrity, retention and path, then reconcile this row. The defer does not block the bounded runtime-transfer profile. Historical source remains read-only; no source/data is copied or deleted and no scientific validity/equivalence/admission is asserted.

### Historical Observatory history-summary disposition (Lab #254)

Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observatory/history_summary.py`, blob `6461b3fce7d0f9e3be0381d4e64177331a6af313` (mode `100644`, 2,557 bytes). The recorded symbols `_lines;build_history_summary;write_history_summary` were verified. It reads per-run NDJSON/gzip journal segments, hashes compressed file bytes, counts entries/schema versions/organism-state strings, computes an integer tick range, and writes a derived JSON summary. No current Lab consumer or approved TARGET summary contract/path was identified. Therefore this pinned implementation is `DROP` from migration input, not deletion/disposition of historical records and not a decision that Lab must never build a newly specified evidence index. Any future index requires explicit Lab custody/retention requirements and a target-authored contract. No scientific validity, equivalence, admission, or source deletion is inferred.

### Historical Observatory history-summary test disposition (Lab #279)

Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observatory/tests/test_history_summary.py`, blob `172039a1ab472acd38fc82cbb6822175cf3bbff3` (mode `100644`, 1,217 bytes). Verified symbol: `test_summary_covers_raw_and_compacted_segments_without_replacing_them`. It characterizes the legacy `build_history_summary` helper by asserting a count, tick range, organism-state strings and the presence of raw NDJSON and gzip segment names after reading them. The helper is separately `DROP` under Lab #254 (blob `6461b3fce7d0f9e3be0381d4e64177331a6af313`), with no authorized TARGET consumer or summary contract; this source-only characterization test therefore has no justified TARGET test responsibility and is `DROP` as migration input. This does not dispose of historical journal records, delete or alter the pinned source, assert the derived fields as scientifically meaningful, or decide whether a newly specified Lab evidence index is needed. Any future implementation requires an owner-authored Lab custody/retention contract and separate TARGET tests. No scientific validity/equivalence/admission is inferred.

### Historical Observatory operational configuration (Lab #253)

The pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observatory/config.py` (blob `3400ea0a13552fd3d62cd2bc5178daada89792f8`, mode `100644`, 1,334 bytes), defines the legacy state directory, loopback server host/port, SSE polling, heartbeat/staleness, and limits tied to the historical tick and body schemas. Pinned callers are the old Observatory `server.py` and `adapter.py`; the adapter is separately dispositioned as DROP in Lab #250. The target Observation repository defines passive semantic observation, not an Observatory server, filesystem, streaming, heartbeat, or this schema-bound ingestion API. Lab has no target Observatory runtime consumer.

Disposition: `DROP` as TARGET operational configuration. Do not carry the old values into TARGET by analogy. Any future presentation or transport requirements need an owner-authored contract and independently justified bounds. This does not claim future UI/transport is unnecessary or make scientific validity, equivalence, or evidence-admission claims; historical source remains read-only.

### Historical Observation cadence helper disposition (Lab #232)

| Source path | Disposition | Current target responsibility references | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observation/cadence.py` | DROP as a historical Lab runtime scheduling helper; no target cadence scheduler is authorized | No target counterpart. World owns causal-cycle stepping and Embodiment owns physical transitions, but neither currently defines a cross-domain execution-rate policy. | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob `d1b3d23389c659142570b1360b89301be61786a0` (2,133 bytes), symbol `ExecutionRates`. It validates physics/cognition rates and computes substeps plus observation/render sampling cadence. In the pinned source, only `lab/src/lab/app/physics3d/runs.py` and `lab/src/lab/physics3d/engine.py` consume it; its unit test is source characterization, not target evidence. No target package currently implements or imports this policy. A future cadence need would require a separate design defining clock authority and cross-domain coupling. This disposition is not a scientific conclusion, a ban on future functionality, or deletion of protected historical source. |

### Historical Observation frame contract disposition (Lab #233)

| Source path | Disposition | Current target responsibility references | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observation/contracts.py` | REWRITE the inherited frame/constants; drop its historical `observed_frame` event shape and any compatibility/wire promise | `repos/observation/src/observation/semantic.py` owns semantic claim primitives, not a composed frame; no target composition/delivery owner or envelope path is approved. | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob `14dd5186a187820d679d88b542c639cf84b57adc` (2,822 bytes), symbols `PRESENTATION_PROJECTION`, `COMPLETED_FRAME_CONTRACT`, `OBSERVATION_IDENTITY_CONTRACT`, `ObservedFrame`. Source docs describe an observer-only rendered-tick presentation frame; source `physics3d.py` composes body, cognition, vitals, mind and identity from multiple authorities and emits an `observed_frame` event. Current Observation `MIGRATION.md` at `repos/observation@2f4751f5` classifies the copied frame/constants as a REWRITE candidate: it says the Lab-composed frame is a delivery/composition artifact, not one semantic claim. The existing `observation/src/observation/contracts.py` is documented as transitional, not a stable target schema. A future composition/delivery design must choose its owner and envelope separately. This migration disposition makes no scientific-validity, custody, admission, or equivalence claim. |

### Historical Observation delta transport disposition (Lab #234)

| Source path | Disposition | Current target responsibility references | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observation/delta.py` | DROP as historical Lab JSON patch/anchor transport implementation | None. `repos/observation/src/observation/plane.py` streams semantic messages with explicit rebasing; it is not a replacement for this JSON delta format. | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob `b4573fd49979fd8eee088f3dfa98fe5b0f147c44` (9,259 bytes). The module canonicalizes JSON for hashes, computes patches, maintains per-channel revisions and periodic anchors, and encodes/decodes `observer-live-delta-v1`. The pinned source uses it in the Lab ObservationBus and browser stream patcher; tests establish only that historical transport's round-trip and rejection behavior. Current target search found no implementation or consumer of this wire protocol. Any future transport compression must be designed separately under an authorized delivery contract. This excludes the protocol from migration input, not deletes protected source; no semantic, scientific or equivalence claim is made. |

### Historical Development history read model disposition (Lab #235)

| Source path | Disposition | Current target responsibility references | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observation/development_history.py` | DROP as the historical browser-oriented Development history reader | None. Biopeia Frontend v0.1 explicitly excludes history/persistence; Lab main has no reader consumer; Observation has no history API. | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob `36e96d6d772b16faf1224efea6994018f7f83e1a` (14,260 bytes; SHA-256 `ad991b1f7ead2c5b708152915a68d07c1edeee66b40c9157025e8aec9b5d746b`). `build_development_history` enumerates Lab-managed runs, opens source Physics3D telemetry v4.1, computes Development-view point summaries and sparse snapshots, and reports run coverage/availability; it relies on source Lab mind-snapshot projection. It is a browser-oriented derived read model, not the owner runtime or telemetry source. Current target evidence: Lab main `563eb7e44f0876b9af8b218f282ade5f36712a6e` has no corresponding implementation/test; Frontend main `326613b74e388d3108cbafd3bab9128a35bd2246` documents no history or persistence and its source/tests contain no history reader; Observation main `2f4751f53678f2210930770605844cac766b1da4` has no such API. This drops only this historical reader from migration input. It does not delete or dispose of underlying telemetry/evidence artifacts or decide their custody/retention. No scientific result, evidence admission, semantic authority, or equivalence claim is made. A future history capability needs separate target design and evidence governance. |

### Historical subsystem status disposition (Lab #244)

Pinned source: `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observation/subsystem_status.py`, blob `c20ec51d7c3cd37eb498f1b43d773ed2f30c61f8` (2,087 bytes; mode `100644`). The verified module defines five lifecycle string constants, `LIFECYCLES`, and `generative_status`, which reads Lab runtime internals to report operational readiness/work state. This is not an Observation semantic projection or evidence-custody implementation. Observation migration records the helper as DROP: subsystem operational readiness is not source-state availability or an Observation semantic family; any Lab UI status is separately authored by Lab. No TARGET code owner/path or consumer justifies migration of this helper. DROP excludes only the historical implementation from TARGET migration input; it does not establish scientific invalidity, behavior equivalence, or lack of future need. Historical source remains read-only.

### Historical Symbiont affordance adapter disposition (Lab #245)

Pinned source: `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observation/symbiont_affordance.py`, blob `5e37fbd287cb4c72199d00bf2541d5e0b6580025` (3,752 bytes; mode `100644`). Its sole exported function wraps the historical `AffordanceObservation` as a Symbiont-authority `SemanticObservation`, derives lineage from affordance/effect/prediction/evidence/context/embodiment references, and optionally adds Lab run context. Current Organism owns independently authored action-affordance primitives in `repos/organism/src/organism/agency/affordance.py`, but this does not establish the historical adapter, claim-family semantics, or behavioral equivalence. Searches of current Observation and Lab source/tests found no consumer of this helper or approved target affordance claim adapter. Classify the historical adapter as `DROP` from migration input; any future claim projection requires owner-approved TARGET contract and a separately authored adapter. This does not question scientific validity, admit evidence, assign authority, or assert future need is absent. Historical source remains read-only.

### Historical Observation wire serializer disposition (Lab #246)

Pinned source: `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observation/wire.py`, blob `160df024ef608db2ee97603e8d4a326c53718fae` (4,895 bytes; mode `100644`). It serializes the legacy `SemanticObservation` and `PlaneMessage` into `observation-semantic-wire-v1`, including identity, lineage, context and value fields. TARGET Observation `src/observation/http_bridge.py` is a local-only read-only bridge restricted to two approved families and defines its own allowlisted encoding; it is not this general wire schema or an equivalent path. No current Lab consumer or approved target wire contract for the historical payload was found. Classify the serializer/schema as `DROP` from migration input; any future wire/API requires a separately approved target contract. This does not assign semantic authority or make evidence/scientific/equivalence claims; historical source remains read-only.

### Historical World scene presentation disposition (Lab #247)

Pinned source: `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observation/world_scene.py`, blob `fdf54be9b1dce8c0347c0ea4c40abf2cb6299699` (6,704 bytes; mode `100644`). It projects a historical rich runtime/world observation into a Lab observer scene (including receptor sampling, percept, signal/knowledge and entity payloads), and provides a revisioned scene publisher/delta application protocol. Current World causal-cycle/state contracts and Environment owner state are not this Lab viewer schema, delta protocol, or publisher; Observation has no world-scene family or current target consumer. Classify the historical view/protocol as `DROP` from migration input. Any future UI scene projection must be separately specified and target-authored. This does not admit evidence, assign semantic authority, or establish scientific validity/equivalence. Historical source remains read-only.

### Historical Observatory runtime adapter disposition (Lab #250)

Pinned source: `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observatory/adapter.py`, blob `9efdb6ac867699039fa2f3621190f7c4d5082fac` (69,145 bytes; mode `100644`). AST inspection confirms the inventory function set: bounded field/classification helpers, projections for body schema, cognition, generative cognition, physiology, metabolism, development/degradation, attention, social/social resource, culture, communication, sensory phenotype, and embodiment, plus `project_tick`, `project_topology`, envelope, and replay writers. The adapter reads runtime-rich historical structures and emits Observatory v1-v3 snapshot/replay schemas. TARGET owners have their own state contracts; Observation has its distinct bounded semantic model and an HTTP bridge for only explicitly approved families; Lab has no TARGET consumer for this snapshot/replay interface. No target-owned composite schema or concrete destination path justifies transferring any part of the historical adapter. Classify it `DROP` from migration input. Any future projection must use target-authored contract(s) and independently justified fields. This does not make scientific validity, authority, evidence-admission, behavior-equivalence, or future-need claims; historical source remains read-only.

### Historical Observatory instance registry disposition (Lab #260)

Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, `lab/src/lab/observatory/registry.py`, blob `22fd3b107ae2141940802972d019af50863c6f8f` (mode `100644`, 4,255 bytes). Verified symbols: `derive_instance_id;new_run_id;_atomic_write_json;write_heartbeat;_aware_datetime;_valid_registry_record;read_registry;classify_liveness`. The module derives local instance identity from a resolved state-file path, generates run UUIDs, writes per-instance JSON heartbeat records with PID/display ID/organism ID/key fingerprint/topology revision, validates records and classifies heartbeat freshness. It does not itself hold study results or experimental evidence, but combines local process liveness, identity and domain-related identifiers. Observation contracts currently carry transitional `instance_id` projections but define no durable instance registry, heartbeat, or liveness service; Lab has no TARGET Observatory runtime consumer. Do not infer a TARGET owner from either the projection or Lab's separate scientific evidence custody. This is a bounded `DEFER`, pending linked Observation #38 decisions on operational archive/source identity and Lab #266 disposition of the adjacent instance schema. Competent Observation/Lab owners must decide whether any fields and operational semantics have a TARGET responsibility, name the owner/contract/path, or explicitly `DROP` this behavior. The #260 coordinator tracks re-evaluation. Closure trigger: record the owner-authorized responsibility/path or explicit `DROP`, then reconcile this row. This item does not block the bounded runtime-transfer profile. No code/state is copied or deleted; historical source remains read-only. No scientific validity, equivalence, evidence-admission, or future-need claim is made.


### Historical Observatory body-schema adapter test (Lab #276)

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/tests/test_body_schema_adapter.py` | DROP as TARGET test | No TARGET test destination | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`; blob `66c27df821f6ee57d7ea5e51b175381c56a575ec`, mode `100644`, 6,494 bytes. Verified symbols: `result`, `sense_part`, `region_part`, `body_schema_v1`, `body_schema_v2`, `BodySchemaAdapterTests`. Every assertion exercises the legacy `project_tick` adapter and its projection of v1/v2 body self-knowledge into Observatory snapshot v3, including synthetic cognitive-region fixtures and fail-closed redaction of private fields. TARGET Observation/Lab contracts do not adopt this snapshot API; the underlying schema was separately classified in Lab #264 and its alias remains tracked by #251. Exclude this implementation-coupled test from TARGET tests only. It is not a target schema/API contract or scientific result; this does not imply future body self-knowledge observation or safeguards are unnecessary and makes no scientific validity, equivalence or evidence-admission claim. Historical source remains read-only. |


### Historical Observatory contract test suite (Lab #277)

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/tests/test_contract.py` | DROP as TARGET tests | No TARGET test destination | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`; blob `21d05a8ad1bd5fc0b9e341838e4d3caa55f602a7`, mode `100644`, 9,307 bytes. Verified symbols: `ROOT`, `_read_js_bundle`, `ObservatoryContractTests`, `ObserverProvenanceContractTests`, `SensoryWorldMapContractTests`. The assertions inspect legacy snapshot/body/cognition/topology/instance/replay JSON schemas, frontend module contents, historical resident CLI behavior, and optional sensory snapshot fields for replay compatibility. These are source-contract checks for the historical Observatory API/UI/CLI, not independent TARGET contracts or scientific evidence. Corresponding schema decisions remain separately classified, including unresolved DEFER entries; this DROP does not resolve or override them. No authorized TARGET destination adopts this snapshot, frontend, or CLI contract. Future requirements and tests must be target-authored against accepted owner contracts. Do not infer that boundedness, privacy, provenance, replay compatibility, sensory projection, or future safeguards are unnecessary. Historical source remains read-only; no scientific validity, equivalence, or evidence-admission claim is made. |


### Historical Observatory evidence-endpoint tests (Lab #278)

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/observatory/tests/test_evidence_endpoints.py` | DEFER (bounded) | No authorized TARGET endpoint/response contract | Pinned source `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`; blob `2029ddd95201008a1e16c237411b835fa0e11d31`, mode `100644`, 4,461 bytes; verified class `EvidenceEndpointTests`. The three tests exercise legacy HTTP projection of selected manifest provenance/digest fields while omitting private paths/config, history-summary selection via current registry run, and rejection of malformed instance IDs. No TARGET endpoint contract/service is authorized. Manifest custody/field authority remains DEFER under Lab #257; registry identity/current-run semantics remain DEFER under Lab #260 and Observation #38/Lab #266; journal/history custody remains DEFER under Lab #256. The historical summary generator is independently DROP under #254 and server implementation DROP under #271; those classifications do not settle whether any owner-authorized endpoint or evidence index is needed. Lab #278 coordinator tracks closure; Lab evidence-custody owner and competent Lab/Observation/domain owners must determine DROP or specify a new target-authored contract with field authority, source/run identity, privacy, schema, custody/retention, storage path and owner. Observation owner must separately resolve source/lake boundaries under #38. Closure trigger: record those decisions, then replace this bounded DEFER with explicit DROP or open a linked implementation/test Issue against accepted contract. This does not block bounded runtime transfer because no TARGET consumer/API dependency is identified. No source/tests/data are copied or deleted; no scientific validity, equivalence, evidence admission, or future-need claim is made. |


### Historical Observatory server-test disposition (Lab #289)

The pinned `lab/src/lab/observatory/tests/test_server.py` file
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`997a603fc37dbb931790928016390972e2fcf8de`, SHA-256
`56cd25bd981f701c2d7b395eb139f9923fc9d40d9c153e79199b7676110e73b8`) records
top-level `OUTSIDE_STATIC_ROOT` and class `ServerTests`. Seven test methods cover
loopback-only binding/rejection, SSE fleet membership from registry heartbeat,
static-path/extension rejection, per-instance journal replay, and reading a
compacted journal segment. They characterize one historical HTTP/SSE server
contract that combines server routes with registry and journal behavior; they
do not establish scientific validity or split into independently authorized
TARGET test paths.

Disposition is bounded `DEFER`, not `SPLIT`: the server implementation is
`DROP` under Lab #271, but this test file also exercises distinct stream/history
responsibilities whose target ownership and contracts remain unresolved. Lab
#278 keeps historical endpoint tests `DEFER`; journal custody/retention remains
`DEFER` under #256 and registry/identity under #260/#266. Observation #38 keeps
source/lake/delivery boundaries unresolved. Lab coordinates the migration and
retains only separately governed scientific evidence custody; Observation and
relevant state owners must authorize any outward projection/identity semantics.
Closure trigger: competent owners explicitly `DROP` historical-only routes and
assertions, or approve target-authored endpoint/stream contracts naming semantic
owner, schema, identity, delivery/completeness, privacy, evidence
custody/retention, concrete paths and native tests; then reconcile this row.
This does not block bounded runtime transfer. No source, runtime, records or
compatibility are copied/deleted; no scientific validity, equivalence, evidence
admission or future-need claim is made.


### Historical Observatory integration-test disposition (Lab #282)

The pinned historical file `lab/src/lab/observatory/tests/test_observatory_integration.py`
(at `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`3581df581e56afc91f490d707975c01707b62ca9`) contains two integration tests
for the legacy resident/instance registry: independent residents receive
distinct `instance_id` and `run_id`; restarting the same state file preserves
`instance_id` and starts a new `run_id`. This does not establish target registry
semantics. The inventory row is **DEFER**, not `SPLIT`: no target-authored
registry/restart contract or test path is authorized, and the behaviors are
coupled in one historical composition test. Lab #260/#266 and Observation #38
leave identity authority and the registry/projection/evidence-custody boundary
unresolved. Lab remains accountable for custody; Observation and the competent
Organism/World owners decide their respective field and projection contracts.
Closure requires an explicit owner-authorized `DROP` or an approved target
contract naming schema, authority and path, followed by row reconciliation.
This is outside the bounded runtime-transfer causal-cycle profile. No source
code is copied or removed, and no scientific validity, equivalence, identity
compatibility or evidence admission is inferred.


### Historical Observatory publisher-test disposition (Lab #283)

The pinned `lab/src/lab/observatory/tests/test_publisher.py` file
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`dd8a8891c32669072d04cc367db21ebe8751208b`) has five tests for the historical
publisher implementation: stdout JSON-line output, `JournalSink` delegation and
summary finalization, whole-file replay export, and identical-envelope fan-out.
The publisher itself is `DROP` under Lab #259, but the JournalSink assertions
intersect possible evidence custody/retention, still `DEFER` under Lab #256.
Observation #38 leaves archive, identity/delivery/completeness, retention and
API decisions unresolved; Docs #173 is readiness documentation, not
implementation authorization. The file does not split into authorized target
test paths, so it remains bounded `DEFER`, not `SPLIT` or `DROP`. Lab is
accountable for custody; Observation owns only any approved passive
projection. Closure requires an explicit owner-authorized `DROP` for the
journal responsibility or a target-authored publication/journal contract naming
semantics, authority, custody/retention and path, after which target-native tests
may be separately justified. No publisher, replay, persistence or scientific
behavior is implemented or inferred from the historical assertions. This does
not block the bounded runtime-transfer profile and makes no scientific validity,
equivalence, replay-compatibility or evidence-admission claim.


### Historical Observatory registry-test disposition (Lab #284)

The pinned `lab/src/lab/observatory/tests/test_registry.py` file
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`11b7d3d51f701b0c8fa31ae28ab7042ab9809c0b`) contains five tests for the legacy
registry: path-derived hashed instance IDs, fresh run IDs, atomic heartbeat
write/read including topology revision, malformed-record skipping, and
alive/stale/expired classification. These characterize the single historical
registry contract and do not establish separately authorized Observation/Lab
test paths. The implementation remains bounded `DEFER` under Lab #260, the
instance schema under Lab #266, and Observation #38; current instance-ID
projections do not authorize a durable registry, heartbeat or liveness service.
The `Observation / Lab` hint is not an owner decision, nor does Lab's evidence
custody responsibility authorize process identity semantics. Closure requires
competent Observation/Lab and represented-field owners to decide explicit
`DROP` or name the TARGET responsibility, contract/schema and path, then
reconcile both implementation and test rows. Outside bounded runtime transfer;
no source or state is copied/deleted and no scientific validity, identity
equivalence, privacy sufficiency or evidence-admission claim is made.


### Historical Observatory resident-contract test disposition (Lab #285)

The pinned `lab/src/lab/observatory/tests/test_resident_contract.py` file
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`3b877574c1eddb5b3ac3a9d34ac8df2fd380c673`) launches the historical resident
in three subprocess tests. They check the legacy snapshot schema/redaction,
registry + first-tick topology + journal publication, and revision-zero
topology on cognition-configured first launch. This couples the legacy resident,
snapshot validator, registry/journal and startup projection; it does not split
into authorized TARGET test paths. Registry and instance-schema concerns remain
bounded `DEFER` under Lab #260/#266 and Observation #38; this issue authorizes
no TARGET resident/snapshot publication contract or path. Organism retains
authority over any future cognition/genome start-state contract; Lab over any
separately approved execution/custody responsibility. Closure requires competent
owners to decide explicit `DROP` for historical-only assertions or approve
target-authored contracts naming semantics and test paths, then reconcile this
row. Outside bounded runtime transfer; the tests are software characterization,
not science. No source/runtime is copied/changed and no scientific validity,
schema equivalence, newborn-cognition equivalence or evidence-admission claim
is made.


### Historical Observatory runtime-projection E2E test disposition (Lab #287)

The pinned `lab/src/lab/observatory/tests/test_runtime_projection_e2e.py` file
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`30fb83886faf6ef06a59787643ca01376f634259`, SHA-256
`e7c8ed732f708bfa0fd5dbfabc9815cda83e8192a185ee962f2245b1a6a75d59`) has eight
test functions. They characterize one legacy Observatory v1-v3 composite
snapshot interface: runtime tick projection/schema validation; social relation
and resource fields; degradation counters; observer provenance exclusion from
organism data; embodiment projection/redaction; and fail-closed schema-version
fallback. This is not eight independent TARGET contracts. The historical
adapter and snapshot schema are already `DROP` as TARGET artifacts; this test
file therefore does not split into authorized TARGET test destinations.

Disposition is bounded `DEFER`, not `SPLIT`: the assertions span owner-meaningful
data, but no target-owned composite snapshot/test path or independently approved
field contracts authorize migration of this coupled historical test. Observation
#38 leaves the observational ingestion/provenance/retention design unresolved;
Organism, Embodiment and other represented state owners must separately
authorize any outward semantic projections. Lab remains accountable only for
its distinct, governed scientific evidence custody. Closure requires those
competent owners to record explicit `DROP` for historical-only assertions or
approve target-authored contracts naming each semantic owner, schema/path,
privacy/provenance limits and separately justified target-native tests; then
reconcile this row. This does not block bounded runtime transfer. No code or
data is copied/deleted, and no scientific validity, equivalence, causality,
evidence admission or future-need claim is made.


### Historical reversible-structure contract test disposition (Lab #286)

The pinned `lab/src/lab/observatory/tests/test_reversible_structure_contract.py`
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`d80f10280f219d428f5619d02f2776bb44b8fcbd`) has one assertion: the historical
`cognition_state.schema.json` enum includes `remove_node`. It does not execute a
mutation, establish runtime acceptance, or demonstrate learning/reversible
plasticity. The schema alias and underlying contract remain `DEFER`, with Lab
#265 tracking owner review. Organism owns cognitive graph/mutation semantics;
Observation owns only any approved passive projection. No TARGET cognition-state
schema/test path or owner-approved mutation contract is established. Closure
requires competent owners to decide explicit `DROP` or approve a target-authored
contract/path and justified native tests, then reconcile both rows. Outside
bounded runtime transfer; historical source remains read-only and no scientific
validity, mutation equivalence, learning or evidence-admission claim is made.


### Historical Observatory snapshot-version test disposition (Lab #290)

The pinned `lab/src/lab/observatory/tests/test_snapshot_versions.py` source
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`04f44728649cce6ae9e245e189b95beaf8bf0d48`) has twelve test methods. They
characterize the legacy Observatory v1-v3 wire-snapshot validator: body and
cognition combinations, sensory phenotype, bounded population telemetry,
observer-provenance placement, private-field redaction, and malformed field
rejection. This is one coupled historical snapshot contract, not separate
TARGET contracts and not scientific evidence.

Disposition is bounded `DEFER`, not `SPLIT`: no target-owned composite wire
snapshot or authorized target test path is established. The historical adapter
and schema are separately `DROP` as TARGET artifacts; those drops do not settle
whether separately authorized semantic projections or evidence custody are
needed. Observation #38 remains unresolved; Organism and Embodiment own their
represented state semantics, while Lab's custody role applies only if a
distinct evidence responsibility is authorized. Closure requires competent
owners to choose explicit `DROP` for historical-only assertions or define
target-authored contracts naming field authority, schema, privacy/provenance
boundary and test paths, then reconcile this row. It does not block bounded
runtime transfer. No code/data is copied or deleted and no scientific validity,
schema equivalence, privacy sufficiency or evidence-admission claim is made.


### Historical Lab Physics3D CLI disposition (Lab #293)

The pinned `lab/src/lab/physics3d/cli.py` (`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob `e0e4a390f25db1b6f6bfe807222b3153b5eb3d6e`, 7,508 bytes, SHA-256 `8381814f73e3b0bc67a9d1b688a4ef4371b73561d966cc31ea30221b9e14ab67`) contains top-level symbols `run_replay;main`. It is an argparse wrapper for launching the historical physics runtime or loading telemetry into the private Lab Mission Control viewer. Its options couple world execution parameters, Environment recipes, Embodiment state, Lab persistence/telemetry, host model servicing and the legacy viewer; it defines no domain semantics itself.

Disposition is `DROP` as TARGET code: no target-owned command, replay viewer, wire contract or direct consumer of this historical Lab module is authorized. This drops only this CLI/UI and its compatibility surface, not the domain-owned capabilities represented by its options. Future target commands must be separately justified and composed against accepted owner contracts. No source code, runtime, telemetry or viewer contract is transferred/deleted; no physical/cognitive/scientific validity, simulation equivalence, evidence admissibility or general lack-of-future-utility claim is made.


### Historical Physics3D effective-model audit disposition (Lab #294)

The pinned `lab/src/lab/physics3d/effective_model_audit.py`
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`33d20da18a82ea2d1e5013619eae606a8c30509f`, mode `100644`, 21,990 bytes) is
a read-only analyzer comparing declared Physics3D scene/joint/segment/material/
resource/environment/vision values with compiled MuJoCo state. It classifies
findings and emits a deterministic, hashed JSON report. It is one coupled
diagnostic/evidence artifact, not independent TARGET contracts or scientific
validation.

Disposition is bounded `DEFER`, not `SPLIT` or `DROP`: no target-owned report
schema, field authority, validation protocol, evidence custodian/retention
policy, direct report consumer or implementation path is authorized. The source
test row is independently `DROP` as an implementation-coupled test; that does
not decide the analyzer's possible diagnostic/evidence role. Lab #330 tracks
request/authority boundaries but does not authorize this tool. Embodiment,
Environment and World owners must decide which compiled-vs-declared relations
are requirements and own each field; Lab must decide whether reports constitute
scientific evidence requiring provenance/custody/retention/admissibility or are
unretained diagnostics. Closure requires those decisions and an authorized
report schema/path, or explicit owner-authorized `DROP`, followed by row
reconciliation. This tooling is outside and does not block bounded runtime
transfer. No model/scientific validity, simulation equivalence or evidence
admissibility claim is made; no source/report/code is copied or deleted.

### Historical Physics3D effective-model audit CLI disposition (Lab #295)

The pinned `lab/src/lab/physics3d/effective_model_audit_cli.py`
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`79efc42e6ab1d42f7aa12de8066b712d0e5dbcc7`, mode `100644`, 5,247 bytes)
composes Embodiment body apparatus and Environment recipes into compiled
scenarios, invokes the coupled analyzer in Lab #294, and emits a deterministic
hashed JSON audit suite. The CLI's mismatch exit code is a software gate, not
scientific acceptance. It defines no independent target responsibility, so the
prior `SPLIT` classification was corrected to bounded `DEFER` alongside #294.

No target-owned suite/report contract, field authority, protocol, report
consumer, evidence custodian/retention/admissibility policy, or authorized
destination is established. Embodiment, Environment and World owners must
decide field assertions and ownership; Lab must decide whether output is
evidence or diagnostics and define custody/report policy. Closure requires
those decisions and an authorized suite schema/path, or explicit owner-approved
`DROP`, then reconciliation of this CLI and #294 together. This is outside the
bounded runtime-transfer profile and does not block it. No code, scenarios, or
reports are copied/deleted; no validity, equivalence, or admissibility claim is
made.

### Historical Physics3D engine disposition (Lab #297)

The pinned `lab/src/lab/physics3d/engine.py`
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`f98aca80171e64485e39631a89ec3e56c5c7f349`, mode `100644`, 44,487 bytes)
implements a monolithic cross-domain execution loop: it schedules physics,
cognition, observation and rendering; constructs/restores the Embodiment
runtime; persists organism and body checkpoints; applies Lab guard/termination
callbacks; and manages telemetry, provenance and monitoring. The previous
`SPLIT` classification is not substantiated merely by these dependencies: no
accepted multi-owner TARGET runtime contract or concrete target implementation
path authorizes this source as a transfer candidate. Its classification is
corrected to bounded `DEFER`, not `DROP`.

World must define causal participant/commit orchestration; Embodiment the body
runtime and checkpoint contract; Environment its lifecycle; Lab its experiment
policy, telemetry/evidence custody and adapter scope. The exact owner-approved
runtime design, lifecycle/identity/checkpoint/provenance policies, and concrete
consumer/path are absent. Closure requires these contracts/path, or explicit
owner-authorized `DROP` of this historical engine, followed by reconciliation
of dependent runtime/CLI rows. This core runtime is not treated as disposable
because it is historical, and this bounded ledger defer does not block the
separately defined runtime-transfer profile. No code/state is copied/deleted;
no scientific validity, equivalence, autonomy or evidence-admission claim is
made.

### Historical Physics3D snapshot-equivalence disposition (Lab #298)

The pinned `lab/src/lab/physics3d/equivalence.py`
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`db6a9b34ada3f706d28e40b921ea2a418fc84c52`, mode `100644`, 13,944 bytes)
replays copied snapshots through the legacy engine and hashes per-tick payloads,
traces, provenance, body and model state, reporting divergence or equality for
the exercised snapshot/configuration. Its source documentation limits a PASS
to those exercised conditions; it is not proof of general equivalence or
scientific validity.

Disposition is bounded `DEFER`, not `SPLIT`: hashing several dimensions does
not establish separate target responsibilities. No TARGET run/equivalence
contract, snapshot schema, comparison dimensions/protocol, owner semantics,
evidence-vs-diagnostic decision, custodian/retention/admissibility policy or
consumer/path is authorized. This depends on engine #297 and its unresolved
World causal / Embodiment physical-state contracts; Lab must define evidence
status and custody. Closure requires target engine/snapshot contracts, scope
and comparison protocol, evidence policy/path, or explicit owner-authorized
`DROP`, then reconciliation of associated tests/results. This does not block
the bounded runtime-transfer profile. No snapshot is executed, source/output
is not copied/deleted, and no equivalence, determinism, validity or evidence
admission claim is made.

### Historical Physics3D causal-equivalence suite disposition (Lab #299)

The pinned `lab/src/lab/physics3d/equivalence_suite.py`
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`1442fc941c416fbd2e7d8d00a4d11432ccff3b7f`, mode `100644`, 11,255 bytes)
validates snapshot manifests, executes baseline/candidate runs twice per
scenario, classifies assessability/failure, checks training-event coverage and
compares deterministic state digests. A PASS is bounded to that snapshot and
configuration; READY only means input capture/validation, not scientific
approval.

Disposition is bounded `DEFER`, not `SPLIT`: this is one coupled evaluation
protocol/tool, and multiple comparison dimensions do not establish multiple
TARGET owners. It depends on primitive #298, engine #297 and snapshot archive
retention. No target snapshot/run/equivalence contract, protocol/scope,
thresholds, baseline/candidate authorization, custodian, raw-result
retention/admissibility or target consumer/path is established. Lab must define
protocol authority and evidence custody; World/Embodiment the compared
causal/physical semantics; Environment participates only if scenario scope
requires it. Closure needs authorized contracts/protocol/run authorization,
thresholds/coverage and evidence policy/path, or owner-authorized DROP with
result-custody decisions, followed by related-row reconciliation. This is
outside bounded runtime transfer. No experiment/snapshot is executed, no
code/data copied/deleted, and no equivalence, efficacy, determinism or
admissibility claim is made.

### Historical Physics3D observer-semantics disposition (Lab #300)

The pinned `lab/src/lab/physics3d/observer_semantics.py`
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`ea458b9ffba761a94426c436ed347f947c282ba0`, mode `100644`, 7,776 bytes)
maps opaque receptor/action/actuator identifiers to evaluator-side physical
labels, categories, joint/direction metadata and mapping status. Its contract
says these labels are ground truth for evaluation only and never enter organism
discovery, sensory, cognition, BodySchema or actuation inputs; action mapping is
observational only.

Disposition is bounded `DEFER`, not `SPLIT`: this is one observer projection
that consumes physical metadata and opaque refs, but no target evaluator
projection schema, owner contract, consumer/path or evidence-custody policy is
authorized. Embodiment must define stable physical/joint/actuator metadata;
Observation any projection/publication semantics; Lab whether this is diagnostic
or scientific evidence and its custody/retention/admissibility. Closure requires
a target-owned projection contract/path and owner review plus Lab custody policy,
or explicit owner-authorized `DROP`, then reconciliation of related observer and
equivalence rows. The historical no-feedback constraint is preserved, not
permission to invent target mapping. This does not block bounded runtime
transfer. No labels/source are copied/deleted; no sensory meaning, autonomy,
scientific validity, admissibility or equivalence claim is made.


### Historical Physics3D persistence facade disposition (Lab #301)

The pinned `lab/src/lab/physics3d/persistence.py` source
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`2658c40c11d52a162d573d5b7bd4c319bae0f665`, mode `100644`, 23,500 bytes)
is a mixed persistence facade: it assembles a portable `.symbiont` ZIP and
manifest, includes/extracts private model artifacts, synchronizes Workbench
`metadata.json`, wraps raw runtime/body JSON, and writes/reads passive
Physics3D telemetry. The exact top-level symbol list is retained in the source
inventory and checked against this pinned blob.

Disposition is `SPLIT` because owner-scoped checkpoint responsibilities are
distinct: Organism's opaque private checkpoint boundary is
`repos/organism/src/organism/checkpoint.py`; Embodiment's body/metabolic state
contract is `repos/embodiment/src/embodiment/checkpoint.py`; World stores exact
owner-produced bytes without interpreting them at
`repos/world/src/world/owner_checkpoint_store.py`. These are current target
contracts, not evidence that the historical facade or wire formats were
transferred. The historical portable ZIP/manifest, model-artifact package and
restore behavior, Workbench metadata sync, raw JSON wrappers, and telemetry
writer/reader convenience API are not retained as compatibility behavior: no
owner-approved TARGET bundle/telemetry schema, producer-consumer contract, or
evidence-custody/restore policy is established for them. Lab's evidence-custody
role alone does not authorize scientific admission or migration. A future
requirement needs the accountable owners to approve schema, producers and
consumers, custody, retention, and restore policy before reconsideration. No
source or artifacts were copied or deleted; no durability equivalence,
scientific admission, validity, or runtime-restoration claim is made.


### Historical Physics3D private-model training service disposition (Lab #302)

The pinned `lab/src/lab/physics3d/private_model_training.py`
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`46a90fb74edc7fad2055686cfb03a5d6be4e343e`, mode `100644`, 29,865 bytes)
is one host-side service: it accepts organism-authored training requests and
corpora, trains private models in a worker, stores model/tokenizer artifacts,
computes candidate/baseline and optional paired-reference metrics, attaches
inference and applies a source promotion decision. Its source-level ownership
claims do not establish a Biopeia target contract. The listed symbols were
verified against the pinned source and are recorded in the inventory.

Disposition is bounded `DEFER`, not `SPLIT`: current TARGET source has no
private-model `TrainingRequest`, corpus, registry, bridge or training-service
contract or consumer, so there is no concrete retained target path. The source
owner hint `World / Embodiment / Environment / Lab` is not evidence of target
ownership. Organism must decide whether this capability is required at all; if
retained, it needs target-native request/corpus/artifact/registry/compute and
promotion contracts, a concrete implementation owner/path, and restore/security
boundaries. Lab must decide custody/admissibility before paired evaluation
records can be treated as evidence. Closure trigger: a linked Organism-owner
decision to retain or DROP; if retained, a separate target contract and
implementation issue plus Lab custody decision. This does not block bounded
Lab runtime migration because there is no current target consumer/package
dependency. No training job was run; no source or artifact was transferred or
deleted, and no learning efficacy, scientific validity, promotion
appropriateness, durability or equivalence claim is made.


### Historical Physics3D runtime disposition (Lab #303)

The pinned `lab/src/lab/physics3d/runtime.py` source
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`d2a70e298d05547c1aadb75195ab6c0f17496a43`, mode `100644`, 112,656 bytes)
contains the recorded symbols `LONGITUDINAL_CONTRACT`,
`metabolic_cost_from_actuator_work`, `WORLD_BODY_ID`,
`PhysicsServerDisconnected`, `Tick3D`, and `Physics3DEmbodimentRuntime`. The
class spans construction/settling, physical and owner checkpoint payloads,
passive physical/world/telemetry projections, cognition/action payloads,
actuation, and a long-running `step` implementation.

Disposition is `SPLIT`: the monolithic historical host runtime combines
responsibilities now represented by distinct target components: Organism action
execution (`organism/src/organism/actuation/system.py`); World coordination and
MuJoCo numerical stepping (`world/src/world/causal_cycle.py`,
`world/src/world/adapters/mujoco.py`); Embodiment physical-state adoption and
owner checkpoint (`embodiment/src/embodiment/physics3d/physical_transition.py`,
`embodiment/src/embodiment/checkpoint.py`); Environment physical geometry
(`environment/src/environment/physical.py`); and passive body projections
(`observation/src/observation/embodiment.py`). These are current target components
at the reviewed revisions: Organism `d8ed534d48188fb2f629faaa8dd85b95063a0c2d`,
World `a7c8099cf6ede9cfdb8f6cf7eaefb2eab8dc9bad`, Embodiment
`d73315d87bbb3f2eea14e8c33812b37b59a5d72f`, Environment
`d09e45c40633c9b2bf927c7aec3f6326318c2ea8`, and Observation
`a8b43af65b79ca4e2455bfc1ff1b55faf3d4d353`. These are current target
components, not evidence that source code was transferred or that behavior is
equivalent.

This does not migrate the old host service, lifecycle, `Tick3D` wire/telemetry
shape, diagnostic/evaluation metrics, predictor/cognition payloads, or the
source's cross-domain step ordering. No target contract in this bounded review
authorizes those behaviors; they remain excluded pending their respective owner
contracts and any required Lab evidence-custody decision. No legacy runtime was
executed, no code/data was copied or deleted, and no autonomy, scientific
validity, numerical equivalence, or evidence admissibility is claimed.


### Historical Physics3D passive settling disposition (Lab #304)

The pinned `lab/src/lab/physics3d/settling.py` source
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`0f77e2ca231e0550bfc9e74d47750cdfeea2d068`, mode `100644`, 4,539 bytes)
contains exactly `SettlingResult`, `SETTLING_MAX_STEPS`, and
`settle_passive_body`. The routine mutates a passive solver scene, testing
linear/angular velocity and joint displacement against configured thresholds
for a stable-sample interval, then returns convergence status and residual/peak
joint/contact diagnostics; the default bound is 2,400 solver steps.

Disposition is bounded `DEFER`, not `SPLIT` or `DROP`. TARGET has physical-state
adoption in Embodiment (`embodiment/src/embodiment/physics3d/physical_transition.py`)
and numerical MuJoCo stepping in World (`world/src/world/adapters/mujoco.py`),
but neither establishes a passive initialization/settling contract, stable
criteria, target consumer, or ownership of the legacy diagnostic result. The
historical source's comment that the humanoid settles in about 1,600 steps and
that 2,400 steps is sufficient is not a validated TARGET calibration. Embodiment
must decide whether this behavior is required and define the somatic acceptance
contract; World must define the solver-step boundary if retained; Lab must decide
evidence custody/admissibility if measurements are treated as scientific records.
Closure requires those owner decisions and an approved target contract/path, or
an explicit owner-authorized `DROP` with custody disposition. This bounded source
review is not a runtime requirement and does not block target runtime extraction.
No source code was copied, no settling experiment was run, and no convergence,
scientific validity, evidence admissibility, or equivalence is claimed.


### Historical Physics3D asynchronous telemetry worker disposition (Lab #305)

The pinned `lab/src/lab/physics3d/telemetry/async_worker.py` source
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`1284969522e713685e7cfac58e165d35f1059627`, mode `100644`, 3,223 bytes)
contains only `AsyncTelemetryWorker`. It wraps an opaque writer with a bounded FIFO,
serializes append calls on a non-daemon thread, forwards writer metadata, and
provides flush/close/error propagation.

Disposition is bounded `DEFER`: this module is infrastructure for a legacy
Physics3D telemetry writer, not itself a telemetry schema or domain runtime. No
TARGET writer, async durability/lifecycle contract, producer-consumer interface,
or Lab evidence-custody/admission policy is established for this worker. Lab must
decide whether the resulting records are diagnostic apparatus output or
governed scientific evidence, including custody, retention, failure semantics
and admissibility; producer owners must accept any record contract. The schema
review in [Lab #312](https://github.com/biopeia/lab/issues/312) is a prerequisite,
with reader/record rows [#311](https://github.com/biopeia/lab/issues/311) and
[#313](https://github.com/biopeia/lab/issues/313) requiring reconciliation.
Closure requires those decisions plus a concrete target path, or owner-authorized
`DROP`. This does not block bounded runtime transfer. No worker/writer was run,
no records were copied, and no durability, evidence-admissibility, scientific
validity or equivalence claim is made.


### Historical Physics3D binary telemetry codec disposition (Lab #306)

The pinned `lab/src/lab/physics3d/telemetry/binary.py` source
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`74372cbf18081db4fc96295122c415ca53c5bb03`, mode `100644`, 43,726 bytes)
contains the 34 top-level symbols listed in the canonical inventory. It combines
unsigned/signed varints, string/value and record encoding, record hashing,
template compression, frame schema, dense, path-registry, delta, event and static
writers/readers, plus tick buckets. These are interdependent formats within the
legacy telemetry API, not separate TARGET domain owners or independent reusable
formats.

Disposition is bounded `DEFER`: there is no target consumer or accepted binary
wire/schema contract, version/migration policy, producer/reader pair, or
Integrity/durability guarantee for these byte encodings. Lab must decide whether
any stream contains governed scientific evidence and define custody, retention
and admission; Lab and producer owners must establish the record contract before
a target codec path can be authorized. The linked schema review [Lab #312]
(https://github.com/biopeia/lab/issues/312) and neighboring telemetry rows must
be reconciled before reconsideration. Closure requires a target-owned schema and
consumer contract with a concrete path, or an owner-authorized `DROP` plus
evidence disposition. This does not block bounded runtime transfer. No codec or
stream was executed/copied, and no compatibility, integrity, durability,
evidence admissibility, scientific validity or equivalence is claimed.


### Historical Physics3D telemetry CLI disposition (Lab #307)

The pinned `lab/src/lab/physics3d/telemetry/cli.py` source
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`7fdeaa4b535902afabe13160d52cb2964ddfdf3c`, mode `100644`, 1,602 bytes)
contains only `benchmark_main`. The argparse wrapper selects historical telemetry
benchmarking or run comparison, optionally evaluates a v4.1 gate, and prints JSON.
It defines no independent domain behavior or target contract.

Disposition is `DROP` as TARGET CLI code: no target command/consumer, telemetry
reader/benchmark path, or accepted CLI contract was identified. This disposition
excludes only the source command wrapper from TARGET migration; it does not delete
the pinned source, dispose of recorded telemetry/results, or resolve underlying
benchmark/gate behavior. Those belong to separate tool and v4.1 inventory rows
([Lab #314](https://github.com/biopeia/lab/issues/314), [#315]
(https://github.com/biopeia/lab/issues/315)) and require the appropriate Lab
evidence-custody/claim review. No CLI or gate was run, no code/evidence was
copied/deleted, and no acceptance, scientific validity, admissibility or
equivalence claim is made.


### Historical Physics3D telemetry compaction utility disposition (Lab #308)

The pinned `lab/src/lab/physics3d/telemetry/compaction.py` source
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`dfe2e3b51c140fc85f51be74da4b257b5ae874e5`, mode `100644`, 11,044 bytes;
SHA-256 `fc61dbe77c5ec023488e5748a5d436ff14ccaacc84f1aa474debd88a36b04d4b`)
defines canonical JSON/hash helpers, JSON-pointer operations, a content-addressed
object store, a compaction policy, and deterministic JSON-tree differ/patcher. Its
default references explicitly span observer semantics, cognitive topology, body
schema, self-model and motor primitives. This is one generic storage/patch utility
with cross-domain state paths, not evidence of four independent target runtimes.

Disposition is bounded `DEFER`, not `SPLIT`: no approved TARGET telemetry
compaction/reference schema, owner-specific contract, or concrete consumer path was
found in inspected Lab, World, Embodiment, Environment, or Observation `main`
revisions (respectively `51b554baf835819a42448ad1926c3b1e5be272b6`,
`a7c8099cf6ede9cfdb8f6cf7eaefb2eab8dc9bad`,
`d73315d87bbb3f2eea14e8c33812b37b59a5d72f`,
`d09e45c40633c9b2bf927c7aec3f6326318c2ea8`, and
`a8b43af65b79ca4e2455bfc1ff1b55faf3d4d353`). The closure trigger is a Lab
decision on diagnostic output versus governed evidence (custody, retention,
validation/admission), plus producer-owner acceptance of a telemetry schema,
reference resolution and patch/integrity/failure contract with concrete consumers.
Related reviews [Lab #311](https://github.com/biopeia/lab/issues/311), [#312]
(https://github.com/biopeia/lab/issues/312), and [#313]
(https://github.com/biopeia/lab/issues/313) remain prerequisites. This bounded
defer does not block unrelated migration rows. No code/record/object/result was
copied, deleted or executed; no durability, integrity, evidence-admissibility,
scientific-validity or equivalence claim is made.

### Historical Physics3D event-stream codec disposition (Lab #309)

The pinned `lab/src/lab/physics3d/telemetry/events.py` source
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`492c9c89f424d9efe6260624fdc4a77577cd67bb`, mode `100644`, 7,369 bytes;
SHA-256 `23787065c17982ae21452e2b9058668c349a7c8fd41e291531c7c6f16adc53c7`)
defines one writer/reader/file-iterator codec for snapshots, resets, ephemeral
events and cumulative appends, driven by historical `EVENT_RULES` temporal classes.
The source groups this wire/storage behavior around channel lifetimes; it does not
constitute separate target runtimes for each producer domain.

Disposition is bounded `DEFER`: no approved TARGET event-stream wire/storage
contract or concrete owner-consumer path was found in inspected Lab, World,
Embodiment, Environment or Observation `main` revisions recorded in the #308
review. Closure requires Lab's decision on diagnostic versus governed-evidence
custody, retention and admission, plus producer-owner acceptance of channel schemas,
ordering/reset/temporal semantics, reader failure behavior and concrete consumers.
Telemetry schema review [Lab #312](https://github.com/biopeia/lab/issues/312) is a
prerequisite; related reader and structural reviews are [#311]
(https://github.com/biopeia/lab/issues/311) and [#313]
(https://github.com/biopeia/lab/issues/313). The defer is limited to this codec and
does not block unrelated migration rows. No code/stream/result/evidence was copied,
deleted or executed; no completeness, integrity/durability, evidence-admissibility,
scientific-validity or equivalence claim is made.

### Historical Physics3D numeric-frame codec disposition (Lab #310)

The pinned `lab/src/lab/physics3d/telemetry/numeric.py` source
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`a43ee4d66749543e32b1f0999b513a08522a65fb`, mode `100644`, 11,631 bytes;
SHA-256 `bab887e1f75ef52fa9debffbc603ec30d3f27da3bbf5c08b624869a363684069`)
defines one codec that flattens nested values into shape templates and scalar
vectors, deduplicates channel schemas, and writes full/sparse/copy frames. This is
wire/storage representation, not distinct domain behavior per producer.

Disposition is bounded `DEFER`: no approved TARGET numeric-frame schema/registry or
consumer contract was found in inspected target repositories. Closure requires Lab's
decision on diagnostic versus governed-evidence custody, retention and admission,
plus producer-owner acceptance of channel shape/version semantics, sparse base/reset
rules, schema identity/integrity, reader failure behavior and concrete consumers.
Telemetry schema review [Lab #312](https://github.com/biopeia/lab/issues/312) is a
prerequisite; related reader and structural reviews are [#311]
(https://github.com/biopeia/lab/issues/311) and [#313]
(https://github.com/biopeia/lab/issues/313). This defer is limited to this codec and
does not block unrelated migration rows. No code/stream/result/evidence was copied,
deleted or executed; no completeness, integrity/durability, evidence-admissibility,
scientific-validity or equivalence claim is made.

### Historical Physics3D telemetry reader disposition (Lab #311)

The pinned `lab/src/lab/physics3d/telemetry/reader.py` source
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`c9dbc43f6d7b4670d866b62fcde893073d6dd9a0`, mode `100644`, 2,406 bytes;
SHA-256 `e429820a08f8ed02e173248182ed32c145d4b9fff61bd708cf7eb3195b0c30b2`)
defines a protocol plus discovery/opening for historical v4.1 run directories,
delegating to `TelemetryV41Reader`. Parent-directory discovery selects the
reverse-sorted first child run, which needs a deliberate target selection contract.
This is one version-detection/reader interface, not separate domain runtime code.

Disposition is bounded `DEFER`: no approved TARGET telemetry reader/schema contract
or evidence consumer path was found in inspected Lab, World, Embodiment, Environment
or Observation `main` revisions. Closure requires Lab's decision on telemetry
custody, retention and admission; producer-owner definitions of accepted schemas,
versions and state/summary/event semantics; and Lab decisions for run selection,
verification and error handling. Related issues remain individually open: schema
[#312](https://github.com/biopeia/lab/issues/312), structural validation [#313]
(https://github.com/biopeia/lab/issues/313), tools [#314]
(https://github.com/biopeia/lab/issues/314), v4.1 gate [#315]
(https://github.com/biopeia/lab/issues/315), and writer lifecycle [#305]
(https://github.com/biopeia/lab/issues/305). This defer is limited to the reader and
does not block unrelated migration rows. No code/telemetry/result/evidence was
copied, deleted or executed; no completeness, integrity/durability,
evidence-admissibility, scientific-validity or equivalence claim is made.

### Historical Physics3D telemetry layout schema disposition (Lab #312)

The pinned `lab/src/lab/physics3d/telemetry/schema.py` source
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`a683b08f6a7e859cd015be90fb9b1ac688d398ee`, mode `100644`, 9,250 bytes;
SHA-256 `b18b29e807517d702395985899030abb2f529da81422b3125279260575eed2cc`)
defines one v4.1 layout contract that partitions paths into dense, structural,
event and static channels, leaves unclassified paths in fallback, and reassembles
state. Its path taxonomy spans concepts represented by multiple domain owners.

Disposition is bounded `DEFER`: no approved TARGET telemetry schema, channel
taxonomy or consumer contract was found in inspected target main revisions. Closure
requires Lab's custody/retention/admission decision, producer-owner authorization of
field/channel meaning, temporal classes and versioning, and consumer acceptance of
reassembly/fallback rules. Related reader/codecs are #309–#311; structural/tool/gate
reviews remain separate in [#313](https://github.com/biopeia/lab/issues/313), [#314]
(https://github.com/biopeia/lab/issues/314) and [#315]
(https://github.com/biopeia/lab/issues/315). This defer covers only this legacy
layout and does not block unrelated migration rows. No code/telemetry/result/evidence
was copied, deleted or executed; no scientific validity, evidence admissibility,
completeness, integrity/durability or equivalence claim is made.

### Historical Physics3D structural telemetry codec disposition (Lab #313)

The pinned `lab/src/lab/physics3d/telemetry/structural.py` source
(`alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d`, blob
`e2ad894ae01cfbe1d5246040c0716cef25f7dd90`, mode `100644`, 3,995 bytes;
SHA-256 `196075f5cfe6fcc298c9b6e05e799fc7f8b4a4de76998541c61bac1a46c5895f`)
encodes nested mappings/lists and identity-keyed lists into a reversible telemetry
AST. Candidate identifiers span multiple domain concepts, but the module is one
generic structural codec rather than separate target runtime behavior.

Disposition is bounded `DEFER`: no approved TARGET structural telemetry AST/schema
or consumer contract was found. Closure requires Lab's diagnostic/evidence
custody-retention-admission decision, producer-owner authorization of represented
entity IDs, edge identity and ordering semantics, and consumer acceptance of AST
tags/error behavior. Related schema [#312](https://github.com/biopeia/lab/issues/312),
codecs #309–#311, and tool/gate reviews #314/#315 remain distinct. This defer is
limited to this codec and does not block unrelated migration rows. No
code/telemetry/result/evidence was copied, deleted or executed; no identity validity,
structural completeness, integrity/durability, evidence-admissibility,
scientific-validity or equivalence claim is made.
