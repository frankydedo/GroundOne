---
type: source
author: "Seyedarmin Azizi, Erfan Baghaei Potraghloo, Massoud Pedram (University of Southern California)"
date: 2026-10-01
venue: "arXiv 2610.02586 [cs.AI], preprint"
url: "https://arxiv.org/abs/2610.02586"
tags: [source, paper, decision-models, readout, label-bias, prompt-rendering, qwen2.5, laya, robustness]
---
# Azizi 2026 – Labels Override Definitions in Jev-Style Typed Decision Models

**Raw file**: `raw/Azizi 2026 - Labels Override Definitions in Jev-Style Typed Decision Models (arXiv 2610.02586)_ingested.pdf`

## Overview
In a Jev-style request each option carries a short **label** (e.g. `billing`) and a written **definition**, which is where the caller states the rule. The paper asks whether the returned probability follows the definitions or the labels. It calls a preference for the label **option-label bias**. Systems studied, all open-weight (Jev itself is not measured):
- three [[Laya]] checkpoints (`laya-typed-decisions`, `laya`, `laya-multilingual`);
- **VON**, another open ModernBERT implementation (395M);
- **three readouts on a [[Qwen2.5]] backbone** (0.5B, 1.5B, 7B): length-normalised label log-probability, constrained first-token, and generate-then-parse. Llama-3.1-8B and Mistral-7B serve as cross-checks.

Tasks: eleven public classification tasks, plus **PolicyBench**, a synthetic routing suite in which the rule appears only in the definitions and the gold comes from the generating attributes. The controlled version (XF, both options carry definitions of comparable substance) is the primary suite. Intervals are paired percentile bootstraps (4,000 resamples).

## Key Insights
1. **The labels carry the decision.** For laya-typed-decisions, deleting every definition leaves accuracy unchanged (0.8559 vs 0.8487), although the definitions alone, with letters as labels, support 0.7971 (control with neither channel: 0.5690). When a label contradicts its definition, accuracy falls to 0.1357, below the control: the decision follows the label.
2. **Meaningful names hurt when the rule is in the definition.** On PolicyBench-XF, naming the options A and B instead of `escalate` / `hold` raises laya-typed-decisions accuracy by **+0.1511** [+0.1377, +0.1646] (0.742 → 0.893). Unrelated words and digits recover most of the gap too. Under misleading labels, `laya` falls to 0.5297, near chance (0.5).
3. **The cause is one line of prompt rendering, not the decision head.** Laya writes each option as `"{label}: {definition}"`; VON writes only the definition. Patching that expression, with no weight changed, makes all three Laya checkpoints **exactly invariant** to the labels (+0.0000 [+0.0000, +0.0000]). Adding the label to VON creates the effect: under contradicting labels its accuracy falls from 0.8511 to 0.2281. This refutes an earlier attribution (Sun et al. 2026) to the constrained decision head.
4. **Ordinary LM readouts show the same effect.** The Qwen2.5-7B label-log-probability readout gains **+0.1203** [+0.1019, +0.1395] from A/B labels, comparable to Laya. Mistral-7B gains +0.1531. Qwen2.5-1.5B is at chance in every condition, a capacity floor, not robustness.
5. **Readout comparison on one backbone.** The two scoring readouts (length-normalised log-probability and constrained first token) agree within their intervals in every cell. Scoring vs generation depends on the suite: on the uncontrolled suite under misleading labels, scoring falls to 0.5010 while generation reaches 0.8490; on the controlled suite it reverses (scoring 0.8352, generation 0.7933, Qwen2.5-7B). The paper therefore does not claim that the readout is a second condition for the effect. Even with no contradiction, exchanging which letter carries which definition moves Qwen2.5-7B by +0.0305; for VON it is exactly zero.
6. **Negated questions are not read.** Prefixing a yes/no question with "Is it false that" flips the decision on 96.6–98.3 % of items for the Laya checkpoints and 97.1 % for VON, while the probability barely changes. Accuracy goes from 0.6419 to 0.3576 (sum ≈ 1). An explicit instruction does not help. The Qwen2.5-1.5B readout flips 79.7 %, so typed heads are worse than the LM baseline on polarity.
7. **Confidence ranks errors the wrong way under a corrupted rendering.** Under ordinary labels laya-typed-decisions confidence has error AUROC 0.8123; under misleading labels 0.2433. A confidence gate would then forward correct decisions and accept wrong ones.
8. **Mitigations, measured.** M1, arbitrary labels: +0.1511 on PolicyBench, but it costs accuracy on classification tasks, where the class name is informative. M2, null-state prior correction (contextual calibration, [[Zhao 2021 - Calibrate Before Use|Zhao 2021]]): +0.0391 for laya-typed-decisions and +0.0748 for Qwen2.5-7B under aligned labels; it **destroys** VON (exactly 0.5000). M3, an instruction to ignore labels: +0.0138 only. M4, flagging items where two renderings disagree: 0.8921 accuracy on the unflagged items at 0.81 coverage. **Two-call test:** ask once, rename the labels, ask again; if the distributions differ, the labels matter.
9. **Evaluation audit cited (Tang & Zheng 2026).** Of the first 28 papers on these models, 5 of 26 included a label-probability baseline from an ordinary LM, and 1 of 27 tested invariance to option names.

## Relevance to GroundOne
- **GroundOne's option labels are arbitrary by design.** The fixed instruction reads "Answer A for supported, B for contradicted, C for not mentioned" (`prompts.py`), and the mapping is trained. The label channel carries no class name, which is the condition Azizi finds safest (M1). The definitions are fixed and trained, not supplied by a caller at run time, so option-label bias in Azizi's sense does not arise.
- **Letter priors remain.** Which letter carries which definition still shifts an untrained Qwen2.5 readout (+0.0305 at 7B). For GroundOne this is a class prior absorbed by training and by the per-class bias of the calibration; for the untrained B1 it is uncorrected ([[Letter-Token Readout]]).
- **Scoring vs generation.** Azizi's result on one Qwen2.5 backbone is mixed and suite-dependent, and it is zero-shot. GroundOne's B2 control is fine-tuned and shows a clear readout advantage (+0.07 to +0.25). The two do not conflict: the B2 gap comes from the restricted training loss, which a zero-shot model does not have.
- **Confidence is not a safety net under a systematic error.** When the error is systematic, confidence can rank it backwards. GroundOne's copied-but-altered sentences are a systematic failure, so the thesis should not present thresholding as a fix for them ([[Selective Prediction]]).
- **Baselines the audit asks for.** GroundOne already has both checks the audit found missing in most papers: an ordinary-LM label-probability baseline (untrained B1) and a readout-vs-generation control (B2).

## Links
- Concepts: [[Letter-Token Readout]], [[Laya]], [[System One Models]], [[Calibration]], [[Selective Prediction]], [[Decision-Model Benchmarks]], [[Qwen2.5]]
- Related sources: [[Zhao 2021 - Calibrate Before Use]], [[Zheng 2024 - LLMs Are Not Robust Multiple Choice Selectors]], [[Wang 2024 - My Answer is C (first-token probabilities vs text answers)]], [[Convai Innovations 2026 - Laya model card]], [[Deusser 2026 - Evaluating and Benchmarking the System One Model Jev (arXiv 2609.37647)]]
