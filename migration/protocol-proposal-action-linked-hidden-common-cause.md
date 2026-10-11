# Protocol proposal — action-linked evidence under a hidden common cause

**Status: PROPOSED. Reviewed by the owner-designated Advisor; not accepted, not executed.**

- Tracking issue: [biopeia/lab#59](https://github.com/biopeia/lab/issues/59), bounded child of [biopeia/lab#45](https://github.com/biopeia/lab/issues/45).
- Work class: SCIENTIFIC (protocol design). Scientific acceptance authority: Lab owner (`alessbarb`).
- Lab base revision: `273c41207332ef7c7de02de625253d03d642a200`.
- This document proposes a method. It contains no result, authorizes no run, and
  sets no numeric threshold. Every quantity written `⟨…⟩` is an open value that
  the Lab owner must fix, under the parameter-selection policy of §8, in a
  reviewed revision of this document, before any execution.
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

- Organism pin: `biopeia/organism@b19a39079b57a65f00eaecbe2c5cee3427a54f80` (`origin/main` when written).
- Docs pin: `biopeia/docs@2c414f7d546075f961046fc5cc9ac2b67ea46514`.

| Contract | Revision | Standing |
|---|---|---|
| `organism:src/organism/actuation/evidence.py::CausalEvidenceLedger` — intervention rows, passive windows, opportunity counts per effect and per atom (`atom_opportunities`) | Organism pin | Implemented, source-unit tested; not assembled by any production runtime |
| `organism:src/organism/actuation/model.py::controllability_confidence` — zero action-linked hits yield zero | same revision; `organism:MIGRATION.md`, "zero action-linked hits cannot imply causal controllability" | Zero-hit invariant is owner-ratified. The positive-confidence estimator is **not** ratified ([biopeia/organism#42](https://github.com/biopeia/organism/issues/42), open) |
| `organism:src/organism/actuation/effects.py` — `EffectSpace.signature` (quantised change on Organism-prefixed features), `EffectAtom` (one feature, one direction, one of three magnitude classes), at most 16 atoms kept per transition, largest change first | Organism pin | Implemented |
| ADR-0074, ADR-0098 — World owns causal integration and commit; Environment owns external environmental truth | Docs pin | Accepted |
| ADR-0102 — Lab composes studies and intervenes explicitly; it owns no Organism, World or Environment state | Docs pin | Accepted |
| ADR-0101, ADR-0078 — interventions are explicit attributable requests; Observation is causally passive | Docs pin | Accepted |
| ADR-0090, ADR-0108 — causal time is explicit, never host wall-clock; entropy entering causal state is explicit and controlled | Docs pin | Accepted |

The ledger answers one question about a source and an effect or atom with four
integers: `action_n`, `action_hits`, `other_n`, `other_hits`. `other` is every
other retained row in the same context — passive windows **and** rows of every
other source (finding F-0103, recorded in biopeia/organism#42). That interface,
not any particular score computed from it, is the method under test.

A whole-transition effect identifier is a hash of **every** quantised feature
change in the window. If issuing a command moves any other Organism-visible
feature, action windows and passive windows receive different effect
identifiers even when the target channel changes identically, and a contrast on
effect identifiers would measure co-occurring features, not the target change.
The outcome of this study is therefore defined on one atom (§4).

## 3. Question

When an unobserved variable changes both the probability that an action is
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
| `U` | Binary state drawn independently for each window | Environment (external truth) | **Not as such.** Where a condition has a `U → Y` edge it reaches the Organism only through its influence on `Y`; otherwise not at all. No other feature, state reference or `context_ref` carries it in any condition |
| `A` | 1 if the command is issued in the window, 0 if the window is passive | Requested by the study's controller as an explicit, attributable Lab intervention (ADR-0101, ADR-0102); how such a request becomes a ledger row is a feasibility gap (§13) | Yes, as an issued command |
| `Y` | 1 if the **target atom** — one named feature of the target channel, one direction, one magnitude class — is among the atoms observed in the window, else 0 | Change is committed by World; atom identity is assigned by Organism from Organism-prefixed features | Yes |

Two factors are crossed.

**Channel structure** (how `Y` is generated). The fixture is additive by
construction: `P(Y=1 | A=a, U=u) = b + τ·a + γ·u`, with every value inside
`(0, 1)` and no `A × U` interaction.

| Condition | `τ` (effect of `A`) | `γ` (effect of `U`) | Role |
|---|---|---|---|
| `DIRECT` | positive | zero | positive control |
| `CONFOUNDED` | zero | positive | the hidden-common-cause case |
| `NULL` | zero | zero | negative control |
| `MIXED` | positive | positive | a real effect inflated by confounding |
| `MASKED` | positive | negative | a real effect hidden by confounding |

The conditions are one arm per combination of the two edges that may or may
not exist, plus the sign of confounding. They are derived from the causal
question, not from the historical channel list.

**Assignment regime** (how `A` is generated):

| Regime | Rule | Purpose |
|---|---|---|
| `U_ASSIGNED` | `P(A=1 | U=u) = a_u`, with `0 < a_0 < 1`, `0 < a_1 < 1` | The confounded evidence stream the method is tested on |
| `RAND_ASSIGNED` | `A` drawn from a seeded stream independent of `U`, with `P(A=1)` equal to the marginal of its paired `U_ASSIGNED` cell, `P(U=1)·a_1 + P(U=0)·a_0` | Empirical reference for the interventional effect |

A `RAND_ASSIGNED` cell differs from its paired `U_ASSIGNED` cell **only** in
the assignment stream. The `U` stream, the mechanism generating `Y`, the window
schedule, the context reference and the intervention signature are identical,
seed for seed.

Confounding strength is summarised by
`κ = P(U=1 | A=1) − P(U=1 | A=0)`, which follows from `P(U=1)`, `a_0` and
`a_1`. The design includes `κ = 0` (that is, `a_0 = a_1`) as an internal
negative control, and at least `⟨K⟩` further levels of `κ`.

In both regimes the command is requested by the study controller. Neither
regime is self-initiated action, and neither says anything about how an
Organism comes to act: `U_ASSIGNED` is an externally synthesised dependence of
action on `U`, standing for any unrecorded influence on action initiation.
Routing `U` through a transduced signal into Organism arbitration is a
different study and is out of scope (§10).

## 5. Estimand

Target of inference, per channel condition `c`, in a single context:

```text
τ_c = P(Y=1 | do(A=1)) − P(Y=1 | do(A=0))
```

`τ_c` is known by construction. That the fixture reproduces it under
`RAND_ASSIGNED` is established beforehand, in fixture qualification on
development seeds (§8), and tested on the study seeds as `H-exogenous` (§12);
it is never a condition for keeping a run.

Quantity under test, per run, from the ledger's **atom** opportunity counts
for the target atom and the one intervention signature, with passive windows
as the only other rows:

```text
δ = action_hits / action_n − other_hits / other_n
```

`δ` is defined only when `action_n > 0` and `other_n > 0`; see §11 for cells
where it is not.

**Primary estimand:** the bias of the action-linked contrast under
`U`-dependent assignment, `β_c = E[δ | c, U_ASSIGNED] − τ_c`, with
`β_CONFOUNDED` as the primary quantity.

**Stated prediction.** For independent windows and the additive fixture of §4,
elementary probability gives, in every condition,

```text
E[δ | c, U_ASSIGNED]    = τ_c + γ_c · κ
E[δ | c, RAND_ASSIGNED] = τ_c
```

so in `CONFOUNDED` the contrast is `γ·κ`: positive whenever `U` moves both
quantities, linear in `κ`, and zero at `κ = 0`. In `MIXED` the contrast
overstates `τ`; in `MASKED` it understates it and can reach zero or change
sign. This follows from the definition of the counts and from no measurement.
It predicts that a positive count contrast over `U`-assigned rows is **neither
sufficient nor necessary** for `τ > 0`. The study exists to check that
prediction against the real ledger and effect pipeline, to size the bias, and
to leave a fixture against which any estimator later proposed under
biopeia/organism#42 can be tested — including one that must not erase the real
effect in `MIXED`.

The identity depends on: windows independent and identically distributed
within a cell; no carry-over between windows; no `A × U` interaction; passive
windows as the only `other` rows; every window written to the ledger. Each is
enforced by design (§6, §7) or checked (§11).

**Secondary, descriptive only:** the value of
`controllability_confidence(action_n, action_hits, other_n, other_hits)` at the
pinned Organism revision. It is reported per cell and carries no decision
rule, because the estimator is not ratified.

## 6. Control and baseline

- **Baseline for `δ`:** passive windows only. The fixture has exactly one
  competence, one intervention signature and one context, so `other` contains
  no competing source. This removes the pooling described in F-0103 by design;
  the study therefore says nothing about multi-source ledgers.
- **Negative controls:** `NULL` in both regimes; every condition at `κ = 0`;
  `CONFOUNDED` in `RAND_ASSIGNED`.
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
- **Latency and censoring:** `Y` is read within the window that contains the
  command. The fixture's change must complete within `⟨L⟩` ticks; a condition
  with cross-window carry-over is out of scope. Every scheduled window is
  written to the ledger. A window cut short by the end of a run is not
  written and not counted; the schedule is fixed in advance so that this
  affects no window by design.
- **Outcome identity:** the fixture's change must map to the target atom —
  same feature, direction and magnitude class in every window where it occurs
  — and no-change must produce no atom on the target feature. A window keeps
  at most 16 atoms, largest change first; the fixture must keep the number of
  changing Organism-visible features within that bound, or the target change
  among the largest, so the target atom is never dropped. Features carry
  Organism prefixes assigned through the normal transduction path, not labels
  supplied by Lab.
- **Capacity:** windows per run are chosen so that neither ledger list evicts
  (defaults at the pinned revision: 4096 intervention rows, 1024 passive
  rows). A run in which eviction occurred is void.
- **Quantities:** `δ`, `τ`, `γ`, `β`, `κ` are differences of probabilities,
  dimensionless, in `[−1, 1]`.

## 8. Seed, configuration and parameter-selection policy

- A fresh seed set of size `⟨N⟩` is written into the reviewed revision of this
  document before any execution. No run is added or dropped after results are
  seen.
- Seeds are unique (`lab.studies.common.pairing.assert_unique_seeds`), disjoint
  from the historical design seeds in the source `experiment.toml` and from
  every seed used during fixture development or piloting
  (`assert_disjoint_seeds`), and identical across all cells
  (`assert_paired_seeds`).
- **Fixture qualification.** Before the study seeds are used, the fixture is
  run on development seeds to confirm that it reproduces the constructed
  `τ_c` under `RAND_ASSIGNED` and emits the target atom as specified.
  Development seeds are disjoint from the study seeds and their runs are not
  admissible evidence. A fixture that fails qualification is corrected and
  re-qualified; the study seeds are not touched until it passes.
- `U`, the assignment of `A`, and any noise in `Y` are drawn from separately
  named streams derived from the run seed. No operating-system entropy enters
  causal state (ADR-0108).
- The full configuration — `P(U=1)`, `a_0`, `a_1`, `b`, `τ`, `γ` per
  condition, `⟨L⟩`, `⟨W⟩`, windows per run, the `κ` levels — is frozen and
  digested before execution. These are fixture parameters; none is proposed
  here.

**How the open values are to be chosen.** No value is ratified on judgement
alone. Each is derived, in a written design calculation attached to the
revision that fixes it, as follows:

1. `⟨ε⟩` is anchored to the smallest bias of interest: the smallest `γ·κ`
   among the planned non-zero `κ` levels. `⟨m⟩` is anchored to the smallest
   `τ` the study is meant to detect.
2. For one run, with `n_1` action windows and `n_0` passive windows and hit
   probabilities `p_1`, `p_0`,
   `Var(δ) ≈ p_1(1 − p_1)/n_1 + p_0(1 − p_0)/n_0`.
   Windows per run and `⟨N⟩` are chosen so that the `⟨1−α⟩` interval for each
   seed-paired difference of §11 has half-width at most `⟨ε⟩/2`, with power
   `⟨1−β⟩` to detect a difference of `⟨ε⟩`.
3. Windows per run are capped so that the expected number of passive windows
   at the design `P(A=0)`, plus a stated margin, stays below the passive
   capacity, and action windows below the intervention capacity.
4. The fixture parameters must give both values of `A` under both values of
   `U` in every run with stated probability, and keep every
   `P(Y=1 | A, U)` inside `(0, 1)`. In `MASKED`, at the largest `κ` level
   `|γ|·κ` must be at least `τ`, so that the masking claim is testable.
5. Criteria evaluated at `K` levels of `κ` use simultaneous intervals at
   level `1 − α/K` (Bonferroni), so that every interval statement in §12
   holds jointly across levels.
6. Sensitivity of the chosen values to the fixture parameters is reported.

The design calculation uses only the sampling model written in this document.
It is not a run of the study, exercises no Biopeia component, and yields no
admissible evidence.

## 9. Admissible evidence

Admissible, if and only if all of the following hold for a run:

- executed from clean trees at commits of Lab, Organism, World, Environment
  and Embodiment that are recorded with the run, under a recorded run
  identity;
- produced under an accepted revision of this protocol, with the frozen
  configuration digest and a preregistered seed;
- accompanied by the ledger export for each cell and its digest, the
  realised counts of `U`, `A`, `Y` per cell, and the fixture's statement of
  `τ_c` and `γ_c`;
- passing every validity check in §11.

Not admissible: the historical `results.json` or anything derived from it;
pilot or development runs; design calculations; runs from a modified tree;
runs that reused a seed; any cell with eviction or a failed validity check; a
value of `controllability_confidence` offered as a causal finding.

## 10. Limitations

- The world of the study is synthetic, binary, single-source, single-context,
  additive, with `U` independent across windows. Nothing transfers to a
  situated Organism without further work.
- Assignment in both regimes is built by the study controller. The study does
  not show that an Organism's own action selection is or is not confounded,
  and must not be cited for that.
- With an `A × U` interaction the interventional effect depends on the
  distribution of `U` and the identity of §5 does not hold; that case is out
  of scope.
- The study evaluates a count contrast and reports an unratified score. It
  neither validates nor refutes any estimator, and settles none of the open
  questions in biopeia/organism#42.
- Passive-only baselines are imposed by design; the behaviour of `other` with
  competing sources is untested here.
- Outcome identity depends on a quantisation and a three-class magnitude
  scale that are implementation properties of the pinned revision.
- A result here is a property of this fixture at these revisions.

## 11. Analysis

Fixed before execution; no analysis is added after results are seen without
being labelled exploratory.

1. **Validity checks, per run.** A run failing any check is void, in all its
   cells, and is reported as void. No check depends on the observed outcome
   `Y`: voiding runs on an outcome would select the runs on which the
   hypotheses are then tested, and, because paired cells share a seed, would
   bias the primary estimand.
   (a) Apart from the target channel in conditions with a `U → Y` edge, `U`
   appears in no Organism-visible feature, state reference or `context_ref`.
   (b) Both values of `A` occur under both values of `U`.
   (c) `action_n > 0` and `other_n > 0` in every cell.
   (d) Realised `κ` is within `⟨t_κ⟩` of its design value.
   (e) No eviction; ticks strictly increasing; windows length-matched; every
   scheduled window present in the ledger.
   (f) In the fixture's own record of the changes it generated, each
   generated target change is the target atom and no other atom on the target
   feature. This is checked against what the fixture emitted, not against
   ledger hit counts.
   (g) In each `RAND_ASSIGNED` cell, realised `action_n` is within `⟨t_n⟩` of
   its paired `U_ASSIGNED` cell.
2. **Void rate.** The number and fraction of void runs, and the check each
   failed, are reported. If the void rate exceeds `⟨v⟩` the study is
   inconclusive.
3. **Per cell and seed:** read the four atom opportunity counts through the
   ledger's query for the target atom and the intervention signature; compute
   `δ`. Record the realised `P(Y=1 | U)` beside its design value.
4. **Across seeds:** for each cell report the mean of `δ` with a
   `⟨1−α⟩` interval over seeds by `⟨interval method⟩`, using seed-paired
   differences (`lab.studies.common.statistics.paired_deltas`) for every
   between-cell comparison.
5. **Comparisons:** each `U_ASSIGNED` cell against `NULL`; each `U_ASSIGNED`
   cell against the predicted `τ_c + γ_c·κ` across `κ` levels; each
   `U_ASSIGNED` cell against its `RAND_ASSIGNED` counterpart.

## 12. Falsification criteria

`⟨ε⟩` is an equivalence margin and `⟨m⟩` a minimum contrast, fixed under §8.
Criteria evaluated at `K` levels of `κ` use simultaneous intervals at level
`1 − α/K`, so that the error rate of each claim is set before any result
exists. A claim of equivalence is supported only by an interval wholly inside
its margin; an interval that straddles the margin is inconclusive, not
support.
In the predictions, `τ_c` and `γ_c` are the frozen design values and `κ` is
the realised value of the run.

| Claim | Falsified when |
|---|---|
| **H-sufficient:** over `U`-assigned rows, an action-linked contrast above `⟨ε⟩` implies `τ > 0` | the interval for `δ(CONFOUNDED, U_ASSIGNED) − δ(NULL, U_ASSIGNED)` lies wholly above `⟨ε⟩` at any `κ > 0` level, where `τ = 0` by construction |
| **H-necessary:** over `U`-assigned rows, `τ > 0` implies an action-linked contrast above `⟨ε⟩` | the interval for `δ(MASKED, U_ASSIGNED) − δ(NULL, U_ASSIGNED)` lies wholly below `⟨ε⟩` at any `κ > 0` level, while `τ > 0` by construction and confirmed in `RAND_ASSIGNED` |
| **H-bias-model:** the contrast is the one predicted in §5 | in any `U_ASSIGNED` cell the interval for `δ − (τ_c + γ_c·κ)` is not wholly inside `±⟨ε⟩`, `κ = 0` included |
| **H-sensitivity:** without confounding the contrast detects a caused change | the interval for `δ(DIRECT, U_ASSIGNED) − δ(NULL, U_ASSIGNED)` does not lie wholly above `⟨m⟩` |
| **H-exogenous:** exogenous assignment removes the bias | in any `RAND_ASSIGNED` cell the interval for `δ − τ_c` is not wholly inside `±⟨ε⟩` |

Reading of outcomes:

- `H-sufficient` and `H-necessary` falsified, and `H-bias-model`,
  `H-sensitivity` and `H-exogenous` each supported by an interval meeting its
  criterion: the predicted result. In this fixture, rows from `U`-dependent assignment
  support neither the presence nor the absence of a causal effect;
  exogenously assigned rows do.
- `H-sufficient` or `H-necessary` **not** falsified: contradicts §5. Treat
  first as a fixture or analysis defect and investigate before any
  interpretation.
- `H-bias-model`, `H-sensitivity` or `H-exogenous` not supported, or the void
  rate above its limit: the fixture is not fit for the question. The study is
  inconclusive, not negative.

No outcome licenses a statement about agency, ownership of consequences, the
behaviour of a living Organism, or the validity of any estimator.

## 13. Feasibility and dependencies

Open at the revisions in §2; each blocks execution, none blocks review of the
method. All are post-migration scientific work.

- No production composition reports transitions and passive windows to the
  ledger. A study fixture that does so through declared Organism, World and
  Environment surfaces does not exist. This is the reopen trigger recorded in
  lab#59.
- Lab does not depend on Organism. Using the ledger requires an Organism
  surface declared for study use — including the atom-level opportunity query
  for an intervention signature — and an explicit Lab integration pin; Lab
  must not import Organism internals as a shortcut.
- Environment has no declared way to hold a per-window state whose only
  route to the Organism is one named channel. Check (a) of §11 needs one.
- In both regimes the command is requested by Lab, yet a ledger row
  records an attempt and intervention signature as Organism actuation. No
  declared surface lets an attributable Lab-requested command enter Organism
  actuation and the ledger; ADR-0101 makes such a request one to the owning
  authority, not a write by Lab.
- The estimator question in biopeia/organism#42 is open. A ratified estimator
  would be added as a further quantity under test in a revised protocol.

## 14. Review and acceptance record

| Step | Required by | State | Record |
|---|---|---|---|
| Method review by the owner-designated Advisor | lab#59; owner instruction of 2026-10-11 | RECORDED | Findings and outcomes on lab#70. The reviewer also advised on the draft, so this is not an independent review in the sense of the review policy |
| Lab owner fixes every `⟨…⟩` value under §8 | this document | PENDING | — |
| Lab owner scientific acceptance | lab#59 | PENDING | — |
| Feasibility confirmed against an available fixture | lab#59 trigger | PENDING | — |

Until every row is complete, this protocol must not be executed and no claim
may cite it as a method in force.

## 15. Non-claims

No scientific validity, efficacy, reproducibility, equivalence, method or
estimand preservation, transferability or Biopeia result is claimed. No
historical source bytes are copied, moved or deleted. No experiment, campaign,
pilot or design simulation was run to write this document. It introduces no
physiology, no cognition semantics and no production behaviour.
