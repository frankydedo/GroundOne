---
type: source
author: "Jie Huang, Xinyun Chen, Swaroop Mishra, Huaixiu Steven Zheng, Adams Wei Yu, Xinying Song, Denny Zhou (Google DeepMind, UIUC)"
date: 2024
venue: "ICLR 2024 (arXiv 2310.01798v2; venue stated in the page header)"
url: "https://arxiv.org/abs/2310.01798"
tags: [source, paper, self-correction, intrinsic-feedback, oracle-labels, evaluation-methodology, verify-and-revise]
---
# Huang 2024 – Large Language Models Cannot Self-Correct Reasoning Yet

**Raw file**: `raw/demo/Huang 2024 - Large Language Models Cannot Self-Correct Reasoning Yet (arXiv 2310.01798)_ingested.pdf`

## Overview
A critical re-evaluation of LLM self-correction. The paper defines **intrinsic self-correction**: the model revises its own answer using only its own abilities, with no external feedback. It finds that on reasoning benchmarks, intrinsic self-correction **does not help and often hurts**. Earlier positive results (RCI, Reflexion) relied on **oracle labels** to decide when to stop. Multi-agent debate is no better than self-consistency at an equal number of responses, and the Self-Refine gain on constrained generation disappears with a better initial prompt (§1, Table 1). The conclusion: use external feedback when it exists, compare at equal inference cost, and put equal effort into the initial prompt (§6).

## Key Insights
1. **Setup (§3.1).** GSM8K, CommonSenseQA and HotpotQA. GPT-3.5-Turbo, GPT-4, GPT-4-Turbo and Llama-2-70b-chat. Three-step prompting (answer → review and feedback → answer again), at most 2 rounds, i.e. 3 and 5 calls.
2. **With oracle labels it "works" (Table 2).** GPT-3.5: GSM8K 75.9 → 84.3, CommonSenseQA 75.8 → 89.7. GPT-4: HotpotQA 49.0 → 59.0. The labels stop the loop as soon as the answer is correct, so these numbers measure an oracle, not self-correction.
3. **Without labels it degrades (Tables 3–4).** GPT-3.5: CommonSenseQA 75.8 → 38.1 (round 1) → 41.8 (round 2); GSM8K 75.9 → 75.1 → 74.7. GPT-4: GSM8K 95.5 → 91.5 → 89.0. Llama-2: GSM8K 62.0 → 43.5 → 36.5. Other feedback prompts (Tables 5–6) still lose.
4. **Why (§3.3, Fig. 1).** Most answers stay unchanged (74.7% on GSM8K for GPT-3.5). Of those that change, a *correct → incorrect* switch is more likely than an *incorrect → correct* one. "The fundamental issue is that LLMs cannot properly judge the correctness of their reasoning". On multiple choice, the feedback prompt itself pushes the model to switch to another plausible option.
5. **Equal-cost baselines (§4, Table 7).** On GSM8K, multi-agent debate with 6 or 9 responses scores 83.2 / 83.0, against 85.3 / 88.2 for self-consistency (majority vote) with the same number of responses. The gain comes from consistency, not from critique.
6. **Prompt design (§5, Table 8).** On CommonGen-Hard, a standard prompt that clearly asks for all concepts reaches 81.8, above Self-Refine's 67.0 after self-correction. Applying self-correction on top of the better prompt lowers coverage to 75.1.
7. **Scope and limitations (§7).** The study covers reasoning only. Self-correction can still help on style or safety alignment, where models judge appropriateness well. The paper also explicitly endorses **external feedback**: code execution (self-debugging), tools ([[Gou 2024 - CRITIC, LLMs Can Self-Correct with Tool-Interactive Critiquing (arXiv 2305.11738)|CRITIC]]) and **trained verifiers or critique models** (§6).

## Relevance to GroundOne
- **The core motivation for an external verifier in the demo loop.** If the generator judges its own sentences, Huang 2024 predicts little gain and possible damage: correct sentences rewritten into wrong ones. The demo therefore takes the feedback from a separate, trained verifier, exactly the "trained verifier" route the paper recommends (§6) ([[Verify-and-Revise Loops]], [[GroundOne]]).
- **GroundOne is external but not an oracle.** The paper's correct → incorrect failure mode returns whenever the verifier raises **false flags**: a correctly grounded sentence sent for rewriting can come back worse. This is why the decision threshold τ and the per-class blocking policy matter. Raising τ raises recall of errors but sends more correct sentences to be rewritten. The demo should log both kinds of transition (fixed and broken) per round, as Fig. 1 does ([[Selective Prediction]], [[Calibration]]).
- **Evaluation protocol for the demo.** (a) Compare the loop against a baseline with **equal compute**, for example resampling the answer N times and keeping the best by GroundOne score, not only against the single first draft. (b) Make sure the initial generation prompt already asks for grounded answers, so that gains are not just a better instruction smuggled in through the feedback. (c) Never use gold labels to stop the loop; the stop rule must use only the verifier's verdicts.
- **Groundedness is a checkable task.** Unlike open reasoning, groundedness has an external reference, the retrieved document, so a reliable external signal is possible in principle. This is the condition under which the paper expects correction to work ([[Groundedness Verification]]).

## Links
- Concepts: [[Verify-and-Revise Loops]], [[LLM-as-a-Judge]], [[Hallucination Detection]], [[Selective Prediction]], [[Calibration]], [[Statistical Significance and Bootstrap]], [[Demo Application]]
- Related sources: [[Madaan 2023 - Self-Refine, Iterative Refinement with Self-Feedback (arXiv 2303.17651)]], [[Gou 2024 - CRITIC, LLMs Can Self-Correct with Tool-Interactive Critiquing (arXiv 2305.11738)]], [[Dhuliawala 2024 - Chain-of-Verification Reduces Hallucination in LLMs (arXiv 2309.11495)]], [[Kadavath 2022 - Language Models (Mostly) Know What They Know]]
