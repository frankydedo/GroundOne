---
type: source
author: "Katherine Tian, Eric Mitchell, Allan Zhou, Archit Sharma, Rafael Rafailov, Huaxiu Yao, Chelsea Finn, Christopher D. Manning"
date: 2023
venue: "EMNLP 2023 (arXiv 2305.14975)"
url: "https://arxiv.org/abs/2305.14975"
tags: [source, paper, calibration, verbalized-confidence, rlhf, llm]
---
# Tian 2023 – Just Ask for Calibration

**Raw file**: `raw/Tian 2023 - Just Ask for Calibration_ingested.pdf`

## Overview
The paper evaluates ways to get confidence scores out of **RLHF-tuned LLMs**: gpt-3.5-turbo, GPT-4, Claude 1, Claude 2 and Llama-2-70B-Chat. Datasets are TriviaQA, SciQ and TruthfulQA. The main finding is that **verbalized confidence** (the model writes "0.8" or "likely") is often *better* calibrated than the model's conditional probabilities. It often **reduces ECE by about 50% relative** (abstract, §3).

## Key Insights
1. **RLHF degrades logit calibration.** Fig. 2 (Llama-2-70B base vs. chat) shows ECE rising and AUC falling after RLHF. The explanation (§1): the RL objective concentrates mass on the preferred answer instead of matching frequencies.
2. **Methods compared (§2)**:
   - **Label prob.**: $p(y\mid x)$, **estimated from 10 samples** because the closed APIs exposed no token log-probs;
   - **'Is True' prob.**: a Kadavath-style $P(\text{True})$, also estimated from samples;
   - **Verb. 1S/2S top-k**: numeric probabilities given in one or two stages;
   - **Ling. 1S**: linguistic expressions ("almost certain", ...) mapped to numbers using a human survey, or optimised on held-out data;
   - CoT variants.
3. **Results (Tables 1–5).** For gpt-3.5-turbo on TriviaQA, Label prob. has ECE 0.140, while Verb. 1S top-2 has 0.050. On SciQ: 0.256 → 0.132 (top-2), and 0.065 for top-4. Asking for **several candidate answers before the confidence** ("considering the opposite") helps. **CoT does not help** verbalized calibration. Llama-2-70B-Chat improves less consistently. Claude 1 verbalizes badly; Claude 2 is better (§3).
4. **Metrics (§2)**:
   - **ECE** (also after temperature scaling, "ECE-t");
   - **Brier score on temperature-scaled confidences (BS-t)**;
   - **AUC of selective accuracy vs. coverage**, taken from [[Geifman 2017 - Selective Classification for Deep Neural Networks|Geifman & El-Yaniv 2017]].

   Footnote 5 gives a key pitfall: *"For binary classification, a system that guesses randomly and outputs 50% confidence each time has perfect ECE."*
5. **Limitations (§4).** Only short-form factual QA was tested. Correctness was judged by GPT-4/3.5 equivalence checks. Closed models offer few details about what makes verbalization work.

## Relevance to GroundOne
- This is the **counter-argument** GroundOne has to address. If verbalized confidence from a large RLHF model is well calibrated, why read logits? Points for the thesis:
  1. Tian's "logit" baseline for closed models is a **sampling estimate**, not a real logit readout. It is also the *untrained* conditional of an RLHF model.
  2. GroundOne reads the **true restricted logits** of a model **fine-tuned for the decision** and then temperature-scaled, which is a different regime.
  3. Verbalized confidence needs **generation** (dozens of tokens per verdict, sometimes two stages). This is exactly the decode cost that a System One avoids. See [[Prefill and Decode]].
- A natural **baseline** for the evaluation: an [[LLM-as-a-Judge]] that verbalizes a support probability per sentence (Verb. 1S style). Compare its ECE, Brier and AURC, and its latency, against GroundOne.
- Metric hygiene: never report ECE alone (footnote 5). Report ECE + Brier + NLL + AURC, and also ECE after temperature scaling to separate "fixable" miscalibration from poor ranking. See [[Expected Calibration Error]] and [[Selective Prediction]].
- Open question the paper raises in §4: whether long-form outputs become more reliable if they are broken into **a sequence of short questions**. GroundOne's per-sentence verification is one concrete version of that idea.

## Links
- Concepts: [[Calibration]], [[Expected Calibration Error]], [[Selective Prediction]], [[LLM-as-a-Judge]], [[Hallucination Detection]]
- Related sources: [[Kadavath 2022 - Language Models (Mostly) Know What They Know]], [[Guo 2017 - On Calibration of Modern Neural Networks]], [[Geifman 2017 - Selective Classification for Deep Neural Networks]]
- Thesis context: [[System One Models]], [[When System One Beats an LLM]], [[Groundedness Verification]]
