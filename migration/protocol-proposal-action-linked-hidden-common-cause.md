# Protocol proposal — action-linked evidence under a hidden common cause

**Status: PROPOSED. Not reviewed, not accepted, not executed.**

- Tracking issue: [biopeia/lab#59](https://github.com/biopeia/lab/issues/59), bounded child of [biopeia/lab#45](https://github.com/biopeia/lab/issues/45).
- Work class: SCIENTIFIC (protocol design). Scientific acceptance authority: Lab owner (`alessbarb`).
- Lab base revision: `273c41207332ef7c7de02de625253d03d642a200`.
- This document proposes a method. It contains no result, authorizes no run, and
  sets no numeric threshold. Every quantity written `⟨…⟩` is an open value that
  the Lab owner must fix, in a reviewed revision of this document, before any
  execution.
- Location: placed beside the disposition record it answers because Lab has no
  established home for TARGET protocol proposals. The location is the author's
  choice and can be moved by the Lab owner without changing the content.

## 1. Relation to the historical unit

The disposition of `embodiment.hidden-common-cause` is `REIMPLEMENT_METHOD` for
the scientific question only; see
[`study-disposition-register-80d372a.tsv`](study-disposition-register-80d372a.tsv).
Source identity, recorded there in full:

| Item | Identity |
|---|---|
| Source | `alessbarb/symbiont-lab@80d372a186513035f85a769db886e505cabba52d` |
| Protocol | `lab/experiments/embodiment/hidden-common-cause/experiment.toml`, blob `1ef13e9fa48ec642525a31dc8c83aa2b6b64ccda` |
| Implementation | `lab/src/lab/studies/embodiment/hidden_common_cause.py`, blob `5cdfd88635fc28c3a44c25774c3c9a0ba7c068ce` |
| Recorded output | `lab/experiments/embodiment/hidden-common-cause/results.json`, blob `6d1cf24be824884ec5a2f5510ce1ec0f404c2de0` |

What is taken from that unit is the question in one sentence: can evidence
linked to an action tell a change the action caused from a change that merely
accompanies the action because both share an unobserved cause. Nothing else is
taken. The historical algorithm, decision thresholds, estimand, seeds, tests,
output values and its `scientifically_valid` field are not inputs to this
proposal, are not reproduced by it, and are not evidence for or against it.
This proposal does not claim to preserve, continue or be equivalent to the
historical method.

## 2. Biopeia contracts this proposal is written against

| Contract | Revision | Standing |
|---|---|---|
| `organism:src/organism/actuation/evidence.py::CausalEvidenceLedger` — intervention rows, passive windows, opportunity counts | `biopeia/organism@b19a390` | Implemented, source-unit tested; not assembled by any production runtime |
| `organism:src/organism/actuation/model.py::controllability_confidence` — zero action-linked hits yield zero | `biopeia/organism@b19a390`; `organism:MIGRATION.md`, "zero action-linked hits cannot imply causal controllability" | Zero-hit invariant is owner-ratified. The positive-confidence estimator is **not** ratified ([biopeia/organism#42](https://github.com/biopeia/organism/issues/42), open) |
| `organism:src/organism/actuation/effects.py::EffectSpace` — effect identity from quantised change on Organism-prefixed features | `biopeia/organism@b19a390` | Implemented |
| ADR-0074, ADR-0098 — World owns causal integration and commit; Environment owns external environmental truth | `biopeia/docs@2c414f7` | Accepted |
| ADR-0102 — Lab composes studies and intervenes explicitly; it owns no Organism, World or Environment state | `biopeia/docs@2c414f7` | Accepted |
| ADR-0101, ADR-0078 — interventions are explicit attributable requests; Observation is causally passive | `biopeia/docs@2c414f7` | Accepted |
| ADR-0090, ADR-0108 — causal time is explicit, never host wall-clock; entropy entering causal state is explicit and controlled | `biopeia/docs@2c414f7` | Accepted |

The ledger answers one question about a source and an effect with four
integers: `action_n`, `action_hits`, `other_n`, `other_hits`. `other` is every
other retained row in the same context — passive windows **and** rows of every
other source (finding F-0103, recorded in biopeia/organism#42). That interface,
not any particular score computed from it, is the method under test.

## 3. Question

When an unobserved variable raises both the probability that an action is
issued and the probability that a sensory change occurs, does the contrast
between action-linked windows and passive windows, as counted by the Organism
evidence ledger, differ from the contrast produced by a change the action
actually causes?

The answer bears on what evidence is admissible for causal confidence. It does
not bear on whether an Organism learns, perceives or controls anything.

## 4. Causal variables

One observation unit is a **window**: a fixed span of causal ticks in which
either one motor command of a single fixed intervention signature is issued, or
none is.

| Variable | Meaning | Owner | Visible to the Organism |
|---|---|---|---|
| `U` | Binary state drawn independently for each window | Environment (external truth) | **No** — not transduced into any signal, not encoded in `context_ref`, state references or effect features |
| `A` | 1 if the command is issued in the window, 0 if the window is passive | Issued by the study's controller as an explicit, attributable Lab intervention (ADR-0101, ADR-0102) | Yes, as its own command |
| `Y` | 1 if the target effect identifier is observed in the window, else 0 | Change is committed by World; effect identity is assigned by Organism's `EffectSpace` on Organism-prefixed features | Yes |

Two factors are crossed.

**Channel structure** (how `Y` is generated):

| Condition | Structure | Interventional effect of `A` on `Y` |
|---|---|---|
| `DIRECT` | `A → Y`; `Y` independent of `U` | positive |
| `CONFOUNDED` | `U → Y`; `Y` independent of `A` given `U` | zero |
| `NULL` | `Y` independent of `A` and `U` | zero |

`NULL` is the negative control and `DIRECT` the positive control. They are
derived from the causal question (one arm per edge that may or may not exist),
not from the historical channel list.

**Assignment regime** (how `A` is generated):

| Regime | Rule | Purpose |
|---|---|---|
| `SELF` | `P(A=1 | U=u) = a_u`, with `0 < a_0 < 1`, `0 < a_1 < 1` | The confounded evidence stream the method is tested on |
| `RAND` | `A` drawn from a seeded stream independent of `U` | Empirical reference for the interventional effect |

Confounding strength is summarised by
`κ = P(U=1 | A=1) − P(U=1 | A=0)`, which follows from `P(U=1)`, `a_0` and
`a_1`. The design includes `κ = 0` (that is, `a_0 = a_1`) as an internal
negative control within `CONFOUNDED`, and at least `⟨K⟩` further levels of `κ`.

In `SELF`, the dependence of `A` on `U` is constructed by the study controller.
It stands for any unrecorded influence on action initiation; it is not a claim
about how an Organism comes to act. Routing `U` through a transduced signal
into Organism arbitration is a different study and is out of scope (§10).

## 5. Estimand

Target of inference, per channel condition `c`, in a single context:

```text
τ_c = P(Y=1 | do(A=1)) − P(Y=1 | do(A=0))
```

`τ_c` is known by construction (`τ_CONFOUNDED = τ_NULL = 0`, `τ_DIRECT > 0`)
and is also estimated from the `RAND` regime as a check on the fixture.

Quantity under test, per run, from the ledger's opportunity counts for the one
intervention signature, with passive windows as the only other rows:

```text
δ = action_hits / action_n − other_hits / other_n
```

**Primary estimand:** the bias of the action-linked contrast under confounded
assignment, `β_c = E[δ | c, SELF] − τ_c`, with `β_CONFOUNDED` as the primary
quantity.

**Stated prediction.** In `CONFOUNDED`, elementary probability gives

```text
E[δ | CONFOUNDED, SELF] = (P(Y=1 | U=1) − P(Y=1 | U=0)) · κ
```

so the contrast is predicted to be positive whenever `U` moves both
quantities, to scale linearly in `κ`, and to vanish at `κ = 0`. This follows
from the definition of the counts and from no measurement. It predicts that a
count contrast over self-assigned rows does **not** separate `CONFOUNDED` from
`DIRECT`. The study exists to check that prediction against the real ledger
and effect pipeline, to size the bias, and to leave a fixture against which
any estimator later proposed under biopeia/organism#42 can be tested.

**Secondary, descriptive only:** the value of
`controllability_confidence(action_n, action_hits, other_n, other_hits)` at the
pinned Organism revision. It is reported per cell and carries no decision
rule, because the estimator is not ratified.

## 6. Control and baseline

- **Baseline for `δ`:** passive windows only. The fixture has exactly one
  competence, one intervention signature and one context, so `other` contains
  no competing source. This removes the pooling described in F-0103 by design;
  the study therefore says nothing about multi-source ledgers.
- **Negative controls:** `NULL` in both regimes; `CONFOUNDED` at `κ = 0`;
  `CONFOUNDED` in `RAND`.
- **Positive control:** `DIRECT` in both regimes.
- **Conformance check, not a scientific result:** every cell with
  `action_hits = 0` must give a `controllability_confidence` of exactly zero,
  per the ratified invariant. A violation is a software defect to report to
  Organism, and voids the run.

## 7. Units and time basis

- **Unit of observation:** one window. **Unit of analysis:** one seeded run,
  yielding one ledger per cell (channel condition × regime × `κ` level).
  Windows within a run are not independent replicates; inference is across
  seeds.
- **Time:** causal ticks named explicitly per ADR-0090; no host wall-clock
  value enters the fixture, the ledger or the analysis. Action windows and
  passive windows have the same length `⟨L⟩` ticks. Windows are
  non-overlapping with strictly increasing ticks, enforced by the fixture
  because the ledger does not enforce it. `⟨W⟩` washout ticks separate
  consecutive windows.
- **Latency:** `Y` is read within the window that contains the command. The
  fixture's change must complete within `⟨L⟩` ticks; a condition with
  cross-window carry-over is out of scope.
- **Effect identity:** the fixture's change magnitude must map to one stable
  effect identifier under `EffectSpace` quantisation, and no-change must map
  to no effect. Features carry Organism prefixes assigned through the normal
  transduction path, not labels supplied by Lab.
- **Capacity:** windows per run are chosen so that neither ledger list evicts
  (defaults at the pinned revision: 4096 intervention rows, 1024 passive
  rows). A run in which eviction occurred is void.
- **Quantities:** `δ`, `τ`, `β`, `κ` are differences of probabilities,
  dimensionless, in `[−1, 1]`.

## 8. Seed and configuration policy

- A fresh seed set of size `⟨N⟩` is written into the reviewed revision of this
  document before any execution. `⟨N⟩` is fixed in advance from a stated
  precision target for `β_CONFOUNDED`; no run is added or dropped after
  results are seen.
- Seeds are unique (`lab.studies.common.pairing.assert_unique_seeds`), disjoint
  from the historical design seeds in the source `experiment.toml` and from
  every seed used during fixture development or piloting
  (`assert_disjoint_seeds`), and identical across all cells
  (`assert_paired_seeds`).
- `U`, the assignment of `A`, and any noise in `Y` are drawn from separately
  named streams derived from the run seed. No operating-system entropy enters
  causal state (ADR-0108).
- The full configuration — `P(U=1)`, `a_0`, `a_1`, the conditional
  probabilities of `Y`, `⟨L⟩`, `⟨W⟩`, windows per run, the `κ` levels — is
  frozen and digested before execution. These are fixture parameters, to be
  chosen by the Lab owner so that both values of `A` occur under both values
  of `U`; none is proposed here.

## 9. Admissible evidence

Admissible, if and only if all of the following hold for a run:

- executed from clean trees at commits of Lab, Organism, World, Environment
  and Embodiment that are recorded with the run, under a recorded run
  identity;
- produced under an accepted revision of this protocol, with the frozen
  configuration digest and a preregistered seed;
- accompanied by the ledger export for each cell and its digest, the
  realised counts of `U`, `A`, `Y` per cell, and the fixture's statement of
  `τ_c`;
- passing every validity check in §11.

Not admissible: the historical `results.json` or anything derived from it;
pilot or development runs; runs from a modified tree; runs that reused a seed;
any cell with eviction or a failed validity check; a value of
`controllability_confidence` offered as a causal finding.

## 10. Limitations

- The world of the study is synthetic, binary, single-source, single-context,
  with `U` independent across windows. Nothing transfers to a situated
  Organism without further work.
- `SELF` assignment is built by the study controller. The study does not show
  that an Organism's own action selection is or is not confounded.
- The study evaluates a count contrast and reports an unratified score. It
  neither validates nor refutes any estimator, and settles none of the open
  questions in biopeia/organism#42.
- Passive-only baselines are imposed by design; the behaviour of `other` with
  competing sources is untested here.
- Effect identity depends on a quantisation whose resolution is an
  implementation property of the pinned revision.
- A result here is a property of this fixture at these revisions.

## 11. Analysis

Fixed before execution; no analysis is added after results are seen without
being labelled exploratory.

1. **Validity checks, per run.** (a) `U` appears in no Organism-visible
   feature, state reference or `context_ref`. (b) Both values of `A` occur
   under both values of `U`. (c) Realised `κ` is within `⟨t_κ⟩` of its design
   value. (d) No eviction; ticks strictly increasing; windows length-matched.
   (e) In `RAND`, the estimate of `τ_c` agrees with its constructed value
   within `⟨t_τ⟩`. A run failing any check is void, and is reported as void.
2. **Per cell and seed:** read the four opportunity counts through the
   ledger's query for the intervention signature; compute `δ`.
3. **Across seeds:** for each cell report the mean of `δ` with a
   `⟨1−α⟩` interval over seeds by `⟨interval method⟩`, using seed-paired
   differences (`lab.studies.common.statistics.paired_deltas`) for every
   between-cell comparison.
4. **Comparisons:** `δ(CONFOUNDED, SELF)` against `δ(NULL, SELF)`;
   `δ(DIRECT, SELF)` against `δ(NULL, SELF)`; `δ(CONFOUNDED, SELF)` across
   `κ` levels against the predicted line of §5; each `SELF` cell against its
   `RAND` counterpart.

## 12. Falsification criteria

`⟨ε⟩` is an equivalence margin and `⟨m⟩` a minimum contrast, both to be fixed
by the Lab owner with a written rationale before execution.

| Claim | Falsified when |
|---|---|
| **H-distinguish:** the action-linked contrast over self-assigned rows separates a caused change from a hidden-common-cause change | the interval for `δ(CONFOUNDED, SELF) − δ(NULL, SELF)` lies wholly above `⟨ε⟩` at any `κ > 0` level |
| **H-bias-model:** the bias is the one predicted in §5 | `δ(CONFOUNDED, SELF)` departs from `(P(Y=1|U=1) − P(Y=1|U=0)) · κ` by more than `⟨ε⟩` at any level, including a non-zero contrast at `κ = 0` |
| **H-sensitivity:** the contrast detects a caused change | the interval for `δ(DIRECT, SELF) − δ(NULL, SELF)` does not lie wholly above `⟨m⟩` |
| **H-exogenous:** exogenous assignment removes the bias | the interval for `δ(CONFOUNDED, RAND) − δ(NULL, RAND)` is not wholly inside `±⟨ε⟩` |

Reading of outcomes:

- `H-distinguish` falsified, the other three not: the predicted result. Rows
  from self-assigned actions do not by themselves support causal confidence
  in this fixture; exogenously assigned rows do.
- `H-distinguish` **not** falsified: contradicts §5. Treat first as a fixture
  or analysis defect and investigate before any interpretation.
- `H-sensitivity` or `H-exogenous` falsified, or any validity failure: the
  fixture is not fit for the question. The study is inconclusive, not
  negative.

No outcome licenses a statement about agency, ownership of consequences, or
the behaviour of a living Organism.

## 13. Feasibility and dependencies

Open at the revisions in §2; each blocks execution, none blocks review of the
method.

- No production composition reports transitions and passive windows to the
  ledger. A study fixture that does so through declared Organism, World and
  Environment surfaces does not exist. This is the reopen trigger recorded in
  lab#59.
- Lab does not depend on Organism. Using the ledger requires an Organism
  surface declared for study use and an explicit Lab integration pin; Lab
  must not import Organism internals as a shortcut.
- Environment has no declared way to hold a per-window state that is
  guaranteed absent from transduction. Check (a) of §11 needs one.
- The estimator question in biopeia/organism#42 is open. A ratified estimator
  would be added as a further quantity under test in a revised protocol.

## 14. Review and acceptance record

| Step | Required by | State | Record |
|---|---|---|---|
| Independent Advisor review of the method | lab#59 | PENDING | — |
| Lab owner fixes every `⟨…⟩` value | this document | PENDING | — |
| Lab owner scientific acceptance | lab#59 | PENDING | — |
| Feasibility confirmed against an available fixture | lab#59 trigger | PENDING | — |

Until every row is complete, this protocol must not be executed and no claim
may cite it as a method in force.

## 15. Non-claims

No scientific validity, efficacy, reproducibility, equivalence, method or
estimand preservation, transferability or Biopeia result is claimed. No
historical source bytes are copied, moved or deleted. No experiment, campaign
or pilot was run to write this document. It introduces no physiology, no
cognition semantics and no production behaviour.
