# V5 Mixture & Curriculum Plan

**Budget:** 2T tokens  ·  1% = 20B tokens

**Compute.** At 6ND, a 2T run costs `6 x N_active x 2e12` FLOPs: **~1,040 GPU-days** at 3B
active parameters, ~2,430 at 7B (H100, ~40% MFU). OPUS adds a few percent of overhead and
returns roughly 6x in effective tokens. The 1B and 3B proxy runs below cost a small fraction
of this and are what the numbers in this plan are staked on.

---

## Lane: Agentic — 2%

**Share:** 2% = **40B tokens**

### Why not more
Real supply is **0.63B tokens** (SWE-Gym, SWE-smith, OpenHands rollouts, ToolBench,
Glaive, Nexus). A 9% lane would demand 180B — a **286x gap** requiring 6M verified
trajectories. At 100 parallel sandboxes that is 3.8 years. 2% is the largest share a
real pipeline can stand behind.

### Schedule

| stage | stage tokens | agentic % | tokens |
|---|---|---|---|
| seed | 100B | 0.3% | 0.3B |
| general | 1,100B | 1.0% | 11.0B |
| reasoning | 440B | 1.8% | 7.9B |
| long-context | 300B | 5.2% | 15.6B |
| **anneal** | 60B | **9.0%** | **5.4B** |
| | | | **40.2B** |

Near-zero early because an agentic trajectory presupposes language, code and tool syntax the
model does not yet have. It rises through long-context (trajectories are long by nature) and
concentrates in the anneal, which holds the **5.4B reserve** -- 13.5% of the lane. It is never
zero: 0.3% in seed means the format is familiar long before it matters.

### Where the 40B comes from

| source | tokens | how |
|---|---|---|
| existing datasets | 0.63B | download |
| cohort organic usage | 0.72B | export the cohort's own coding-assistant sessions |
| harvested GitHub `issue -> patch -> passing test` | ~5B | mine merged PRs with tests |
| **bug injection** | **~18B** | mutate working repos; existing tests are the verifier |
| **total unique** | **~24B** | |
| **epochs to reach 40B** | **~1.7** | normal repetition, not fabrication |

### Pipeline
1. Mine tasks (real PRs) and manufacture tasks (inject bugs into repos whose tests pass)
2. Attempt with an **open-weights coder model on our own GPUs** — no rate limit, no ToS issue,
   full raw trajectory
3. Execute in a **pre-built container per repo** — tool outputs cost nothing and are real
4. **Keep only trajectories whose tests pass.** The verifier filters the dataset.

Tool outputs are ~78% of a trajectory and are **loss-masked**, so they fill context, not gradient.

### Rejected alternatives
- **Subscription coding-agent products**: rate limits make 1.31M
  trajectories a 3.6-36 year job; most do not export raw token-level traces; training a
  competitor on their output violates their terms.
- **Managed per-run agent platforms:** ~58x the cost of our own containers
  ($100 vs $1.74 per 1,000 attempts) for the one component that was already cheap.

### Open uncertainty --> the pilot
Timeline spans **22 days to 5.9 months** depending on three unmeasured variables:
seconds/attempt, pass rate, tokens/trajectory.

**Proxy experiment:** build 10,000 trajectories over two weeks on ~50 repos and measure all
three. Refutation threshold: if sustained yield implies **< 12B unique tokens in 3 months**,
drop the agentic share to 1% and reallocate.

---

## Lane: Indic — 12%

**Share:** 12% = **240B tokens**  ·  **Protected floor: 12%** (lane = floor, see below)

OPUS rejects Indic outside the protected lane at ~2-5%, so **the floor is not a minimum, it
is the whole lane** (mechanism in *Protected floor* below).

### Why 12% and not more
Supply is 275.9B. At 12% we consume 240B: **100% of Tier A and Tier B**, plus the best 79%
of Tier C -- and deliberately discard the weakest **35.9B** of translated/transliterated
material. Above 12% the lane is padded with exactly the data we least want.

### Tier split against real supply

| tier | what it is | supply | our use |
|---|---|---|---|
| A verified native | human-written, checked (Sangraha verified) | 64.0B | 100% |
| B unverified crawl | Sangraha unverified 24B + IndicCorpV2 20.9B | 44.9B | 100% |
| C translated | Sangraha synthetic 162B + BPCC 3B + Samanantar 2B | 167.0B | 79% |
| D synthetic | model-generated Indic | **0B exists** | 0% |

**Splitting tier C** is a pipeline step, done by script detection in one pass:
Latin/Roman characters -> romanized transliteration (~72B, IndicXlit);
native script -> machine translation (~90B, IndicTrans2). Cheap and exact.

### Placement across the curriculum

**The mixture is a schedule, not a constant.** The 12% headline is the token-weighted
average of the per-stage shares. These match the master schedule below exactly.

| stage | stage tokens | indic | % of stage | weighted |
|---|---|---|---|---|
| seed | 100B | 30.6B | 30.6% | 1.53 pts |
| general | 1,100B | 103.4B | 9.4% | 5.17 pts |
| reasoning | 440B | 45.3B | 10.3% | 2.27 pts |
| long-context | 300B | 45.0B | 15.0% | 2.25 pts |
| **anneal** | 60B | 15.6B | **26.0%** | 0.78 pts |
| | | **240.0B** | | **12.00%** |

Stage durations: seed 5% / general 55% / reasoning 22% / long-context 15% / anneal 3%.
Tier ledger: A 64.0/64.0B = 1.00 ep · B 44.9/44.9B = 1.00 ep · C 131.1/167.0B = 0.79 ep.
The discarded 35.9B is the weakest translated and transliterated material.

### Tier placement -- bands overlap, they do not switch

A stage-boundary jump in data *quality* is what spikes the gradient norm, so no tier appears
for the first time at full strength. Every stage carries a tail of the next-harder tier.
Rows sum to the tier budgets; columns sum to the stage allocations above (both exact).

| tier | seed | general | reasoning | long-ctx | anneal | **used / budget** |
|---|---|---|---|---|---|---|
| C-romanized | 26.3B | 44.0B | 1.6B | 0.1B | — | **72.0 / 72.0B** |
| C-translated | 3.1B | 48.5B | 7.2B | 0.2B | — | **59.1 / 59.1B** |
| B unverified | 1.1B | 8.1B | 29.0B | 6.7B | — | **44.9 / 44.9B** |
| A verified | 0.1B | 2.8B | 7.5B | 38.1B | 15.6B | **64.0 / 64.0B** |
| **total** | **30.6B** | **103.4B** | **45.3B** | **45.0B** | **15.6B** | **240.0B** |

As proportions of each stage's Indic slice:

```
seed       C-rom 86.1%  ·  C-trans 10.2%  ·  B 3.5%   ·  A 0.3%
general    C-rom 42.5%  ·  C-trans 46.9%  ·  B 7.9%   ·  A 2.7%
reasoning  C-rom  3.4%  ·  C-trans 16.0%  ·  B 64.0%  ·  A 16.6%
long-ctx   C-rom  0.2%  ·  C-trans  0.4%  ·  B 14.8%  ·  A 84.6%
anneal                                                  A 99.7%
```

Tier A is present from the **seed stage at 0.3%** and reaches 2.7% in general, so by the
anneal the model has been reading verified native text for the whole run. **The anneal
concentrates Tier A; it does not introduce it.** Tier B likewise enters at 3.5% in seed, long
before it becomes the reasoning stage's main tier.

Within Tier A the anneal slice is **selected, not left over**: the 15.6B held for the cooldown
is the highest-ranked 15.6B of the 64B, not whatever long-context did not consume.

Each transition is additionally blended across a warmup band of several billion tokens rather
than switched at the stage boundary.

### Anneal reserve
**15.6B of Tier A**, held back for the cooldown -- the highest-ranked 15.6B, not the residue.
Tier A total use is 64B of 64B = 1.00 epochs.

### Hinglish / Indian English -- measured, not assumed
A script/code-mix scan of our own cleaned S4 corpus (14,073 docs) found **7 Hinglish
documents, 0.05%**, of which one is genuine. Latin 46.2%, Devanagari 22.1%, Telugu 11.7%,
Bengali/Assamese 11.2%, Odia 8.7%, Urdu 0.0%.

**We therefore fund no Hinglish share**, because no supply stands behind one. Instead we make
two pipeline changes so we stop destroying it: (1) exempt code-mixed documents from the
English-LM perplexity gate, (2) treat `hi-Latn` as a valid language label rather than a
failed English detection.

**Proxy experiment:** run the same detector over the documents the S4 pipeline *rejects*.
If Hinglish appears there, the filters are the cause and the fix is cheap. If it does not,
it was never crawled and would need deliberate sourcing. Metric: Hinglish token share of
rejected documents. Threshold: above 1% justifies a funded sub-lane.

---

## Protected floor (always-on)

```
12% Indic  +  2% agentic  =  14% of every batch, bypassing OPUS
                             86% OPUS-selected
```

**Cost of that protection:** protected tokens do not receive OPUS's ~6x effective-token
multiplier. At 14% protection the effective multiplier falls 6.00 -> 5.30, costing ~11.7%
of effective tokens. We accept it because without the floor OPUS drives Indic toward zero
and MILU / IndicGenBench go with it.

**Benchmark train-splits** total only ~0.13B tokens across our target set (SWE-bench train
~105M, MMLU auxiliary_train ~15M, MILU val ~2.2M; most targets are test-only). They are
injected at a fraction of a percent, not paired symmetrically with Indic -- at 1% of a 2T
run they would repeat 15 times.

**Monitor:** log realized Indic share per optimizer step; alarm if the 1,000-step moving
average falls below 11.5%.

---

## Lane: Reasoning — 10%

**Share:** 10.00% = **200B tokens**  ·  no protected floor (OPUS's proxy includes AIME/GPQA)

### Schedule

| stage | stage tokens | reason % | tokens | weighted |
|---|---|---|---|---|
| seed | 100B | 1.0% | 1.0B | 0.05 pts |
| general | 1,100B | 6.1% | 67.1B | 3.36 pts |
| reasoning | 440B | 17.1% | 75.2B | 3.76 pts |
| long-context | 300B | 13.6% | 40.8B | 2.04 pts |
| **anneal** | 60B | **27.0%** | 16.2B | 0.81 pts |
| | | | **200.3B** | **10.02%** |

Only 1% in seed: reasoning traces teach nothing to a model that cannot yet form a sentence.
27% in anneal: reasoning is a RESERVED lane, its best traces held for the cooldown.

### Supply

| source | tokens | tier | use |
|---|---|---|---|
| AON (V4 corpus) | 78.0B | A | pretraining |
| OpenR1-Math (R1-distilled) | 1.6B | D | **RESERVED — reasoning-training stage only** |
| NuminaMath | 0.5B | A | pretraining |

Pretraining supply 78.5B against 200B demand = **2.55 epochs**.

**Open question for review:** the inventory lists AON (V4 corpus) at 78.0B in the reasoning
lane, while the V4 corpus breakdown describes the same 78.1B AON pool as
`bench_train 11.2B + indic_guaranteed 66.9B`. If those are the same tokens, the reasoning
lane is double-counting Indic supply and its real size is ~13B, not 80B — which would make
reasoning a second synthesis problem on the scale of agentic. **This needs confirming before
the number is trusted.**

### Reasoning-effort bands — the reasoning-training stage

These are **not** a pretraining data label. B0-B5 describes the difficulty of what the model
**reads**; LOW/MEDIUM/HIGH/ULTRA describes how long the model **writes**. Effort tags are
written into the prompt and the model is taught to obey them by RL against a verifier.

| band | character | target tokens | when it should fire |
|---|---|---|---|
| **LOW** | the decisive step only | ~100 | arithmetic, lookup, one-line code |
| **MEDIUM** | the essential steps | ~400 | routine multi-step problems |
| **HIGH** | derive, then check | ~1,500 | competition problems, non-trivial debugging |
| **ULTRA** | restate, explore, verify | ~6,000 | research-level, adversarial, long-horizon |

#### One problem at all four depths

**Q. How many trailing zeros does 100! have?**  *(answer 24 in all four)*

| band | trace |
|---|---|
| **LOW** | `floor(100/5) + floor(100/25) = 20 + 4 = 24` |
| **MEDIUM** | A trailing zero needs `10 = 2 x 5`; 2s are far more common, so count 5s. `floor(100/5) = 20`, plus `floor(100/25) = 4` for the second 5 in multiples of 25. Total 24. |
| **HIGH** | `zeros = min(v2, v5)` by Legendre's formula `vp(n!) = sum_i floor(n/p^i)`. `v5 = 20 + 4 = 24` (`floor(100/125) = 0`, terminates); `v2 = 50+25+12+6+3+1 = 97`. `min(97,24) = 24` — the 5s bind, as expected. |
| **ULTRA** | Restates the goal, proves Legendre's formula from the counting argument, computes both valuations in full, argues `v2 > v5` for every `n` so the 5-count always binds, verifies against `10! = 3,628,800` (two zeros; formula gives `floor(10/5) = 2`), then answers 24. |

What changes across the bands is not the answer or its correctness — only the derivation,
checking and self-verification the model is willing to spend.

#### Supply — and the band that is actually scarce

| source | examples | approx tokens |
|---|---|---|
| **OpenThoughts2-1M** | 1M | ~2-4B (math, science, code, puzzles; R1-distilled) |
| OpenR1-Math | 0.2M | 1.6B — **already subsumed by OpenThoughts2, do not count twice** |

**R1-style distillation produces long chain-of-thought by construction.** Every published
reasoning corpus is therefore concentrated at HIGH and ULTRA. Nobody publishes short traces
because short traces are not impressive to publish.

**So the scarce bands are LOW and MEDIUM, not ULTRA** — which is the opposite of what the
supply table suggests at a glance.

#### How the tagged set gets built

| band | method | note |
|---|---|---|
| ULTRA | **harvest** | OpenThoughts2 as-is; already this length |
| HIGH | **harvest + trim** | cut the trace at its verification step |
| MEDIUM | **generate** | compress a long trace to its essential steps |
| LOW | **generate** | compress to the single decisive calculation |

Generating LOW and MEDIUM is **compression, not reasoning**: the correct answer is already
known, so a cheap open model can do it and correctness is checked by string-matching the
final answer against the source trace. This is far cheaper than the agentic pipeline.

The set must be **paired** — the same problem rendered at all four depths — otherwise the
model learns that certain *questions* get long answers rather than that the *tag* controls
the length.

#### Budget

**200,000 problems x 4 depths = ~1.6B tokens** for the reasoning-training stage:

| band | tokens each | total |
|---|---|---|
| LOW | ~100 | 0.02B |
| MEDIUM | ~400 | 0.08B |
| HIGH | ~1,500 | 0.30B |
| ULTRA | ~6,000 | 1.20B |
| | | **1.60B** |

This sits **outside the 2T pretraining budget**. Bands must span mathematics, code and general
problem solving, or the effort control stays tied to one domain.

---

## Master schedule — all seven lanes across pretraining

**Budget 2T.** Stage durations: seed 5% (100B) · general 55% (1,100B) · reasoning 22% (440B)
· long-context 15% (300B) · anneal 3% (60B).

Every row's token-weighted average equals its headline share. Every column sums to 100%.
Both verified exactly (max error 0.0000).

| lane | seed | general | reasoning | long-ctx | anneal | **AGG** |
|---|---|---|---|---|---|---|
| Web | 54.8% | 34.6% | 11.1% | 4.9% | 2.5% | **25.00%** |
| Indic | 30.6% | 9.4% | 10.3% | 15.0% | 26.0% | **12.00%** |
| Code | 8.3% | 27.6% | 27.3% | 24.5% | 24.0% | **26.00%** |
| STEM | 4.0% | 17.2% | 22.1% | 14.6% | 9.0% | **17.00%** |
| Reasoning | 1.0% | 6.1% | 17.1% | 13.6% | 27.0% | **10.00%** |
| Long-context | 1.0% | 4.2% | 10.3% | 22.1% | 2.5% | **8.00%** |
| Agentic | 0.3% | 1.0% | 1.8% | 5.2% | 9.0% | **2.00%** |
| **TOTAL** | **100%** | **100%** | **100%** | **100%** | **100%** | **100%** |

### What each stage is for

| stage | purpose | primary lanes |
|---|---|---|
| **seed** | learn to form sentences; acquire the scripts | Web, Indic |
| **general** | build world knowledge and broad competence | Web, Code |
| **reasoning** | code and logic; the difficulty step-up | Code, STEM, Reasoning |
| **long-context** | stretch the context window | Long-context, Code |
| **anneal** | premium data only, at low learning rate | Reasoning, Indic, Code |

**Web's seed share.** V4 ran web 72 -> 18. 72% is not available to us: V4 carried Indic at
4%, we carry it at 30.6% of seed, and 72 + 30.6 = 102.6%. **The lower seed web share is not a
preference, it is what a 3x larger Indic commitment costs.**

**Overlap.** No cell is zero -- code enters at 8.3% in seed, long-context at 1.0%, agentic at
0.3%. A lane the model has never seen is a distribution shock at the point in training where
it can least absorb one. Each transition is additionally blended across a warmup band of
several billion tokens.

### Supply check on the aggregates

The single source of truth for supply and repetition. Per-lane sections do not repeat it.

| lane | share | demand | supply | epochs | verdict |
|---|---|---|---|---|---|
| Web | 25% | 500B | 4,500B | 0.11 | covered |
| Code | 26% | 520B | 1,100B | 0.47 | covered |
| Indic | 12% | 240B | 275.9B | 0.87 | covered |
| STEM | 17% | 340B | 250B | 1.36 | repetition |
| Long-context | 8% | 160B | 100B | 1.60 | repetition |
| Reasoning | 10% | 200B | 80.1B | 2.50 | repetition |
| Agentic | 2% | 40B | 0.63B | -- | **synthesized** |

Code carries the 7% freed when agentic fell from 9% to 2%: it is the primary benchmark
target and the only lane with genuine headroom (55% share available at one epoch).
STEM was not raised because it is already above one epoch at 17%.

---

## Difficulty ladder — B0 to B5 across the stages

Difficulty is a **distribution per stage**, not a label per stage. Every band is present in
every stage so that no level of difficulty debuts late; the mass simply moves right.

| band | seed | general | reasoning | long-ctx | anneal | AGG |
|---|---|---|---|---|---|---|
| **B0** nursery | 45.0% | 8.0% | 1.0% | 0.5% | 0.5% | 6.96% |
| **B1** grade-school | 35.0% | 26.0% | 6.0% | 2.0% | 1.0% | 17.70% |
| **B2** high-school | 14.0% | 38.0% | 24.0% | 10.0% | 4.0% | 28.50% |
| **B3** undergraduate | 4.0% | 21.0% | 38.0% | 30.0% | 14.0% | 25.03% |
| **B4** graduate | 1.5% | 6.0% | 25.0% | 38.0% | 40.0% | 15.77% |
| **B5** research / PhD | 0.5% | 1.0% | 6.0% | 19.5% | 40.5% | 6.04% |
| **TOTAL** | 100% | 100% | 100% | 100% | 100% | 100% |

### A real example at each level

| band | English | Indic | code |
|---|---|---|---|
| **B0** | "The cat sat on the mat. The mat was warm." | बिल्ली चटाई पर बैठी। | `print("hello")` |
| **B1** | "Plants make food from sunlight. This is called photosynthesis." | पौधे सूरज की रोशनी से भोजन बनाते हैं। | `for i in range(5): print(i)` |
| **B2** | "Solve for x: 3x + 7 = 22." | न्यूटन का दूसरा नियम: बल = द्रव्यमान × त्वरण। | a function with a loop, a conditional and a docstring |
| **B3** | "Prove that a continuous function on a closed bounded interval attains its maximum." | NCERT class-12 physics derivation in Hindi | a small class with unit tests |
| **B4** | "Derive the backpropagation update for a two-layer network under cross-entropy loss." | a peer-reviewed Indic-language academic article | a multi-file module with an interface and error handling |
| **B5** | an arXiv abstract and its proof from proof-pile-2 | verified native scholarly Indic prose (Tier A) | a real merged pull request with its test suite |

**Sources of the band label:** DCLM/FineWeb-Edu quality scores and reading-level classifiers
for web; grade tags for textbook material; repository stars, test coverage and file count for
code; venue for academic text. The label is assigned during cleaning, not at training time.

---

## Reasoning trace lengths inside pretraining

The **effort tags** (`low` / `medium` / `high` / `ultra`) belong to the reasoning-training
stage. Pretraining carries no tags — but it must carry the **length variety**, or the model
has no representation of sustained reasoning for the later stage to control.

| trace length | seed | general | reasoning | long-ctx | anneal |
|---|---|---|---|---|---|
| short (<64 tok) | 70% | 55% | 30% | 20% | 10% |
| medium (64-160) | 25% | 33% | 40% | 38% | 30% |
| long (160-400) | 4% | 10% | 24% | 32% | 40% |
| very long (>400) | 1% | 2% | 6% | 10% | 20% |

Reasoning tokens per stage: seed 1.0B · general 67.1B · reasoning 75.2B · long-context 40.8B
· anneal 16.2B = **200B**. Long traces are present from the first stage at 4%, so the anneal
concentrates them rather than introducing them.

---

## Lane: Code — 26%

**Share:** 26% = **520B tokens** · no floor needed
(OPUS's proxy contains LiveCodeBench and HumanEval, so code scores well on merit).

**Buys:** LiveCodeBench, Aider Polyglot; feeds SWE-bench and Terminal-Bench jointly with the
agentic lane.

| source | tokens | tier |
|---|---|---|
| The Stack v2 | 900B | B |
| D3 Code (V4 corpus) | 199B | B |
| CommitPack / CommitPackFT | 4B | B |

Code carries the 7% freed when agentic fell from 9% to 2%. It is the only lane with genuine
headroom — 55% of the budget would still be one epoch. Language selection happens during
cleaning: we do not spend budget on languages no benchmark rewards.

## Lane: STEM / math — 17%

**Share:** 17% = **340B**. Not raised despite headroom
elsewhere, because it is already above one epoch. Sources: proof-pile-2 55B (tier A),
D4 STEM 49B, peS2o 42B (tier A), plus the educational slice of FineWeb-Edu.
**Buys:** AIME, GPQA Diamond, and shares HLE with the reasoning lane.

## Lane: Long-context — 8%

**Share:** 8% = **160B**. Sources: repo-packed code 32K+
(60B) and book-length corpora (40B), both tier B. **Buys:** long-eval.

Concentrated at its own stage (22.1%) because attention cost grows with sequence length —
training long early would burn the budget teaching basic language at 64x the attention cost.
**Packing note:** this lane requires genuinely long single documents. A 32K sequence packed
from eight unrelated 4K documents produces long sequences with no long dependencies and does
not train the capability.

## Lane: General web — 25%

**Share:** 25% = **500B** · deliberately cut from the 34%
default. Sources: DCLM-Baseline 2,600B, FineWeb-Edu 1,300B, D2 Web-Diverse 627B,
D1 Web-Foundation 164B. **Buys:** MMLU.

We accept a weaker MMLU to fund code and Indic. The cut is applied as a **schedule, not a
constant**: web still leads the seed stage at 54.8% because language and world knowledge must
be acquired before anything else can be built on them, and falls to 2.5% by the anneal.
Cutting web early is what produces a model whose code compiles and does not work.

---

## Proxy experiments

Every number above is a hypothesis. Three are testable cheaply, before full scale.

| # | hypothesis | metric | refutation threshold |
|---|---|---|---|
| 1 | The agentic pipeline yields enough to fund 2% | unique tokens produced in a 2-week pilot on ~50 repos, measuring seconds/attempt, pass rate and tokens/trajectory | sustained yield implying **< 12B unique tokens in 3 months** -> drop agentic to 1% |
| 2 | Our filters, not our crawl, are what destroy Hinglish | Hinglish document share in the raw crawl vs the cleaned corpus | **< 1%** -> it was never crawled; needs deliberate sourcing, not a filter fix |
| 3 | Indic at 12% improves MILU without costing more than 1 point of MMLU | MILU and MMLU at 1B scale, two arms differing only in the Indic share (8% vs 12%) | MMLU loss **> 1 point** -> fall back to 8% |

Experiment 3 is the one that decides the headline mixture and should run first at 1B, then
confirm at 3B before the full run.

### Experiment 2 -- run, and it refutes the hypothesis

`scripts/corpus_scan.py` classifies documents by script and by romanized-Hindi function-word
rate. Run over both the raw crawl and the cleaned corpus:

| corpus | documents | Hinglish | share |
|---|---|---|---|
| raw crawl (pre-cleaning) | 13,218 | 13 | **0.098%** |
| cleaned corpus | 14,073 | 7 | **0.050%** |

**0.098% is below the 1% threshold, so the hypothesis is refuted.** Hinglish is not being
destroyed by our filters -- it was never crawled in meaningful quantity. Cleaning roughly
halves an already negligible amount. **Funding a Hinglish share would therefore be funding a
lane with no supply**, and the filter changes proposed above, while still correct on their
own merits, will not create one. Hinglish needs deliberate sourcing from Indian forum,
comment and social text, or it stays out of scope.

Two findings fell out of the same scan:

**Filter bias is real and already measured.** The Session 4 pipeline records that an
English-tuned quality filter would reject **2,463 of ~2,779 Hindi documents**, against 109
for the script-aware filter (Odia 1,737 -> 103; Telugu 2,409 -> 487; English 2,662 -> 2,662,
unaffected). The bias is confirmed; it simply is not what explains the Hinglish gap.

**Sangraha carries language-ID errors.** `sangraha.asm.jsonl` contains non-Indic text --
`"Fiye 33:1-20 Esau En Yakobo Kimindegumuk..."`, a Bible translation in an unrelated
language. Since Sangraha is the backbone of Tier A and Tier B, a language-ID audit belongs
in the cleaning plan before those tiers are trusted.


---

## Repository contents

```
README.md                     this plan
scripts/
  mixture_matrix.py           builds the master schedule (RAS); asserts both constraints
  supply_check.py             demand vs real supply per lane; Indic tier split
  corpus_scan.py              experiment 2 -- script and code-mix classifier
data/
  corpus.clean.jsonl          cleaned Session 4 corpus (14,073 docs)
  stats.json                  per-stage cleaning retention, filter-bias counts
  raw/sangraha.*.jsonl        raw pre-cleaning crawl (13,218 docs, 6 language slices)
```

Reproduce:

```bash
python scripts/mixture_matrix.py
python scripts/supply_check.py
python scripts/corpus_scan.py data/corpus.clean.jsonl
python scripts/corpus_scan.py "data/raw/sangraha.*.jsonl"
```
