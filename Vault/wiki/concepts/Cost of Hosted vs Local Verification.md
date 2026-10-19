---
type: concept
tags: [concept, cost, hosted-llm, local-inference, locality-pillar, groundone]
---
# Cost of Hosted vs Local Verification

Order-of-magnitude comparison made for the thesis (D30, 2026-10-19; Ch. 8, Table "Costo indicativo"; script `Project/experiments/locality/scripts/cost_comparison.py`, output `results/locality/cost_comparison.json`).

## Method
- **Hosted judge:** about 906 input tokens per answer (median T1 document + answer, 756 Qwen2.5 tokens, plus 150 for instructions) and the output tokens measured for the thesis' 3B judges (36 terse, 248 verbose), at standard list prices accessed 2026-10-19 ([[Anthropic 2026 - Claude API pricing]], [[OpenAI 2026 - API pricing]], [[Google 2026 - Gemini API pricing]]).
- **GroundOne locally:** measured net chip energy per answer × EU average household electricity price ([[Eurostat 2026 - Electricity price statistics]]).

## Result (10,000 answers)
| System | Terse | Verbose |
| --- | --- | --- |
| Claude Haiku 5.5 / gpt-6-luna | $1.1 | $2.2 |
| Gemini 3.5 Flash-Lite | $3.6 | $8.9 |
| Gemini 3.8 Flash | $8.2 | $16 |
| Claude Sonnet 5.5 / gpt-6.1-sol / Gemini 4 Argon | $22 | $43 |
| Claude Opus 5.5 | $43 | $86 |
| gpt-6-astra | $109 | $215 |
| GroundOne 0.5B / 3B (electricity) | €0.004 / €0.03 | |

## Reading
- Two to four orders of magnitude apart, but **cheap hosted judges cost little in absolute terms**: cost is not the decisive argument for locality; independence (documents never leave the machine, no external provider) is ([[Privacy and Data Sovereignty]]).
- Not included: hardware purchase and amortisation, caching and batch discounts, and the quality of hosted judges (not measured in the thesis).
- Prices move fast (Gemini promotional prices expire in Nov–Dec 2026), so any cost claim must carry its date.

## Links
- [[On-Device Inference]], [[Energy of LLM Inference]], [[LLM-as-a-Judge]], [[GroundOne]]
