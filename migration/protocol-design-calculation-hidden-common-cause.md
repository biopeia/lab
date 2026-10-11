# Design calculation — hidden-common-cause protocol

**Status: PROPOSED VALUES. Not ratified, not accepted, not used in any run.**

- Belongs to [`protocol-proposal-action-linked-hidden-common-cause.md`](protocol-proposal-action-linked-hidden-common-cause.md)
  (biopeia/lab#59, PR biopeia/lab#70). It applies the parameter-selection
  policy of that document's §8.
- Authorized by the Lab owner on 2026-10-11 as a design calculation that may
  use analytic calculations and statistical models. No fixture run, pilot or
  experiment on Biopeia was authorized, and none was made.
- The protocol's open values `⟨…⟩` stay open. This document proposes a value
  for each; the Lab owner decides. Nothing here is a result of the study.
- Reproduce with
  `python migration/design_calculation_hidden_common_cause.py`
  (Python 3.12.3, numpy 1.26.4, scipy 1.17.1; Monte Carlo seed `20261011`,
  20,000 trials per seed count). The script imports no Biopeia package.

## 1. What was computed, and what was not

The script evaluates the sampling model of the protocol's §4–§5: independent
windows, `U ~ Bernoulli(P(U=1))`, `A | U ~ Bernoulli(a_U)`,
`Y | A, U ~ Bernoulli(b + τ·A + γ·U)`.

- **Analytic part:** expected contrast and per-run variance per cell, and the
  number of seeds each claim of §12 needs, from normal approximations with
  Student-t critical values.
- **Monte Carlo part:** a check of those approximations on the same model. It
  draws the four `(A, U)` counts of a run and the hits in each, which has
  exactly the distribution of drawing every window. It is a **statistical
  model only**: no ledger, no effect pipeline, no Organism, World or
  Environment code. It is not a run of the study fixture and is not
  admissible evidence. It is named here so that the owner can object to it.
- **Not derivable here:** window length `⟨L⟩` and washout `⟨W⟩`. They depend
  on how long the fixture's change takes in causal ticks, which only an
  existing fixture can show. They stay open.

## 2. Proposed fixture parameters

| Parameter | Proposed | Reason |
|---|---|---|
| `P(U=1)` | 0.5 | Balanced hidden state; gives the widest attainable range of `κ` |
| Marginal `P(A=1)` | 0.5 at every level | Equal numbers of action and passive windows minimise the variance of `δ` for a given number of windows, and make the randomised cells identical in design across levels |
| `a_0`, `a_1` | `0.5 ∓ κ/2` | With the two rows above, `κ = a_1 − a_0` exactly |
| `κ` levels | 0, 0.22, 0.44, 0.66 (`⟨K⟩` = 3 non-zero) | Evenly spaced; the largest keeps `a_1 = 0.83` below 1 so both values of `A` occur under both values of `U` |
| Windows per cell and run | 1800 | Largest round number whose passive count stays under the passive capacity with negligible risk (§5) |

| Condition | `b` | `τ` | `γ` | `P(Y=1 | A, U)` range | Note |
|---|---|---|---|---|---|
| `NULL` | 0.25 | 0 | 0 | 0.25 | |
| `DIRECT` | 0.25 | 0.25 | 0 | 0.25–0.5 | |
| `CONFOUNDED` | 0.25 | 0 | 0.3 | 0.25–0.55 | |
| `MIXED` | 0.25 | 0.25 | 0.3 | 0.25–0.8 | |
| `MASKED` | 0.5 | 0.25 | −0.45 | 0.05–0.75 | `b` raised so every probability stays positive; the lowest, 0.05, is close to the boundary. `|γ|·κ = 0.297` at the largest level exceeds `τ`, so the contrast changes sign and the masking claim is testable |

Expected contrast under `U`-dependent assignment, `τ + γ·κ`:

| Condition | `κ = 0` | 0.22 | 0.44 | 0.66 |
|---|---|---|---|---|
| `NULL` | 0 | 0 | 0 | 0 |
| `DIRECT` | 0.25 | 0.25 | 0.25 | 0.25 |
| `CONFOUNDED` | 0 | 0.066 | 0.132 | 0.198 |
| `MIXED` | 0.25 | 0.316 | 0.382 | 0.448 |
| `MASKED` | 0.25 | 0.151 | 0.052 | −0.047 |

The standard deviation of `δ` in one run is between 0.020 and 0.023 in every
cell.

These numbers were chosen for this design from its own constraints. None is
taken from the historical study, and none of the historical decision
thresholds appears among them.

## 3. Proposed margins

| Value | Proposed | Derivation |
|---|---|---|
| `⟨ε⟩` | 0.033 | Half of the smallest bias of interest, `0.3 × 0.22 = 0.066`. Strictly below it, as §8 requires |
| `⟨m⟩` | 0.125 | Half of the smallest effect to detect, `τ = 0.25` |

Why half: `ε` trades two claims against each other. A smaller `ε` makes the
equivalence claims expensive; a larger one leaves `H-sufficient` little room
above the margin. Seeds required by the most demanding claim:

| `ε` | `H-sufficient` | `H-bias-model`, `H-exogenous` | Largest |
|---|---|---|---|
| 0.022 | 10 | 40 | 40 |
| **0.033** | 15 | 20 | **20** |
| 0.044 | 29 | 13 | 29 |

## 4. Proposed number of seeds

`α` and the target power are conventional choices and are the owner's to
make. The proposal uses `α = 0.05` and power 0.9, with intervals that are
simultaneous over the levels each claim is evaluated at (§12 of the protocol):
3 for `H-sufficient`, 1 for `H-necessary` and `H-sensitivity`, 20 for
`H-bias-model` and 20 for `H-exogenous`. For the two equivalence claims,
"supported" needs all 20 cells inside the margin, so the per-cell power is set
to `0.9^(1/20)`.

Seeds required per claim (analytic):

| Setting | `H-sufficient` | `H-necessary` | `H-sensitivity` | `H-bias-model` | `H-exogenous` |
|---|---|---|---|---|---|
| **`α` 0.05, power 0.9, 1800 windows** | 15 | 4 | 3 | 20 | 20 |
| power 0.8 | 12 | 4 | 3 | 19 | 19 |
| power 0.95 | 17 | 4 | 3 | 21 | 21 |
| `α` 0.01 | 19 | 6 | 4 | 24 | 24 |
| 1400 windows | 18 | 4 | 3 | 25 | 25 |
| 900 windows | 26 | 5 | 4 | 36 | 36 |

Monte Carlo check at the proposed values (standard error at most 0.0035):

| Seeds | `H-sufficient` falsified | `H-necessary` falsified | `H-sensitivity` supported | `H-bias-model` supported | `H-exogenous` supported | All five as predicted |
|---|---|---|---|---|---|---|
| 20 | 0.979 | 1.000 | 1.000 | 0.944 | 0.945 | 0.873 |
| 22 | 0.987 | 1.000 | 1.000 | 0.983 | 0.983 | 0.955 |
| 24 | 0.995 | 1.000 | 1.000 | 0.996 | 0.995 | 0.986 |
| 26 | 0.996 | 1.000 | 1.000 | 0.999 | 0.999 | 0.994 |

Error rates, checked with the true value placed exactly on the margin: a
superiority interval lies wholly beyond it in 0.8–0.9 % of trials (nominal
`α/(2·3)` = 0.83 %), and an equivalence interval lies wholly inside in
0.08–0.16 % (nominal `α/(2·20)` = 0.125 %). Both are at their nominal level
within Monte Carlo error.

**Proposed `⟨N⟩` = 22 seeds.**

- 20 is the smallest count at which every claim reaches power 0.9, analytic
  and Monte Carlo agreeing.
- The protocol forbids replacing a void run, so voids reduce the effective
  count. Two seeds of headroom keep 20 valid runs even with two voids; under
  a correct fixture two voids are far less likely than one in a million (§6).
- At 22 the probability that all five claims come out as predicted is about
  0.95. The protocol asks only for per-claim power. Whether joint power
  should be required is an owner decision; this document does not make it.
- If the owner prefers `α = 0.01`, the same reasoning gives 24 + 2 = 26.

Scale: 5 conditions × 4 levels × 2 regimes = 40 cells per seed, each with its
own ledger; 22 seeds × 40 cells × 1800 windows is about 1.6 million windows.

Two conservatisms. Paired cells share a seed and therefore their random
streams; the calculation treats them as independent, which overstates the
variance of every between-cell difference. And the Monte Carlo draws the 20
cells of an equivalence claim independently, which understates the
probability that all of them fall inside the margin. Real power should be
somewhat higher than tabulated; neither figure is exact.

One observation for the owner. With the same marginal `P(A=1)` at every level
and shared streams, the four `RAND_ASSIGNED` cells of a condition are the same
run. The protocol counts them as 20 cells and the calculation follows the
protocol; the effective number of distinct randomised cells is 5, so the
correction for `H-exogenous` is stricter than it needs to be. Changing that
would be a protocol change and is not proposed here.

## 5. Ledger capacity

Passive windows in one cell are `Binomial(windows, 0.5)`. Probability that
they exceed the passive capacity of 1024 at the pinned Organism revision:

| Windows per cell and run | Probability of eviction |
|---|---|
| 1700 | 1 × 10⁻¹⁷ |
| **1800** | 2 × 10⁻⁹ |
| 1900 | 3 × 10⁻⁴ |
| 2000 | 0.14 |

Action windows peak near 900, far below the intervention capacity of 4096.
1800 is the proposal. A fixture that configures a larger passive capacity
could use more windows and fewer seeds; that would be a different design.

## 6. Proposed invalidity thresholds

None of these depends on the outcome `Y`.

| Value | Proposed | Derivation | False void, correct fixture |
|---|---|---|---|
| `⟨t_κ⟩` | 0.11 | Half the spacing between adjacent `κ` levels, so a run executed at a neighbouring level always fails the check. The realised `κ` has standard deviation at most 0.024 | about 5 × 10⁻⁶ per run |
| `⟨t_n⟩` | 135 windows | 4.5 standard deviations of the difference in `action_n` between paired cells (standard deviation 30). A marginal `P(A=1)` wrong by 0.08 is caught in a single run with probability 0.62, and almost surely within a few runs | about 3 × 10⁻⁵ per run |
| Both values of `A` under both of `U`; non-zero denominators | — | The rarest `(A, U)` combination has probability 0.085; over 1800 windows it is never empty in practice | below 10⁻⁶⁰ |
| Eviction | — | §5 | 1 × 10⁻⁸ per run |
| `⟨v⟩` | more than 2 void runs of 22 | Overall false-void probability is about 3 × 10⁻⁵ per run. With a correct fixture the chance of even one void in 22 runs is below 0.1 %, and of two or more below one in a million. More than two therefore indicates a defect, and also leaves fewer than 20 valid runs | — |

The realised `κ` and `action_n` are the same in every condition at a given
level, because conditions share the assignment stream; the false-void figures
count one check per level, not one per cell.

`⟨t_τ⟩` no longer exists in the protocol: reproduction of the constructed
effect was moved to fixture qualification so that no run is discarded on an
outcome.

## 7. Other proposed values

| Value | Proposed | Note |
|---|---|---|
| `⟨1−α⟩` | 0.95, adjusted per claim to `1 − α/k` | Owner choice; `α = 0.01` tabulated in §4 |
| `⟨1−β⟩` | 0.9 | Owner choice; 0.8 and 0.95 tabulated in §4 |
| `⟨interval method⟩` | Student-t interval over seeds on seed-paired differences | Each run's `δ` is an average over about 900 windows per arm, so the across-seed distribution is close to normal; the error-rate check in §4 supports this at 20–26 seeds |
| Seed set | not proposed | To be drawn and written into the protocol when the owner fixes `⟨N⟩`; it must be disjoint from development seeds and from the Monte Carlo seed used here |

## 8. Limitations of this calculation

- It assumes the protocol's sampling model exactly: independent windows,
  additive effects, no carry-over, every window recorded. A fixture that
  departs from any of these needs a new calculation.
- Variances are for the model's Bernoulli outcomes. If the fixture adds
  variance the model lacks, more seeds are needed; fixture qualification on
  development seeds is where that would show.
- Fixture parameters are one admissible choice, not the only one. Power is
  most sensitive to `ε` and to windows per run (§3, §4).
- It says nothing about feasibility. The four dependencies in §13 of the
  protocol are untouched.
