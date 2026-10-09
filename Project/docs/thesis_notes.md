# Thesis notes: findings and arguments to reuse when writing

A running record of results, explanations and arguments that came up during the experiment, organised by thesis chapter.
Every number points to its source file.

**Rules:**
- Add an entry whenever a result or insight appears; never delete one, mark it superseded instead.
- English, short and factual. The thesis prose is written later from these notes.
- Raw logs and status are in `tracker.md`; this file keeps what the thesis needs.

---

## Ch. 2 / Ch. 7: what "working in RAG" means (2026-10-07)

- A RAG check and a generic (source, claim) check are formally the same task: does the document support the sentence? What differs is the **distribution**, and a fine-tuned verifier learns the distribution.
- **Who writes the claim.**
  - In RAG an LLM writes it right after reading the source. Sentences reuse many words of the document and are mostly correct (≈ 90 % supported in RAGTruth). Errors are LLM-typical: fabricated details (baseless) more often than contradictions, swapped numbers or names, intrusions of world knowledge.
  - In fact-verification datasets (VitaminC, FEVER) humans write the claims adversarially: minimal edits, numeric comparisons ("more than 23.5 million"), paraphrases that avoid the source's words.
- **Context.** In RAG a sentence sits inside a multi-sentence answer (coreference, discourse), and the document is long: several retrieved passages, or structured data (JSON) in data-to-text.
- **Error forms.** In RAGTruth "contradicted" is mostly *evident* conflicts (85 % of contradicted training sentences come from Evident Conflict spans), concentrated in data-to-text.
- **Claim scope for the thesis.** GroundOne is a verifier of *LLM-written text grounded on a source*, not a universal fact checker. Specialisation is the point of the thesis, not a weakness to hide.

## Ch. 4: data (see also `data/processed/groundone/DATACARD.md`, `experiments/eda/report/eda_report.md`)

- **Dataset.** Train 13,203 answers / 90,795 decisions; dev 1,468 / 9,996; T1 2,647 / 17,284; T2 29,320 pairs; T3 3,000 pairs. Checks: C2 96.3 % / 8.5 %, C3 98.75 %, leakage PASS.
- **Size vs earlier datasets** (for the author, not for the thesis text):
  - 2× the labelled decisions of the first dataset, all in the RAG domain;
  - about 25–30 % fewer tokens, because each document is read once per answer.
- **Why the 2,048-token cap.** It is not a limit of the model: Qwen2.5 accepts 32K tokens. It is a design choice:
  - (i) training memory on 16 GB, since activations grow with length across the whole batch, especially for the 3B;
  - (ii) coverage: 99 % of RAGTruth fits;
  - (iii) time: attention cost grows faster than linearly with length.

  Inference can go beyond the cap (server parameter), but the model never saw longer documents, so quality is not guaranteed and latency grows. Prefill ≈ 0.37 ms/token on the 0.5B and ≈ 2.2 ms/token on the 3B, so a 15K-token document takes ≈ 5–6 s on the 0.5B and ≈ 30 s on the 3B. For long sources the safe route is chunking, with the maximum (or the most relevant chunk) per sentence.

## Ch. 3: method

- **Readout design (b), the default.** One forward pass per answer. A marker " Verdict:" follows every scored sentence, and the A/B/C logits are read there. The output head is applied only at marker positions. Prompt version `groundone-v2-marked`.
  - Training uses a class-weighted cross-entropy at all markers, with each class contributing equally (supported 0.379, contradicted 7.49, not_mentioned 4.41).
  - Cost: the verdict on sentence *i* sees only sentences 1..*i*, and the untrained model has no meaning for the marker, so baseline B1 stays in format (a).
- **Calibration: definition of ECE** (author's request: include it in the calibration section).
  - Bin predictions by confidence into M = 15 equal-width bins. ECE = Σₘ (|Bₘ|/n) · |acc(Bₘ) − conf(Bₘ)|.
  - Binary variant: bins of P(supported) against the observed share of supported sentences. Top-label variant for three classes: maximum probability against correctness.
  - ECE is *not* the difference between the class distribution of the test set and that of the predictions. That is a different quantity (e.g. T1: 17 % predicted not_mentioned vs 6 % true). ECE compares, *for predictions with similar stated confidence*, the confidence with the observed frequency.
  - It depends on the binning. It is never reported alone, because a constant base-rate predictor has ECE ≈ 0; always report Brier, NLL and reliability diagrams with it. Cite Naeini 2015 and Guo 2017.

## Ch. 6: results of the validation run g1-05b-b1 (2026-10-07)

Setup: 0.5B, design (b), all training answers, 802 steps (accumulation 4, ≈ 16 answers per step), 5.4 h on the M4. Best dev checkpoint at step 600. Sources: `outputs/results/g1-05b-b1/{t1,t2,t3}/metrics.json`, `outputs/models/g1-05b-b1/train_log.jsonl`, `outputs/figures/training-g1-05b-b1/`.

**Training dynamics.**
- Loss 1.24 at step 25, and below the prior-only level ln 3 = 1.10 by step 75; 0.52–0.56 at the end.
- Dev three-way balanced accuracy (mean over tasks): 0.32 (step 0), 0.55 (150), 0.58 (300), 0.63 (450), 0.633 (600), 0.633 (750), 0.629 (802).
- The untrained model in format (b) predicts "contradicted" for 88 % of sentences.

**T1, RAGTruth test.**
- Three-way macro recall **0.769**: supported 0.825, contradicted 0.675, not_mentioned 0.806.
- Binary balanced accuracy 0.815, **AUROC 0.905** (word-overlap baseline 0.737). Lenient policy: balanced accuracy 0.805, AUROC 0.908. ECE 0.30 (uncalibrated).
- By task: Data2txt 0.812; QA 0.589 (contradicted recall 0.03 on only 31 examples, indicative); Summary 0.544 (contradicted 0.13).
- By K band: 1–4: 0.606; 5–8: 0.758; 9–13: 0.824; ≥ 14: 0.723. No collapse at high K; short answers (mostly QA and Summary) are the hardest.

**T2, LLM-AggreFact test** (11-way macro balanced accuracy).
- Overall 70.1. References: MiniCheck-RoBERTa (ours) 74.0, earlier GroundOne model 72.0, Qwen2.5-0.5B zero-shot 64.2, Qwen2.5-7B zero-shot 72.8.
- **RAG subset 74.4** (RoBERTa 74.6). **RAGTruth column 82.1** (RoBERTa 76.5; published RoBERTa 77.2).
- Lower than RoBERTa on the non-RAG columns: AggreFact-CNN 59.1 vs 67.1, XSum 62.8 vs 70.9, FactCheck-GPT 66.8 vs 74.1, Reveal 79.9 vs 88.9. This is the accepted cost of training on RAGTruth only. 1,310 items needed chunking.

**T3, VitaminC.**
- Three-way macro recall 0.442 (chance 0.33): supported 0.27, contradicted 0.11, not_mentioned 0.95. Predicted shares 11 / 6 / 82 %.
- Binary AUROC 0.722 vs word overlap 0.698.

**Dataset validation verdict.** All criteria fixed before the run pass on T1: above 0.57, QA and Summary above 0.36, AUROC above 0.74, no collapse at high K, all classes predicted. The dataset is useful.

## Ch. 6 / Ch. 7: error analysis by word overlap (2026-10-07)

**Why T3 is weak.** Base rates are not the explanation:
- the class-weighted loss removes the "88 % supported" prior, and on T3 the model does not over-predict supported (it over-predicts not_mentioned);
- AUROC, which is independent of base rates and thresholds, is itself weak (0.72 ≈ word overlap).

**T3 by word overlap** (share of content words of the claim found in the evidence):
| Overlap | Macro recall | Supported recall | Contradicted recall |
| --- | --- | --- | --- |
| ≤ 0.4 | 0.36 | **0.02** | 0.06 |
| 0.4–0.7 | 0.39 | 0.14 | 0.12 |
| > 0.7 | 0.53 | 0.64 | 0.23 |

- Contradicted recall is 0.00 on claims without digits.
- 67 % of supported claims are predicted not_mentioned, and 85 % of contradicted claims too.
- The model falls back on lexical overlap: a paraphrased support looks "not mentioned", and a small (often numeric) edit is not seen.

**T1 by word overlap:**
| Overlap | Macro recall | Contradicted recall | Not-mentioned recall |
| --- | --- | --- | --- |
| ≤ 0.4 | 0.773 | 0.79 | 0.88 |
| 0.4–0.7 | 0.770 | 0.73 | 0.80 |
| > 0.7 | 0.537 | **0.24** | **0.43** |

- **The same blind spot exists in RAG.** Hallucinations hidden in sentences that copy most of the source are missed.
- Formulation for the thesis: T3 is not "harder" in absolute terms. It consists mostly of the cases on which the model is weak (paraphrased support, minimal edits), and that weakness also exists, with less weight, in the RAG domain.

## Ch. 8: extensions and future work

**Auditing an LLM-written wiki (Karpathy-style, as in `Vault/`).**
- Wiki source pages are LLM-written summaries of a raw source, i.e. the distribution GroundOne works on, with large K.
- Obstacles:
  - no labels, so a case study measures only the precision of flagged sentences by checking them by hand;
  - raw sources are 10–20K-token papers, so they need chunking or retrieval;
  - concept pages synthesise several sources by design, so "not mentioned" is not an error there; exclude them.
- The nearest RAGTruth task is summarisation, the model's weakest (0.544).

**Grounded ingestion loop** (author's idea, 2026-10-07; assessment in the next entry). A local, smaller ingestion model writes wiki pages. GroundOne checks every sentence against the source under configurable thresholds or policies (strict / lenient). Rejected sentences are regenerated.

**Assessment of the grounded ingestion loop (2026-10-07).**
- **Why it fits.**
  - Generated pages have many sentences (high K), and verification must cost little compared with generation.
  - It runs locally.
  - The strict and lenient policies come directly from the three probabilities.
  - Verifying each generated section against the chunk it was written from avoids retrieval altogether.
- **Known risk.** The verifier's blind spot (above) is exactly the error a small generator makes when it copies a sentence and changes a number or a name. Fabrications (not mentioned) are caught well; subtle edits less so.
- **Design points.**
  - Regenerate only the rejected sentence, telling the generator why (not supported / contradicted), with a maximum number of retries; after that, drop the sentence or flag it for a human.
  - Use the strict policy for source pages and treat concept pages separately.
- **Evaluation without manual annotation.** Inject controlled errors into faithful pages (swap numbers, names or dates; add fabricated facts), then measure how many survive with and without the loop, and at what cost in time.
- Related work to verify before citing: post-hoc revision and attribution such as RARR, Chain-of-Verification and the Self-RAG critic.

## Ch. 6: calibration of the 0.5B (2026-10-07)

Source: `outputs/results/g1-05b-b1/calibration/metrics.json`; figures `outputs/figures/calibration-g1-05b-b1/` (reliability_binary, risk_coverage). Command: `groundone calibrate-b`.

**Maps fitted on dev** (NLL):
- temperature only: T = 0.74;
- temperature + bias: T = 0.92, bias (supported, contradicted, not_mentioned) = (0, −2.76, −2.35).

The adapter's `calibration.json` holds the affine map.

**Raw probabilities underestimate P(supported).** In the reliability diagram the raw curve lies well above the diagonal (dev and T1). This is the expected effect of the class-weighted loss, which trains the model as if the classes were balanced. The bias restores the true base rates.

**Results** (binary metrics are on P(supported)):
| Split | Map | Three-way macro recall | Accuracy | ECE, binary | ECE, top label | Brier (3-class) |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | raw | 0.769 | 0.819 | 0.301 | 0.104 | 0.298 |
| T1 | temperature | 0.769 | 0.819 | 0.252 | 0.046 | 0.282 |
| T1 | affine | 0.627 | 0.934 | **0.019** | 0.017 | **0.104** |
| dev | affine | 0.596 | 0.913 | 0.009 | 0.008 | 0.137 |
| T3 | raw | 0.442 | 0.442 | 0.169 | 0.223 | 0.691 |
| T3 | affine | 0.474 | 0.474 | 0.205 | 0.165 | 0.696 |

**Readings.**
- **On RAG data, calibration works and transfers from dev to test.** T1 binary ECE drops from 0.30 to 0.02, NLL from 0.55 to 0.21, and AUROC is unchanged (0.905), because a monotone map does not change the ranking.
- **The bias moves the argmax towards "supported".** Calibrated probabilities follow the natural base rate, so the argmax maximises accuracy (0.93) rather than balanced accuracy (macro 0.77 → 0.63). Two uses must be kept apart:
  - decisions with balanced error costs: use the raw argmax, or a threshold on calibrated probabilities chosen on dev;
  - probabilities used as confidence (thresholds τ, policies, selective prediction): use the calibrated ones.

  For the thesis, the primary classification metrics are on the raw (balanced) decision; calibration is evaluated with ECE / Brier / NLL / risk-coverage.
- **Calibration does not transfer to VitaminC** (binary ECE 0.17 → 0.21). The bias encodes RAGTruth's base rate (≈ 88 % supported) and VitaminC's is 33 %. Here a base-rate argument does apply, and it confirms that calibration is distribution-specific: a deployment must calibrate on data like its own.
- **Selective prediction** (binary decision, calibrated): AURC 0.015 on T1 and 0.022 on dev, against 0.284 on T3. Deferring the least confident sentences makes errors very rare on RAG data.

## Ch. 5: setup decisions of 2026-10-07

- **Test sets frozen** 2026-10-07 13:49 (`data/processed/groundone/tests_frozen.json`). A full rebuild reproduces the three hashes byte for byte, so the builder is deterministic.
- **3B run (g1-3b-b1)**: same recipe as the 0.5B, except:
  - size;
  - 6,500 random training answers (≈ 45K decisions, ≈ 5.6 M tokens);
  - micro-batches of ≈ 2 answers (token budget 2,304) with accumulation 8, so ≈ 16 answers per step as for the 0.5B;
  - warm-up 5 %;
  - dev evaluation every 80 steps on a fixed subset of 200 dev answers, because a full dev pass costs ≈ 1 h on the 3B.

  Learning rate 1e-4 as for the 0.5B: with only ≈ 400 steps, the 5e-5 of the earlier 3B config risked under-training, and keeping it equal limits confounders. The subset size follows from the measured 3B speed of ≈ 0.75 M tokens/h (3-step smoke test), against an initial estimate of 0.4 M.
- **Latency protocol** (`groundone baselines judges`):
  - 200 T1 answers, 50 per K band;
  - in-process MLX, one answer at a time;
  - 3 warm-up answers excluded;
  - System One median of 3 repetitions; judges timed once (greedy decoding is deterministic).
- **Judge outputs checked by hand.** The untrained 0.5B does not produce verdicts: it copies the answer sentences ("1: Based on the provided structured data, ..."). The ≈ 50 % (terse) and ≈ 97 % (verbose) format-failure rates in the smoke test are genuine, not parser errors. This is consistent with Phase 0b (97 % failures for the 0.5B verbose judge).
- **Subsamples of slower systems**: Rizzo-Flow on 300 T1 answers and 600 T3 pairs; untrained 3B on 600 T1 answers; judges on the 200 latency answers.
- **Marker length**: " Verdict:" is 3 tokens (" Ver", "dict", ":").

## Ch. 6: MiniCheck-RoBERTa on the frozen tests (2026-10-07)

Source: `outputs/results/minicheck-roberta/{t1,t3}/metrics.json` (full T1 and T3; T1 took 72 min on MPS).

| | GroundOne 0.5B | MiniCheck-RoBERTa |
| --- | --- | --- |
| T1 binary balanced accuracy | **0.815** | 0.762 |
| T1 AUROC | **0.905** | 0.814 |
| T1 AUROC, QA | **0.916** | 0.894 |
| T1 AUROC, Summary | 0.775 | **0.872** |
| T1 AUROC, Data2txt | **0.929** | 0.714 |
| T3 balanced accuracy / AUROC | 0.597 / 0.722 | **0.912 / 0.968** |

**Readings.**
- GroundOne's advantage on T1 comes mostly from **data-to-text**, where in-domain training and the template cues help: +0.21 AUROC. QA is close (+0.02), and on **summarisation the encoder is better** (−0.10).
- RoBERTa's AUROC by K band falls with K: 0.882 (1–4), 0.828, 0.773, 0.763 (≥ 14). GroundOne's does not: 0.857, 0.899, 0.926, 0.908. **Caveat**: the K bands are confounded with the task mix, because long answers are mostly data-to-text, where RoBERTa is weakest. Check per task × K before claiming a K effect.
- On VitaminC the encoder is near-perfect, and **verified (2026-10-07) the reason is that T3 is in-distribution for it**:
  - MiniCheck-RoBERTa is initialised from AlignScore's RoBERTa-L (Tang et al. 2024);
  - AlignScore was trained on 4.7M examples that include **VitaminC** and NLI-style FEVER (Zha et al. 2023, Table 1; wiki pages `Tang 2024 - MiniCheck`, `Zha 2023 - AlignScore`).

  This is not test leakage in the strict sense: AlignScore used VitaminC's training split, and our T3 comes from the test split, split by article. But T3 measures transfer only for GroundOne, not for this encoder. The T3 comparison must be presented this way. For HHEM, check its training data before interpreting its T3 result.

## Ch. 6: GroundOne 3B (g1-3b-b1) and the other baselines (2026-10-08)

**3B training.** 6,500 answers, 403 steps, 12.25 h on the M4 (≈ 0.48 M tokens/h, slower than the 0.75 M/h of the 3-step smoke test, which had shorter answers); peak 5.9 GB.
- Dev (200 answers) by step: 0.339 (0), 0.626 (80), 0.658 (160), 0.684 (240), **0.705 (320, best)**, 0.700 (400 and 403).
- Loss below ln 3 by step 25 (1.02); 0.41–0.49 at the end.

**3B vs 0.5B on the frozen tests** (`outputs/results/g1-3b-b1/{t1,t3}/metrics.json`):
| | 0.5B | 3B |
| --- | --- | --- |
| T1 three-way balanced accuracy | 0.769 | **0.832** |
| T1 recall S / C / NM | 0.83 / 0.67 / 0.81 | 0.88 / 0.76 / 0.86 |
| T1 binary balanced accuracy / AUROC | 0.815 / 0.905 | **0.874 / 0.940** |
| T1 QA (three-way; contradicted recall) | 0.589 (0.03) | 0.699 (**0.30**) |
| T1 Summary (three-way; contradicted recall) | 0.544 (0.13) | 0.629 (**0.30**) |
| T1 Data2txt | 0.812 | 0.873 |
| T1 K bands 1–4 / 5–8 / 9–13 / ≥ 14 | 0.61 / 0.76 / 0.82 / 0.72 | 0.68 / 0.83 / 0.86 / **0.84** |
| T3 three-way (contradicted recall) | 0.442 (0.11) | **0.527 (0.34)** |
| T3 AUROC | 0.722 | **0.817** |

**Readings.**
- **Size compensates in part**, as predicted: contradictions outside data-to-text go from almost none to ≈ 30 %, and T3 improves clearly. T1 evaluation of the 3B took 85 min, T3 15 min.
- **On T3 the gain comes from model size, not from the RAGTruth training.** The *untrained* 3B already reaches AUROC 0.821 and a three-way 0.531 on T3 (`outputs/results/untrained-3b/t3`), the same as the trained 3B (0.817 / 0.527). On T1 training matters a lot: untrained 3B 0.437 three-way / 0.726 AUROC (600 answers) vs trained 0.832 / 0.940.

**Other baselines** (`outputs/results/{minicheck-roberta,hhem,rizzo-flow-4b-q4}`, `outputs/results/untrained-*`):
| System | T1 binary bacc / AUROC | T1 three-way | T3 bacc / AUROC | T3 three-way | Note |
| --- | --- | --- | --- | --- | --- |
| HHEM-2.1-open | 0.731 / 0.821 | – | 0.692 / 0.795 | – | full tests |
| MiniCheck-RoBERTa | 0.762 / 0.814 | – | 0.912 / 0.968 | – | T3 in-distribution (AlignScore includes VitaminC) |
| Rizzo-Flow 4B Q4 | 0.769 / 0.894 | 0.603 | 0.847 / 0.909 | 0.712 | 300 T1 answers (1,971 sentences), 600 T3 pairs |
| Untrained 0.5B (format a) | 0.500 / 0.502 | 0.372 | 0.500 / 0.503 | 0.334 | never answers "supported" |
| Untrained 3B (format a) | 0.630 / 0.726 | 0.437 | 0.653 / 0.821 | 0.531 | T1 on 600 answers |

- HHEM by task (AUROC): QA 0.894, Summary 0.824, Data2txt 0.747.
- Rizzo-Flow predicts "supported" for 90 % of T1 sentences.
- **Same-subset comparisons** (identical sentence ids; `outputs/results/subset_comparisons.json`):
| Subset | System | Three-way | Binary bacc | AUROC |
| --- | --- | --- | --- | --- |
| T1, Rizzo's 300 answers (1,971 sentences) | Rizzo-Flow 4B | 0.603 | 0.769 | 0.894 |
| | GroundOne 0.5B | **0.798** | 0.826 | 0.916 |
| | GroundOne 3B | **0.840** | **0.887** | **0.950** |
| T3, Rizzo's 600 pairs | Rizzo-Flow 4B | **0.712** | **0.847** | **0.909** |
| | GroundOne 0.5B | 0.442 | 0.594 | 0.744 |
| | GroundOne 3B | 0.537 | 0.640 | 0.845 |
| T1, untrained 3B's 600 answers (3,869 sentences) | untrained 3B | 0.437 | 0.630 | 0.726 |
| | GroundOne 0.5B | 0.750 | 0.811 | 0.907 |
| | GroundOne 3B | **0.818** | **0.877** | **0.946** |

  The specialists beat the 4B generalist System One in the RAG domain: +0.20 three-way for the 0.5B, which is 8× smaller. The generalist transfers much better to VitaminC.

**Latency and generative judges** (`outputs/results/{g1-*,untrained-*,judge-*}/latency/metrics.json`; 200 T1 answers, 50 per K band). Median seconds per answer, K bands 1–4 / 5–8 / 9–13 / ≥ 14:
| System | 1–4 | 5–8 | 9–13 | ≥ 14 | Overall | Three-way (failures wrong) | Format failures |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GroundOne 0.5B (design b) | 0.20 | 0.32 | 0.37 | 0.41 | 0.33 | 0.835 | 0 % |
| System One 0.5B, design a (untrained) | 0.22 | 0.38 | 0.48 | 0.59 | 0.42 | 0.363 | 0 % |
| Terse judge 0.5B | 0.35 | 0.52 | 0.69 | 0.80 | 0.64 | 0.233 | 23 % |
| Verbose judge 0.5B | 0.79 | 1.47 | 2.09 | 2.51 | 1.81 | 0.017 | 97 % |
| System One 3B, design a (untrained) | 1.31 | 2.21 | 2.78 | 3.83 | 2.47 | 0.360 | 0 % |
| Terse judge 3B | 1.57 | 2.63 | 3.65 | 4.44 | 3.16 | 0.390 | 0.1 % |
| Verbose judge 3B | 4.65 | 8.74 | 13.78 | 15.86 | 10.23 | 0.402 | 7.6 % (248 generated tokens per answer) |

- At K ≥ 14, GroundOne 0.5B is ≈ 2× faster than the terse 0.5B judge and ≈ 6× faster than the verbose one.
- The 3B GroundOne latency run is pending (queue).

## Ch. 6: 3B calibration, latency and error analysis (2026-10-08)

**3B calibration** (`outputs/results/g1-3b-b1/calibration/metrics.json`): affine T = 1.03, biases (0, −2.19, −2.06).
| Split | Map | Three-way | Accuracy | Binary ECE | NLL | AURC |
| --- | --- | --- | --- | --- | --- | --- |
| T1 | raw | 0.832 | 0.872 | 0.183 | 0.362 | 0.064 |
| T1 | affine | 0.703 | 0.943 | **0.019** | 0.173 | 0.010 |
| dev (full) | raw | 0.784 | 0.859 | 0.171 | 0.388 | 0.066 |
| T3 | raw / affine | 0.527 / 0.540 | | 0.141 / 0.191 | | |

The raw 3B probabilities are better calibrated than the 0.5B's (T1 ECE 0.18 vs 0.30). On the full dev the 3B reaches 0.784 three-way, against 0.731 for the 0.5B.

**3B latency** (`outputs/results/g1-3b-b1`): median 1.23 / 1.93 / 2.25 / 2.57 s per answer for K bands 1–4 / 5–8 / 9–13 / ≥ 14 (overall 1.99 s), three-way 0.90 on the latency subset, 0 % failures. At K ≥ 14 that is 1.7× faster than the terse 3B judge (4.44 s), 6.2× faster than the verbose 3B judge (15.86 s) and 1.5× faster than design (a) (3.83 s).
- 0.5B at K ≥ 14: 0.41 s vs 0.80 (terse, 2.0×), 2.51 (verbose, 6.1×), 0.59 (design a, 1.4×).
- The GroundOne 0.5B is ≈ 6× faster than the GroundOne 3B (0.33 vs 1.99 s median), the size lever.

**Overlap analysis, 3B vs 0.5B** (recall by overlap bin):
| Test | Bin | 0.5B three-way (C / NM) | 3B three-way (C / NM) |
| --- | --- | --- | --- |
| T1 | ≤ 0.4 | 0.773 (0.79 / 0.88) | 0.837 (0.86 / 0.92) |
| T1 | 0.4–0.7 | 0.770 (0.73 / 0.80) | 0.833 (0.80 / 0.85) |
| T1 | > 0.7 | 0.537 (**0.24 / 0.43**) | 0.627 (**0.36 / 0.56**) |
| T3 | ≤ 0.4 | 0.36 (supported 0.02) | 0.41 (supported 0.04) |
| T3 | > 0.7 | 0.53 | 0.62 |

The blind spot on copied-but-altered sentences shrinks with size but persists. Paraphrased support on VitaminC is still almost never recognised.

## Ch. 5 / Ch. 7: fairness of the comparisons (2026-10-08)

**Latency claims are made only among systems measured under identical conditions.**
- Conditions: GroundOne, the design (a) System One and the terse/verbose judges run in-process on MLX, the same Qwen2.5 8-bit base weights, the same machine, one answer at a time, on the same 200 answers.
- GroundOne carries an unmerged LoRA adapter, which adds a little compute, so if anything the comparison is conservative.
- Differences in protocol, stated in Ch. 5: judges timed once (greedy decoding is deterministic) vs the median of 3 for System One.

**No latency comparison is claimed for Rizzo-Flow or the encoders**, and none should be made from the current numbers.
- Rizzo-Flow: its times (median 3.75 s per T1 answer, 0.76 s per T3 pair, `outputs/results/rizzo-flow-4b-q4`) were measured through its HTTP server, on another runtime (llama.cpp, GGUF, 4-bit), with a 4B model.
- Encoders: per-sentence times (MiniCheck-RoBERTa 0.17 s, HHEM 0.15 s) are in-process PyTorch MPS, with one call per (document chunk, sentence) pair.

**If wanted, a fair system-level comparison** would put every system behind the same interface on the same 200 answers:
- GroundOne behind its HTTP server, which first needs moving to design (b), vs Rizzo-Flow behind its server;
- the encoders timed per answer (K sentence calls) in-process.

Even then, runtime, quantisation and model size differ, so the result is a deployment comparison, not a mechanism comparison.

**Accuracy comparisons**: the same frozen test items and the same metrics for every system.
- Rizzo-Flow and the untrained 3B are compared on their own subsamples, with identical sentence ids (`outputs/results/subset_comparisons.json`).
- Rizzo-Flow runs 4-bit (8-bit did not fit in memory) and receives the document and numbered answer as shared state, with one three-way choice question per sentence: the closest equivalent of GroundOne's input.
- The encoders score (document, sentence) pairs without the rest of the answer, which is how they are designed.
- MiniCheck-RoBERTa has VitaminC in its training lineage.

## Ch. 1 / Ch. 2: PILLAR, full locality and independence of the solution (author, 2026-10-08)

**Principle.** One of the pillars of the thesis is that GroundOne is **entirely local and independent**:
- training, calibration, evaluation and inference all run on one consumer laptop (Apple M4, 16 GB unified memory);
- the pipeline makes no call to any external API or service;
- the network is used only to download public datasets and open model weights once.

This must be stated in the introduction and argued with evidence, not just mentioned. The early chapters need an overview of local inference. The full write-up comes later; these notes collect the outline and the evidence.

**Planned overview (Ch. 1 motivation, Ch. 2 background).**

1. **Local vs remote (API) inference**:
   - privacy and data sovereignty (documents never leave the device; GDPR, confidential corpora);
   - offline availability;
   - latency (no network round trip, but limited compute);
   - cost (per-token API pricing vs a one-off hardware cost and energy);
   - control and reproducibility (fixed model versions, no silent API updates or deprecations, no rate limits);
   - vendor independence;
   - the downsides: the capability gap of small models, memory limits, energy and battery, maintenance;
   - hybrid set-ups (local verifier, remote generator, or the reverse).
2. **Evolution of local inference**:
   - runtimes: llama.cpp and the GGUF format, MLX on Apple silicon, Ollama and LM Studio as distribution layers; mobile runtimes;
   - quantisation (8-bit, 4-bit; QLoRA for training);
   - the rise of small open models (Qwen2.5 0.5B–7B and others);
   - on-device models shipped by platform vendors.
3. **Hardware available today, compared**:
   - Apple silicon with unified memory (M-series; memory size and bandwidth);
   - consumer NVIDIA GPUs (VRAM as the limit);
   - AMD and Intel/Qualcomm laptops with unified memory or NPUs;
   - phones.

   Key comparison axes: memory capacity (which model fits), memory bandwidth (decode speed), compute (prefill speed), power. **All specifications to be taken from vendor documentation and cited; none are filled in here.**
4. **The link to System One (the core argument).**
   - Autoregressive decoding is memory-bandwidth-bound and slow on local hardware; prefill is compute-bound and fast.
   - Measured on the M4 (Phase 0): prefill ≈ 0.37 ms/token vs decode ≈ 5.9 ms/token on the 0.5B (≈ 16× per token), and 2.2 vs 31.8 ms/token on the 3B.
   - A System One avoids decoding entirely, so its advantage is largest exactly where inference is local. This turns locality from a constraint into the reason the design matters.

**Further points (all approved by the author, 2026-10-08; to-do in `tracker.md`).**
- **Co-residence**: a local RAG assistant must hold generator, verifier and retriever in the same memory. Measured peaks: GroundOne training 2.6 GB (0.5B) and 5.9 GB (3B); the 3B judge plus generator budget is in Phase 0.
- **Energy per verification** with `powermetrics`: joules per answer for GroundOne vs the generative judges on the latency answers. It needs root, so the author starts `sudo powermetrics` or grants a rule.
- **Proof of independence**: re-run a full evaluation with the network disabled (`HF_HUB_OFFLINE=1`, Wi-Fi off) and report that it completes. It is cheap and makes the claim verifiable.
- **Licences as part of independence**: Qwen2.5-0.5B is Apache-2.0, while Qwen2.5-3B is under the Qwen Research licence; datasets RAGTruth MIT, VitaminC CC BY-SA, LLM-AggreFact evaluation only.
- **Cost comparison with a remote judge**: the cost of verifying N answers with a hosted LLM judge vs locally. Prices must be taken from the providers' pages on a stated date, and are not filled in here.
- **Fully local baselines**: every baseline (encoders, Rizzo-Flow, generative judges) also ran on the same laptop, so the comparison itself is local.

**Evidence already available.**
- Every step of this project ran on the M4: dataset build, the 0.5B and 3B training (5.4 h and 12.25 h), all evaluations, all baselines, the latency protocol.
- Measured verification time per answer: 0.33 s (0.5B) and 1.99 s (3B) median; no generated tokens.

## Ch. 6: GroundOne 3B on LLM-AggreFact (T2, full test, 2026-10-09)

Source: `outputs/results/g1-3b-b1/t2/metrics.json`. 887.8 min (14.8 h, plus a 25-min pause) for 29,320 items (32,070 document chunks, 22.65 M tokens); peak 5.2 GB.

| Balanced accuracy (%) | GroundOne 3B | GroundOne 0.5B | MiniCheck-RoBERTa (ours) |
| --- | --- | --- | --- |
| **Macro average (11)** | **74.8** | 70.1 | 74.0 |
| **RAG subset (4)** | **76.9** | 74.4 | 74.6 |
| AggreFact-CNN | 59.3 | 59.1 | **67.1** |
| AggreFact-XSum | 69.1 | 62.8 | **70.9** |
| ClaimVerify | 76.0 | 74.1 | **78.3** |
| ExpertQA | **57.7** | 56.4 | 57.2 |
| FactCheck-GPT | 73.2 | 66.8 | **74.1** |
| LFQA | **86.8** | 85.0 | 86.2 |
| RAGTruth | **87.3** | 82.1 | 76.5 |
| REVEAL | **90.3** | 79.9 | 88.9 |
| TofuEval-MediaS | **71.6** | 66.9 | 69.3 |
| TofuEval-MeetB | 74.7 | 70.6 | **75.9** |
| WiCE | **76.9** | 67.9 | 69.8 |

Pooled AUROC: 0.895 (3B) and 0.866 (0.5B). Published references: Qwen2.5-7B zero-shot 72.8; MiniCheck-Flan-T5-L (0.8B) 75.0; Bespoke-MiniCheck-7B 77.4.

**Readings.**
- The 3B reaches the encoder on the macro average (+0.8) and exceeds the zero-shot 7B (+2.0), despite being trained only on RAGTruth.
- Its gain over the 0.5B is broad: +4.7 macro, with large gains on REVEAL (+10.4), WiCE (+9.0), FactCheck-GPT (+6.4) and XSum (+6.3). Size improves transfer outside the training domain, consistent with T3.
- Still below the encoder on news summarisation (AggreFact-CNN −7.8, XSum −1.8) and ClaimVerify (−2.3). The RAGTruth column (+10.8 over RoBERTa) is in-domain for GroundOne and must be read with that caveat; the fair RAG comparison is the subset average excluding it, or a note.

## Ch. 3 / demo: real outputs and the coherence of the served output (2026-10-09)

Two real runs of GroundOne 0.5B (`g1-05b-b1/best` + calibration), design (b).
- **Toy example.** Document "Acme was founded in 2005 in Turin and has 120 employees."; answer "Acme was founded in 2005. It is based in Milan. Its CEO is Maria Rossi." Result: supported 0.98; **not mentioned 0.80** for "It is based in Milan"; not mentioned 0.63 for the CEO sentence. 133 input tokens, 0 output tokens, 0.10 s.
  - The model's choice for "Milan" is defensible: the document gives where Acme was *founded*, not where it is *based* now. The illustrative JSON written earlier in chat ("contradicted") was wrong. Good example for the thesis of what "not mentioned" means.
- **Real T1 answer** (rt-14134, QA, Llama-2-13B). 4/4 verdicts equal to the gold labels: two supported at 0.99, two not mentioned. Six sentences without checkable content (greeting, list headings, closing formulas) are kept as context with no verdict. 487 input tokens, 0.19 s.
- **Issue to fix before the demo / API.** For two sentences the label (argmax of the raw, class-balanced output, D24) is "not mentioned", while the calibrated P(supported) shown next to it is 0.54 / 0.52, so the strict flag is off. Showing raw-based labels next to calibrated probabilities is incoherent for a user. The served output must use one coherent rule, chosen on dev: either
  - labels and policy flags both derived from the calibrated probabilities with thresholds tuned on dev, or
  - two clearly separated fields.

## Ch. 5 / Ch. 6: equal-output judge B0d (D25, 2026-10-09)

**Why.** The terse (B0a) and verbose (B0b) judges return less than GroundOne: a letter per sentence, no probabilities. Without probabilities a judge has no ECE, no adjustable threshold and no strict/lenient policy. The comparison with them is therefore "GroundOne with more information, faster", not at equal output. The author asked for a judge that returns exactly what GroundOne returns.

**What "same output" means.** GroundOne's JSON envelope (text, index, flags) is written by code. The model's content is one label and three probabilities per scored sentence. The judge is asked for that minimal content and does not echo the sentences, which would add tokens and make it a strawman.

**Two variants, same size, zero-shot, greedy:**
- **B0d-verbal** (`--system json`): a JSON object `{"<n>": {"label": ..., "p": [pA, pB, pC]}}`. The stated label is the decision; the probabilities feed calibration and ECE. This is what a developer with only a prompt would do. Verbalised confidence is known to be coarse and poorly calibrated.
- **B0d-logit** (`--system terse-logits`): the terse judge, with P(A), P(B), P(C) read from the logits at the generated letter and renormalised over the three letters. It gives the same content at the cost of the terse judge. It is the strongest generative opponent: what remains against GroundOne is training plus one pass instead of K short generations.

**Fairness of calibration.** Both judges get the same temperature + bias as GroundOne, fitted on 200 K-stratified dev answers. GroundOne is re-evaluated on the same 200-answer latency subset with its own dev calibration (`judges-calibrate --calibration`). Binary ECE on that subset: 0.298 → 0.034 (0.5B) and 0.181 → 0.030 (3B); AURC 0.009 and 0.005.

**Prompt choice, on dev, on format only.** 12 dev answers (110 sentences).
- With a numeric example in the prompt, the 3B copied the example's probabilities `[0.8, 0.1, 0.1]` in 9/110 sentences and the 0.5B returned only the example.
- With placeholders, the 3B gave 100 % valid entries with more varied probabilities.
- The 0.5B failed with both prompts (1 % and 0 % valid). It cannot produce the structured output, consistent with the verbose judge's 97 % failures.
- Placeholders were kept.
- First observation: the 3B states mostly extreme probabilities (`[1, 0, 0]`, `[0, 1, 0]`), the expected pattern of verbalised confidence.

**Parsing (in the judge's favour).** One regex per entry, so a truncated object keeps its complete entries. A missing label is taken as the argmax of p. Probabilities are renormalised. Format failure = no valid probabilities. Grammar-constrained decoding was not used, so that the protocol stays the same as B0a/B0b. This is a limitation for the 0.5B failure rates.

**Smoke test, B0d-logit 0.5B** (4 answers): where the 0.5B writes letters, the probabilities are soft (e.g. 0.44 / 0.11 / 0.45), unlike the one-hot terse verdicts. On 3 of the 4 answers it echoed the sentences instead of letters (format failures, as for B0a).

**Results:** pending (queue `jobs/queue_day5.txt`); judge table of the results matrix in `tracker.md`.

**For the thesis (author's request):** show one real output example per system on the same answer: GroundOne JSON, terse, verbose and equal-output judge texts, encoders, Rizzo-Flow. The judge predictions now store the generated text (`text` column of `predictions.parquet`, first sentence row of each answer).


**B0d interim observations (2026-10-09 14:15; latency subset, 200 T1 answers):**
- **B0d-logit 3B = B0a terse 3B in decisions** (macro 0.390 for both, same per-class recall), as expected: same prompt, same greedy generation. Latency at K ≥ 14: 4.38 s vs 4.44 s, so reading the three logits per step costs nothing measurable. The probabilities come for free on top of the terse judge.
- **B0d-verbal 0.5B is degenerate.** The placeholder prompt gives 69 % entries that parse, but almost all lack a label and repeat uninformative vectors: after renormalisation [1/3, 1/3, 1/3] (323 sentences), [0.4, 0.4, 0.2] (232) and [0.5, 0.5, 0] (172). With the lenient "missing label = argmax p" rule, a tie resolves to A (supported). This inflates its supported recall (0.57) without any real judgement. Macro 0.234, the same as the terse 0.5B. To report: tie rate, and macro with ties counted as failures (computable from `predictions.parquet`, no rerun).
