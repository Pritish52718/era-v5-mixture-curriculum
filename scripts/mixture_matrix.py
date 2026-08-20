"""
Builds the V5 master schedule: 7 capability lanes x 5 pretraining stages.

Two hard constraints:
  * every lane's token-weighted average across stages == its headline share
  * every stage's lane shares sum to 100%

Solved by RAS (iterative proportional fitting) in TOKEN space, where it is a
standard matrix-balancing problem: row sums = lane budgets, column sums = stage
budgets, and both total the full training budget.

    python scripts/mixture_matrix.py
"""
import numpy as np

BUDGET_B = 2000.0                                   # billions of tokens
STAGES   = ["seed", "general", "reasoning", "long-ctx", "anneal"]
DUR      = np.array([5, 55, 22, 15, 3]) / 100       # stage durations
STAGE_B  = BUDGET_B * DUR                           # 100 / 1100 / 440 / 300 / 60

LANES    = ["Web", "Indic", "Code", "STEM", "Reasoning", "Long-context", "Agentic"]
SHARE    = np.array([25.0, 12.0, 26.0, 17.0, 10.0, 8.0, 2.0])   # headline %, sums to 100

# Three rows are DECIDED, not fitted. Indic follows its tier plan (cheap romanized
# transliteration early, Tier A held for the anneal); reasoning enters late; agentic is
# zero until the reasoning stage because it has no cheap tier to spend on early exposure.
FIXED = {
    "Indic":     np.array([30.6,  9.4, 10.3, 15.0, 26.0]),
    "Reasoning": np.array([ 1.0,  6.1, 17.1, 13.6, 27.0]),
    "Agentic":   np.array([ 0.0,  0.0,  2.0,  7.6, 14.0]),
}

# The anneal column is pinned by hand: it is the scarcest, most contested stage.
ANNEAL_PCT = np.array([2.5, 26.0, 22.0, 7.0, 27.0, 1.5, 14.0])

# Shape priors for the four fitted lanes over stages 1-4, from what each stage is FOR.
FITTED = ["Web", "Code", "STEM", "Long-context"]
PRIOR = np.array([
    [55, 34, 11,  5],    # Web           high early, fades
    [ 8, 26, 26, 24],    # Code          ramps into general, stays high
    [ 4, 17, 22, 15],    # STEM          peaks at the reasoning stage
    [ 1,  4, 10, 22],    # Long-context  concentrated at its own stage
], dtype=float)


def solve(iters: int = 60_000) -> np.ndarray:
    assert abs(SHARE.sum() - 100) < 1e-9, f"lane shares sum to {SHARE.sum()}, not 100"
    assert abs(ANNEAL_PCT.sum() - 100) < 1e-9, "pinned anneal column must sum to 100"

    idx = [LANES.index(l) for l in FITTED]
    fixed_tok = sum(FIXED[l][:4] * STAGE_B[:4] / 100 for l in FIXED)
    row = np.array([SHARE[i] * BUDGET_B / 100 - ANNEAL_PCT[i] * STAGE_B[4] / 100 for i in idx])
    col = STAGE_B[:4] - fixed_tok

    M = PRIOR * col / 100.0
    for _ in range(iters):                  # RAS: alternately fit rows, then columns
        M *= (row / M.sum(1))[:, None]
        M *= (col / M.sum(0))[None, :]

    pct = np.zeros((len(LANES), 5))
    for lane, v in FIXED.items():
        pct[LANES.index(lane)] = v
    for k, i in enumerate(idx):
        pct[i, :4] = M[k] / STAGE_B[:4] * 100
    pct[:, 4] = ANNEAL_PCT
    return pct


def report(pct: np.ndarray) -> None:
    print(f"budget {BUDGET_B:.0f}B   1% = {BUDGET_B/100:.0f}B\n")
    print(f"{'lane':14s}" + "".join(f"{s:>11s}" for s in STAGES) + f"{'AGG':>8s}{'target':>8s}")
    for i, lane in enumerate(LANES):
        print(f"{lane:14s}" + "".join(f"{x:10.1f}%" for x in pct[i])
              + f"{pct[i] @ DUR:7.2f}%{SHARE[i]:7.1f}%")
    cols = pct.sum(0)
    print(f"{'TOTAL':14s}" + "".join(f"{x:10.1f}%" for x in cols))

    row_err = max(abs(pct[i] @ DUR - SHARE[i]) for i in range(len(LANES)))
    col_err = abs(cols - 100).max()
    print(f"\nmax row error {row_err:.4f}pp   max column error {col_err:.4f}pp")
    assert row_err < 0.05 and col_err < 0.15, "constraints violated"

    print("\ntokens per lane per stage (B):")
    print(f"{'lane':14s}" + "".join(f"{s:>11s}" for s in STAGES) + f"{'total':>9s}")
    for i, lane in enumerate(LANES):
        t = pct[i] * STAGE_B / 100
        print(f"{lane:14s}" + "".join(f"{x:10.1f}B" for x in t) + f"{t.sum():8.1f}B")


if __name__ == "__main__":
    report(solve())
