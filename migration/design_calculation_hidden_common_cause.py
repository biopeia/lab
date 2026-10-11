"""Design calculation for the hidden-common-cause protocol proposal (biopeia/lab#59, #70).

Everything here is a statistical model of sections 4-5 of
``protocol-proposal-action-linked-hidden-common-cause.md``: windows are independent draws
of (U, A, Y) with P(Y=1 | A, U) = b + tau*A + gamma*U. No Biopeia component is imported or
exercised. This is not a run of the study fixture and produces no admissible evidence.
Every number it prints is a PROPOSED value for the Lab owner, not a ratified parameter.

Run:  python migration/design_calculation_hidden_common_cause.py
Needs numpy and scipy (not Lab dependencies; the design calculation is not part of the package).
"""

from __future__ import annotations

from math import sqrt

import numpy as np
from scipy import stats

MC_SEED = 20261011
MC_TRIALS = 20_000

# ---- proposed fixture parameters -------------------------------------------------------
P_U = 0.5  # P(U=1): balanced, and it gives the widest attainable range of kappa
P_A = 0.5  # marginal P(A=1) at every level: balanced action/passive counts
KAPPAS = (0.0, 0.22, 0.44, 0.66)  # a_1 = P_A + kappa/2 must stay below 1
# condition: (b, tau, gamma)
CONDITIONS = {
    "NULL": (0.25, 0.0, 0.0),
    "DIRECT": (0.25, 0.25, 0.0),
    "CONFOUNDED": (0.25, 0.0, 0.3),
    "MIXED": (0.25, 0.25, 0.3),
    "MASKED": (0.5, 0.25, -0.45),  # b = 0.5 keeps every probability positive
}
WINDOWS = 1800  # per cell and run; bounded by the passive capacity (see capacity())
PASSIVE_CAPACITY = 1024  # ledger default at the pinned Organism revision

# ---- owner choices (conventional defaults, shown with alternatives) ----------------------
ALPHA = 0.05
POWER = 0.9

SMALLEST_BIAS = min(abs(g) for _, _, g in CONDITIONS.values() if g) * KAPPAS[1]
EPSILON = SMALLEST_BIAS / 2  # strictly below the smallest bias of interest
SMALLEST_TAU = min(t for _, t, _ in CONDITIONS.values() if t)
M_MARGIN = SMALLEST_TAU / 2  # strictly below the smallest effect to detect
K_NONZERO = len(KAPPAS) - 1
CELLS = len(CONDITIONS) * len(KAPPAS)


def assignment(kappa: float, rand: bool) -> tuple[float, float]:
    return (P_A, P_A) if rand else (P_A - kappa / 2, P_A + kappa / 2)


def cell(condition: str, kappa: float, *, rand: bool = False, windows: int = WINDOWS) -> dict:
    """Expected contrast and its per-run variance for one cell."""
    b, tau, gamma = CONDITIONS[condition]
    a0, a1 = assignment(kappa, rand)
    u1_given_a1 = P_U * a1 / P_A
    u1_given_a0 = P_U * (1 - a1) / (1 - P_A)
    p1 = b + tau + gamma * u1_given_a1
    p0 = b + gamma * u1_given_a0
    n1, n0 = windows * P_A, windows * (1 - P_A)
    return {
        "a0": a0,
        "a1": a1,
        "kappa": u1_given_a1 - u1_given_a0,
        "p1": p1,
        "p0": p0,
        "delta": p1 - p0,
        "var": p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0,
        "p_min": min(b + tau * a + gamma * u for a in (0, 1) for u in (0, 1)),
        "p_max": max(b + tau * a + gamma * u for a in (0, 1) for u in (0, 1)),
    }


def critical(seeds: int, k: int, alpha: float) -> float:
    return float(stats.t.ppf(1 - alpha / (2 * k), seeds - 1))


def seeds_superiority(gap: float, sd: float, k: int, power: float, alpha: float) -> int:
    """Smallest N with P(interval wholly beyond the margin) >= power, true value `gap` past it."""
    for seeds in range(2, 5000):
        if stats.norm.cdf(gap / (sd / sqrt(seeds)) - critical(seeds, k, alpha)) >= power:
            return seeds
    raise ValueError("no N found")


def seeds_equivalence(eps: float, sd: float, k: int, power_each: float, alpha: float) -> int:
    """Smallest N with P(interval wholly inside +-eps) >= power_each, true difference zero."""
    for seeds in range(2, 5000):
        if 2 * stats.norm.cdf(eps / (sd / sqrt(seeds)) - critical(seeds, k, alpha)) - 1 >= power_each:
            return seeds
    raise ValueError("no N found")


def analytic_plan(
    *, eps: float = EPSILON, m: float = M_MARGIN, windows: int = WINDOWS,
    power: float = POWER, alpha: float = ALPHA,
) -> dict[str, int]:
    """Seeds required per claim. Paired cells are treated as independent (conservative)."""
    null_var = cell("NULL", 0.0, windows=windows)["var"]
    confounded = cell("CONFOUNDED", KAPPAS[1], windows=windows)
    masked = cell("MASKED", KAPPAS[-1], windows=windows)
    direct = cell("DIRECT", 0.0, windows=windows)
    sd_u = max(sqrt(cell(c, k, windows=windows)["var"]) for c in CONDITIONS for k in KAPPAS)
    sd_r = max(sqrt(cell(c, 0.0, rand=True, windows=windows)["var"]) for c in CONDITIONS)
    return {
        "H-sufficient": seeds_superiority(
            confounded["delta"] - eps, sqrt(confounded["var"] + null_var), K_NONZERO, power, alpha
        ),
        "H-necessary": seeds_superiority(
            eps - masked["delta"], sqrt(masked["var"] + null_var), 1, power, alpha
        ),
        "H-sensitivity": seeds_superiority(
            direct["delta"] - m, sqrt(direct["var"] + null_var), 1, power, alpha
        ),
        # "supported" needs every one of the cells inside the margin: per-cell power**CELLS
        "H-bias-model": seeds_equivalence(eps, sd_u, CELLS, power ** (1 / CELLS), alpha),
        "H-exogenous": seeds_equivalence(eps, sd_r, CELLS, power ** (1 / CELLS), alpha),
    }


# ---- Monte Carlo on sufficient statistics (exact for the sampling model) -----------------
def simulate(rng, condition: str, kappa: float, rand: bool, runs: int, shift: float = 0.0):
    """Per-run (delta, delta minus prediction at realised kappa, kappa_hat, passive count).

    Draws the four (A, U) cell counts and the hits in each; identical in distribution to
    drawing every window. `shift` adds a constant to P(Y=1 | A=1) for size checks.
    """
    b, tau, gamma = CONDITIONS[condition]
    a0, a1 = assignment(kappa, rand)
    probs = [(1 - P_U) * (1 - a0), P_U * (1 - a1), (1 - P_U) * a0, P_U * a1]  # (A,U)=00,01,10,11
    n00, n01, n10, n11 = rng.multinomial(WINDOWS, probs, size=runs).T
    y00 = rng.binomial(n00, b)
    y01 = rng.binomial(n01, b + gamma)
    y10 = rng.binomial(n10, b + tau + shift)
    y11 = rng.binomial(n11, b + tau + gamma + shift)
    action, passive = n10 + n11, n00 + n01
    delta = (y10 + y11) / action - (y00 + y01) / passive
    kappa_hat = n11 / action - n01 / passive
    return delta, delta - (tau + gamma * kappa_hat), kappa_hat, passive, action


def intervals(x: np.ndarray, seeds: int, k: int, alpha: float = ALPHA):
    x = x.reshape(-1, seeds)
    mean, se = x.mean(1), x.std(1, ddof=1) / sqrt(seeds)
    crit = critical(seeds, k, alpha)
    return mean - crit * se, mean + crit * se


def monte_carlo(seeds: int, trials: int = MC_TRIALS) -> dict[str, float]:
    """Power of each claim's predicted outcome at `seeds`. Cells are simulated independently."""
    rng = np.random.default_rng(MC_SEED + seeds)
    runs = seeds * trials

    def contrast_vs_null(condition, kappa, shift=0.0):
        return (
            simulate(rng, condition, kappa, False, runs, shift)[0]
            - simulate(rng, "NULL", kappa, False, runs)[0]
        )

    out = {}
    low, _ = intervals(contrast_vs_null("CONFOUNDED", KAPPAS[1]), seeds, K_NONZERO)
    out["H-sufficient falsified"] = float((low > EPSILON).mean())
    _, high = intervals(contrast_vs_null("MASKED", KAPPAS[-1]), seeds, 1)
    out["H-necessary falsified"] = float((high < EPSILON).mean())
    low, _ = intervals(contrast_vs_null("DIRECT", 0.0), seeds, 1)
    out["H-sensitivity supported"] = float((low > M_MARGIN).mean())
    for name, rand in (("H-bias-model supported", False), ("H-exogenous supported", True)):
        inside = np.ones(trials, dtype=bool)
        for condition in CONDITIONS:
            for kappa in KAPPAS:
                sim = simulate(rng, condition, kappa, rand, runs)
                # H-exogenous is defined on delta - tau; only H-bias-model uses realised kappa
                x = sim[0] - CONDITIONS[condition][1] if rand else sim[1]
                low, high = intervals(x, seeds, CELLS)
                inside &= (low > -EPSILON) & (high < EPSILON)
        out[name] = float(inside.mean())
    out["all five as predicted (independent claims)"] = float(np.prod(list(out.values())))
    # size: true value exactly at the margin must be called at most alpha/(2k) of the time
    low, _ = intervals(contrast_vs_null("NULL", KAPPAS[1], shift=EPSILON), seeds, K_NONZERO)
    out["size: superiority at the margin"] = float((low > EPSILON).mean())
    low, high = intervals(simulate(rng, "NULL", 0.0, True, runs, shift=EPSILON)[0], seeds, CELLS)
    out["size: equivalence at the margin"] = float(((low > -EPSILON) & (high < EPSILON)).mean())
    return out


def capacity() -> dict[int, float]:
    """P(passive windows exceed the passive capacity) for one ledger, by windows per run."""
    return {n: float(stats.binom.sf(PASSIVE_CAPACITY, n, 1 - P_A)) for n in (1700, 1800, 1900, 2000)}


def invalidity() -> dict[str, float]:
    """Tolerances for validity checks (d) and (g) and the void rate they imply when correct."""
    spacing = min(b - a for a, b in zip(KAPPAS, KAPPAS[1:]))
    t_kappa = spacing / 2  # a run executed at a neighbouring level is always caught
    void_kappa = 0.0
    for kappa in KAPPAS:
        p1, p0 = (1 + kappa) / 2, (1 - kappa) / 2  # P(U=1 | A=1), P(U=1 | A=0)
        sd = sqrt(p1 * (1 - p1) / (WINDOWS * P_A) + p0 * (1 - p0) / (WINDOWS * (1 - P_A)))
        void_kappa += 2 * stats.norm.sf(t_kappa / sd)
    sd_n = sqrt(2 * WINDOWS * P_A * (1 - P_A))  # action_n(RAND) - action_n(U_ASSIGNED)
    t_n = round(4.5 * sd_n)
    void_n = len(KAPPAS) * 2 * stats.norm.sf(t_n / sd_n)
    void_capacity = (len(KAPPAS) + 1) * stats.binom.sf(PASSIVE_CAPACITY, WINDOWS, 1 - P_A)
    smallest_cell = P_U * (P_A - KAPPAS[-1] / 2)
    void_positivity = 4 * (1 - smallest_cell) ** WINDOWS
    per_run = void_kappa + void_n + void_capacity + void_positivity
    detect = {
        shift: float(stats.norm.sf((t_n - shift * WINDOWS) / sd_n) + stats.norm.cdf((-t_n - shift * WINDOWS) / sd_n))
        for shift in (0.04, 0.08)
    }
    return {
        "t_kappa": t_kappa, "t_n": t_n, "sd_action_n_difference": sd_n,
        "void_per_run": float(per_run),
        "detect_P(A)_off_by_0.04_per_run": detect[0.04],
        "detect_P(A)_off_by_0.08_per_run": detect[0.08],
    }


def main() -> None:
    import scipy

    print(f"numpy {np.__version__}, scipy {scipy.__version__}, MC seed {MC_SEED}, trials {MC_TRIALS}")
    print(f"epsilon = {EPSILON:.4g} (smallest bias {SMALLEST_BIAS:.4g} / 2), m = {M_MARGIN:.4g}")
    print("\n## cells, U_ASSIGNED: condition kappa a0 a1 P(Y|A=1) P(Y|A=0) delta sd_run p_min p_max")
    for condition in CONDITIONS:
        for kappa in KAPPAS:
            c = cell(condition, kappa)
            print(
                f"{condition:11} {kappa:.2f} {c['a0']:.2f} {c['a1']:.2f} {c['p1']:.4f} {c['p0']:.4f} "
                f"{c['delta']:+.4f} {sqrt(c['var']):.4f} {c['p_min']:.2f} {c['p_max']:.2f}"
            )
    print("\n## seeds required per claim (analytic)")
    print("base", analytic_plan())
    for eps in (0.022, EPSILON, 0.044):
        print(f"epsilon {eps:.3g}", analytic_plan(eps=eps))
    for windows in (900, 1400, WINDOWS):
        print(f"windows {windows}", analytic_plan(windows=windows))
    for power in (0.8, POWER, 0.95):
        print(f"power {power}", analytic_plan(power=power))
    for alpha in (ALPHA, 0.01):
        print(f"alpha {alpha}", analytic_plan(alpha=alpha))
    print("\n## capacity: P(passive > 1024) per ledger", capacity())
    inv = invalidity()
    print("\n## invalidity", {k: (round(v, 8) if isinstance(v, float) else v) for k, v in inv.items()})
    for seeds in (24, 26):
        p = inv["void_per_run"]
        print(
            f"seeds {seeds}: P(no void) {stats.binom.pmf(0, seeds, p):.6f}, "
            f"P(2 or more voids) {stats.binom.sf(1, seeds, p):.2e}"
        )
    print("\n## Monte Carlo power by seeds (standard error at most", round(0.5 / sqrt(MC_TRIALS), 4), ")")
    for seeds in (19, 20, 22, 24, 26):
        print(seeds, {k: round(v, 4) for k, v in monte_carlo(seeds).items()})


if __name__ == "__main__":
    main()
