---
type: source
author: "Stanford Institute for Human-Centered AI (HAI), AI Index"
date: 2025
venue: "AI Index Report 2025, Technical Performance chapter highlights, web page (retrieved 2026-10-11)"
url: "https://hai.stanford.edu/ai-index/2025-ai-index-report/technical-performance"
tags: [source, report, ai-index, benchmarks, open-weight, small-models, test-time-compute]
---
# Stanford HAI 2025 – AI Index Report, Technical performance

**Raw file**: `raw/local_inference/Stanford HAI 2025 - AI Index Report, Technical performance_ingested.md`

## Overview
The web summary of the **Technical Performance** chapter of the Stanford **AI Index Report 2025**: about a dozen highlight paragraphs, not the chapter itself. It covers benchmark progress, the shrinking open/closed and US/China gaps, test-time compute, new hard benchmarks, video generation, small models and agents. The extraction starts with newsletter boilerplate ("Sign Up…") and carries a placeholder publication date (`2000-01-01`); the report year is 2025. Figures, sources and methods are not in the extracted text. The full report PDF should be cited for exact numbers and definitions.

## Key Insights
1. **Benchmark progress 2023→2024.** +18.8 pp on MMMU and +48.9 pp on GPQA. On SWE-bench, 4.4% of problems solved in 2023 vs 71.7% in 2024.
2. **Open vs closed weights.** On the Chatbot Arena leaderboard, the leading closed-weight model beat the top open-weight model by **8.04% in early January 2024**, and by **1.70% by February 2025**. The gap "had nearly disappeared".
3. **US vs China.** End-2023 gaps on MMLU / MMMU / MATH / HumanEval of 17.5 / 13.5 / 24.3 / 31.6 pp had narrowed to 0.3 / 8.1 / 1.6 / 3.7 pp by end-2024.
4. **Frontier is crowded.** The Elo difference between the top and 10th-ranked Arena models fell from 11.9% to 5.4% (early 2025), and between the top two from 4.9% (2023) to 0.7% (2024).
5. **Test-time compute costs.** o1 scored 74.4% on an IMO qualifying exam vs GPT-4o's 9.3%, but is "nearly six times more expensive and 30 times slower".
6. **Small models (key for this thesis).** In 2022, the smallest model above **60% on MMLU** was PaLM at **540B** parameters. In 2024 Microsoft's **Phi-3-mini (3.8B)** reached the same threshold, a **142-fold** reduction in two years.
7. **New hard benchmarks.** Humanity's Last Exam: top system 8.80%. FrontierMath: 2%. BigCodeBench: 35.5% vs a 97% human standard.
8. **Limits.** Even with chain-of-thought, LLMs still cannot reliably solve problems with provably correct solutions (arithmetic, planning), especially on instances larger than seen in training. The report flags this as a trust issue for high-risk applications.
9. **Agents (RE-Bench).** With a 2-hour budget, top AI systems score 4× human experts. At 32 hours, humans outscore AI 2 to 1.

**Quality notes.** An authoritative and widely cited report, but this page only summarises it. The percentage gaps on Arena are differences in Elo expressed as percentages, and the extract does not define them. Numbers are as of early 2025 and are outdated for the 2026 landscape; for the open/closed gap in 2026, see [[Epoch AI - Open vs closed capability gap (ECI)]].

## Relevance to GroundOne
- **Small models got much stronger.** The 540B → 3.8B, 142× reduction for the same MMLU threshold is a clean, citable fact for Ch. 1–2. Models of a few billion parameters, i.e. laptop-sized, now reach scores that needed datacenter-scale models in 2022 ([[Small Language Models]]). GroundOne's 3B sits at this scale. Note that MMLU measures general knowledge, not grounded verification.
- **Open weights are competitive.** The closed/open gap shrinking from 8.04% to 1.70% on Arena supports choosing an open-weight base ([[Open-Weight Models]]). This concerns the best open models, not small ones.
- **Cost of reasoning.** o1 being about 6× more expensive and 30× slower than GPT-4o illustrates the cost of generating more tokens at inference. GroundOne makes the opposite trade: zero generated tokens, one prefill ([[Prefill and Decode]], [[When System One Beats an LLM]]). The AI Index figure is about API cost and latency, not local hardware.
- **Reliability caveat.** The note that LLMs fail on provably solvable problems, with consequences for high-risk use, supports the need for an external, cheap verifier in RAG ([[Groundedness Verification]]).

## Links
- Concepts: [[Prefill and Decode]], [[Groundedness Verification]], [[When System One Beats an LLM]], [[Small Language Models]] (proposed), [[Open-Weight Models]] (proposed), [[Open-Weight Models|Open-Closed Capability Gap]] (proposed)
- Related sources: [[Epoch AI - Open vs closed capability gap (ECI)]], [[Epoch AI 2025 - Frontier AI performance becomes accessible on consumer hardware within a year]], [[Lu 2024 - Small Language Models, Survey, Measurements, and Insights (arXiv 2409.15790)]]
