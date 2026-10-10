---
type: concept
tags:
  - evaluation
  - metrics
---
# LLM-as-a-Judge

LLM-as-a-Judge is an evaluation paradigm where a Large Language Model (or a [[System One Models|System One Model]] like [[Jev]]) is used to score, grade, or evaluate the outputs of another AI system.

## Applications
- **Quality Assurance**: Checking if an answer is factually correct based on provided documentation.
- **Routing**: Evaluating prompts to decide which model or tool should handle them.
- **Monitoring**: Running at scale in production (e.g., using MLflow) to catch regressions or hallucinations.

## Key Considerations
- **Rationale vs. Speed**: Traditional LLMs can provide a text-based rationale (explaining *why* an answer is bad), which is great for debugging. However, they are slow and expensive.
- **System One Evaluators**: Models like [[Jev]] provide instant, cheap classifications with calibrated probabilities but lack the ability to generate explanatory text. They are ideal for large-scale evaluation pipelines where cost and latency are critical bottlenecks.

## Judge formats (Zheng et al. 2023)
[[Zheng 2023 - Judging LLM-as-a-Judge]] (MT-Bench / Chatbot Arena) defines three formats (§3.1):
- **Pairwise comparison**: pick the better of two answers or tie. Pairs grow quadratically with the number of systems.
- **Single-answer grading**: assign a score (e.g. 1–10). Scales better but absolute scores may fluctuate across judge models.
- **Reference-guided grading**: the judge sees a reference answer. Faithfulness/groundedness checking is a version of this: the retrieved context is the reference.

## Agreement with humans (measured)
- GPT-4 vs expert humans on MT-Bench: **85%** agreement on non-tie votes, above human–human **81%**; ~66% for both when ties are counted (Zheng 2023, Table 5). Chatbot Arena: GPT-4 vs crowd 87% (Table 6).
- Agreement grows from ~70% to ~100% as the quality gap between the compared models grows (Zheng 2023, Fig. 2): LLM judges are most reliable on easy contrasts.
- RAG faithfulness: a decomposed prompt (extract statements, then Yes/No per statement) agrees with humans 0.95 on WikiEval, vs 0.72 for a direct 0–10 score prompt and 0.54 for pairwise ranking with the same ChatGPT model ([[Es 2024 - RAGAS]], Table 1). How the judge is prompted matters more than which model is used.
- A **fine-tuned small judge** (DeBERTa-v3-Large, ARES) ranks RAG systems better than few-shot GPT-3.5 (Kendall's τ ~0.06 higher on average) and much better than RAGAS ([[Saad-Falcon 2024 - ARES]] §5.1). Its per-example faithfulness accuracy on AIS is still only 62.5–84.0% (ARES Table 2).

## Known biases and failure modes
From [[Zheng 2023 - Judging LLM-as-a-Judge]] (§3.3, measured unless noted):
- **Position bias**: when the two answers are swapped, the verdict stays the same only 65.0% (GPT-4), 46.2% (GPT-3.5), 23.8% (Claude-v1) of the time; Claude-v1 prefers the first answer 75% of the time (Table 2). Also a name bias toward "Assistant A".
- **Verbosity bias**: answers padded with rephrased content win 91.3% of the time with GPT-3.5 and Claude-v1, 8.7% with GPT-4 (Table 3, 23 answers).
- **Self-enhancement bias**: GPT-4 ~10% and Claude-v1 ~25% higher win rate for themselves, but the authors say they **cannot conclude** it exists (limited data). Relevant to self-critique designs such as [[Asai 2024 - Self-RAG|Self-RAG]], where the generator judges its own output.
- **Limited reasoning**: GPT-4 is misled by wrong candidate answers on math it can solve; reference-guided judging cuts failures 70% → 15% (Table 4).
- **Prompt sensitivity**: holistic scoring prompts are sensitive to prompt design; pairwise selection is affected by order ([[Es 2024 - RAGAS]] §2).
- **Domain shift**: fine-tuned judges degrade on drastic shifts (ARES τ 0.28–0.38 on code, cross-lingual, entity extraction; §5.4).

Mitigations proposed by Zheng et al.: evaluate both orders and only count consistent wins; few-shot examples (GPT-4 consistency 65.0% → 77.5%); chain-of-thought; reference answers; fine-tuning an open judge (preliminary).

## Cost and latency
- Zheng et al. motivate LLM judges as cheaper and faster than **humans**, but report no per-judgement latency or price (not stated). They note few-shot judge prompts make API calls **~4× more expensive** (§3.4).
- RAGAS faithfulness needs at least two generative calls per answer, and its verification prompt asks for an explanation before each verdict, so cost is dominated by output tokens ([[Prefill and Decode]]).
- ARES picked GPT-3.5 over GPT-4 as a baseline "due to the lower financial costs"; its own judges need ~32 GB GPUs and hours of fine-tuning but are cheap at inference (ARES §7, Table 1).
- Independent measurement on a small set: see [[Jev vs LLMs Cost Comparison]] and [[Can Jev replace your LLM judge]].

## Generative judge vs System One judge
| | Generative LLM judge | [[System One Models|System One]] judge (e.g. [[Jev]], GroundOne) |
| --- | --- | --- |
| Output | Text: rationale + verdict/score, parsed afterwards | Probabilities over a closed answer set, read from logits |
| Cost per decision | Prefill + many decode steps | Prefill only (one forward pass); shared context reusable via [[KV Cache]] |
| Explanation | Yes (the claimed "explainability" advantage, Zheng §3.2) | **None**: returns a probability, no rationale |
| Format failures | Possible (Zheng Table 2 lists up to 3.8% wrong-format outputs; 23–97 % for unconstrained 0.5B judges in GroundOne) | Not possible by construction (the readout is a one-step mask over the answer letters, [[Constrained Decoding]]) |
| Biases | Position, verbosity, self-enhancement (measured above) | Option-order sensitivity of the readout still possible and must be tested; no self-enhancement if the judge is a separate model |
| Confidence | Verbalised or ad hoc (coarse and overconfident: [[Xiong 2024 - Can LLMs Express Their Uncertainty]]) | Probability, but [[Calibration]] must be measured, not assumed ([[Verbalised vs Logit Confidence]]) |

A System One judge therefore trades the rationale for speed and a probability. For RAG groundedness this is often acceptable when the output is used for gating or highlighting unsupported sentences; when an audit trail is needed, a hybrid that escalates low-confidence cases to a generative judge is the natural design ([[When System One Beats an LLM]]). Self-RAG's `IsSup` critic token, consumed as a normalised token probability, is the closest published precedent for reading a groundedness verdict from logits ([[Asai 2024 - Self-RAG]]).

## Small local judges in GroundOne (measured, 2026-10-09/10)
Zero-shot Qwen2.5 judges of the same size as GroundOne (0.5B, 3B), MLX in-process, greedy decoding, on the 200-answer T1 latency subset:

| Judge | 0.5B three-way / format failures | 3B three-way / format failures | Speed vs GroundOne at K ≥ 14 |
| --- | --- | --- | --- |
| Terse (B0a): one letter per sentence | 0.233 / 23 % | 0.390 / 0.1 % | GroundOne 1.95× (0.5B), 1.73× (3B) faster |
| Verbose (B0b): rationale then verdict | 0.017 / 97 % | 0.402 / 7.6 % | about 6.2× faster |
| Equal output, logits (B0d-logit) | 0.234 / 23.5 % | 0.390 / 0.1 % | about 2× faster |
| Equal output, verbalised JSON (B0d-verbal) | 0.234 (0.081 strict) / 30.9 % | 0.410 / 0 % | 6–7× faster |
| **GroundOne** (System One) | **0.835 / 0 %** | **0.900 / 0 %** | reference |

- **Format failures** dominate the 0.5B judges because no grammar-constrained decoding was used. This keeps one protocol across judges and is stated as a limitation. See [[Constrained Decoding]].
- **Confidence at equal output.** Verbalised probabilities are almost uninformative (3B: one-hot for 93 % of sentences). Logit-read probabilities are better (3B AUROC 0.68 vs 0.58) but far from GroundOne (0.94–0.97). After the same calibration every judge has ECE 0.03–0.05, so ECE alone cannot rank them. See [[Verbalised vs Logit Confidence]].
- **Readout matters even with the same weights.** Using GroundOne's own fine-tuned model as a single-token generator (control B2) costs 0.25 (0.5B) / 0.07 (3B) three-way. See [[Letter-Token Readout]].
- **Fairness caveat.** The judges are zero-shot, while GroundOne is fine-tuned in domain (RAGTruth). The comparison measures what a same-size generative judge offers out of the box, not the readout alone.
- Letter-based judges inherit **option-ID token bias** ([[Zheng 2024 - LLMs Are Not Robust Multiple Choice Selectors]]). First-token and text answers of instruction-tuned judges can disagree ([[Wang 2024 - My Answer is C (first-token probabilities vs text answers)]]).

## Related
[[Verbalised vs Logit Confidence]], [[Constrained Decoding]], [[Letter-Token Readout]], [[Statistical Significance and Bootstrap]], [[RAG Evaluation Frameworks]], [[Retrieval-Augmented Generation]], [[Groundedness Verification]], [[Hallucination Detection]], [[LLM-AggreFact]], [[RAGTruth]], [[Calibration]]
