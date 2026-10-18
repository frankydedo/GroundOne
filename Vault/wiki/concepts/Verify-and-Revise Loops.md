---
type: concept
tags: [concept, self-correction, refinement, verification, rag, demo, hallucination]
---
# Verify-and-Revise Loops

Generate an answer, check it, revise what fails, repeat until it passes or a limit is reached. The literature below is the basis for the repair loop of the GroundOne demo ([[Demo Application]]).

## The main methods
| Method | Critic | Revision | Key result and caveat |
| --- | --- | --- | --- |
| Self-Refine ([[Madaan 2023 - Self-Refine, Iterative Refinement with Self-Feedback (arXiv 2303.17651)\|Madaan 2023]]) | the generator itself | full rewrite, up to 4 rounds | specific feedback > generic > none; math barely moves (the critic says "everything looks good" for 94 % of cases); 61 % of failures are wrong feedback; Vicuna-13B cannot refine even with oracle feedback |
| RARR ([[Gao 2023 - RARR, Researching and Revising What Language Models Say (arXiv 2210.08726)\|Gao 2023]]) | retrieved evidence + agreement gate | minimal edit | without the gate the model over-edits; attribution trades against preservation (EFEC preservation 10.4 vs RARR 83.1); no "contradicted" class |
| CRITIC ([[Gou 2024 - CRITIC, LLMs Can Self-Correct with Tool-Interactive Critiquing (arXiv 2305.11738)\|Gou 2024]]) | external tools | correction, 2–3 rounds | without tools the gain is about zero; latency grows linearly with rounds; starred results are oracle |
| CoVe ([[Dhuliawala 2024 - Chain-of-Verification Reduces Hallucination in LLMs (arXiv 2309.11495)\|Dhuliawala 2024]]) | short verification questions answered apart from the draft | regenerate | FactScore 55.9 → 71.4; short questions answered far better than long lists; precision partly rises by deleting content |
| CRAG ([[Yan 2024 - Corrective Retrieval Augmented Generation (arXiv 2401.15884)\|Yan 2024]]) | T5-large retrieval evaluator (0.77B) | re-retrieve / refine knowledge *before* generation | the small evaluator beats ChatGPT at judging retrieval (84.3 vs 58–65 %); three actions from hand-set thresholds |

## What the literature agrees on
- **Feedback must come from outside the generator.** Without external signal self-correction does not help and can hurt (GPT-3.5 CommonSenseQA 75.8 → 38.1; correct answers flip to wrong more often than the reverse) ([[Huang 2024 - Large Language Models Cannot Self-Correct Reasoning Yet (arXiv 2310.01798)\|Huang 2024]]). Earlier positive results often used oracle labels.
- **Gate the edits and edit minimally** (RARR) to keep what was right.
- **Most of the gain comes in 2–3 rounds**; cost grows with each round.
- **Compare at equal compute**: a best-of-N baseline with the same budget is the fair comparison (Huang 2024).

## What GroundOne adds as the critic
- A **trained, specialised, local** external verifier, in one forward pass: re-checking a revision costs one prefill, not a generated critique ([[Prefill and Decode]], [[When System One Beats an LLM]]).
- **Per-sentence three-way verdicts**: the repair is targeted (only flagged sentences), and "not mentioned" can trigger re-retrieval (CRAG-like) instead of a rewrite.
- **Calibrated probabilities and a dev-fitted threshold τ** instead of yes/no prompts or hand-set thresholds ([[Calibration]], [[Guardrails and Policies]]).

## What it does not solve
- GroundOne is not an oracle: false alarms push correct sentences into rewrites, misses let errors through.
- A verdict with no rationale is less actionable than a written critique (but is what the generator can act on cheaply).
- A small generator may fail to repair (Self-Refine's Vicuna result).
- The loop can game the verifier by deleting or hedging content (CoVe's precision-by-deletion).

## How to evaluate it (if evaluated)
Preservation of correct content, transitions in both directions (wrong → right and right → wrong), repair success per round, rounds to stop, and an equal-compute best-of-N baseline; faithfulness judged by an independent checker, not by GroundOne itself.

## Links
- [[Demo Application]], [[Guardrails and Policies]], [[Groundedness Verification]], [[Hallucination Detection]], [[LLM-as-a-Judge]], [[Retrieval-Augmented Generation]], [[Asai 2024 - Self-RAG]]
