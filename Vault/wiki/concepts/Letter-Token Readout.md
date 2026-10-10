---
type: concept
tags: [readout, logits, mcq, first-token, selection-bias, system-one, groundone, evaluation]
---
# Letter-Token Readout

## Definition
A **letter-token readout** turns a language model into a classifier over a closed answer set:
1. The question is written as a multiple choice with one single-token label per option ("A", "B", "C").
2. One forward pass is run up to the answer position.
3. The logits of the label tokens are read there, and only those are compared: $p_k = \mathrm{softmax}(z_{\ell_1},\dots,z_{\ell_n})_k$.

The decision is the argmax over the **admissible** labels; the rest of the vocabulary is ignored. It is the standard way MCQ benchmarks score open models (MMLU, HELM, lm-harness; [[Zheng 2024 - LLMs Are Not Robust Multiple Choice Selectors|Zheng 2024]] §2.1, [[Wang 2024 - My Answer is C (first-token probabilities vs text answers)|Wang 2024]] §3), and the mechanism behind family (b) of [[System One Models]].

**In plain words:** instead of letting the model write an answer and parsing it, ask "of A, B and C, which do you score highest right here?" There is no generation, so there are no format failures and no parsing, and the probabilities come for free.

## Restricted vs full-vocabulary decision
Two decisions can be read from the same logits at the same position:

| | Restricted readout | Full-vocabulary argmax (= greedy first generated token) |
| --- | --- | --- |
| Support | the n label tokens | all ~150K tokens |
| Output always valid? | yes, by construction | no: preambles ("Sure"), spaces, other words |
| Probabilities | conditional on "the answer is one of the labels" | unconditional next-token distribution |
| Equivalent to | constrained decoding of length one ([[Constrained Decoding]]) | free generation, first step |

The two agree only when the model already puts most of its mass on the labels. They disagree whenever the model would write something else first.
- **Zero-shot instruction-tuned models.** The text is the model's "real" answer and the first-token readout is a poor proxy. Llama2-7B-Chat's first-token MMLU answer mismatches its text answer 51.4 % of the time, and accuracy drops from 41.0 to 34.9 (Wang Table 3). Mismatch falls with size and with prompts that demand a single letter, but an example template ("Answer: C") pushes the first token to "C" about 85 % of the time (Wang §4.1).
- **A model trained on the restricted readout.** The readout *is* the trained decision and the generated token becomes the poor proxy. This is GroundOne (below).

## Biases of letter readouts
- **Token / selection bias.** Models put prior mass on particular label tokens independent of content. llama-30B picks A/B/C/D 34.6 / 27.3 / 22.3 / 15.8 % on balanced MMLU; moving all gold answers to A lifts its accuracy by 15.2 points (Zheng Table 1). The bias comes mostly from the ID tokens themselves, not from option position (Zheng §2.4), and prompting does not remove it (§2.6).
- **Contextual label bias.** In few-shot prompts the model favours frequent, recent and pre-training-common labels. The net effect is mostly a shift of the output distribution ([[Zhao 2021 - Calibrate Before Use|Zhao 2021]] §4).
- **Format sensitivity.** Lettered single-token options give the best-calibrated MCQ probabilities ([[Kadavath 2022 - Language Models (Mostly) Know What They Know|Kadavath 2022]] §3). Tokenisation matters: " A" (with a space) and "A" are different tokens.

**Corrections:**
- *Label-free:* contextual calibration (divide by the probabilities for a content-free input; Zhao §5), and PriDe (estimate the ID prior by permuting option contents on a few items, then divide it out; Zheng §3).
- *Supervised:* a per-class bias fitted on held-out data (vector scaling, [[Calibration]]).
- *Design:* a fixed label-to-class mapping turns "selection bias" into a plain class prior, which training and the bias term can absorb.

## How System One models use it
- [[SemIf]] (frozen Qwen3.5-4B) and [[Rizzo-Flow]] (LoRA, soft cross-entropy) read option-letter logits after a shared state prefix. Being zero-shot or lightly tuned, they rely on the model *already* tending to answer with the letter, so readout and generation roughly coincide.
- [[Jev]] (family a) is inferred to use a dedicated head rather than the LM head (see [[System One Models]]).
- [[Asai 2024 - Self-RAG|Self-RAG]] reads its `IsSup` critic tokens as normalised token probabilities, a published precedent for reading a groundedness verdict from logits.

## GroundOne: design (b) and the B2 control
- **Readout.** The answer is written with the marker " Verdict:" after each scored sentence. One pass per answer, the output head is applied only at the markers, and the verdict is the softmax over the logits of A / B / C (supported / contradicted / not mentioned), restricted to those three (`prompts.encode_marked`, `readout.py`). Training uses a class-weighted cross-entropy over the same three logits.
- **Consequence of the restricted loss.** The loss depends only on the *relative* logits of A/B/C, not on their absolute mass. After training, the three readout letters hold only about **4–5 %** of the probability mass at the markers. Left free, the model would write the **spaced** letter " A" (0.5B: 75 % of argmaxes are spaced letters; 3B: 99 %).
- **Control B2** (same weights, same pass, verdict = full-vocabulary argmax mapped to a class, anything else = format failure), on full T1:

| | Restricted readout | Generated token (B2) |
| --- | --- | --- |
| 0.5B three-way | 0.769 | 0.521 (24.7 % format failures, 74.4 % agreement) |
| 3B three-way | 0.832 | 0.761 (1.2 % failures, 92.3 % agreement) |
| 0.5B / 3B at K ≥ 14 | 0.723 / 0.839 | 0.377 / 0.773 |

  Paired cluster bootstrap: readout − generated token = +0.248 [+0.228, +0.269] (0.5B) and +0.071 [+0.059, +0.083] (3B). B2 is skewed towards " A", consistent with a token/class prior.
- **Reading.** With identical weights, latency and pass, the restriction to the admissible options is itself worth +0.07 to +0.25. It matters more the smaller the model. GroundOne is a three-way classifier built on the LM, not a faster generator. Its speed advantage comes from **not generating at all**, not from "generating one token instead of many". Its probabilities are conditional on the answer being A, B or C, and the dev calibration makes them reliable ([[Calibration]]).
- **Possible improvement, not run:** read and train the spaced letters, to align readout and generation. The effect on accuracy is unknown, since the restricted loss is invariant to absolute mass.
- **Untested robustness check:** permuting the letter-to-class mapping for the untrained B1 and the generative judges, to separate judgement from letter preference (Zheng).

## Labels vs definitions, and three readouts on Qwen2.5 (Azizi 2026)
[[Azizi 2026 - Labels Override Definitions in Jev-Style Typed Decision Models (arXiv 2610.02586)|Azizi 2026]] studies requests where each option has a **label** and a **definition**:
- **Option-label bias.** When options are rendered as `"{label}: {definition}"`, the decision follows the label. Deleting all definitions leaves accuracy unchanged, and contradicting labels push it below chance. This holds for Laya's encoder heads and for ordinary LM readouts. On PolicyBench-XF (rule only in the definitions), replacing meaningful labels with A/B gains +0.1511 for laya-typed-decisions, **+0.1203 for a Qwen2.5-7B label-log-probability readout** and +0.1531 for Mistral-7B. Qwen2.5-1.5B is at chance throughout (capacity floor).
- **The cause is rendering.** Removing the label from Laya's input makes it exactly label-invariant; adding it to VON (which renders definitions only) creates the effect.
- **Three readouts on one Qwen2.5 backbone** (length-normalised label log-probability, constrained first token, generate-then-parse). The two scoring readouts agree within their intervals in every cell, so the scoring rule and length normalisation do not matter. Scoring vs generation depends on the suite: generation wins under misleading labels on the uncontrolled suite (0.849 vs 0.501), scoring wins on the controlled one (0.835 vs 0.793), all zero-shot at 7B.
- **Letter priors remain.** Swapping which letter carries which definition, with no contradiction, moves Qwen2.5-7B by +0.0305; a definition-only encoder head is exactly invariant.
- **Mitigations measured:** arbitrary labels (largest gain when the rule is in the definition, a loss when class names are informative); null-state prior correction, i.e. contextual calibration ([[Zhao 2021 - Calibrate Before Use|Zhao 2021]]); two-rendering disagreement flags. A two-call test (rename labels, compare distributions) tells which regime a model is in.

**For GroundOne.** Its labels are already arbitrary letters with a fixed, trained mapping ("Answer A for supported, B for contradicted, C for not mentioned"), and the definitions are fixed rather than caller-supplied, so option-label bias in Azizi's sense does not arise. The residual letter prior (+0.03 at 7B zero-shot) is what the per-class bias in GroundOne's calibration absorbs; the untrained B1 keeps it uncorrected. Azizi's zero-shot scoring-vs-generation result is mixed. GroundOne's fine-tuned B2 gap (+0.07 to +0.25 for the readout) is a different regime: the gap comes from the restricted training loss.

## Links
- Sources: [[Wang 2024 - My Answer is C (first-token probabilities vs text answers)]], [[Zheng 2024 - LLMs Are Not Robust Multiple Choice Selectors]], [[Zhao 2021 - Calibrate Before Use]], [[Kadavath 2022 - Language Models (Mostly) Know What They Know]], [[Willard 2023 - Efficient Guided Generation for LLMs (Outlines)]], [[Asai 2024 - Self-RAG]]
- Concepts: [[System One Models]], [[Constrained Decoding]], [[Calibration]], [[Verbalised vs Logit Confidence]], [[LLM-as-a-Judge]], [[When System One Beats an LLM]], [[Prefill and Decode]]
- Systems: [[GroundOne]], [[SemIf]], [[Rizzo-Flow]], [[Jev]], [[Laya]]
- 2026 evidence: [[Azizi 2026 - Labels Override Definitions in Jev-Style Typed Decision Models (arXiv 2610.02586)]], [[Deusser 2026 - Evaluating and Benchmarking the System One Model Jev (arXiv 2609.37647)]] (open LLMs scored by exact option-code probabilities), [[Decision-Model Benchmarks]]
