# Campaign V1 — longitudinal learning pilot: classification and custody record

**Status: exploratory instrumentation pilot. Not scientifically accepted.** This
directory is Lab's custody record for the campaign run by Antigravity on
2026-10-16 (UTC). It adds no result and no conclusion. It preserves what was
produced, says what the frozen protocol planned and what was executed, and
corrects published statements that the preserved data do not support.

Program issue: [lab#465](https://github.com/biopeia/lab/issues/465), which
stays open. The frozen protocol is published by
[lab#561](https://github.com/biopeia/lab/pull/561).

The independent methodological review of the protocol is
[lab#465 comment 6232391158](https://github.com/biopeia/lab/issues/465#issuecomment-6232391158).
The corrections in this directory were authored by the same agent (Claude),
after that review. They are therefore not independently reviewed, and need
their own independent review before merge.

## Identity of the frozen protocol

| Item | Value |
|---|---|
| File | `docs/protocols/protocol-lab-longitudinal-learning-v1.md` (added by lab#561) |
| Commit | `e91c5ba9e9d4526c4a6b251371f253d6dfc6686c`, the only commit of lab#561 |
| SHA-256 | `e6b088a04ae3228d39da377438cfcb67d0de35891f6250f9a92db5e2250a14d2`, 9,495 bytes, byte-identical to the original file |
| Original last written | 2026-10-16T23:22:45Z (01:22:45 +02:00) |

The commit `e91c5ba9bbf07f78c85c2c4bf190eec2604618e4` first cited for the
protocol names no commit, and the authoring time first given as 21:22:45Z was
read in the wrong time zone. Both records were corrected on 2026-10-17. The
protocol file itself is not modified.

## Classification

- **Exploratory, same session, not preregistered, not confirmatory.** The
  protocol was last written about four minutes before the first data file
  (23:26–23:29Z). Its status line reads "Pendiente de Revisión", and the runs
  took place before any review.
- **Non-conforming variant.** The executed scripts differ from the frozen
  text in parameters and procedures; see [deviations.md](deviations.md). The
  results are outcomes of that variant, not of the protocol as written.
- **Factor S is joint proprioception, not interoception.**
  `KinematicSomaticTransductionV1` carries joint position and velocity from
  the articulated body to the action composer. That is proprioception. It
  carries no energy, integrity or viability signal, so it is not the somatic
  state of ADR-0094. Where the frozen text says "retroalimentación somática
  interoceptiva" (§1) or "somática" (§2–§3), read joint proprioception. Under
  the owner's DOC-H3 disposition (docs#235), no statement about interoceptive
  regulation, metabolic regulation or physiological viability can rest on
  this campaign.
- **Factor P is an experimenter-scheduled Oja update.** The rate, modulation,
  eligibility decay and the one eligible edge are set by the script, and
  prediction error does not enter the update. A weight change under it is a
  check of the update path, not learning.

## What may and may not be stated

May be stated (preserved data, this variant only):

- the weight change under the scheduled update, and its absence without it;
- the factors as executed did not interact: identical weights in G3 and G4,
  identical competence statistics in G2 and G4;
- weight unchanged across the E2 extinction phase;
- the summarised end state of G4 equal after an in-process restore at cut 10
  (see [dossier-rectification.md](dossier-rectification.md) for exactly what
  is equal).

May not be stated: functional change (no functional measurement was made),
adaptive motor learning, functional reuse of the primitive, adaptation to the
environment or to the body, interoceptive or physiological regulation,
durability across a process crash, or any statistical difference (one
deterministic run per cell).

## Observations that still block scientific acceptance

From the review, as they stand after these corrections:

| # | State |
|---|---|
| B1 | Corrected in lab#561's body and in the publication record on lab#465. |
| B2 | Documented in [deviations.md](deviations.md). The deviation itself cannot be undone: the results remain those of a non-conforming variant. |
| B3 | **Open.** The restore ran with `owner_checkpoint_verifier=lambda refs: True`, in the same process, and was compared by summaries. No durability claim is admissible. |
| B4 | **Open.** One deterministic run per cell; no estimand, seed or replicate. |
| B5 | Classification recorded above. |
| B6 | Artifacts preserved in [artifacts/](artifacts/), with [provenance.md](provenance.md). Admission is Lab's decision and has not been made. |

Any future campaign meant to support a scientific claim needs a new protocol,
reviewed before execution. This record does not authorize runs.

## Files

| File | Content |
|---|---|
| [deviations.md](deviations.md) | protocol versus execution, item by item |
| [provenance.md](provenance.md) | revisions, environment, commands, original paths, reproducibility limits |
| [dossier-rectification.md](dossier-rectification.md) | rectification of the historical dossier |
| `artifacts/original/` | byte-exact copies of the three scripts, three result files and the dossier, with `SHA256SUMS` |
| `artifacts/run-outputs.tar.gz` | World manifests, journals and owner checkpoints written by the runs |
| `artifacts/run-outputs-manifest.tsv` | the archive's files: original path, size, modification time, SHA-256 |
| `artifacts/SHA256SUMS` | hashes of the archive and its manifest |

`tests/unit/test_campaign_v1_custody.py` checks every hash above.
