---
type: concept
tags: [calibration, uncertainty, verbalized-confidence, logits, llm-as-a-judge, evaluation, groundone]
---
# Verbalised vs Logit Confidence

## The two ways to get a probability out of an LLM
- **Logit (token-probability) confidence.** Read the model's probability for the answer token(s), e.g. $P(\text{A})$ vs $P(\text{B})$ renormalised over the options, or $P(\text{True})$ for a proposed answer. It needs white-box access, costs no extra generation, and can be fixed post hoc by temperature or affine scaling ([[Calibration]]).
- **Verbalised confidence.** The model *writes* a number ("0.8") or a phrase ("likely"), optionally after reasoning, several guesses, or several samples. It works through any text API but needs generation, often many tokens or several calls.

**In plain words:** either look at how much weight the model puts on each answer internally, or ask it to tell you how sure it is. They are different measurements and do not have to agree.

## What the literature finds
| Source | Setting | Finding |
| --- | --- | --- |
| [[Kadavath 2022 - Language Models (Mostly) Know What They Know\|Kadavath 2022]] | Base and RLHF Anthropic models, MCQ and P(True) | Logit probabilities of lettered options are well calibrated with the right format, improving with size. RLHF policies look overconfident, but one temperature (T = 2.5) largely fixes them (§3.3). |
| [[Tian 2023 - Just Ask for Calibration\|Tian 2023]] | Large RLHF models (GPT-3.5/4, Claude, Llama-2-70B-Chat), factual QA | Verbalised confidence is often *better* calibrated than "label probability", about 50 % lower ECE. But for closed APIs the label probability was estimated from 10 samples, not read from logits. Llama-2-70B-Chat verbalises less consistently. |
| [[Xiong 2024 - Can LLMs Express Their Uncertainty\|Xiong 2024]] | GPT-3/3.5/4, Vicuna-13B, LLaMA-2-70B, reasoning QA | Verbalised confidence is overconfident: 80–100 %, multiples of 5. GPT-4's average failure-prediction AUROC is only 62.7 %. Prompting lowers ECE without improving AUROC. Sampling plus consistency helps (GSM8K AUROC 54.8 → 92.7 % with M = 5). White-box token probability beats verbalised, but narrowly (AUROC 0.522 → 0.605, §B.1). |

Synthesis:
1. Large RLHF models can verbalise usefully; small open models mostly cannot.
2. The cheapest *good* verbalised methods need several samples, so they multiply the decode cost.
3. **ECE alone cannot separate the two**: a constant confidence can reach a low ECE (Tian fn. 5; Xiong §5.2, where GPT-4 gets ECE 0.064 on GSM8K by saying 100 % for everything). Ranking metrics are needed: AUROC, and AURC from [[Selective Prediction]].

## GroundOne's measurement: the equal-output judge (B0d, D25)
To compare at **equal output**, zero-shot same-size Qwen2.5 judges were asked for GroundOne's content per sentence (a label plus three probabilities), in two variants:
- **B0d-verbal:** a JSON object with label and stated probabilities.
- **B0d-logit:** the terse judge, with P(A), P(B), P(C) read from the logits at the generated letter and renormalised over the three letters.

All systems got the same temperature + per-class bias, fitted on 200 dev answers. 200 T1 answers (latency subset):

| System | Three-way | Format failures | Binary AUROC | ECE raw → cal. | AURC cal. | s/answer K ≥ 14 |
| --- | --- | --- | --- | --- | --- | --- |
| GroundOne 0.5B | 0.835 | 0 % | 0.940 | 0.298 → 0.034 | 0.009 | 0.41 |
| B0d-logit 0.5B | 0.234 | 23.5 % | 0.483 | 0.350 → 0.039 | 0.063 | 0.81 |
| B0d-verbal 0.5B | 0.234 (0.081 with tied unlabelled entries as failures) | 30.9 % | 0.470 | 0.526 → 0.051 | 0.061 | 2.47 |
| GroundOne 3B | 0.900 | 0 % | 0.969 | 0.181 → 0.030 | 0.005 | 2.57 |
| B0d-logit 3B | 0.390 | 0.1 % | 0.681 | 0.181 → 0.041 | 0.048 | 4.38 |
| B0d-verbal 3B | 0.410 | 0 % | 0.576 | 0.367 → 0.044 | 0.062 | 17.00 |

Findings, and how they line up with the literature:
- **Verbalised probabilities are nearly uninformative at this size.** The 3B writes a one-hot vector for 93 % of sentences (16 distinct vectors in 1,747). The 0.5B writes tied vectors ([1/3, 1/3, 1/3], [0.5, 0.5, 0]). This is the small-model end of Xiong's coarse-verbalisation pattern; it is not Tian's large-RLHF regime.
- **Logit beats verbalised** (3B AUROC 0.681 vs 0.576) at about a quarter of the latency. This matches Xiong §B.1 and Kadavath.
- **Training beats both by a wide margin.** GroundOne reaches AUROC 0.94–0.97 and AURC 5–12× lower. The gap comes from training, not from the readout: B0d-logit makes the same decisions as the terse judge (macro 0.390).
- **ECE is uninformative after calibration.** All systems end at 0.03–0.05. The discriminating metrics are AUROC and AURC ([[Expected Calibration Error]]).
- **Writing the probabilities is expensive.** The 3B verbal judge is as slow as the verbose judge (17.0 s vs 15.9 s at K ≥ 14, 248 generated tokens) and no more accurate than the terse one.

**Caveats.** The judges are zero-shot and GroundOne is fine-tuned, so B0d measures "what a same-size generative judge gives at equal output", not the readout alone. The readout-alone comparisons are B1 vs B0d-logit (both untrained) and the B2 control ([[Letter-Token Readout]]). The judges ran without grammar constraints, which inflates the 0.5B format failures ([[Constrained Decoding]]).

## Links
- Sources: [[Kadavath 2022 - Language Models (Mostly) Know What They Know]], [[Tian 2023 - Just Ask for Calibration]], [[Xiong 2024 - Can LLMs Express Their Uncertainty]], [[Guo 2017 - On Calibration of Modern Neural Networks]], [[Wang 2024 - My Answer is C (first-token probabilities vs text answers)]]
- Concepts: [[Calibration]], [[Expected Calibration Error]], [[Selective Prediction]], [[LLM-as-a-Judge]], [[Letter-Token Readout]], [[Constrained Decoding]], [[Prefill and Decode]], [[System One Models]]
- Systems: [[GroundOne]], [[Jev]]
