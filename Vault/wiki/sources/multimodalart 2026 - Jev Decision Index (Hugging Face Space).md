---
type: source
author: "multimodalart (community-maintained Hugging Face Space; evaluation kit at github.com/apolinario/decision-index)"
date: 2026
venue: "Hugging Face Space multimodalart/jev-decision-index, revision f4ecd9f (retrieved 2026-10-10): README, data/methodology-v0.2.1.json, data/index-v0.2.1.json, data/v03.json"
url: "https://huggingface.co/spaces/multimodalart/jev-decision-index"
tags: [source, leaderboard, benchmark, decision-models, system-one, ragtruth, calibration, chance-correction, decision-index]
---
# multimodalart 2026 – Jev Decision Index (Hugging Face Space)

**Raw file**: `raw/multimodalart 2026 - Jev Decision Index Space README_ingested.md`
**Supplementary raw files** (unchanged JSON from the same revision): `raw/multimodalart 2026 - Jev Decision Index methodology v0.2.1_ingested.json`, `raw/multimodalart 2026 - Jev Decision Index results v0.2.1_ingested.json`, `raw/multimodalart 2026 - Jev Decision Index board v0.3.1_ingested.json`

## Overview
The **Decision Index** is the community leaderboard that almost every decision-model card in the 2026 wave reports against (Cloudflare Clef, Liquid d1, Perplexity, vLLM-SR, Bespoke Labs, Kev, Strands). It lives in a static Space that started as a "Jev Reproductions Tracker" ("Who is rebuilding TypeSafe's Jev … in the open?") and also tracks news items with an engagement-based trending score. The README calls it "Unofficial and community-maintained; not affiliated with TypeSafe AI." Edition 0.2.1 is dated 2026-09-28 and scores Jev version 1.13.0.

## Key Insights
1. **Protocol (methodology v0.2.1).** 120,340 requests (119,898 scoreable after 442 excluded questions), 43 benchmarks, a 38-benchmark index panel in five areas (Knowledge & Reasoning, Language Understanding, Retrieval & Classification, Tools & Automation, Arts & Human Taste), run on one NVIDIA RTX PRO 6000. Hard rules: no truncation (a request that does not fit is unsupported), no label filtering, no prompt tuning (each entrant's native helpers and readout), no labels in the adapter, no correctness-based retry, native abstentions stand, and **unanswered = wrong**.
2. **Chance correction.** Since v0.2, scores are chance-corrected so 0 is random and 100 is perfect; area weights are fixed (Arts 10 %, others by the square root of their benchmark count) and "gold" benchmarks weigh 1.2. Calibration is summarised separately on 32 benchmarks from a 1-in-6 sample (ECE, Brier, reliability bins).
3. **Full score (README, edition 0.3).** 20 % public benchmarks, 50 % private tests of the same skills, 30 % private tasks from new domains; "most of the score comes from tests nobody can train on". The 0.3.1 board of 2026-10-10 ranks a Fastino "GLiDE no-thinking (28B)" level with Jev (tied rank 2).
4. **RAGTruth is part of the index (added in v0.2).** Benchmark 59, "RAGTruth response-level hallucination": all 2,700 test responses (900 each of QA, Summary, Data2txt), state = `{prompt, response}` with the exact generation prompt, one `noul` ("The response contains content that is not supported by the context in the prompt."), gold = hallucinated iff at least one annotated span (943 positives), headline F1 on the hallucinated class at P(yes) ≥ 0.5. Since v0.2.1 the chance line is "always hallucinated", F1 0.5177.
5. **RAGTruth results on the 0.2.1 board (70 entrants plus Jev).** Jev 0.765 (median latency 1,039.7 ms). Top entrants: pplx-decider-v1-27b 0.803, Jevfire 0.803, Jev-Omni (12B) 0.800, Jebadiah 27B 0.782. By served size:
   | Served parameters | Entrants | Median F1 | Best | Above 0.6 |
   |---|---:|---:|---|---:|
   | < 1B | 22 | 0.44 | JPT-0.8B 0.553 | 0 |
   | 1–3B | 7 | 0.28 | Decision 1.0 Sol 0.614 | 1 |
   | 3–6B | 17 | 0.53 | JPT-4B 0.742 | 6 |
   | 6–15B | 8 | 0.66 | Jev-Omni 0.800 | 6 |
   | ≥ 15B | 16 | 0.74 | pplx-decider-v1-27b 0.803 | 16 |
   31 of the 70 entrants score at or below the always-hallucinated baseline. Named small models: [[Laya]] 0.488, GLiNER2.5-Decide 0.253, Julia 1 0.520, Kev 0.8B 0.400, Kev 4B 0.330, SemIf 0.534. (Size buckets computed from the board's `served_params` field.)
6. **Related grounding tasks** in the suite: ContractNLI (Jev macro-F1 0.717), ANLI (0.748), HoVer (accuracy 0.729), NLI4CT.

## Relevance to GroundOne
- **The decision-model community already measures RAGTruth, at response level and zero-shot.** No entrant under 1B parameters gets meaningfully above chance (best 0.553 vs 0.518), and only large models (≥ 15B) are reliably above 0.6. This is the strongest available evidence that **small general-purpose decision models cannot verify groundedness zero-shot**, which supports GroundOne's specialisation argument (H1) and its claim that the gain comes from training and scale, not from the System One interface ([[When System One Beats an LLM]]).
- **Comparable number to compute.** GroundOne's T1 covers 2,647 of the 2,700 RAGTruth test answers (the quality-flagged ones are dropped). Aggregating its sentence verdicts to "any sentence not supported" and computing hallucinated-class F1 at the served threshold would place GroundOne 0.5B/3B on this scale. The comparison would still be specialist (trained on RAGTruth train) vs zero-shot generalists, and must be labelled so ([[RAGTruth]], [[Decision-Model Benchmarks]]).
- **Protocol lessons GroundOne already follows**: no truncation, unanswered = wrong (GroundOne counts format failures as errors), chance-aware metrics, separate calibration reporting.
- **Caveat.** Community board, numbers produced by the maintainer's harness or adopted from author-submitted runs after reproduction checks; the private tiers cannot be audited.

## Links
- Concepts: [[Decision-Model Benchmarks]], [[Decision-Model Landscape (Hugging Face, 2026)]], [[RAGTruth]], [[Hallucination Detection]], [[System One Models]], [[Jev]]
- Related sources: [[Cloudflare 2026 - Clef model card]], [[Perplexity 2026 - pplx-decider-v1.1-27b model card]], [[KR Labs and vLLM Semantic Router 2026 - Vela 2.0 9B model card]], [[Benchmark Heaven 2026 - JevBench v1.6.1 dataset card]]
