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

# The anneal column is pinned by hand: it is the scarcest, most contested stage
# and we want code high in it. Everything else is fitted around it.
ANNEAL_PCT = np.array([2.5, 26.0, 22.0, 7.0, 27.0, 1.5, 14.0])

# Shape priors for the first four stages, derived from what each stage is FOR.
# RAS moves these as little as it can while satisfying both constraints.
PRIOR = np.array([
    [55, 34, 11,  5],    # Web           high early, fades
    [30,  9, 10, 15],    # Indic         script early, Tier A late
    [ 8, 26, 26, 24],    # Code          ramps into general, stays high
    [ 4, 17, 22, 15],    # STEM          peaks at the reasoning stage
    [ 1,  6, 17, 14],    # Reasoning     enters late
    [ 1,  4, 10, 22],    # Long-context  concentrated at its own stage
    [.01,.01, 2, 7.6],   # Agentic       ZERO until reasoning; no cheap tier to spend early
], dtype=float)


def solve(iters: int = 50_000) -> np.ndarray:
    assert abs(SHARE.sum() - 100) < 1e-9, f"lane shares sum to {SHARE.sum()}, not 100"
    assert abs(ANNEAL_PCT.sum() - 100) < 1e-9, "pinned anneal column must sum to 100"

    lane_tokens = BUDGET_B * SHARE / 100
    anneal_tok  = ANNEAL_PCT * STAGE_B[-1] / 100
    row = lane_tokens - anneal_tok          # tokens left per lane for stages 1-4
    col = STAGE_B[:4]                       # capacity of stages 1-4

    M = PRIOR * col / 100.0
    for _ in range(iters):                  # RAS: alternately fit rows then columns
        M *= (row / M.sum(1))[:, None]
        M *= (col / M.sum(0))[None, :]
    return np.column_stack([M / col * 100, ANNEAL_PCT])


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
