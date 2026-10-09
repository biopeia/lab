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

The application entry point clones Environment and Embodiment state through
their own checkpoint APIs, checks the caller-provided intervention envelope is
bound to its operator label, intervention id, exact source id and exact target
body id, caps the request by that envelope and the Environment offer, debits
only the amount Embodiment accepts, and returns the
candidate owner states only after `WorldRuntime.tick` returns a committed
record. Observation projection occurs after that return. A World callback or
journal failure yields no result/projection and leaves input owner objects
unchanged; the existing World runtime enters `RECOVERY_REQUIRED`. This is not
a distributed transaction, durable commit, or recovery protocol: callers must
not continue ordinary causal execution after that World state. Callers must
explicitly adopt returned candidate state; this API does not silently mutate
owners. Tests verify this local contract.

The transfer is deliberately an unspecified scalar. Current Embodiment intake
maps accepted material amount into its energy-reserve scalar, but no conversion
unit, physical energy equivalence, contact condition, or efficacy is claimed.
No Organism intention/readout authorizes this intervention.

#### Scientific-apparatus and intervention-identity boundary

Lab remains the scientific apparatus/application layer for this operation. It
composes owner APIs and stages an explicit requested intervention; it does not
own resource quantity, somatic acceptance, causal commit, identity management,
or scientific interpretation. The present bounded API carries
`intervention_id`, caller-provided
`operator_id`, `source_id`, `target_body_id`, and requested/offered/accepted/
debited scalar values. These support local intervention provenance and a
World-recorded causal event. They do not constitute an authenticated principal
reference, approved protocol, or scientific result. The intervention contract
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
and Embodiment APIs retain authority over offered quantity and accepted amount,
and World records the causal event. The causal record applies to this one
committed transfer invocation only; it does not establish experimental
causality, efficacy, repeatability, or physical interaction. This API is
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
Git commit references: Embodiment `047bc4fdb2d3348237295032777b3d6e499c7c89`
(merged PR #11), Environment `05087c6debe5e02734128b23d4ce8887a26b91ad`
(current `main`), Observation `8261dda79551a4ad13bf2b91692098f7509c2c9b`
(current `main`), and World `8413e263ffa0a7887901a0bb875e24abd2a5e600`
(merged World #10). Lab requires World callback payload support; the pinned
World main now provides it. Lab CI therefore uses Python 3.12,
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
