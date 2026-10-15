# Protocol proposal — action-linked evidence under a hidden common cause

**Status: PROPOSED. Reviewed by the owner-designated Advisor. A fresh-context reviewer reviewed an earlier candidate (`abe1f93`); the subsequent changes at merged HEAD `948f35b0a05e73d038cb9b7c03d7bb920572e36d` were not re-reviewed. The final revision has no independent review; not accepted, not executed.**

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
`(0, 1)` and no `A × U` interaction. Additivity is a property of the
mechanism, not only of these probabilities: in every condition a window
contains **at most one** target change, produced by a single random event
whose probability is `b + τ·a + γ·u`, and that change always has the same
size. The fixture must not build `MIXED` or `MASKED` from two separate
increments on the target feature, which could sum into another magnitude
class or cancel.

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

The counts are read with the ledger's atom query for the target atom, with
`field="intervention_signature_id"`, the one signature as the only value, and
the cell's `context_ref`. Every row of a cell — action and passive — carries
that same `context_ref`; the ledger totals are per context, so a passive row
written with a different or null reference would leave `other_n` at zero.

`δ` is defined only when `action_n > 0` and `other_n > 0`; see §11 for cells
where it is not. At the pinned revision the ledger counts a window with no
observed change among the opportunities (a row with no effect identifier is
indexed like any other), so quiet action and passive windows enter `action_n`
and `other_n` and the denominators are the numbers of windows.

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
windows as the only `other` rows; every window written to the ledger; and a
ledger hit being exactly a change the fixture generated (§7, reconciliation).
Each is enforced by design (§6, §7) or checked (§8, §11).

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
- **Conformance observation, not a scientific result and not a validity
  check:** every cell with `action_hits = 0` should give a
  `controllability_confidence` of exactly zero, per the ratified invariant. A
  violation is reported to Organism as a software defect. It does not void a
  run, because it is triggered by the outcome.

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
  — and no-change must produce no atom on the target feature. At the pinned
  revision a change is quantised as `round(7·x)`, so the fixed change size
  must be well above 1/14 and away from the edges between magnitude classes.
  A window keeps at most 16 atoms, sorted by size and then by feature name;
  the fixture must keep the number of changing Organism-visible features in a
  window at 16 or fewer, so that no ordering can drop the target atom. The
  return of the target feature to its baseline is an opposite-direction
  change, hence a different atom; it must occur inside the washout, and the
  feature must not saturate.
- **Reconciliation:** for every window, the target atom is in that window's
  ledger row if and only if the fixture generated the change in that window.
  This is exact, not statistical. It is established in fixture qualification
  (§8) and re-checked over the whole study; a single mismatch means the
  pipeline does not record what the fixture produced, and invalidates the
  study as a whole — it is not grounds for voiding individual runs. Features carry
  Organism prefixes assigned through the normal transduction path, not labels
  supplied by Lab.
- **Capacity:** windows per run are chosen so that neither ledger list evicts
  (constructor defaults at the pinned revision: 4096 intervention rows and a
  quarter of that, 1024, passive rows; these are defaults, not properties of
  the ledger). A run in which eviction occurred is void.
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
  run on `⟨N_q⟩` development seeds. It passes when all of the following hold:
  the reconciliation of §7 is exact in every window; in each `RAND_ASSIGNED`
  cell the mean of `δ` is within `⟨t_q⟩` of the constructed `τ_c`; and in
  every cell the variance of `δ` across development runs is at most `⟨r⟩`
  times the binomial value assumed by the design calculation. Development
  seeds are disjoint from the study seeds and their runs are not admissible
  evidence. A fixture that fails is corrected and re-qualified on fresh
  development seeds, each attempt being recorded; the study seeds are not
  touched until it passes. If the variance criterion fails for a reason that
  is a property of the fixture and not a defect, `⟨N⟩` is recalculated before
  it is frozen.
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

1. `⟨ε⟩` is set strictly below the smallest bias of interest — the smallest
   `|γ|·κ` among the planned non-zero `κ` levels — and `⟨m⟩` strictly below
   the smallest `τ` the study is meant to detect. A margin equal to the
   quantity it is compared with could never be exceeded by an interval.
2. For one run, with `n_1` action windows and `n_0` passive windows and hit
   probabilities `p_1`, `p_0`,
   `Var(δ) ≈ p_1(1 − p_1)/n_1 + p_0(1 − p_0)/n_0`.
   Windows per run and `⟨N⟩` are chosen so that each claim of §12 reaches
   power `⟨1−β⟩` in its own sense:
   - equivalence claims (`H-bias-model`, `H-exogenous`): probability at least
     `⟨1−β⟩` that the interval lies wholly inside `±⟨ε⟩` when the true
     difference is zero;
   - `H-sufficient`: probability at least `⟨1−β⟩` that the interval lies
     wholly above `⟨ε⟩` when the true contrast is the smallest planned `γ·κ`;
   - `H-sensitivity`: the same with `⟨m⟩` and the smallest planned `τ`;
   - `H-necessary`: probability at least `⟨1−β⟩` that the interval lies
     wholly below `⟨ε⟩` at the largest `κ` level under the design values.
3. Windows per run are capped so that the expected number of passive windows
   at the design `P(A=0)`, plus a stated margin, stays below the passive
   capacity, and action windows below the intervention capacity.
4. The fixture parameters must give both values of `A` under both values of
   `U` in every run with stated probability, and keep every
   `P(Y=1 | A, U)` inside `(0, 1)`. In `MASKED`, at the largest `κ` level
   `|γ|·κ` must be at least `τ`, so that the masking claim is testable.
5. A criterion evaluated at `k` levels of `κ` uses simultaneous intervals at
   level `1 − α/k` (Bonferroni), so that its interval statements hold jointly
   across those levels. `k` is stated per criterion in §12.
6. Sensitivity of the chosen values to the fixture parameters is reported,
   including the largest inflation of per-run variance over the binomial
   model that the chosen `⟨N⟩` tolerates; `⟨r⟩` is set at or below it.
7. `⟨N⟩` is recalculated if `⟨ε⟩`, the windows per run, the multiplicity rule
   or the measured variance changes.

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
runs that reused a seed; any run with eviction or a failed validity check; a
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
   failed, are reported. If the void rate exceeds `⟨v⟩` the fixture is not
   fit for the question and no claim is evaluated. A void run is removed
   whole, in every cell, before any pairing; pairs are never dropped
   individually.
3. **Per cell and seed:** read the four atom opportunity counts through the
   ledger's query for the target atom and the intervention signature; compute
   `δ`. Record the realised `P(Y=1 | U)` beside its design value.
4. **Across seeds:** for each cell report the mean of `δ` with a
   `⟨1−α⟩` interval over seeds by `⟨interval method⟩`, using seed-paired
   differences (`lab.studies.common.statistics.paired_deltas`) for every
   between-cell comparison.
5. **Comparisons:** exactly those of §12 — `D(c)` for `CONFOUNDED`, `MASKED`
   and `DIRECT`; each `U_ASSIGNED` cell against the predicted `τ_c + γ_c·κ`;
   each `RAND_ASSIGNED` cell against `τ_c`.

## 12. Falsification criteria

`⟨ε⟩` is an equivalence margin and `⟨m⟩` a minimum contrast, fixed under §8.
With `⟨K⟩` non-zero levels of `κ`, a criterion evaluated at `k` levels uses
simultaneous intervals at level `1 − α/k`, so that the error rate of each
claim is set before any result exists. In the predictions, `τ_c` and `γ_c` are
the frozen design values and `κ` is the realised value of the run. `D(c)`
denotes `δ(c, U_ASSIGNED) − δ(NULL, U_ASSIGNED)` at the same `κ` level.

Every claim has exactly three outcomes. It is **supported** when its
"supported" condition holds, **falsified** when its "falsified" condition
holds, and **inconclusive** in every other case — an interval straddling a
margin, an interval on the side neither condition names, or an unmet
side-condition. Inconclusive neither supports nor falsifies. `τ_c` in the
claims is the value fixed by construction, not an estimate.

| Claim | Evaluated at | Supported when | Falsified when |
|---|---|---|---|
| **H-sufficient:** over `U`-assigned rows, a contrast above `⟨ε⟩` implies `τ > 0` | the `⟨K⟩` non-zero `κ` levels | at every level the interval for `D(CONFOUNDED)` lies wholly inside `±⟨ε⟩` | at any level the interval for `D(CONFOUNDED)` lies wholly above `⟨ε⟩`, where `τ = 0` by construction |
| **H-necessary:** over `U`-assigned rows, `τ > 0` implies a contrast above `⟨ε⟩` | the largest `κ` level | the interval for `D(MASKED)` lies wholly above `⟨ε⟩` | the interval for `D(MASKED)` lies wholly below `⟨ε⟩` **and** the side-condition holds: in every `MASKED` `RAND_ASSIGNED` cell the `H-exogenous` interval, at the `H-exogenous` level, lies wholly inside `±⟨ε⟩`, so that `τ > 0` is shown in the fixture and not only assumed |
| **H-bias-model:** the contrast is the one predicted in §5 | every `U_ASSIGNED` cell: 5 conditions × `⟨K⟩ + 1` levels, `κ = 0` included | in every cell the interval for `δ − (τ_c + γ_c·κ)` lies wholly inside `±⟨ε⟩` | in any cell that interval lies wholly outside `±⟨ε⟩` |
| **H-sensitivity:** without confounding the contrast detects a caused change | `DIRECT` at `κ = 0` | the interval for `D(DIRECT)` lies wholly above `⟨m⟩` | that interval lies wholly below `⟨m⟩` |
| **H-exogenous:** exogenous assignment removes the bias | every `RAND_ASSIGNED` cell, one per condition and paired level | in every cell the interval for `δ − τ_c` lies wholly inside `±⟨ε⟩` | in any cell that interval lies wholly outside `±⟨ε⟩` |

Reading of outcomes:

- `H-sufficient` and `H-necessary` falsified, and `H-bias-model`,
  `H-sensitivity` and `H-exogenous` supported: the predicted result. In this
  fixture, a count contrast over rows from `U`-dependent assignment supports
  neither the presence nor the absence of a causal effect, while over
  exogenously assigned rows it equals the constructed effect within the
  margin. That is a statement about this fixture; it validates no estimator.
- `H-sufficient` or `H-necessary` **supported**: contradicts §5. Treat first
  as a fixture or analysis defect and investigate before any interpretation.
- `H-bias-model`, `H-sensitivity` or `H-exogenous` falsified, or the void
  rate above its limit: the fixture is not fit for the question. The study
  says nothing about the question.
- Any claim inconclusive: the study was underpowered for that claim. It is
  reported as inconclusive and is not read in either direction.

**What kind of study this is.** Once the reconciliation of §7 holds, every
claim above follows from arithmetic on counts the fixture itself produced,
and §5 derives the predicted outcome without measurement. No observable
result could then count against §5 except a defect in the fixture or in the
pipeline between fixture and ledger. The study therefore tests whether the
real ledger and effect pipeline record what the sampling model assumes.
Whether to keep it framed as a falsification test, or to label it a
conformance study of that pipeline — which a deterministic check could also
provide — is a decision for the Lab owner (§14) and is not made here.

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
| Review by a fresh-context reviewer with no part in the draft | owner decision of 2026-10-11 (option B) | RECORDED | Report posted verbatim on lab#70 at head `abe1f93`. Limits: its brief was written by the protocol's author, and it was not blind to the two errors corrected earlier. Its required changes are incorporated in this revision; whether they are incorporated correctly has not been re-reviewed |
| Study framing: falsification test or conformance study (§12) | independent review, finding F-06 | PENDING | Lab owner decision |
| Reviewer suggestions not adopted: a less conservative interval rule, five randomised cells instead of twenty, additional control arms, an across-seed check on assignment | independent review, findings F-09, F-10, F-11, F-14 | PENDING | Lab owner decision; each would be a protocol change |
| Design calculation proposing a value for each `⟨…⟩` | §8; authorized by the Lab owner 2026-10-11 | PROPOSED | [`protocol-design-calculation-hidden-common-cause.md`](protocol-design-calculation-hidden-common-cause.md). Statistical model only; proposes, does not ratify |
| Lab owner fixes every `⟨…⟩` value under §8 | this document | PENDING | — |
| Fixture qualification on development seeds (§8) | this document | PENDING | It is itself an execution and needs the Lab owner's authorization before it is run |
| Lab owner scientific acceptance | lab#59 | PENDING | — |
| Feasibility confirmed against an available fixture | lab#59 trigger | PENDING | — |

Until every row is complete, this protocol must not be executed and no claim
may cite it as a method in force.

## 15. Non-claims

No scientific validity, efficacy, reproducibility, equivalence, method or
estimand preservation, transferability or Biopeia result is claimed. No
historical source bytes are copied, moved or deleted. No experiment, campaign
or pilot was run. The separately authorized design calculation uses the
sampling model of §4–§5 only and exercises no Biopeia component. It introduces no
physiology, no cognition semantics and no production behaviour.
