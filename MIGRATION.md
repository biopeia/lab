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
| `lab/studies/**` beyond the two common utilities | DEFER | Individual studies have runtime dependencies, experimental conditions and protocols requiring their own transfer review. No study protocol or output is copied here. |
| `lab/experiments/**` | DEFER | Runner, registry, manifests and workspace interact with source layout, runtime composition and persistence/provenance. |
| `lab/physics3d/**`, `lab/integration/**`, `lab/world/**` | DEFER | Mixed physical substrate, semantic authorities and runtime orchestration; not safe for bulk transfer. |
| `lab/observation/**`, `lab/observatory/**`, `lab/server/**`, `lab/app/**` | DEFER | Observation, transport, evidence custody and UI boundaries require separate extraction. |
| CLI and reproduction code | DEFER | Entrypoints and reproduction callers are mixed with CURRENT runtime authorities/interventions. |
| Scientific assets, manifests and run/checkpoint payloads | DROP from this repo scope | No scientific artifacts are copied or relocated. This does not determine their preservation disposition. |

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

### Opaque body-interoception apparatus transducer

| Source path | Disposition | Target path | Provenance / limits |
| --- | --- | --- | --- |
| `lab/src/lab/integration/physics3d/apparatus.py::OpaqueBodyInteroception` | SPLIT + REWRITE | `src/lab/apparatus/interoception.py::OpaqueBodyInteroception` | Source repository `alessbarb/symbiont-lab`, pinned source SHA `80d372a186513035f85a769db886e505cabba52d`; preserves four-slot mapping/transduction but requires explicit target receptor IDs because target Embodiment has no corresponding humanoid receptor contract. |
| `lab/tests/unit/lab/physics3d/test_contract.py` interoception cases | REWRITE (focused contract tests) | `tests/test_interoception.py` | Isolated tests cover bounded projections, ordinal permutation, validation, and label-free checkpoint round-trip; source integration suite is not migrated. |

This extraction isolates a Lab-side apparatus transducer from the former mixed
runtime adapter. It consumes only a structural view of the required scalar
fields, provided by Embodiment-owned state, and emits four opaque receptor
values; Lab does not import Embodiment implementation code or acquire physiology
ownership, add semantics to those values, or assert scientific validity. This
also keeps isolated Lab package CI from requiring private-repository credentials;
the workspace still composes the actual Embodiment package. The runtime adapter
and the rest of `lab/integration/physics3d/apparatus.py` remain deferred. No
experiment, study protocol, scientific asset, or result was copied or run.

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
The World causal cut references the step-scoped Lab evidence checkpoint; the
World's generic causal record does not itself contain the intervention payload.
The causal cut applies to this one committed transfer invocation only; it does
not establish experimental causality, efficacy, repeatability, or physical
interaction. This API is
bounded to controlled experimental transfer under caller-supplied conditions;
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
merge commit references: Embodiment `61da7911fd48bcc6fd7afaac050020ced5118b55`
(owner checkpoint validation PR #15), Environment
`c14814a5bfdca0c23976cf194550b662602b12ff` (identified resource checkpoint
validation PR #17), Observation
`64c3226ab3701f748e276c92a852ca4facd74091` (semantic observation PR #3), and
World `9e808d23e3c063f71a9b5d93b7cd8ba4036c2a28` (owner checkpoint validation
PR #11). World main provides durable owner-closed cuts and
step-participant checkpoints; the intervention payload is preserved by its
Lab evidence reference, not by a generic World record extension. Lab CI
therefore uses Python 3.12,
matching World/Environment. The operator id is caller-supplied provenance, not
authenticated authorization. Quantity remains a scalar with no established
physical material-energy equivalence. No experiments or scientific assets were
moved or run.

### CI boundary for private domain dependencies

The material-transfer contract tests remain real tests in
`tests/integration/test_material_transfer_intervention.py`; they run against
the actual Embodiment, Environment, World, and Observation package APIs. They
were not replaced by mocks. The package repository's default GitHub Actions
token is scoped to Lab and cannot clone those private repositories, as shown by
the failed CI install logs (`fatal: could not read Username for
'https://github.com'`). Therefore, package CI installs the dependency-free
`dev` extra and runs only `tests/unit`; workspace integration runs are separate
and use the sibling local checkouts through `requirements-integration.txt`.
The pinned Git dependencies remain available as an explicit `integration`
extra for authorized consumers. Green package CI alone is not evidence that
the cross-package intervention tests ran.

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
  Current tracked target modules are `lab.apparatus.interoception`,
  `lab.interventions.material_transfer`, and the three extracted common study
  utilities (`digests`, `pairing`, `statistics`). Target tests cover those APIs
  (`tests/unit/test_{interoception,digests,pairing,statistics}.py` and
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
| `lab/src/lab/studies/common/{statistics,pairing,digests}.py`; `conditions.py`, `rng.py`, `summaries.py`, `causal_selection.py`, `actuator_probing_calendar.py` | `lab/tests/unit/lab/test_common_stats.py`, `test_pairing.py`, `test_digests.py`; `ExperimentRunner` is the tracked digest caller. Biopeia directly consumes only the three already-extracted utilities. | Existing three: `MOVE` (bounded extraction, see prior records). Remaining common modules: `DEFER` | Statistical helpers and deterministic pairing/digests are independently useful apparatus, but each remaining utility needs caller, API and provenance review. Do not infer target demand from a source test or study. |
| `lab/src/lab/studies/**` (132 source files across ablations, continuity, embodiment, genetics, learning, observability, perception, physics3d, world and root-level studies); symbols include `run_*_study`, study/result dataclasses, condition and metric helpers | `lab/tests/integration/studies/**` (50), protocol/runner tests, and `lab/experiments/**` manifests/README files; source `lab/experiments/registry.py::get_protocol` dispatches selected runners. No target study imports. | `DEFER` per study, then `SPLIT` or `REWRITE` where a portable measurement/protocol utility is justified | Studies are scientific apparatus, not automatically reusable product modules. Each requires design, conditions, estimand, outcome, source/runtime dependencies, evidence custody and any human approval to be separately reviewed. Preserve historical protocols/results as evidence; do not port them as runtime compatibility. |
| `lab/src/lab/experiments/{execution_workspace,generations,loader,manifest,registry,resource_guard,runner,snapshot_archive,spec,verified_child}.py`; symbols include `ExperimentRunner`, `ExperimentSpec`, `RunManifest`, `GenerationStore`, `pinned_worktree`, `run_verified`, `get_protocol` | Source `lab/experiments/**`, `lab/tests/experiments/{protocols,runners}/**`, CLI study/experiment entry points; no Biopeia target caller. | `SPLIT` / `REWRITE` candidate; `DEFER` pending Lab experiment/run contract | Study orchestration, run identity, manifests, resource controls, provenance and controlled execution belong in Lab, but source registry/runtime is monorepo- and protocol-coupled. Do not carry implicit source defaults, process-global registry or runner semantics forward. |
| `lab/src/lab/observation/{semantic,contracts,projection,plane,bus,wire,delta,provenance_journal,world_scene,environment_resource,body_pose,body_physiology,joint_kinematics,physics3d,atlas,development_history,symbiont_affordance,subsystem_status,cadence,observatory}.py` | Source observation unit/smoke/integration suites; referenced by `observatory`, `physics3d`, `workbench`, `server` and source runtime adapters. Current Biopeia Observation repository owns its own semantic-model work; Lab has no implementation consumer. | `SPLIT` / `REWRITE` candidate; transport/UI-specific pieces `DROP` or `DEFER` after consumer audit | Ratified architecture keeps Observation a passive projection, distinct from scientific evidence custody. Its approved conceptual model does not authorize copying this source schema/API/transport. Lab may admit claims into evidence but must not become primary authority for Embodiment, Environment, Organism or World claims. |
| `lab/src/lab/observatory/{adapter,config,history_summary,journal,manifest,provenance,publisher,registry,schema_validate,server}.py`, schemas, `world.html`, and nested tests | 48 source package files including schemas/tests; source `lab/tests/smoke/test_observatory_source_adapter.py`, server/runtime projection tests, source Workbench/app. No target consumers. | `SPLIT` candidate for Lab evidence/provenance custody; `DROP` candidate for domain-state adapters/schemas/UI that duplicate domain or Observation contracts; otherwise `DEFER` | Distinguish experiment evidence records from passive Observation claims, source state and delivery. Existing JSON shapes (`instance`, `snapshot`, `topology`) are not approved Biopeia records. Determine custody, retention, replay and integrity requirements before implementing any successor. |
| `lab/src/lab/physics3d/{engine,runtime,effects,equivalence*,persistence,settling,observer_semantics,world_observation,private_model_training,telemetry/**}.py`; examples include physics runtime/engine, telemetry readers/writers and effect characterization | `lab/tests/unit/lab/physics3d/**`, integration/equivalence tests, Physics3D runs and CLI; no target Lab runtime consumer. | `SPLIT` / `REWRITE` candidate for scientific apparatus, analysis and retained telemetry evidence; `DROP` candidate for stale adapters/obsolete schemas only after per-path proof; core runtime `DEFER` | Biopeia ratifies solver as numerical substrate, not semantic authority; Environment and Embodiment own adoption and World commits. Do not transfer a source runtime as a solver authority. Preserve raw scientific outputs where governance requires; this candidate code disposition does not dispose of records. |
| `lab/src/lab/integration/{integrated_habitat.py,organism/**,physics3d/**,world/**}` including `OpaqueBodyInteroception` and source adapters; `lab/src/lab/world/{population,runtime,transaction,persistence,cli_view}.py` | Source integrated-habitat/world/physics tests; current target uses rewritten `lab.apparatus.interoception` and `lab.interventions.material_transfer`; workspace suite has `tests/integration/test_operator_material_transfer.py` and `test_first_biopeia_physical_causal_step.py`. | Already extracted items: `SPLIT + REWRITE` (see earlier records). Remaining adapters/runtime: `DROP` candidate for superseded source composition or `DEFER` when independent Lab apparatus remains useful | World/Environment/Embodiment split is ratified; source World/hex/population assumptions do not transfer by name. New integrations must call current owner APIs and preserve causal commit order; no old namespace bridge. Determine each behavior against Biopeia contracts, not source file location. |
| `lab/src/lab/app/physics3d/**`, `lab/src/lab/server/{api,server,sse}.py`, `lab/src/lab/cli/**` | Source unified server/app/CLI smoke tests and source users; no target consumer. | `DROP` candidate for old monolith/UI/commands; `REWRITE` candidate only for independently justified operator tooling or Lab application endpoints; otherwise `DEFER` | Do not preserve old HTTP/SSE, command syntax, browser assets or launch flow by compatibility. Any future operator tooling must not turn caller identity into authentication/authorization and must keep Lab out of causal ownership. |
| `lab/src/lab/workbench/{coordinator.py,web/**}` | Source Workbench/browser tests; source `observatory`/`server` integration; no target consumer. | `DROP` candidate for source-coupled presentation; possible `REWRITE` candidate as a new Lab UI after requirements | Frontend and static assets are implementation-specific, not scientific evidence or semantic contracts. This candidate is not a ruling to delete historical screenshots/assets from protected evidence stores. |
| `lab/src/lab/evaluation/**`, `evolution/**`, `experience/**`, `reproduction/**`, `modeling/**`, `kernel_characterization/**` | Corresponding source unit/integration tests and study/experiment callers; no target Lab consumer. | `SPLIT` / `REWRITE` or `DEFER`, module by module | Some can be Lab methods, analysis, model/evaluator apparatus; some source modules may encode Organism or lifecycle semantics. Keep longitudinal private state and cognition out of Lab. Establish owner for every persistent state and claim before any broad MOVE. |
| `lab/experiments/**` (364 source files at pin: experiment definitions, protocols, README, result summaries, frozen reports, manifests, receipts, seeds, selection outputs and snapshots) | Referenced by source registry/studies/CLI; no target path consumes the source tree. | Executable definitions: `DEFER`/`REWRITE`; scientific results, receipts, manifests, snapshots: `DEFER` evidence-custody review; unsupported/stale test artifacts: candidate `DROP` only with evidence-owner approval | Distinguish executable code from scientific evidence. Do not migrate or regenerate recorded results as if source code. Preserve source/provenance and obtain owner decision before any destructive disposition. |
| `lab/tests/**` (297 source test files) | Grouped under unit, integration/studies, experiments, smoke, workbench, Observatory and physics; exercise source implementation and source-coupled fixtures. | `DROP` as source tests from Biopeia package; selected assertions may be `REWRITE` as contract tests once target behavior exists; scientific evidence suites `DEFER` | Tests are not production API and must not be bulk copied. A rewritten test must state invariant and whether it is contract, validation or scientific experiment; no source experiment run is claimed. |
| `lab/examples/**`, manifests, saved run/checkpoint payloads and model assets referenced by package | Source CLI/reproduction/Workbench or individual experiments; no target package consumer. | `DEFER` evidence/preservation inventory; then `DROP` from runtime distribution or `MOVE` to governed evidence archive only by explicit authorization | Code inventory does not authorize moving, deleting, exposing or reinterpreting evidence/artifacts. No data/evidence disposition is final in this PR. |

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

**Status: complete path/blob accounting snapshot; semantic disposition and
scientific custody remain open.** This is not migration completion, cut-over,
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
| `MOVE` | 6 | Three already-extracted utility modules and their three focused test files; this records existing target state, not a new transfer in this change. |
| `SPLIT` | 149 | Mixed responsibility or authority; target owner(s) are named, but unresolved target path means no source implementation is approved to move. |
| `REWRITE` | 2 | Target package/document root is independently authored; old package roots are not compatibility surfaces. |
| `DROP` | 322 | Excluded from Biopeia migration input; **not** deletion of the protected historical source. Future functionality, if required, must be newly justified and target-authored. |
| `DEFER` | 693 | Open disposition, not final. Must be revisited before migration completion. |

The file-level classifications are intentionally conservative. A `SPLIT` row
does not assert that a particular source symbol is worth preserving. A `DROP`
row means “do not migrate this source artifact or its legacy interface”; the
historical source copy remains untouched. A `DEFER` row is explicit migration
debt and cannot be counted as completed inventory.

### Lab tests and scientific assets

All 297 pinned source test files have a row. The current target test coverage is
selective: three focused utility test files are already present as `MOVE`, one
mixed physics contract test file is `SPLIT` because only selected interoception
assertions were rewritten, 76 science/protocol/integrity-oriented test files
remain `DEFER`, and 217 source-coupled tests/fixtures are `DROP` from the target
test plan. These are migration dispositions only: source tests remain in the
historical repository, and `DROP` does not erase historical results or evidence.

All 364 files under `lab/experiments/` and all 112 files under `lab/research/`
remain `DEFER`. This includes executable protocol/run definitions, study
descriptions, manifests, result records, receipts, snapshots, seeds, audit
reports, and compressed traces. No custodial owner has approved which artifacts
must be retained, their target archive/path, access controls, integrity scheme,
retention policy, scientific admissibility, or linkage to future Biopeia runs.
They therefore remain only in the untouched source repository; this change
does not copy, regenerate, republish, relabel, or delete any of them. The
historical replay example is also deferred for custody review. This is a
material unresolved blocker to declaring Lab migration complete.

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
