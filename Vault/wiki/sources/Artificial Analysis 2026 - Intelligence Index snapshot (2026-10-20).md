---
type: source
author: "Artificial Analysis"
date: 2026-10-20
venue: "Artificial Analysis leaderboard, Intelligence Index v4.3.2 (chart downloaded by the author; open-weights flags from the page data)"
url: "https://artificialanalysis.ai/leaderboards/models"
tags: [source, benchmark, leaderboard, open-weight, closed-models, locality-pillar]
---
# Artificial Analysis 2026 – Intelligence Index snapshot (2026-10-20)

**Raw file**: `raw/local_inference/Artificial Analysis 2026 - Intelligence Index snapshot (2026-10-20)_ingested.md` (chart image alongside: `Artificial Analysis 2026 - Intelligence Index chart (2026-10-20).png`)

## Key Insights
- Index v4.3.2 aggregates 10 evaluations (AA-Briefcase, GDPval-AA, AutomationBench-AA, Terminal-Bench 4.0, SciCode, Humanity's Last Exam, GDP.pdf, CritPt, AA-Omniscience, AA-LCR). Models at the reasoning setting shown in brackets.
- **Best closed model 58 (Claude Opus 5.5), best open-weight model 46 (MiMo-V2.6-Pro): a 12-point gap** on this index. Open-weight models DeepSeek V4.1 Flash, GLM-5.3 (45), Step 5 Preview, Kimi K3 (44) match or exceed mid-tier closed models (Claude Haiku 5.5 43, Gemini 3.8 Flash 41).
- All the strong open-weight models are in AA's "large" parameter class; the only "small" one in the chart, Qwen3.8 27B, scores 34.
- Open-weights status comes from the `isOpenWeights` field of the model objects in the page; chart values agree with the unrounded page values within rounding.

## Relevance to GroundOne
- Thesis Ch. 2 §2.2.2 (figure `aa_intelligence_snapshot`, `groundone figures locality`): a current snapshot that complements Epoch AI's trend ([[Open-Weight Models]]). The point for locality: the relevant gap is also between the largest open-weight models and those that fit local hardware ([[Small Language Models]], [[Local Inference Hardware]]).

## Links
- [[Open-Weight Models]], [[Small Language Models]], [[On-Device Inference]], [[Artificial Analysis - Announcing the Openness Index]]
