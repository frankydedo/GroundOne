---
type: source
author: "Xinpeng Wang, Bolei Ma, Chengzhi Hu, Leon Weber-Genzel, Paul Röttger, Frauke Kreuter, Dirk Hovy, Barbara Plank"
date: 2024
venue: "Findings of ACL 2024 (arXiv 2402.14499)"
url: "https://arxiv.org/abs/2402.14499"
tags: [source, paper, mcq, first-token, logit-readout, instruction-tuning, evaluation, llm]
---
# Wang 2024 – "My Answer is C": First-Token Probabilities Do Not Match Text Answers

**Raw file**: `raw/Wang 2024 - My Answer is C (first-token probabilities vs text answers)_ingested.pdf`

## Overview
Multiple-choice evaluation of LLMs usually ranks the option letters by the log-probability of the **first token** after the prompt and takes the argmax ("first-token evaluation"). The paper asks how often that answer agrees with the answer the model actually **writes** when it generates freely. Six instruction-tuned models are tested (Llama2-Chat 7B/13B/70B, Mistral-Instruct v0.1/v0.2, Mixtral-8x7B-Instruct) on MMLU and a 414-question public-opinion subset of OpinionQA (§3). Text answers are mapped to options by a QLoRA-fine-tuned Mistral-7B classifier with 99 % accuracy (Table 2). The answer: the two evaluation modes are **severely misaligned**, with mismatch rates above 60 % in the worst case (abstract, §4.1).

## Key Insights
1. **Mismatch is large and size-dependent.** On OpinionQA the Llama2 mismatch falls from 66.2 % (7B) to 13.3 % (70B); Mistral models mismatch less (Fig. 2a). On MMLU with the medium-constraint instruction, Llama2-7B mismatches 51.4 % and its accuracy drops from 41.0 (text) to 34.9 (first token); Mixtral mismatches 9.0 % (Table 3). Strongly chat- or safety-tuned models are hit hardest.
2. **Why.** Instruction-tuned models open with a preamble ("Sure! Here's my response: …"), hedge, choose several options, or refuse. The first-token distribution over A/B/C/D then says little about the final answer (Fig. 1, Table 8). Refusals explain part but not all of the mismatch (light bars in Fig. 2a; §4.2).
3. **Constraining the prompt helps but does not close the gap.** Asking for "only a single letter" (medium) or "start your answer with a single letter" (high) lowers mismatch for five of six models (Table 1, Fig. 2a). An example template with "Answer: C" makes things worse: Llama2-70B's first token picks "C" about 85 % of the time, against 32.1 % under the high-constraint prompt, while the text answers stay spread out (§4.1, Fig. 3). The first-token distribution copies the template; the text does not.
4. **First-token answers are less consistent.** Under ten option shuffles, first-token choices have higher entropy than text answers for five of six models (Table 4), i.e. more selection bias.
5. **Decoding temperature.** Higher temperature lowers mismatch and refusal but hurts consistency (App. A.1).
6. **Limitation stated by the authors.** Only first-token log-probabilities are studied, not full-sequence likelihoods of each option (Limitations).

## Relevance to GroundOne
- The paper is the main reference for the claim that **reading option-letter logits is not the same as asking the model to answer**. GroundOne's control **B2** measures exactly this gap on the same weights and the same pass. The result points in the *opposite* direction from Wang's, and the two readings fit together:
  - Wang study zero-shot instruction-tuned models, where the free text is the "real" answer and the first token is a poor proxy for it.
  - GroundOne is **trained on the restricted readout** (class-weighted cross-entropy over the logits of A/B/C only). The readout is therefore the trained decision, and the generated token is the poor proxy. With full-vocabulary argmax at each " Verdict:" marker, T1 three-way accuracy falls from 0.769 to 0.521 for the 0.5B (24.7 % format failures, 74 % agreement) and from 0.832 to 0.761 for the 3B (1.2 % failures, 92 % agreement). After the marker the model would write the *spaced* letter " A"; the three readout letters hold only about 4–5 % of the probability mass. See [[Letter-Token Readout]].
- Both results support one statement for Ch. 3: **first-token probability and generated text are two different decision rules**, and only one of them can be the trained target. A [[System One Models|System One]] chooses the restricted readout by definition. The claim must not be phrased as "one generated token instead of many".
- Wang's preamble effect is relevant to the **zero-shot baselines**. The untrained B1 (design (a)) reads the letter at the start of the assistant turn, where an instruction-tuned Qwen2.5 might prefer a preamble. Per the project notes, the unspaced letter is the natural first token there, but this should be verified by the share of probability mass on the letters, as was done for B2.
- The example-template effect (Fig. 3) is a warning for judge prompts. The project already observed it: with a numeric example in the B0d prompt, the 3B copied the example probabilities `[0.8, 0.1, 0.1]` in 9 of 110 sentences, so placeholders were used instead.

## Links
- Concepts: [[Letter-Token Readout]], [[System One Models]], [[LLM-as-a-Judge]], [[Constrained Decoding]], [[Verbalised vs Logit Confidence]]
- Related sources: [[Zheng 2024 - LLMs Are Not Robust Multiple Choice Selectors]], [[Zhao 2021 - Calibrate Before Use]], [[Kadavath 2022 - Language Models (Mostly) Know What They Know]], [[Willard 2023 - Efficient Guided Generation for LLMs (Outlines)]]
- Thesis context: [[GroundOne]], [[When System One Beats an LLM]]
