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
