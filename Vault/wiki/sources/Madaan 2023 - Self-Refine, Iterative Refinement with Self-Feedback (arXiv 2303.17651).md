---
type: source
author: "Aman Madaan, Niket Tandon, Prakhar Gupta, Skyler Hallinan, Luyu Gao, Sarah Wiegreffe, Uri Alon, Nouha Dziri, Shrimai Prabhumoye, Yiming Yang, Shashank Gupta, Bodhisattwa Prasad Majumder, Katherine Hermann, Sean Welleck, Amir Yazdanbakhsh, Peter Clark (CMU, AI2, UW, NVIDIA, UCSD, Google)"
date: 2023
venue: "NeurIPS 2023 (arXiv 2303.17651; the raw file is the v2 preprint, marked 'Preprint. Under review', so the venue is not stated on page 1)"
url: "https://arxiv.org/abs/2303.17651"
tags: [source, paper, self-correction, self-feedback, iterative-refinement, verify-and-revise, prompting]
---
# Madaan 2023 – Self-Refine: Iterative Refinement with Self-Feedback

**Raw file**: `raw/demo/Madaan 2023 - Self-Refine, Iterative Refinement with Self-Feedback (arXiv 2303.17651)_ingested.pdf`

## Overview
Self-Refine is the reference **intrinsic** refinement loop: one LLM generates an output, writes feedback on it, and rewrites the output using that feedback, repeating until a stop condition is met. No training, no reward model and no external tool are used; the same model is generator, critic and refiner, steered only by few-shot prompts (abstract, §2, Algorithm 1). On 7 tasks with GPT-3.5, ChatGPT and GPT-4 the authors report an average gain of about 20% absolute over one-step generation (abstract, Table 1). Gains are large on open-ended or preference-based tasks and close to zero on math reasoning.

## Key Insights
1. **Method (§2, Algorithm 1).** Three prompts: `p_gen` (initial output), `p_fb` (feedback) and `p_refine` (rewrite). Feedback is prompted to be **actionable** (it names a concrete action) and **specific** (it points at the phrases to change). The refine step sees the whole history of earlier outputs and feedback (Eq. 4). The loop stops after a fixed number of steps or when the feedback contains a stop indicator.
2. **Feedback source: the model itself.** It is not grounded in any external signal. The authors list this as the paper's distinguishing feature (§5, Table 3).
3. **Iterations (§3.1, Fig. 4).** At most 4 feedback-refine iterations. Gains shrink with each step: Code Optimization goes 22.0 → 27.0 → 27.9 → 28.8 over y0–y3 and Constrained Generation 29.0 → 40.3 → 46.7 → 49.7. Quality is not always monotonic on multi-aspect tasks.
4. **Main results (Table 1).** For example, GPT-4 Dialogue Response goes 25.4 → 74.6 (preference), Code Optimization 27.3 → 36.0 and Constrained Generation 15.0 → 45.0. **Math Reasoning barely moves** (GPT-4 92.9 → 93.1; GPT-3.5 64.1 → 64.1). The reason given is that the model cannot tell whether an answer is wrong: ChatGPT's feedback is "everything looks good" for 94% of instances (§3.3).
5. **External signal helps where self-feedback fails (App. H.1, Table 9).** With oracle feedback, which refines only answers that are actually wrong, Math Reasoning rises by 4.8 points for GPT-3.5 and 0.7 for GPT-4. (The main text says "5%+", while Table 9 shows +4.8 / +1.4 / +0.7.) This is the oracle caveat that [[Huang 2024 - Large Language Models Cannot Self-Correct Reasoning Yet (arXiv 2310.01798)|Huang 2024]] later generalises.
6. **Feedback quality matters (Table 2, §4).** Specific feedback beats generic feedback, which beats no feedback. Sentiment Reversal scores 43.2 / 31.2 / 0, Acronym Generation 56.4 / 54.0 / 48.0. In a manual failure analysis (70 samples), 33% of failures came from feedback that put the error in the wrong place, 61% from feedback that suggested a wrong fix, and only 6% from the refiner applying good feedback badly.
7. **Weak models cannot run the loop (§4).** Vicuna-13B could not produce feedback in the required format. Even with oracle or hard-coded feedback it often repeated its output or hallucinated a conversation instead of refining.
8. **Costs and limitations (§6).** Every iteration adds two generative calls. The method needs strong few-shot or instruction-following models (all experiments use closed GPT-3.5, GPT-4 and Codex), English only, and offers no guard against misuse. Huang 2024 (Table 8) also shows that the Constrained Generation gain partly comes from an under-specified initial prompt.

## Relevance to GroundOne
- **The baseline that the demo's loop is *not*.** In the demo, the feedback comes from an **external** specialised verifier ([[GroundOne]]) that checks each sentence against the retrieved document, not from the generator judging itself. Self-Refine's own math result (94% "looks good") and the oracle appendix both show that the bottleneck is error *detection*, which is the part GroundOne replaces ([[Verify-and-Revise Loops]]).
- **Feedback must be specific to be useful.** A GroundOne verdict pinpoints the sentence by construction and gives its class (contradicted / not mentioned) and a calibrated probability. That matches the "specific" requirement. It is less "actionable" than a natural-language critique, because GroundOne writes no rationale. The demo should therefore pass the generator the flagged sentence, its class and the relevant document context, not a generic "revise this". The Table 2 gap between specific and generic feedback suggests this choice changes outcomes.
- **Small local generators are a real risk.** The Vicuna-13B failure suggests that a small on-device generator may not follow repair instructions reliably, even with correct feedback. The demo should measure the repair success rate separately from the verifier's accuracy, mirroring the paper's split of failures into feedback errors and refiner errors.
- **Iteration budget.** Most gains arrive in the first 1–2 rounds (Fig. 4), which supports a small `max attempts` in the policy.
- **Cost argument.** Self-Refine pays two LLM generations per round. In the demo loop, one round costs one generator rewrite of the flagged sentences plus one GroundOne forward pass. The verification half is a prefill-only pass, not a generated critique ([[Prefill and Decode]]).

## Links
- Concepts: [[Verify-and-Revise Loops]], [[Hallucination Detection]], [[LLM-as-a-Judge]], [[Groundedness Verification]], [[Demo Application]], [[Small Language Models]]
- Related sources: [[Huang 2024 - Large Language Models Cannot Self-Correct Reasoning Yet (arXiv 2310.01798)]], [[Gou 2024 - CRITIC, LLMs Can Self-Correct with Tool-Interactive Critiquing (arXiv 2305.11738)]], [[Dhuliawala 2024 - Chain-of-Verification Reduces Hallucination in LLMs (arXiv 2309.11495)]], [[Gao 2023 - RARR, Researching and Revising What Language Models Say (arXiv 2210.08726)]]
