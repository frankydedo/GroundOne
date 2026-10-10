---
type: concept
tags: [thesis, project, results, synthesis]
updated: 2026-10-10
---
# GroundOne Results (synthesis, 2026-10-10)

Results of [[GroundOne]] on the frozen tests. Source of truth: `Project/docs/checkpoint_2026-10-10.md` and `Project/docs/thesis_notes.md`, which give every number with its file. Data: [[Datasets for GroundOne]].

## Accuracy
| System | T1 [[RAGTruth]] three-way | T1 AUROC | T2 [[LLM-AggreFact]] macro / RAG subset | T3 [[VitaminC]] three-way / AUROC |
| --- | --- | --- | --- | --- |
| GroundOne 0.5B (run 1 / run 2) | 0.769 / 0.767 | 0.905 / 0.907 | 70.1 / 74.4 · 71.5 / 74.3 | 0.442 / 0.434 · 0.722 / 0.747 |
| GroundOne 3B | **0.832** | **0.940** | **74.8 / 76.9** | 0.527 / 0.817 |
| Untrained 0.5B / 3B | 0.372 / 0.437 | 0.502 / 0.726 | – | 0.334 / 0.531 · 0.503 / 0.821 |
| [[MiniCheck]]-RoBERTa | – | 0.814 | 74.0 / 74.6 | AUROC **0.968** (VitaminC is in its training lineage) |
| [[HHEM]]-2.1-open | – | 0.821 | – | AUROC 0.795 |
| [[Rizzo-Flow]] 4B Q4 (subsamples) | 0.603 (GroundOne 0.798 / 0.840 on the same answers) | 0.894 | 61.5 (1,093 items) | **0.712** / 0.909 (GroundOne 0.537 / 0.845 on the same 600 pairs) |
| Word overlap (no model) | – | 0.737 | – | AUROC 0.698 |

**Significance** ([[Statistical Significance and Bootstrap]], cluster bootstrap by source document, B = 2000):
- **T1.** GroundOne beats every baseline. The 3B beats the 0.5B by +0.063 [+0.052, +0.076].
- **T2.** The 3B is **on par** with MiniCheck (+0.8 [−0.5, +2.1]) and above it on the RAG subset (+2.4 [+1.4, +3.3]). The 0.5B is below MiniCheck on the macro (−3.9).
- **Seed variance.** The two 0.5B runs differ "significantly" on T2 macro and T3 AUROC under data resampling. The intervals therefore ignore seed variance, and cross-system differences smaller than about 1.5 T2 points or 0.025 T3 AUROC are not claimed.

## Speed, output parity, energy (200 T1 answers, 50 per K band)
| Size | GroundOne | Terse judge | Verbose judge | Equal-output judge (logits / verbalised) |
| --- | --- | --- | --- | --- |
| 0.5B, s/answer at K ≥ 14 | **0.41** | 0.80 (1.95× [1.82, 2.14]) | 2.51 (6.16× [5.72, 6.67]) | 0.81 / 2.47 |
| 0.5B, three-way | **0.835** | 0.233 (23 % format failures) | 0.017 (97 %) | 0.234 / 0.234 (0.081 counting ties) |
| 3B, s/answer at K ≥ 14 | **2.57** | 4.44 (1.73×) | 15.86 (6.18×) | 4.38 / 17.00 |
| 3B, three-way | **0.900** | 0.390 | 0.402 | 0.390 / 0.410 |
| Energy, J per answer (0.5B / 3B) | **5.5 / 33** | 8.9 / 43 | 22.5 / 112 | – |

- **The speed-up grows with K.** The claim is made only among in-process MLX systems; the encoders and Rizzo-Flow use other runtimes.
- **Equal-output judges (B0d).** Their AUROC is 0.47–0.68, against 0.94–0.97 for GroundOne. Calibrated AURC is 0.048–0.063, against 0.009 / 0.005. Verbalised probabilities are 93 % one-hot for the 3B ([[Verbalised vs Logit Confidence]]). After calibration every system reaches ECE 0.03–0.05, so ECE alone is misleading ([[Expected Calibration Error]]).
- **Energy is smaller than speed.** GroundOne draws 16 W, against 11–14 W for decoding: a long prefill is compute-bound, decoding is memory-bound ([[Prefill and Decode]], [[Energy of LLM Inference]]). The energy advantage (1.3–1.6× over terse) is therefore smaller than the speed advantage.

## Readout vs generation (control B2, full T1)
With the same weights and pass, the verdict is either the restricted A/B/C readout or the token greedy generation would emit:
- 0.5B: 0.769 vs 0.521 (24.7 % format failures);
- 3B: 0.832 vs 0.761.

The model would write the **spaced** letter (" A"), and the readout letters hold only about 4–5 % of the probability mass. GroundOne is a restricted three-way classifier on top of the LM, not a faster generator ([[Letter-Token Readout]]).

## Calibration and serving
- **Calibration.** Binary ECE on T1 drops from 0.30 to 0.019 (0.5B) and from 0.18 to 0.019 (3B). It does not transfer to VitaminC ([[Calibration]]).
- **Served rule.** The served label is "supported" iff calibrated P(supported) ≥ τ, with τ = 0.935 / 0.895 / 0.925 fitted on dev. This rule matches the evaluated balanced decision within 0.01 on T1 ([[Selective Prediction]]).

## Robustness and errors
- **Seeds.** Seeds 1234 and 777 converge to the same aggregates. Seed 4321 collapsed to a constant predictor (dev 0.333 at step 300) and was stopped. The training loop has no gradient clipping ([[Fine-tuning Instability and Seeds]]).
- **Blind spot.** Sentences that copy the source but alter a detail. In the overlap > 0.7 bin, contradicted recall is 0.24 (0.5B) and 0.36 (3B).
- **Weak transfer outside RAG.** On VitaminC the trained 3B equals the untrained 3B (0.527 vs 0.531).

## What the thesis can claim
1. Specialisation works in the RAG domain; the gain comes from training.
2. The System One advantage is real: about 2× / 6× faster at K ≥ 14, always valid output, much better probabilities at equal output, and less energy, though by a smaller factor than the speed-up.
3. The restricted readout adds accuracy by itself (B2).
4. Calibration is cheap and effective in domain. Judge it with AUROC and AURC, not with ECE alone.
5. Limits: weak transfer outside RAG; on T2 the 3B is on par with MiniCheck, not above it; the copy-and-alter blind spot; the recipe can collapse on some seeds.
