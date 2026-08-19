"""
Sizes every capability lane against the real token supply from the Session 5
dataset inventory, and reports how many epochs each lane needs.

A lane above ~1 epoch repeats data. A lane far above it is not a mixture
decision at all -- it is a synthesis project.

    python scripts/supply_check.py
"""
BUDGET_B = 2000.0

# real available tokens (B), from widget_9 dataset inventory / widget_1 SUPPLY_T
SUPPLY = {
    "Web":          4500.0,   # DCLM-Baseline, FineWeb-Edu, D1/D2 V4 web
    "Code":         1100.0,   # The Stack v2, D3 Code, CommitPack
    "Indic":         275.9,   # Sangraha A/B/C, IndicCorpV2, BPCC, Samanantar
    "STEM":          250.0,   # proof-pile-2, peS2o, D4 STEM
    "Long-context":  100.0,   # repo-packed 32K+, book-length corpora
    "Reasoning":      80.1,   # AON (V4), OpenR1-Math, NuminaMath  -- see caveat
    "Agentic":         0.63,  # SWE-Gym, SWE-smith, OpenHands, ToolBench, Glaive, Nexus
}
SHARE = {"Web": 25, "Code": 26, "Indic": 12, "STEM": 17,
         "Long-context": 8, "Reasoning": 10, "Agentic": 2}

INDIC_TIERS = {                     # tier: (tokens, our use fraction)
    "A verified native":   (64.0,  1.00),
    "B unverified crawl":  (44.9,  1.00),
    "C translated":       (167.0,  0.785),
    "D synthetic":          (0.0,  0.00),   # nothing in the inventory is tagged D
}


def verdict(ep: float) -> str:
    if ep <= 1.0:  return "covered"
    if ep <= 2.0:  return "repetition"
    if ep <= 4.0:  return "heavy repetition"
    return "SYNTHESIS REQUIRED"


def main() -> None:
    assert sum(SHARE.values()) == 100, f"shares sum to {sum(SHARE.values())}"
    print(f"budget {BUDGET_B:.0f}B\n")
    print(f"{'lane':14s}{'share':>7s}{'demand':>10s}{'supply':>10s}{'epochs':>9s}   verdict")
    for lane in sorted(SHARE, key=lambda k: -SHARE[k]):
        d, s = BUDGET_B * SHARE[lane] / 100, SUPPLY[lane]
        print(f"{lane:14s}{SHARE[lane]:6d}%{d:9.0f}B{s:9.1f}B{d/s:9.2f}   {verdict(d/s)}")

    print(f"\ntotal catalogued supply {sum(SUPPLY.values()):,.0f}B\n")
    print("Indic tier split")
    lane = BUDGET_B * SHARE["Indic"] / 100
    used = 0.0
    for tier, (tok, frac) in INDIC_TIERS.items():
        used += tok * frac
        note = "  <- nothing in the inventory is tagged D" if tok == 0 else ""
        print(f"  {tier:22s} supply {tok:6.1f}B   we use {tok*frac:6.1f}B ({frac:.0%}){note}")
    print(f"  {'TOTAL':22s} {'':13s}        {used:6.1f}B  vs lane demand {lane:.0f}B")
    print(f"  discarded (weakest translated/transliterated): "
          f"{sum(t for t, _ in INDIC_TIERS.values()) - used:.1f}B")

    print("\ncaveat: the inventory lists 'AON (V4 corpus)' at 78.0B in the reasoning lane,")
    print("while the V4 corpus breakdown describes the same 78.1B pool as")
    print("bench_train 11.2B + indic_guaranteed 66.9B. If those are the same tokens the")
    print("reasoning lane double-counts Indic and its real size is ~13B, not 80B.")


if __name__ == "__main__":
    main()
