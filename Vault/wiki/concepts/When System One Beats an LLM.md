---
type: concept
tags: [synthesis, system-one, llm, decision-making, trade-offs]
---
# When a System One Model Beats an LLM

Synthesis page answering: *"When is a [[System One Models|System One model]] actually advantageous over an LLM?"*

## Short answer
A System One model wins when the task is a **closed-form decision over a given state**, not an open-ended generation. Formally: the answer space is finite and known at call time (boolean, score, one-of-N), the decision is **high-frequency or latency-sensitive**, and **nobody needs to read an explanation**. Remove any of these three and the advantage shrinks or reverses.

## Where the advantage comes from (mechanism)
1. **No autoregressive decoding.** The model ends prefill with a readout head and returns probabilities directly ([[Jevs Architecture Unmasked|Hume's probing]], [[Jev Input and Output Format]]). Latency is one forward pass instead of TTFT + N sequential tokens, so it is flat and has a tight p50/p99 (no variable-length verbose output).
2. **Shared state, many questions.** The state is prefilled once into the [[KV Cache]] and Q questions branch in parallel. Cost goes from ~Q·S to ~S. This is the strongest argument whenever *many decisions are asked on the same context* (e.g. 21 criteria on one document, a guardrail + a router + a scorer on the same agent step).
3. **Type-safe by construction.** The output can only be a valid Noul/Choice/Score, so there are no schema/JSON failures and no parser. (It can still choose the *wrong* valid option, so this is not "zero hallucination".)
4. **Calibrated probabilities (claimed).** With [[Reinforcement Learning with Calibrated Decisions]] the probability is meant to be usable as a confidence threshold (auto-act above 90%, escalate to a human below 50%). An LLM's verbalized or logit confidence is generally not usable this way.
5. **Cheap enough to be used everywhere.** Jevons-style: when a decision costs ~$0.04/MTok, you can afford to make micro-decisions the agent loop previously skipped.

## Ideal use cases
| Use case | Why System One fits |
| --- | --- |
| Agent routing / tool selection ([[Function Calling]], [[LangChain]] `ModelRouterMiddleware`) | Closed set of options, runs on every step of the loop, latency compounds |
| Guardrails / risk-gating tool calls (`AutoModeMiddleware`) | Binary, must be fast and thresholdable |
| Large-scale [[LLM-as-a-Judge]] monitoring | Millions of judgments, only a verdict is needed |
| Sentence-level [[Groundedness Verification]] of RAG answers (this thesis) | Three-way per sentence, K sentences share one retrieved context, needs a thresholdable probability |
| Structured extraction/scoring over many documents (CV scoring, metadata) | Same state, many rubric questions, batch |
| Real-time control (games, simulations) | 10–30 decisions/s needed |
| Confidence-gated human-in-the-loop | Needs calibrated probabilities |

## Evidence for the advantage
| Evidence | Result | Strength |
| --- | --- | --- |
| Vendor claims ([[jev_simone_rizzo]], [[Che cos'e Jev Spiegazione]]) | up to 193x faster / 444x cheaper; 70–500 ms | Marketing, not independent |
| MLflow judge test ([[Jev vs LLMs Cost Comparison]]) | Jev 100% agreement, 369 ms, $0.0247/1k vs 0.9–1.9 s and $0.06–$3.78/1k for LLMs | Independent but only 30 examples |
| SemIf Phase 1 ([[SemIf RESULTS]], `SystemOne_repos/SemIf/docs/RESULTS.md`) | Same 4B model: 21 criteria in 1.02 s via direct readout vs 5.33 s with the best valid JSON baseline (111 tokens), but only 18/21 same answers; throughput 20 vs 2.3 decisions/s with shared prefix + parallel suffixes | Third-party, frozen model, single state, RTX 3090 |
| [[Rizzo-Flow]] ([[Rizzo-Flow README]]) | 4B Q8_0: ~49 ms per short decision; 20.99 vs 2.60 decisions/s shared vs fresh; LoRA soft-CE fine-tune: typed-decisions accuracy 0.574 → 0.648, ECE 0.349 → 0.112 (2,000 decisions) | Third-party, RTX 5060 Ti; Jev reference from a dataset card |
| [[CLM]] ([[CLM README]]) | 36–44 ms for 1–1,024 candidates (RTX 4090) vs Jev 131–579 ms; but T-Rex agreement with the planner 0.658 vs Jev 0.987 | Speed: author measurement; quality: repo result files, 5 seeds |
| **[[GroundOne]]** (this thesis, [[GroundOne Results]]) | Same-size comparison on the same M4: at K ≥ 14, 1.95× (0.5B) / 1.73× (3B) faster than a terse and ≈ 6.2× than a verbose judge; always-valid output vs 23–97 % judge format failures (0.5B); 1.3–4.1× less energy; T1 three-way 0.769 / 0.832 vs ≤ 0.41 for the judges | Own measurement, 200 answers, bootstrap CIs; in-process MLX only |
| Earlier abandoned experiment: LoRA tool routing (`Project_old/LoRA_Finetuning`) | Qwen2.5 0.5B logit-routing: 86.5% accuracy at ~166 ms/prompt; 3B 8-bit: 87.8% at ~602 ms. Wrong tool picked only 6/304 times; errors are almost all abstain (`Z`) decisions | Own measurement, on-device (Apple Silicon); routing thesis abandoned |
| Earlier abandoned experiment: routing hypothesis (`Project_old/Benchmark&Results/expected_results.md`) | O(1) flat latency vs O(L) for generative router | Hypothesis, never confirmed (abandoned) |
| [[Deusser 2026 - Evaluating and Benchmarking the System One Model Jev (arXiv 2609.37647)\|Deußer 2026]] (independent, 2026-09) | Jev zero-shot on 37 datasets (346,009 requests, US$9.15): above a Qwen3.8-27B letter readout on 27 of 37 datasets (11 significant, none of Qwen's 9 leads significant), above Gemma-4-E4B on all 37; LLM-AggreFact 78.6 vs 76.9 / 75.6; choice ECE 0.028 pooled | Academic, full splits, bootstrap CIs, raw responses released. Against open LLMs read **without generation** in one pass, so it shows Jev's quality, not a decode-vs-readout speed gain. Contamination not excluded |
| [[morrenhale 2026 - Decision benchmark Jev vs Laya vs Julia-1 dataset card\|morrenhale]] (independent, 2026-09) | 19,776 decisions: Jev 0.775 / ECE 0.105, Laya (open encoder, zero-shot) 0.590 / 0.222, Julia-1 0.727 / 0.172; Laya wins only AG News | Auditable (manifests, predictions, paired bootstrap). System One vs System One: says nothing about System One vs LLM |
| [[Yong 2026 - DecideBench dataset card\|DecideBench]] (independent, 2026-10) | Jev 98.0 % at $32 per million tasks vs general LLMs 99.2–99.8 % at 6–14× the cost; self-hosted decoder decision models 63–95 %; encoders 35–60 % (Laya 59.8 %) | The only board that prices LLMs and System Ones together. 400 Claude-written items; LLMs **are more accurate**, so the System One gain here is cost and latency, not accuracy |
| [[mlboydaisuke 2026 - Decision models on Core AI (JevBench public231) dataset card\|Core AI on M4 Max]] (independent, 2026-09) | Local decoder System Ones that re-prefill the state per question take 40–220 s per question on 3k-token states; a truncating encoder answers in 0.02 s but reads only 256 tokens | On-device evidence that the **shared-context design**, not the System One label, decides cost on long documents. Contended GPU |
| [[Li 2026 - JEV-as-a-Judge (arXiv 2609.26550)\|Li 2026]] (academic, CMU, 2026-09/10) | Jev as a judge: 8th of 15 LLM judges, 1.7 points behind GPT-6, at 277× lower fee and 0.15 s median; within ~1 point on HaluEval evidence-grounded factuality (87.3 vs 88.4), 7–28 points behind where verdicts must be derived; a frozen confidence-gated cascade beats GPT-6 by 0.9 points at 41 % of its fee | Strongest evidence so far for the **hybrid** rule: System One where the verdict can be read off the text, escalate the rest. One proprietary Jev version; overlap with benchmarks unknown |
| [[multimodalart 2026 - Jev Decision Index (Hugging Face Space)\|Decision Index RAGTruth]] (community board, 2026-09-28) | Response-level hallucination F1 for 70 decision models: < 1B entrants best 0.553 (chance 0.518), ≥ 15B all above 0.6, Jev 0.765, best 0.803 | Zero-shot general System Ones of GroundOne's size **cannot** verify groundedness; capacity or task training is required. Supports H1 (specialisation). Community harness |
| [[Deka 2026 - From Retrieval to Typed Decisions SBERT2S1 (arXiv 2610.02486)\|Deka 2026]] (academic, 2026-10) | Fine-tuned encoders beat zero-shot 27–31B LLMs on seen biomedical tasks (70.2–75.0 vs 57.4–65.7) with better calibration, lose on held-out tasks (31.0 vs 52.6); routing the 20 % least confident to the LLM raises accuracy | In-domain specialists win, out-of-domain LLMs win: the same pattern as GroundOne T1 vs T3 |


**Critical reading of the 2026 independent evidence (ingest 2026-10-10).**
1. The independent boards confirm that a strong System One (Jev) is accurate and calibrated on short, closed decisions, and much cheaper than a general LLM at similar accuracy (DecideBench).
2. They do **not** show that System Ones beat LLMs on accuracy. On DecideBench three general LLMs are more accurate. On Deußer's suite the reference LLMs are scored *as System Ones* (letter readout, one pass), and a 27B readout is within intervals of Jev where it leads.
3. Small open System Ones are far weaker zero-shot than Jev. Encoders lose most: Laya 0.590 vs 0.775 (morrenhale), 59.8 % vs 98.0 % (DecideBench).
4. On LLM-AggreFact a closed System One (Jev 78.6) and a zero-shot 27B readout (76.9) are above GroundOne 3B (74.8). GroundOne's case rests on in-domain specialisation (T1), full locality on 16 GB, and per-answer cost with K sentences, not on beating every System One on T2 ([[Decision-Model Benchmarks]]).
5. *(Added 2026-10-10, `decision-model` tag.)* The second wave of evidence sharpens the boundary rather than moving it: decision-only judges match strong LLMs where the verdict can be read off the evidence (HaluEval factuality) and fail where it must be derived (Li 2026); on response-level RAGTruth only large general System Ones are useful zero-shot, so a 0.5B/3B verifier must be specialised (Decision Index). Confidence-gated escalation with a locally validated threshold is the recommended deployment pattern in both academic studies (Li 2026, Deka 2026).

## When it is NOT advantageous (use an LLM)
- **You need an explanation/rationale.** System One returns no text. For debugging, iterating on prompts or audit trails an LLM judge is better ([[LLM-as-a-Judge]]).
- **Open-ended output**: writing, summarising, code, translation, free-form arguments for a tool call. Tool *selection* fits System One; tool *parameter filling* (generating the JSON arguments) does not.
- **Multi-step reasoning / chain-of-thought.** The point is *not* thinking at length. A hard decision that needs deliberation is System Two work.
- **Low volume.** If you make a few calls a day, the 1–2 s and cents of an LLM cost nothing, and an LLM is more flexible.
- **Single question on a short state.** Shared-state reuse gives no gain and the latency edge is smaller.
- **Capability gap on hard semantics.** Open 4B models were clearly below Jev (Qwen3.5-4B direct logits 0.845 vs Jev 0.883 on the TypeSafe subset; 0.6B at 0.407). Small models are good enough for routing, much less so for subtle judgments ([[SemIf]]). Fine-tuning narrows but does not close the gap ([[Rizzo-Flow]] 4B 0.648 vs Jev 0.727 on typed-decisions; its 1.7B gains no accuracy).
- **Bi-encoder shortcuts on fine-grained decisions.** Encoding state and candidate separately ([[CLM]]) is fastest but lost to Jev on decision agreement (0.658 vs 0.987 on T-Rex); for entailment-like checks, keep state–claim interaction.
- **Probabilities you must trust but can't verify.** Calibration is a claim for Jev. The open reproduction did **not** reproduce RLCD; direct logits showed order flips and a high-confidence wrong answer on missing evidence. Treat open-model scores as uncalibrated until temperature-scaled on the target workload ([[Calibration]]).
- **Privacy / self-hosting constraints.** Jev is a closed hosted service ([[Che cos'e Jev Spiegazione]]), so for sensitive data you need an open recreation ([[Jevlike]], [[SemIf]], [[Rizzo-Flow]]) or a local LLM.
- **Distribution shift.** A fixed readout trained on given decision types may degrade outside them; an LLM degrades more gracefully.

## Decision rule of thumb
Use System One if **all** hold:
1. Output ∈ {bool, score, one-of-N} known at call time.
2. Decisions are frequent (hundreds+/day) or on a latency-critical path, ideally **several per shared state**.
3. A probability suffices (no rationale needed), ideally with thresholds/fallback.
4. The semantic difficulty is within reach of the model size you can run.

Otherwise, use an LLM, or the **hybrid**: System One as a fast gate/router that escalates low-confidence or complex cases to an LLM ([[Che cos'e Jev Spiegazione]] suggests the same split).

## Thesis hypotheses (GroundOne)
The thesis studies **[[GroundOne]]**: a specialist System One verifier that, for each sentence (claim) of a RAG answer, decides whether it is supported by the retrieved context ([[Groundedness Verification]], [[Hallucination Detection]]). Single forward pass with a marker after each sentence, softmax over the logits of the answer letters A/B/C, i.e. supported / contradicted / not mentioned (family (b) in [[System One Models#Taxonomy of System One implementations]]), no text generation; [[Qwen2.5]] 0.5B and 3B fine-tuned with [[LoRA]] on MLX, on a 16 GB M4 Mac. [[Rizzo-Flow]] is the external baseline; [[CLM]] is related work only.

1. **Specialisation.** A fine-tuned 0.5B/3B verifier reaches accuracy comparable to or better than a **zero-shot 7B LLM judge** on sentence-level support, at a fraction of the size. (Prior signal: zero-shot 4B readout is weak on NLI — SemIf WANLI 0.637 — and fine-tuning helped Rizzo-Flow 4B but not its 1.7B on accuracy.)
2. **Readout vs generation.** *(Prediction, superseded by the B2 result below.)* Against a same-model **single-token generation** control the readout gives ≈ **0 gain**: both are one prefill plus one position. The gain appears when (i) **K claims share one context**, because the context is prefilled once and claims branch from the [[KV Cache]] ([[Prefill and Decode]]) — gain grows with K; and (ii) against judges that **write a rationale or JSON** before the verdict, where decode dominates (largest gain). This makes the "is it just a small model + efficient serving?" open question below an explicit experiment.
3. **Calibration.** Readout probabilities can be made usable as confidence thresholds: report **ECE** before and **after temperature scaling** fitted on a held-out split ([[Calibration]]). Prior signal: SemIf WANLI ECE 0.208 → 0.069 with temperature scaling; Rizzo-Flow fine-tune ECE 0.349 → 0.112. Risk: confident errors on missing evidence (Rizzo-Flow FT 5/36), which is precisely the "unsupported" class.
4. **On-device cost.** The verifier runs within the 16 GB M4 budget with per-claim latency and memory low enough for inline use in a RAG pipeline (measured as latency per claim, per answer of K claims, and peak memory). As run, the comparison is with same-size judges on the same machine (a 7B judge was not run, D13).

### Outcomes (2026-10-10; details in [[GroundOne Results]])
- **H1 specialisation: supported in the RAG domain.** T1 three-way 0.769 (0.5B) and 0.832 (3B), against 0.37 / 0.44 untrained. On LLM-AggreFact the 3B is on par with MiniCheck (74.8 vs 74.0, not significant) and above the published zero-shot 7B (72.8). Transfer outside RAG is weak (VitaminC).
- **H2 readout vs generation: the ≈ 0 prediction was wrong for accuracy.** Latency is the same, but the restricted readout is +0.25 (0.5B) and +0.07 (3B) more accurate than the generated token on the same pass (control B2; [[Letter-Token Readout]]). The gain over judges grows with K, as predicted.
- **H3 calibration: supported in domain.** Binary ECE on T1 goes from 0.30 to 0.019 with temperature + bias. It does not transfer to VitaminC. ECE alone does not separate systems; AUROC and AURC do ([[Verbalised vs Logit Confidence]]).
- **H4 on-device cost: partly supported.** 0.33 s / 1.99 s median per answer and 5.5 J / 33 J per answer. The 3B misses the provisional < 1 s target at K 5–8, and co-resident memory with a generator is not yet measured ([[On-Device Inference]], [[Energy of LLM Inference]]).

## Open questions
- Does the independent MLflow result (30 examples) hold on larger sets and harder tasks?
- How much of the speedup is architecture (readout, shared state) vs. simply a small model + efficient serving? A fair baseline is a *same-size* LLM with constrained decoding / single-token logit readout, which gets most of the O(1) benefit without a "System One" label. **Answered for GroundOne:** the equal-output judge that reads letter logits (B0d) is as fast as a terse judge but far less accurate, and the fine-tuned model's generated token (B2) is less accurate than its restricted readout. Training gives most of the gain; one-pass multi-sentence scoring gives the speed; the restriction to the options adds accuracy and format robustness ([[GroundOne Results]], [[Constrained Decoding]]).
- Can open models reach usable calibration without RLCD data? (Partial evidence: soft-CE fine-tuning + temperature scaling, see [[Rizzo-Flow]], [[SemIf]].)

## Sources
- [[System One Models]], [[Jev]], [[Jev Input and Output Format]], [[Jev vs LLMs Cost Comparison]], [[Laya]], [[Decision-Model Benchmarks]], [[Hugging Face decision-models Tag]], [[Decision-Model Landscape (Hugging Face, 2026)]]
- [[Jevs Architecture Unmasked]], [[Can Jev replace your LLM judge]], [[Che cos'e Jev Spiegazione]], [[jev_simone_rizzo]]
- [[SemIf README]], [[SemIf RESULTS]], [[Rizzo-Flow README]], [[Rizzo-Flow training]], [[CLM README]], [[Kwok 2026 - Contrastive Language Models]]
- Project material outside the wiki: `SystemOne_repos/SemIf/docs/RESULTS.md`, `SystemOne_repos/CLM/examples/t_rex/results/`; earlier abandoned routing thesis: `Project_old/LoRA_Finetuning/training_results/v1/results.md`, `Project_old/Benchmark&Results/expected_results.md`, `Project_old/docs/PlanB/abstract_thesis_eng.md`
