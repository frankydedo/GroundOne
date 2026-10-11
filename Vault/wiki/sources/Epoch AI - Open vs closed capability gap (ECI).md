---
type: source
author: "Epoch AI"
date: 2026-05-29
venue: "Epoch AI Data Insight, web page with data table (retrieved 2026-10-11)"
url: "https://epoch.ai/data-insights/open-closed-eci-gap"
tags: [source, data-insight, open-weight, closed-weight, capability-gap, eci, benchmarks, bootstrap]
---
# Epoch AI – Open vs closed capability gap (ECI)

**Raw file**: `raw/local_inference/Epoch AI - Open vs closed capability gap (ECI)_ingested.md`

## Overview
An Epoch AI data insight (29 May 2026) measuring how far the **best open-weight models** trail the **best closed models** on the **Epoch Capabilities Index (ECI)**, Epoch's composite capability score fitted on many benchmarks. Headline: from 1 January to 28 May 2026, open-weight models lagged closed frontier models by an average of **four months**, an average gap of **8 ECI points**. The prose is short (headline, method, limitations). Most of the file (~640 table lines) is the underlying table of ECI scores per model; only aggregate facts are taken from it here.

## Key Insights
1. **Headline.** The average time lag was **4 months** over 1 Jan–28 May 2026. The average ECI gap was **8 points (90% CI 7–11)**, "similar to the gap between GPT-5 and GPT-5.5". The earlier October 2025 insight found a **3-month** lag over January 2023–October 2025, so the gap widened slightly in 2026.
2. **Method (time gap).** For each day in the window, take the best open model available and find the most recent date on which the closed state of the art was **not significantly better**. Significance uses paired bootstrap refits of ECI: the open model counts as having caught up if it beats the old SOTA in **≥ 5%** of samples. If the open model's point estimate has to be strictly higher instead, the lag grows to **6 months**.
3. **Method (vertical gap).** Release dates are exact, so the ECI gap is the average difference between the absolute SOTA and the open-weight SOTA across the window.
4. **Limitations (both make the gap look smaller).** (a) Open-weight models tend to do worse on private benchmarks than on public ones, plausibly from hill-climbing public benchmarks. (b) Only models with enough public benchmark coverage get an ECI, and closed labs do not always release their most capable models.
5. **Aggregate facts from the table** (computed for this page from the raw table, not stated in the prose):
   - About 620 rows with release dates from 2023-02-24 to 2026-05-19, many of them duplicate entries (same model through different providers or reasoning settings); about 390 have an ECI score.
   - Accessibility labels: API access, Open weights (unrestricted / restricted use / non-commercial), Hosted access (no API), Unreleased. Of the rows with an ECI score, roughly 240 are API-only and roughly 140 open-weight.
   - Highest ECI in the table: **GPT-5.5 Pro, 159.35** (API, 2026-04-23). Highest open-weight: **Kimi K2.6, 151.60** (Moonshot, open weights unrestricted, 2026-04-20). That is a gap of about 8 points at almost the same date, consistent with the headline.
   - At the end of 2025, the best open model was **DeepSeek-V3.2 (146.46, 2025-12-01)** vs **GPT-5.2 Pro (154.19, 2025-12-11)**.
   - The leading open-weight models in 2026 are mostly from Chinese labs (Kimi, MiniMax, GLM/Z.ai, DeepSeek).
   - Small models sit far lower: e.g. Gemma 2B 93.53, Llama 3.1-8B 115.51, Gemma 2 9B 119.51. **Qwen2.5-72B scores 129.40**. Qwen2.5 0.5B and 3B have no ECI entry.

**Quality notes.** Independent analyst work with a stated bootstrap method and stated limitations. Data issues in the table: many rows have empty display names, and there are duplicate rows. Epoch labels **Qwen2.5-72B as "Open weights (unrestricted)"**, whereas the Qwen2.5 technical report lists 72B under the separate "Qwen" licence ([[Qwen2.5]]). Licence labels in this table should therefore not be cited without checking the model card.

## Relevance to GroundOne
- **Context for the "open models are good enough" premise.** By 2026, open-weight models trail the closed frontier by months, not years, in general capability. This supports the thesis's choice of an open-weight base, which gives the weights, logits and local execution that a System One readout needs ([[Open-Weight Models]], [[System One Models]]).
- **Not about small models.** The gap is measured between the *best* open models (hundreds of billions of parameters, MoE, e.g. Kimi K2.x) and closed frontier models. These do not run on a 16 GB laptop. The relevant local comparison is the consumer-hardware lag in [[Epoch AI 2025 - Frontier AI performance becomes accessible on consumer hardware within a year]]. Citing this page as evidence that *laptop* models are near the frontier would be wrong.
- **Benchmark-gaming caveat.** Like Epoch's consumer-GPU page, it notes that open models over-fit public benchmarks. This supports evaluating GroundOne on frozen held-out tests rather than public leaderboard numbers.

## Links
- Concepts: [[Qwen2.5]], [[Mixture of Experts]], [[Statistical Significance and Bootstrap]], [[Open-Weight Models]] (proposed), [[Open-Weight Models|Open-Closed Capability Gap]] (proposed), [[Open-Weight Models|Model Licences]] (proposed)
- Related sources: [[Epoch AI 2025 - Frontier AI performance becomes accessible on consumer hardware within a year]], [[Epoch AI 2025 - What's the best model you can run on a single consumer GPU]], [[Stanford HAI 2025 - AI Index Report, Technical performance]], [[Artificial Analysis - Announcing the Openness Index]]
