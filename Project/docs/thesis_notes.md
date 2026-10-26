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
- ~~The 3B GroundOne latency run is pending (queue).~~ Done: 2.57 s at K ≥ 14 (see below).

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

**Results:** ~~pending~~ done 2026-10-09 15:12, see "B0d results" below.

**For the thesis (author's request):** show one real output example per system on the same answer: GroundOne JSON, terse, verbose and equal-output judge texts, encoders, Rizzo-Flow. The judge predictions now store the generated text (`text` column of `predictions.parquet`, first sentence row of each answer).


**B0d interim observations (2026-10-09 14:15; latency subset, 200 T1 answers):**
- **B0d-logit 3B = B0a terse 3B in decisions** (macro 0.390 for both, same per-class recall), as expected: same prompt, same greedy generation. Latency at K ≥ 14: 4.38 s vs 4.44 s, so reading the three logits per step costs nothing measurable. The probabilities come for free on top of the terse judge.
- **B0d-verbal 0.5B is degenerate.** The placeholder prompt gives 69 % entries that parse, but almost all lack a label and repeat uninformative vectors: after renormalisation [1/3, 1/3, 1/3] (323 sentences), [0.4, 0.4, 0.2] (232) and [0.5, 0.5, 0] (172). With the lenient "missing label = argmax p" rule, a tie resolves to A (supported). This inflates its supported recall (0.57) without any real judgement. Macro 0.234, the same as the terse 0.5B. To report: tie rate, and macro with ties counted as failures (computable from `predictions.parquet`, no rerun).

**B0d results (2026-10-09 15:12; 200 T1 answers; judges calibrated on 200 dev answers; files `results/judge-{json,tlogit}-{05b,3b}/latency/{metrics,calibration}.json`, GroundOne `results/g1-*-b1/latency/calibration.json`):**

| System | Three-way (failures wrong) | Format failures | s/answer K ≥ 14 | Generated tokens | Binary AUROC | ECE raw → cal. | AURC cal. |
| --- | --- | --- | --- | --- | --- | --- | --- |
| GroundOne 0.5B | 0.835 | 0 % | 0.41 | 0 | 0.940 | 0.298 → 0.034 | 0.009 |
| B0d-logit 0.5B | 0.234 | 23.5 % | 0.81 | 58 | 0.483 | 0.350 → 0.039 | 0.063 |
| B0d-verbal 0.5B | 0.234 (0.081 with tied unlabeled entries as failures) | 30.9 % | 2.47 | 213 | 0.470 | 0.526 → 0.051 | 0.061 |
| GroundOne 3B | 0.900 | 0 % | 2.57 | 0 | 0.969 | 0.181 → 0.030 | 0.005 |
| B0d-logit 3B | 0.390 | 0.1 % | 4.38 | 37 | 0.681 | 0.181 → 0.041 | 0.048 |
| B0d-verbal 3B | 0.410 | 0 % | 17.00 | 248 | 0.576 | 0.367 → 0.044 | 0.062 |

AUROC is computed on the valid sentences, before calibration (the affine map barely changes the ranking). ECE and AURC are on valid sentences only, so for the 0.5B judges they cover 70–77 % of the sentences.

Findings:
1. **At equal output GroundOne still wins on every axis.** Accuracy: 0.835 / 0.900 vs at most 0.41. Speed: 2× (logit) and 6–7× (verbal) faster. Quality of the probabilities: AURC 5–12× lower.
2. **ECE alone is misleading.** After the same calibration every system reaches ECE 0.03–0.05, because a calibration map can match the average confidence to the base rate even when the probabilities do not separate classes (judge AUROC 0.47–0.68, near chance for the 0.5B). The discriminating calibration metrics are AUROC and risk–coverage (AURC). The thesis must report them next to ECE.
3. **Verbalised probabilities carry almost no information.** The 3B writes a one-hot vector for 93 % of the sentences (1,629 of 1,747; 16 distinct vectors in total). The 0.5B writes uninformative vectors: 1,110 entries without a label, 786 of them tied (e.g. [0.5, 0.5, 0.5]). Counting the tied unlabeled ones as failures, its macro falls from 0.234 to 0.081: the lenient parsing rule was inflating it.
4. **Logit probabilities are better than verbalised ones** (3B AUROC 0.681 vs 0.576; AURC 0.048 vs 0.062) at a quarter of the latency. They are the strongest generative opponent, and still far from GroundOne. The gap is due to training, not to the readout: B0d-logit makes the same decisions as the terse judge (macro 0.390).
5. **Writing the JSON costs a lot and buys nothing.** The 3B verbal judge is as slow as the verbose judge (17.0 s vs 15.9 s at K ≥ 14, 248 tokens), with about the same accuracy as the terse one (0.410 vs 0.390).
6. **Honest caveat.** Judges are zero-shot and GroundOne is fine-tuned, so B0d measures "what a same-size generative judge gives at equal output", not the readout alone. The readout-alone comparison is B1 vs B0d-logit (both untrained) and design (b) vs design (a) for latency.

## Ch. 5 / Ch. 6: bootstrap intervals and paired tests (2026-10-09)

**Protocol** (`groundone bootstrap`, `GroundOne/src/groundone/eval/bootstrap.py`; results in `results/bootstrap/{metrics.json, summary.md}`; figure `figures/bootstrap/paired_differences.png`).
- No model is run; everything comes from the saved predictions, and the point estimates reproduce `metrics.json`.
- B = 2000 resamples, 95 % percentile intervals.
- Cluster bootstrap by leakage group: RAGTruth source document for T1 (447 groups) and the latency subset; document for T2 (8,329 groups, resampled within each dataset because the macro averages datasets); Wikipedia page for T3 (1,257 groups).
- Paired differences use the same resamples, on the rows both systems scored. Two-sided bootstrap p.

**Significant (p < 0.0005 unless stated):**
- T1: 3B − 0.5B +0.063 three-way [+0.052, +0.076], +0.035 AUROC; at K ≥ 14 +0.116 [+0.050, +0.180] (93 groups).
- T1 AUROC: GroundOne over the encoders +0.08 to +0.13; over word overlap +0.17 / +0.20. Balanced accuracy: +0.05 to +0.14.
- T1 three-way on Rizzo-Flow's 300 answers: 0.5B +0.195 [+0.136, +0.249], 3B +0.237. AUROC 3B +0.056.
- T2: 3B − 0.5B +0.047 macro. 3B over RoBERTa on the RAG subset +0.024 [+0.014, +0.033]. Over Rizzo-Flow on its 1,100 items: 0.5B +0.068 (p = 0.024), 3B +0.123.
- T3: 3B − 0.5B +0.085 three-way, +0.095 AUROC. Rizzo-Flow over the 3B: +0.175 three-way, +0.064 AUROC. RoBERTa over the 3B: +0.151 AUROC.
- Latency subset: GroundOne over every judge by +0.49 to +0.82 three-way. Speed-up at K ≥ 14 (median ratio, paired answers):
  - 0.5B: terse 1.95× [1.82, 2.14], verbose 6.16× [5.72, 6.67], B0d-logit 1.98×, B0d-verbal 6.05×;
  - 3B: terse 1.73× [1.65, 1.82], verbose 6.18× [5.88, 6.65], B0d-logit 1.71×, B0d-verbal 6.62×.

**Not significant (claims to temper):**
- **T2 macro, 3B vs MiniCheck-RoBERTa: +0.008 [−0.005, +0.021], p = 0.24.** The claim "above MiniCheck-RoBERTa" becomes "on par". Corrected in Ch. 6, `abstract.md` and plan §2. The comparison with the zero-shot 7B (72.8) uses a published number, so no interval can be computed.
- T2 RAG subset, 0.5B vs RoBERTa: −0.002, p = 0.74 (on par). T2 macro, 0.5B vs RoBERTa: −0.039, significantly worse.
- T1 AUROC, 0.5B vs Rizzo-Flow on its subsample: +0.023 [−0.007, +0.052], p = 0.15. The three-way difference is significant.

## Ch. 3 / Ch. 5: readout vs single-token generation (B2 check, 2026-10-09)

**Question.** Does greedy single-token generation at each marker (same fine-tuned weights) give the same verdict as the 3-letter readout? The forward pass is the same, so this asks whether the decision rule matters.

**Check.** 200 K-stratified dev answers, 1,740 markers. Script in the session scratchpad; to be turned into a proper B2 run if approved.

| | 0.5B | 3B |
| --- | --- | --- |
| Full-vocabulary argmax = the unspaced letter that the readout reads ("A") | 0.2 % | 0 % |
| Full-vocabulary argmax = a spaced letter (" A", " B", " C") | 75 % | 99 % |
| Spaced letter mapped to a verdict agrees with the readout | 75 % | 92 % |
| Mean probability mass on the unspaced letters | 4.8 % | 4.1 % |
| Mean probability mass on the spaced letters | 11 % | 69 % |

The 0.5B's other argmax tokens: " " (362), "1" (23).

**Interpretation.**
- The readout tokens (unspaced A/B/C) are not the tokens the model would write after " Verdict:". The natural continuation is the spaced letter.
- The loss is a cross-entropy restricted to the three readout letters. It is invariant to their absolute mass, so training shapes their relative logits (a 3-way classifier on top of the LM) and leaves them with about 4–5 % of the mass.
- **Consequences.**
  - The readout is not equivalent to generation, and "B2 = same computation" was true only for the forward pass.
  - Generation with the fine-tuned model would differ from the readout on 8 % (3B) to 25 % (0.5B) of the verdicts, including format failures for the 0.5B.
  - Results are valid, because training and inference use the same tokens (`prompts.py`, `readout.py`).
  - Design (a) and the untrained B1 are not affected: their prompt ends at the start of the assistant turn, where the unspaced letter is the natural first token.
- **Possible improvement, not run:** read and train the spaced letters in design (b). It would align readout and generation. The effect on accuracy is unknown, since the restricted loss does not depend on absolute mass.
- **For the thesis:** state in Ch. 3 that the readout is a restricted classifier over three token logits, not a decoding step.


**Framing (discussion with the author, 2026-10-09).** The B2 check is not an anomaly. It is what defines a System One.
- A System One never decodes: it asks a closed question, runs one pass and takes the best of the admissible options' scores. What the model would write if left free is irrelevant by design.
- In a zero-shot System One (SemIf, Rizzo-Flow, B1), the readout works because the model already tends to answer with the option letter, so readout and generation roughly agree. That is why they were earlier treated as nearly equivalent ("single-token control").
- After fine-tuning with a loss restricted to the options, the two decouple: GroundOne becomes a classifier that uses the LM, not a faster generator.
- For Ch. 3: the advantage does not come from "generating one token instead of many" but from not generating at all. The returned probabilities are conditional on the answer being A, B or C (the rest of the vocabulary holds about 95 % of the mass at the markers). They are made reliable by the dev calibration.
- B2 becomes optional: it would only quantify the value of the restricted readout over a generative decision on the same pass.

## Ch. 5 / Ch. 7: second seed of the 0.5B collapses (2026-10-09)

Run `g1-05b-s2`: same config as `g1-05b-b1`, seed 4321 (LoRA initialisation and batch order). Log: `outputs/models/g1-05b-s2/train_log.jsonl`.

| Step | Train loss seed 1 / seed 2 | Dev macro recall seed 1 / seed 2 | Seed 2 predicted shares (sup / con / nm) |
| --- | --- | --- | --- |
| 100 | 0.93 / 0.83 | | |
| 150 | 0.81 / 1.12 | 0.630 / 0.369 | 0.22 / 0.00 / 0.78 |
| 300 | | 0.688 / 0.333 | 1.00 / 0.00 / 0.00 |
| 450 | 0.77 (step 225) / 1.07 | 0.731 / 0.444 | 0.75 / 0.24 / 0.00 |

- After step 100 the seed-2 loss rose to about 1.03–1.07 and stayed there. That is near the class-weighted loss of a model with no information (≈ ln 3 = 1.10). By step 300 it predicts "supported" for every sentence.
- The run collapsed to a constant predictor. Seed 1 kept improving (0.731 at step 450).
- The training loop has no gradient clipping: `training/train.py` contains no clipping or non-finite check. With lr 1e-4 and class weight 7.5 on "contradicted", one unlucky update can push the LoRA weights into a region the optimiser does not leave.
- **For the thesis:** the recipe is not robust to the seed. This must be reported, not hidden by re-running until a seed works. How often it collapses needs at least a third seed. A fix (gradient clipping, lower lr, warm-up) is a declared change, to be checked on new seeds.
- **Stopped at step ≈ 470 of 801 (the seed-2 run had 801 steps; seed 1 had 802, seed 3 803: batch counts differ slightly with the seed) (21:54, author's decision), log kept; training curve in `figures/training-g1-05b-s2/`.** At step 450 it had moved off the constant predictor (0.444, still never predicting "not mentioned"), but the loss was still ≈ 1.07, far from seed 1. The decision was taken on the step-300 evaluation. Whether it would have recovered by the end of the epoch is unknown, and this must be stated.
- Replaced by a third seed with the identical config (`g1-05b-s3`, seed 777, `jobs/queue_night6.txt`).
- **Reporting decision (author, 2026-10-09 22:00).**
  - In the thesis the completed third-seed run (`g1-05b-s3`) is presented as the second run of the 0.5B. Tables show completed runs only.
  - The stopped run (`g1-05b-s2`) is disclosed in one sentence (footnote or limitations), not hidden. Draft: *"A further run was stopped at 60 % of the epoch after its dev accuracy collapsed to the constant-predictor level (0.33 at step 300, 0.44 at step 450); it is excluded from the tables because it is incomplete, and it indicates that the recipe, which has no gradient clipping, is not fully robust to initialisation."*
  - Logs, notes and figures of the stopped run stay in the repository.


## Ch. 6: run-to-run variance of the 0.5B (2026-10-10, two completed runs)

Seed 1234 (`g1-05b-b1`) vs seed 777 (`g1-05b-s3`, presented as the second run, D26). Same config. `results/g1-05b-{b1,s3}/{t1,t3,calibration}/metrics.json`.

| Metric | Run 1 | Run 2 | Difference |
| --- | --- | --- | --- |
| Dev macro (best checkpoint) | 0.735 | 0.736 | +0.001 |
| T1 three-way | 0.769 | 0.767 | −0.002 |
| T1 AUROC | 0.905 | 0.907 | +0.002 |
| T1 recall supported / contradicted / not mentioned | 0.825 / 0.675 / 0.806 | 0.868 / 0.663 / 0.772 | |
| T1 three-way at K ≥ 14 | 0.723 | 0.746 | +0.023 |
| T3 three-way | 0.442 | 0.434 | −0.008 |
| T3 AUROC | 0.722 | 0.747 | +0.025 |
| T1 binary ECE raw → calibrated | 0.301 → 0.019 | 0.229 → 0.020 | |
| T1 binary balanced accuracy at 0.5 | 0.815 | 0.832 | +0.017 |
| T2 macro / RAG subset | 70.1 / 74.4 | 71.5 / 74.3 | +1.4 / −0.1 |
| T2 per dataset, largest differences | | | WiCE +10.1, XSum +5.1, Reveal +2.7, ClaimVerify −2.7, MeetB −2.5, CNN −1.9 |

**Reading.**
- Aggregate metrics are reproducible: T1 three-way and AUROC differ by about 0.002, well inside the bootstrap intervals (±0.02).
- The run-to-run variation sits in how errors are distributed across classes (supported vs not-mentioned recall ±0.04) and in the smaller slices (K ≥ 14, T3 AUROC, ±0.025).
- Per-class and per-band claims should be stated with that margin.
- Together with the stopped run (D26): when training converges, it converges to the same place. The risk is an early collapse, not a different optimum.

## Ch. 5 / Ch. 6: control B2 on full T1 (2026-10-10)

`groundone test --decision generate`, `results/b2-{05b,3b}/t1/metrics.json`. Same weights and the same single pass as GroundOne. The verdict is the full-vocabulary argmax at each marker, i.e. what greedy single-token generation would emit there. "A"/"B"/"C" with or without a leading space map to the classes; anything else is a format failure (counted as wrong).

| | 0.5B readout | 0.5B B2 | 3B readout | 3B B2 |
| --- | --- | --- | --- | --- |
| T1 three-way (17,284 sentences) | 0.769 | 0.521 | 0.832 | 0.761 |
| Format failures | 0 % | 24.7 % | 0 % | 1.2 % |
| Agreement with the readout | | 74.4 % | | 92.3 % |
| K ≥ 14 | 0.723 | 0.377 | 0.839 | 0.773 |

What B2 emits:
- 0.5B: " A" 11,407; " " 3,739; " C" 1,048; " B" 487; "1" 190; " The" 154.
- 3B: " A" 15,125; " C" 1,134; " B" 826; " No" 99; " We" 65.

B2 is biased towards "supported" (" A") compared with the readout.

**Reading.**
- With identical weights, latency and pass, deciding by the restricted 3-letter readout instead of the generated token is worth +0.25 (0.5B) and +0.07 (3B) three-way. The gap is largest on long answers for the 0.5B.
- The smaller the model, the more the System One readout matters: the 0.5B often does not even emit a letter.
- This quantifies H2a: the readout is not equivalent to single-token generation, and the restriction to the admissible options is itself a source of accuracy and of format robustness.

## Ch. 5 / Ch. 6 / locality pillar: energy per verification (2026-10-10)

`groundone baselines judges --energy`, `results/energy-*/energy/metrics.json`.
- **Protocol.** 100 latency answers (25 per K band), one run per answer. powermetrics Combined Power (CPU + GPU + ANE) at 200 ms, minus idle power measured for 60 s with the model loaded. Idle was about 0.2 W, so net ≈ gross. Measured overnight, Mac otherwise idle. Scope: SoC compute only, no DRAM, display or SSD.

| System | Three-way | Median s/answer | Net J/answer | Net J/decision | Net power | J/answer at K ≥ 14 (est.) |
| --- | --- | --- | --- | --- | --- | --- |
| GroundOne 0.5B | 0.823 | 0.34 | **5.5** | 0.63 | 16.2 W | 6.6 |
| Terse judge 0.5B | 0.231 | 0.65 | 8.9 | 1.01 | 13.5 W | 10.5 |
| Verbose judge 0.5B | 0.009 | 1.74 | 22.5 | 2.56 | 11.6 W | 29.6 |
| GroundOne 3B | 0.894 | 2.07 | **33.1** | 3.77 | 16.2 W | 40.5 |
| Terse judge 3B | 0.355 | 3.13 | 43.3 | 4.92 | 14.2 W | 61.3 |
| Verbose judge 3B | 0.381 | 10.01 | 111.7 | 12.71 | 10.9 W | 166.4 |

**Reading.**
- GroundOne uses the least energy per verification at both sizes. Against the terse judge: 1.6× less (0.5B) and 1.3× less (3B), or 1.5× at K ≥ 14. Against the verbose judge: 4.1× and 3.4× less (4.5× and 4.1× at K ≥ 14).
- **The energy advantage is smaller than the latency advantage.** GroundOne draws more power (16.2 W against 11–14 W) because a single long prefill is compute-bound and keeps the GPU busy. Autoregressive decoding is memory-bound and draws less power, but for much longer.
- The thesis must not equate "N× faster" with "N× less energy". The honest figures are the ones above.
- In absolute terms, 5.5 J is about 0.0015 Wh per verified answer for the 0.5B, and 33 J (≈ 0.009 Wh) for the 3B.
- **T2 (added 2026-10-10 08:37).** The macro differs by 1.4 points and the RAG subset by 0.1. Individual non-RAG datasets move by up to 10 points (WiCE, 358 items). So single-dataset T2 differences between systems smaller than about 5 points should not be interpreted, even when the macro is stable.


## Ch. 5 / Ch. 6: latency of the non-judge baselines (2026-10-10)

Median seconds per answer at K ≥ 14, measured but under different conditions. Sources: `results/{untrained-*,g1-*}/latency/metrics.json`; `results/{minicheck-roberta,hhem}/t1/predictions.parquet` (`seconds` per sentence, summed per answer on the 200 latency answers); `results/rizzo-flow-4b-q4/t1/predictions.parquet` (`answer_seconds`).

| System | K ≥ 14 | Conditions |
| --- | --- | --- |
| GroundOne 0.5B / 3B | 0.41 / 2.57 | MLX in-process, one pass per answer |
| Untrained, design (a) 0.5B / 3B | 0.59 / 3.83 | Same runtime and subset; fair: design (b) is 1.4–1.5× faster than (a) |
| MiniCheck-RoBERTa / HHEM | 2.59 / 2.52 | PyTorch MPS, sentence by sentence without batching (per sentence p50 0.17 / 0.15 s); pessimistic for the encoders |
| Rizzo-Flow 4B Q4 | 6.88 | HTTP to llama.cpp, Q4, 4B, its 300-answer subsample (by band: 2.44 / 3.98 / 5.31 / 6.88) |

- No latency claim against the encoders or Rizzo-Flow.
- The encoders (355M and ≈ 250M parameters) would probably be faster than GroundOne 0.5B if batched. Against them GroundOne's case is accuracy, not speed.
- Fair options: a batched encoder run on the 200 latency answers (cheap), and HTTP vs HTTP against Rizzo-Flow (now possible: the API serves design b since D27).

## Ch. 3 / demo: the served output (D27, 2026-10-10)

`/v1/verify` follows the adapter's design. With design (b):
- **Segmentation and pass.** The answer is segmented with the training rule (`data/segment.py`); sentences without checkable content get `scored: false` and no verdict. All verdicts come from one pass.
- **One coherent rule.** Labels, strict/lenient flags and the probabilities shown follow one rule: calibrated probabilities, "supported" iff P(supported) ≥ τ, otherwise the more probable of contradicted / not mentioned.
- **The threshold τ.** It is fitted on dev by `calibrate-b`, maximising the three-way macro recall, and stored in `calibration.json`. A request may override it, which turns the choice of operating point into a user policy without retraining. Without τ, the label is the raw class-balanced argmax (D24), and the response says so in `decision_rule`.
- **Why this rule.** It removes the incoherence seen on 2026-10-09 (labels "not mentioned" next to calibrated P(supported) = 0.54). It approximates the evaluated balanced decision rather than the calibrated argmax, which collapses towards "supported" (three-way 0.77 → 0.63).
- **Still to do.** ~~Re-run `calibrate-b` to fit τ~~ done 2026-10-10 13:12, see "Served threshold τ" below.
- **Real check** (0.5B, Acme example): 0.10 s, 139 input tokens, 0 output tokens. "Sure!" is unscored; the "Milan" and "CEO" sentences are labelled not mentioned (P = 0.80 / 0.64).


**Served threshold τ, fitted on dev (2026-10-10 13:12; `results/g1-*/calibration/metrics.json` → `served_rule`).**

| Run | τ | Three-way, served rule (dev / T1 / T3) | Three-way, raw decision (dev / T1 / T3) |
| --- | --- | --- | --- |
| 0.5B run 1 | 0.935 | 0.729 / 0.758 / 0.400 | 0.731 / 0.769 / 0.442 |
| 0.5B run 2 | 0.895 | 0.742 / 0.769 / 0.413 | 0.736 / 0.767 / 0.434 |
| 3B | 0.925 | 0.787 / 0.830 / 0.510 | 0.784 / 0.832 / 0.527 |

- τ is high (0.90–0.94) because the calibrated probabilities reflect the base rate (91 % of RAGTruth sentences are supported): a sentence is served as "supported" only when the model is very confident.
- In domain the served rule matches the evaluated raw decision within about 0.01 on T1, so the API delivers what the thesis measures, now with coherent probabilities.
- On T3 it is 0.02–0.04 lower, consistent with calibration not transferring to VitaminC.
- The temperature and bias re-fitted identically (same ECE), so earlier calibration results are unchanged.
- **API check:** `decision_rule` now reports the calibrated threshold rule with τ = 0.935 (0.5B run 1). On the Acme example, "founded in 2005" is supported (P = 0.988 ≥ τ) and "Milan" and "CEO" are not mentioned.

## Audit of 2026-10-10 (docs, thesis, code)

Findings that matter for the thesis (fixes in docs and code are in git):
- **Rizzo-Flow on T2:** 61.5 macro / 58.2 RAG subset on the 1,093 items it scored (7 of 1,100 were over its context and skipped). The bootstrap had counted the skipped items as "unsupported" (60.9); it now drops them, as Rizzo-Flow's own metrics do. GroundOne − Rizzo-Flow on those items: 0.5B +0.062 [+0.001, +0.122] (p = 0.047), 3B +0.120 [+0.074, +0.165].
- **Ch. 6 T3 comparison with Rizzo-Flow** must use GroundOne on the same 600 pairs: 0.442 / 0.537 three-way, 0.744 / 0.845 AUROC (not the full-T3 0.442 / 0.527, 0.722 / 0.817).
- **Speed-ups** to quote with intervals: 1.95× [1.82, 2.14] and 6.16× [5.72, 6.67] (0.5B); 1.73× [1.65, 1.82] and 6.18× [5.88, 6.65] (3B). "Fastest system" only among the in-process MLX systems.
- **Run 1 vs run 2 (bootstrap, same resamples):**
  - T1 three-way +0.001 [−0.008, +0.011]; AUROC −0.002 (both n.s.); K ≥ 14 −0.023 [−0.069, +0.016] (n.s.).
  - T2 macro −0.013 [−0.024, −0.003] and T3 AUROC −0.025 [−0.037, −0.012], both "significant".
  - So the data-resampling intervals do not include seed variance. Differences between systems on T2 and T3 smaller than the seed spread (≈ 1.5 points T2 macro, ≈ 0.025 T3 AUROC, up to 10 points on single T2 datasets) should not be claimed.
- **B2 in the bootstrap:** readout − generated token +0.248 [+0.228, +0.269] (0.5B) and +0.071 [+0.059, +0.083] (3B); at K ≥ 14 +0.346 and +0.066.
- **0.5B training time:** 5.5 h wall clock (guard log 332 min; the train log reaches step 800 at 316 min). The "5.4 h" written earlier is the approximate training-loop time; use 5.5 h.


## Ch. 3 / Ch. 7: optimiser details behind the collapsed seed (2026-10-10)

- `training/train.py` builds `optim.AdamW(learning_rate=sched, weight_decay=0.0)`. In MLX 0.29.3, `AdamW` defaults to **`bias_correction=False`** (checked with `inspect.signature`), so the recipe is Adam **without bias correction**.
- Effect: in the first steps the moment estimates are not de-biased. The first update is about (1 − β1) / √(1 − β2) ≈ 0.1 / 0.032 ≈ 3× larger than with bias correction. The warm-up of 3 % (≈ 24 steps) limits but does not remove this, and gradient norms are not logged.
- Mosbach et al. (2021, ICLR) identify exactly this setup (Adam without bias correction, as in the original BERT optimiser) as a main cause of failed fine-tuning runs, through vanishing gradients early in training. It is a second plausible cause of the seed-4321 collapse, next to the missing gradient clipping (Pascanu et al., 2013).
- **For the thesis:** Ch. 3 must state "AdamW without bias correction (the MLX default) and without gradient clipping". Ch. 7 should give both as plausible causes of the collapse, without claiming either is proven. A recipe fix (bias correction on, clipping at norm 1, gradient-norm logging) would be a declared change, tested on several seeds; not planned.
- **Multiple comparisons:** the bootstrap p-values are not corrected for the ~50 pairs tested. Claims rest on the 95 % intervals and on effects far from zero. The one borderline result, GroundOne 0.5B vs Rizzo-Flow on T2 (p = 0.047), would not survive a correction and must not be claimed as significant.

## Ch. 2 / Ch. 6: external context from the Hugging Face decision-models literature (2026-10-10)

- **Deußer et al. 2026** (arXiv 2609.37647, verified in the PDF): Jev evaluated on 37 datasets. On LLM-AggreFact (test, 29,320 items, mean per-source balanced accuracy, i.e. the same metric as T2) Jev reaches **78.6** [77.6, 79.6]; Qwen3.8-27B read through its answer letters 76.9; Gemma-4-E4B 75.6. Prompts differ from ours, so no paired comparison is possible.
  - GroundOne 3B (74.8) is on par with MiniCheck-RoBERTa but **below** the closed state of the art and much larger open models on this broad benchmark. Stated in Ch. 6, Ch. 7 and the summary.
  - Jev's choice probabilities are well calibrated. Its binary probabilities rank well but are poorly placed w.r.t. a fixed 0.5 threshold; thresholds tuned on training data help a lot. This supports GroundOne's dev-fitted threshold (D27).
- **Laya** (convaiinnovations/laya, Apache-2.0): a ModernBERT-large encoder (421M) with a per-option [MASK] decision head. Each question is encoded with its own copy of the context, in one batched call; there is no shared context.
  - Vendor claims are contradicted by independent results: morrenhale accuracy 0.590 vs Jev 0.775; DecideBench 59.8 % vs 98.0 %; under- rather than over-confidence, fixed by one temperature (Nandakishore 2026); fragility to option order and key renaming; label-over-definition bias (Azizi 2026).
  - These are the family "encoder + decision head" in Ch. 2.
- **Core AI runs on an M4 Max** (mlboydaisuke dataset): the decision models re-prefill the whole state for every question, taking 40–220 s for a 3k-token state. This is measured evidence for GroundOne's one-pass design.
- **Caveats:** the tag has no definition; many cards are LLM-written; DecideBench items were written by Claude; Nandakishore's independence from the Laya author cannot be verified.

## Ch. 6 / Ch. 2: GroundOne on the scale of the Jev Decision Index (RAGTruth, response level; 2026-10-10)

- **Source.** The community "Jev Decision Index" (Hugging Face Space multimodalart/jev-decision-index, v0.2.1; raw files in Vault/raw) has benchmark 59, "RAGTruth response-level hallucination": all 2,700 test responses, F1 of the class "hallucinated". The baseline of always answering "hallucinated" scores 0.518.
- **Index results.** Jev 0.765; best entrant 0.803 (pplx-decider-v1-27b); every entrant under 1B scores ≤ 0.553; 31 of 70 entrants are at or below chance; all entrants ≥ 15B exceed 0.6.
- **GroundOne, computed from the saved T1 predictions** (CPU only). Rule: a response is hallucinated if any scored sentence is not predicted "supported" (raw decision). Gold: any scored sentence labelled contradicted or not mentioned. 2,647 responses (35.4 % hallucinated); always-hallucinated baseline 0.523.

| System | Response-level F1 |
| --- | --- |
| GroundOne 0.5B run 1 / run 2 | 0.657 / 0.680 |
| GroundOne 3B | 0.725 |
| B2 0.5B (generated token) | 0.612 |
| Index: Jev | 0.765 |
| Index: best entrant (27B) | 0.803 |
| Index: best entrant < 1B | 0.553 |

- **Reading.** The 0.5B specialist is far above every general decision model of its size (0.66–0.68 vs ≤ 0.55). The 3B is below Jev and the large entrants.
- **Caveats** (state them if this is used):
  1. GroundOne is trained on RAGTruth train (in-domain); the entrants are zero-shot general decision models.
  2. 2,647 of the 2,700 responses (the token cap and answers without scored sentences were dropped).
  3. The prompt and state format differ.
  4. GroundOne was not tuned for response-level F1. "Any sentence flagged" with sentence decisions tuned for balanced accuracy over-flags long answers; a response-level threshold fitted on dev (e.g. on the minimum P(supported) over sentences) would be fairer. Not computed yet.
- Other findings of the same survey (wiki page "Decision-Model Landscape (Hugging Face, 2026)"):
  - Liquid AI d1-3B uses GroundOne's readout family at GroundOne's size (restricted letter logits, shared state).
  - Cloudflare Clef is the first open decoder + dedicated-head model.
  - Perplexity pplx-decider and the Strands decider train on VitaminC (and Perplexity on WiCE), so they would be contaminated on T3/T2.
  - Li 2026: choosing the threshold by a lower confidence bound cuts the risk of a bad operating point (a cheap upgrade of D27).
  - Deka 2026: the open RLCD recipe gives no calibration gain over cross-entropy after temperature scaling.
  - llama.cpp merged a native `/v1/systemone` server (2026-10-02).

## Ch. 6: two CPU-only experiments (2026-10-11; `results/bootstrap/cheap_experiments_2026-10-11.json`, script in the session scratchpad)

**E1. Response-level verdicts with a dev-fitted threshold (Decision Index protocol).**
- Rule: response score = minimum calibrated P(supported) over its scored sentences; the response is hallucinated iff the score < θ, with θ fitted on dev to maximise the response-level F1 of the class "hallucinated".
- Results on T1 (2,647 responses):

| System | θ | F1 dev | F1 T1 | "Any sentence flagged" rule (2026-10-10) |
| --- | --- | --- | --- | --- |
| GroundOne 0.5B run 1 | 0.69 | 0.773 | **0.733** | 0.657 |
| GroundOne 0.5B run 2 | 0.71 | 0.778 | **0.743** | 0.680 |
| GroundOne 3B | 0.76 | 0.815 | **0.784** | 0.725 |

- Index references (zero-shot general decision models, 2,700 responses):
  - Jev 0.765;
  - best entrant 0.803 (pplx-decider-v1-27b, which trains on VitaminC and WiCE);
  - best entrant < 1B 0.553;
  - always-hallucinated baseline 0.518.
- **Reading.** With an aggregation fitted on dev, the 3B specialist (0.784) is above Jev and close to the best 27B entrant. The 0.5B (0.73–0.74) is far above any general decision model of its size.
- **Caveats:** in-domain training vs zero-shot entrants; 2,647 of 2,700 responses; different prompt format. Context, not a leaderboard claim.

**E2. Li-2026-style threshold for selective binary decisions.**
- Rule: accept a sentence verdict iff confidence max(p, 1 − p) ≥ c. The point estimate takes the smallest c whose dev accuracy reaches the target; the LCB rule takes the smallest c whose one-sided 95 % cluster-bootstrap lower bound reaches it.
- Results on T1:
  - **The point estimate never misses the target** (targets 0.95 / 0.97 / 0.98; risk 0 over 200 dev resamples for every run).
  - The LCB rule raises realised accuracy slightly (e.g. 0.5B, target 0.97: 0.981 → 0.985) but **costs 3–12 points of coverage** (0.734 → 0.656).
- **Reading.** In domain, T1 is cleaner than dev, so the point estimate is already safe and the conservative rule only defers more. Its value is under distribution shift (new workloads, VitaminC), where calibration is known not to transfer. Report as a negative/neutral finding: the current served threshold (D27) needs no change for the RAGTruth domain; a deployment on a new domain should use the LCB rule with a small local labelled sample (Li et al. 2026).

## Ch. 5 / Ch. 6: a general-purpose decision model of the same size (Liquid AI d1-3B, B3b; 2026-10-11)

**Setup.** `groundone baselines frozen --system d1`; results in `results/d1-3b/{t1,t2,t3}`; queues `jobs/queue_night7.txt` (T3) and `queue_night7b.txt` (T1, T2).
- d1-3B is Liquid AI's open decision model (3.1B, LFM2.5-VL-3B base, licence LFM 1.0). It uses the restricted letter readout with the state shared across questions.
- Run zero-shot, in process (PyTorch MPS, bf16, revision 051bcc4) and offline (`HF_HUB_OFFLINE=1`).
- Same state and questions as Rizzo-Flow: document + numbered answer, one three-way choice per sentence, at most 6 questions per call. On T2, documents are chunked exactly as for GroundOne, keeping the maximum over chunks.
- **Engineering note.** PyTorch's MPS backend keeps a compiled graph for every input length, and that memory (≈ 0.2 GB per new shape) is not released by `empty_cache`. The first night queue therefore lost almost all T1 answers to out-of-memory errors. The run now uses worker processes restarted when MPS driver memory exceeds 11 GB: 0 skipped, results unaffected. No latency comparison is made (different runtime).

**Results (bootstrap pairs on the same items):**

| Test | d1-3B | GroundOne 0.5B | GroundOne 3B | Difference (GroundOne − d1) |
| --- | --- | --- | --- | --- |
| T1 three-way (17,284 sentences) | 0.657 | 0.769 | 0.832 | +0.112 [+0.092, +0.133]; +0.175 [+0.157, +0.195] |
| T1 AUROC | 0.863 | 0.905 | 0.940 | +0.042; +0.077 (both significant) |
| T1 three-way, K ≥ 14 | 0.527 | 0.723 | 0.839 | 3B: +0.312 [+0.230, +0.405] |
| T3 VitaminC three-way / AUROC | **0.724 / 0.913** | 0.442 / 0.722 | 0.527 / 0.817 | 3B: −0.197 / −0.096 (d1 better) |
| T2 macro / RAG subset (4,000-item random subsample) | 75.7 / 76.5 | 69.2 / – | 74.3 / 75.8 | 3B: −1.3 [−4.0, +1.0] n.s.; RAG −0.7 n.s.; 0.5B: −6.5 significant |

- d1-3B T1 recall: supported 0.895, contradicted 0.582, not mentioned 0.493. By task: Data2txt 0.654, QA 0.583, Summary 0.516.
- On T2, d1's RAGTruth column is 78.9 vs 87.3 for GroundOne 3B (in-domain), and d1 is clearly better on WiCE (84.6) and TofuEval-MediaS (84.0).
- **Reading.**
  - At equal size, the specialist wins clearly in its domain, and by more on long answers. The 0.5B GroundOne, six times smaller, also beats d1-3B on T1.
  - The general decision model wins clearly out of domain (VitaminC) and is on par with the 3B on the broad grounding benchmark (LLM-AggreFact).
  - Specialisation buys in-domain accuracy and long-answer robustness at the cost of transfer. This is the cleanest statement of RQ1, now with a same-size generalist instead of only untrained models and a 4B generalist.
- **Caution.** The 21-answer smoke test gave d1 0.838 on T1; the full run gives 0.657. Small samples mislead.

## Ch. 1 / Ch. 2: local inference sources ingested (2026-10-11)
- **Prefill/decode asymmetry, independent support.** Apple states that the M5's 3.3–4.1× faster time to first token comes from compute (GPU neural accelerators) and its 1.19–1.27× faster generation from a 1.28× bandwidth increase; EXO Labs measures DGX Spark prefill 3.8× faster and M3 Ultra decode 3.4× faster (Llama-3.1 8B, 8k prompt). Usable in Ch. 2 §Inference on the user's device next to Pope et al. and the own Phase 0 measurement. Wiki: Local Inference Hardware, Prefill and Decode.
- **Terminology.** Qwen2.5 is open-weight, not open source (OSI Open Source AI Definition 1.0); licences differ (0.5B Apache 2.0, 3B Qwen Research). Check the thesis for "open model"/"open-source" wording.
- **Motivation numbers for Ch. 1.** Consumer-GPU-sized open models reach frontier performance in 6–12 months (Epoch AI); open/closed gap on Chatbot Arena 8.04 % → 1.70 % (Stanford AI Index 2025); Jan–May 2026 open models lag about 4 months on ECI (Epoch AI).
- **Privacy case study.** Navier–Stokes credit dispute (Sept 2026): drafts in OpenAI Codex; OpenAI: "While unlikely, we cannot rule out that de-identified data derived from their usage of our products helped improve our models." Use only as an example of unverifiable cloud data handling, not of proven misuse; cite NYU Shanghai RITS or Live Science for the quote.
- **Counter-position to acknowledge.** Qu 2024 (IEEE COMST) argues pure on-device deployment is too limited and favours edge servers.
- Not yet in the bibliography; to add only for the sources the author selects.

## Ch. 2 (new): Local Inference of Language Models (written 2026-10-11)
- **Structure decision (author, 2026-10-11).** Locality is the backbone of the thesis and gets its own chapter (target ≥ 10 pages; thesis target 120–150 pages). The former background sections "Transformer inference" and "Inference on the user's device" moved into it (labels `sec:bg-inference`, `sec:bg-local` kept); the background chapter is now Ch. 3. Sections: 2.1 hosted vs local (privacy as a technical guarantee, GDPR Arts. 4(2), 28, 44–49; Navier–Stokes case; Apple PCC; availability, stability, cost, logits; hybrid designs), 2.2 open-weight and small models (OSI definition, licences of Qwen2.5 0.5B Apache-2.0 vs 3B research, EU AI Act; Epoch/AI Index gap; SLMs, MobileLLM, vendor on-device models), 2.3 cost model (prefill/decode, roofline, decode floor, memory fit), 2.4 hardware (table + figure; Spark vs M3 Ultra; M5; phones/NPUs), 2.5 runtimes and quantisation (LLM.int8, GPTQ, AWQ, GGUF, MLX; speculative decoding), 2.6 energy, 2.7 consequences for verification.
- **Own analytic results in the chapter (arithmetic on vendor specs + own measurements).** M4 roofline: ridge ≈ 23 FLOP/byte (compute reached in prefill ≈ 2.8 TFLOP/s, lower bound; Apple gives no FLOPS); decode ≈ 2 FLOP/byte. Decode floor of the 3B 8-bit (3.28 GB): 27.3 ms/token on the M4 (measured 31.8), 1.8 ms on an RTX 5090. Minimum decoding time of a 3B judge for a K ≥ 14 answer (median 65 / 388 generated tokens, latency protocol): 1.78 s / 10.6 s on the M4, 0.12 / 0.71 s on an RTX 5090; zero for a System One on every machine.
- **Figures** (`groundone figures locality`, PNG in Thesis/images/locality): prefill_vs_decode_m4, roofline_m4, memory_fit, hardware_landscape (thesis machine at its actual 16 GB; bars over memory ranges, after the author's correction), decode_floor_by_hardware, judge_decode_overhead_by_hardware, open_closed_gap.
- **Honesty notes.** No GroundOne measurement on other hardware: the chapter claims the direction of the advantage, not its size (also in Ch. 7 threats). Prices only where a source states them (Framework Desktop $1,999 Aug 2025); Apple store prices could not be extracted reliably. SEO sources (Corelab, Davies Meyer, DasRoot, Presenc, PremAI) not cited.
- **Summary** now has a locality paragraph and the decode lower-bound sentence; Ch. 1 points to Ch. 2; Ch. 8 future work: llama.cpp port to measure on GPU / Spark / Strix Halo / phone.

## Ch. 2 revision (2026-10-12)
- Italian Ch. 2 revised for clarity before the author's review: long sentences split; definitions added inline or as footnotes (edge intelligence, titolare/responsabile del trattamento, decisione di adeguatezza, blow-up, attestazione, air-gapped, server edge, pre-/post-training, FLOP and TFLOP/s, distillation, MMLU, decoder-only, compute-optimal training explained, KV cache and attention, low-rank adapters, batch 1, per-group scales, mixture-of-experts, petaflop and sparsity, time to first token, GGUF, outlier, perplexity).
- Figures reviewed: decode_floor and judge_decode_overhead merged into one two-panel figure (`decode_cost_by_hardware`, cited as 2.x a/b), since they showed the same ranking scaled by a constant. Italian versions of all Ch. 2 figures generated (`groundone figures locality` now writes figures/locality and figures/locality_it).
- New figure of hardware photos (MacBook Pro M4, Mac mini M4, Mac Studio, DGX Spark, RTX 5090) from Wikimedia Commons with free licences; credits in the caption and in images/hardware/CREDITS.md. No free photo of a Strix Halo desktop was found.

## Demo application (D28, 2026-10-18): runtime choice and architecture
- **Decision.** Native macOS app in Swift/SwiftUI with MLX Swift; retrieval, generator and GroundOne in one process. Spec and open questions: `demo_architecture.md`. Wiki: `Demo Application`, `Demo Runtime Choice`, `MLX Ecosystem`, `Local RAG Retrieval`, `Verify-and-Revise Loops`, `Guardrails and Policies`.
- **Justification for the thesis (runtime).** The deciding requirement is numerical: adapters, calibration and fingerprint are MLX artefacts, so a runtime with other weights or kernels (candle, llama.cpp/GGUF, Core ML) re-opens the experiment (recalibration on dev at least). MLX Swift calls the same C++ core through mlx-c; mlx-swift-lm 3.32.3 implements Qwen2, loads mlx-lm adapters unchanged (`LoRAContainer`) and exposes the final hidden states (`Qwen2Model.model`), so the port needs no architecture code, only prompt, segmentation, readout and calibration. Parity is shown by a conformance test (token ids identical, |Δp| < 0.01), not assumed. A Python app would have exact parity but is a server plus a browser, not a self-contained application; Rust options rest on community bindings (mlx-rs: two examples, no Qwen/LoRA) or on candle (README documents CPU/CUDA/WASM, not Metal; no Qwen2.5).
- **Portability, stated precisely.** Swift runs on Linux/Windows/Android; MLX on macOS (Metal) and Linux (CPU, CUDA), not Windows; SwiftUI is Apple-only. Earlier wording "MLX Swift is Apple-only" was imprecise: only the UI is. Engines sit behind protocols so a llama.cpp backend can be added (future work, Ch. 9).
- **Costs to acknowledge.** Xcode needed for the Metal shaders; mlx-swift-lm 3.x broke API (pin the version); tokeniser is swift-transformers (part of the conformance test); pysbd has no Swift port, NLTokenizer's algorithm is undocumented (agreement to measure on T1).
- **Repair loop, position in the literature.** Self-Refine, RARR, CRITIC, CoVe, CRAG; Huang et al. 2024: without external feedback self-correction does not help (GPT-3.5 CommonSenseQA 75.8 → 38.1). GroundOne is an external, specialised, local critic whose re-check costs one prefill; per-sentence three-way verdicts allow targeted edits (RARR-like) and re-retrieval on "not mentioned" (CRAG-like). Limits: not an oracle; small generators may not repair (Vicuna-13B in Self-Refine); the loop can game the verifier by deletion (CoVe).
- **Guardrails.** NeMo Guardrails' fact-checking rail is a yes/no prompt on the whole response (about 80 % on MS MARCO), rails block or abstain without targeted repair, ≈ 3× latency, telemetry on by default (locality point). The demo's policy (strict/lenient, τ, attempts, on-failure action, audit log) is a learned, calibrated per-sentence rail.
- **Shared-base idea.** The verifier's base is Qwen2.5-3B-Instruct 8-bit, the same family as the demo generator: with adapter load/unload one 3.3 GB copy can serve both roles (≈ 1.8 GB saved, slower 8-bit decode). To measure if adopted.
- **Measurement honesty.** Demo measurements are a case study (co-residence, verifier overhead, rounds), not part of the results matrix; a faithfulness gain of the loop would need an independent checker and an equal-compute best-of-N baseline.

## Revision of Ch. 3–9, Italian version (2026-10-18)
- Same criteria as Ch. 1–2: clarity pass (split sentences, conditions first, both sides of comparisons named), definitions in footnotes or inline at first use (about 22 footnotes: encoder, balanced accuracy, LLM-as-a-judge, temperature, rank, Adam/AdamW, softmax, LoRA scale/dropout, cross-entropy, warm-up/cosine, AUROC, Brier, span, Fleiss' κ, recall/precision/F1, hash, wall-clock, bag-of-words, greedy, stratified sampling, multiple comparisons, contamination). balanced accuracy, encoder and LoRA appear in Ch. 1 without a definition and are defined at their first technical use in Ch. 3.
- Ambiguities resolved against the notes: sign convention of the seed differences (first minus second run), 74.4 (GroundOne 0.5B) vs 74.6 (MiniCheck-RoBERTa) on the T2 RAG subset, 3B judges' format failures (0.1 % terse, 7.6 % verbose), "AdamW without bias correction" in Ch. 8 (was "Adam"), raw probabilities vs class frequencies (Ch. 4), checkpoint metric (Ch. 6), p-value definition (Ch. 6), TofuEval's two subsets (Ch. 5: eleven datasets). The tracker note "d1-3B T2 on 6,000 items" was wrong: 4,000 (fixed in `tools/matrix.py`).
- New figures (Italian, TikZ in `Thesis_ita/images/diagrams/*_tikz.tex`, shared style `g1_common.tex`): verifier families, risk–coverage schematic, LoRA (Ch. 3); marked prompt, design (a) vs (b), calibration-to-label flow, software architecture (Ch. 4); dataset pipeline, label rule (Ch. 5); baseline map, paired cluster bootstrap (Ch. 6); when to use a specialist System One (Ch. 8). New plots: analytic cost model (`groundone figures method`, Ch. 4), gain decomposition untrained → B2 → GroundOne (Ch. 8); existing but unused plots added: paired bootstrap differences, T1 AUROC by task, T3 comparison, 3B reliability (Ch. 7).
- All Ch. 5–7 plots now have Italian labels (`GROUNDONE_FIG_LANG=it`, dictionary `figures/i18n.py`; EDA scripts write `report/figures_it/`). The English thesis still uses the English PNGs; the TikZ diagrams need an English version when the English text is aligned.
- Italian thesis: 114 → 127 pages, compiles without errors.

## Ch. 2 / Ch. 6 / Ch. 7 / Ch. 8 — locality pillar: offline proof, 8-bit vs bf16, co-residence (queue_day8, 2026-10-18)
All three jobs ran with `HF_HUB_OFFLINE=1` **inside a macOS sandbox that denies every network operation to the process** (`sandbox-exec -p '(version 1)(allow default)(deny network*)'`; under it `curl` cannot even resolve a host, MLX uses the GPU normally). Queue `jobs/queue_day8.txt`, 39 min, no guard intervention. Results in `results/locality/*.json`, `results/{offline-g1-05b,bf16-g1-05b,coresidence-3b,coresidence-05b}/`.
- **Offline proof (independence).** Full T1 with GroundOne 0.5B in the network-denying sandbox: predictions **bit-identical** to the original run on all 17,284 sentences (max |Δp| = 0; three-way 0.769, AUROC 0.905). Evaluation, model loading and inference need no network at all; this is stronger than "Wi-Fi off", because the process cannot reach the network even when the machine is online.
- **8-bit vs bf16 base (0.5B, same adapter).** Applying the adapter (trained on the 8-bit base) to the bf16 base changes probabilities by 0.011 on average on T1 (99th percentile 0.072, max 0.38) and 0.007 on T3; the argmax agrees on 98.3 % (T1) and 98.9 % (T3) of sentences; three-way balanced accuracy 0.7687 vs 0.7684 (T1), 0.442 vs 0.442 (T3); AUROC 0.905 vs 0.904 (T1), 0.722 vs 0.723 (T3). **The 8-bit base costs no measurable accuracy.** Caveat: this measures sensitivity to the base precision under an adapter trained on the 8-bit base, not a model trained in bf16; 0.5B only (author: 3B bf16 not needed).
- **Co-residence (RQ4, H4).** One process with the demo generator (Qwen2.5-3B-Instruct, MLX 4-bit) and GroundOne (design b, calibrated); 30 T1 documents stratified by task; greedy generation up to 300 tokens (median 169 generated tokens, K = 7):
  | Verifier | MLX memory after loading both | MLX peak during the loop | Median generation | Median verification | Verification share of total time |
  | --- | --- | --- | --- | --- | --- |
  | GroundOne 3B | 5.0 GB | **6.1 GB** | 4.75 s | 1.68 s | 30 % |
  | GroundOne 0.5B | 2.3 GB | **3.3 GB** | 4.65 s | 0.28 s | 6.7 % |
  Both stay far below the 11 GB of H4 and the 16 GB of the machine: **H4 co-residence supported.** Honest note: with the 3B the guard saw the system's available memory dip to 1.6 GB for a moment (other applications open: VS Code, Mail, Claude), so on a 16 GB laptop the 3B + generator pair is comfortable for the process but leaves little headroom for a heavy desktop session; the 0.5B pair leaves ≥ 3.4 GB available. The retriever is not included (document given, as in RAGTruth); an embedding retriever will be measured in the demo. Process RSS (2–3 GB) does not count GPU-resident buffers; MLX active/peak memory is the relevant figure.
- **For the thesis:** Ch. 2 (quantisation section: own measurement that the 8-bit base is lossless here), Ch. 6 (protocol: offline sandbox), Ch. 7 (new short section "Locality: offline run, quantisation, co-residence"), Ch. 8 RQ4 paragraph ("resta da misurare la memoria ... accanto a un generatore" is now measured), demo chapter (reference numbers).

## Ch. 8 (RQ4) / locality pillar: cost of hosted vs local verification (D30, 2026-10-19)
- 10,000 verified answers: hosted judges at list prices (accessed 2026-10-19, standard tier) cost $1.1–2.2 (Claude Haiku 5.5, gpt-6-luna), $22–43 (Sonnet 5.5, gpt-6.1-sol, Gemini 4 Argon), up to $109–215 (gpt-6-astra), with ≈ 906 input tokens per answer and the measured output of our 3B judges (36 terse, 248 verbose). GroundOne locally: 0.015 kWh (0.5B) and 0.092 kWh (3B) of net chip energy, ≈ €0.004 and €0.03 at the EU household average (€0.2896/kWh, Eurostat S2 2025). `results/locality/cost_comparison.json`.
- Honest reading written into Ch. 8: two to four orders of magnitude apart, but cheap hosted judges are inexpensive in absolute terms; hardware, caching/batch discounts and hosted-judge quality are not included; independence remains the decisive locality argument.
- Side finding for Ch. 2: Gemini's free tier uses prompts to improve Google's products, the paid tier does not.

## Ch. 6 / locality pillar: licences of the components (2026-10-22)
- Table 6.1 (Italian, Ch. 6 §"Licenze e condizioni d'uso"), verified on the official pages: Qwen2.5-0.5B Apache 2.0; Qwen2.5-3B Qwen Research License (research and evaluation only; commercial use needs a licence from Alibaba Cloud); MiniCheck-RoBERTa MIT; HHEM Apache 2.0; Rizzo-Flow Apache 2.0; d1-3B LFM Open License 1.0 (commercial use below USD 10 M revenue); RAGTruth MIT (contexts from MS MARCO, research-only, and Yelp Open Dataset, educational use); LLM-AggreFact CC BY-ND 4.0 + evaluation-only gating; VitaminC CC BY-SA 3.0; MLX/mlx-lm/MLX Swift/pySBD/llama.cpp MIT, Transformers Apache 2.0, PyTorch BSD.
- Consequences written in the thesis: independence holds legally (everything runs locally under research-permitting licences); GroundOne 3B and the demo generator are research-only, the 0.5B is commercially reusable; upstream terms of the training contexts make the adapters research artefacts (no legal assessment).

## Ch. 8 / Ch. 9: language (2026-10-24)
- Limitation added to Ch. 8 (Italian): all training and test data are English; Qwen2.5 is multilingual but transfer of the learned specialisation and of the calibration to other languages was not measured (calibration does not even transfer to another English domain, VitaminC).
- Future work added to Ch. 9 (author's idea, refined): first measure zero-shot transfer of the English adapter (e.g. part of T1 translated into Italian); if insufficient, per-language twin adapters trained separately on one shared base (small models have little capacity to share across languages; adapters are small and can be loaded/unloaded at runtime over one base copy; a language detector picks the adapter). Open problems: labelled data per language (translating RAGTruth breaks span alignment and needs label checks), per-language calibration (T, b, τ), cross-lingual RAG (document and answer in different languages). Per-language vs single multilingual adapter is an experiment to run, not a conclusion.

## Demo chapter: decisions and limitations to state (2026-10-24)
- GroundOne Studio (final name); judge comparison mandatory and local (GroundOne's base without the adapter, B0a prompt); source links as optional M3b (GroundOne per passage + similarity, demonstrative, not measured); corpora: T1 for measurements, the author's arXiv library for the demonstration, English only; retriever hybrid with a small retrieval-trained embedding model on MLX.
- **Limitation to write:** rewritten sentences have no reference label; their correctness is judged only by GroundOne, which also stops the loop, so a rewrite in a GroundOne blind spot counts as a repair. Injected errors (D30) measure only whether the injected error disappears. **Future work:** independent check of rewrites (second verifier such as MiniCheck-RoBERTa, or human reading of a sample).
- Framing (author): the focus of the thesis is the experiment; the demo is a demonstration, not a product. State intrinsic limits honestly and list ways to address them as future work, rather than adding validation work to the demo.

## Demo chapter: implementation results (2026-10-24)
- **Conformance (Swift port vs Python, §5.3 of demo_architecture.md):** 200 T1 answers, 1,747 markers. Token ids and marker positions identical 200/200 for both models (piecewise tokenisation with swift-transformers reproduces HF tokenizers exactly). 3B: max |Δp| 0.0048, labels 100 % identical → PASS, thesis numbers hold in the app. 0.5B: max |Δp| 0.031, 3 sentences above 0.01, labels 99.71 % identical with every disagreement within 0.01 of τ. Probable cause: different accumulation order in the Metal kernels at bf16, larger effect on the smaller model; worth one sentence, not a section.
- **Segmentation port:** NLTokenizer + list/checkable rules + three pysbd-like rules (initials and abbreviations, lowercase continuation, list markers) give identical segmentation to pysbd on 98.4 % of the 2,647 T1 answers (95.2 % without the extra rules). Residual differences: titles with "v." / quotes spanning sentences.
- **Retrieval check (embedding choice):** 12 questions over the research library (109 files, 5,886 passages): hybrid hit@5 1.00 / MRR 1.00 with both bge-small and Qwen3-Embedding-0.6B; bge-small chosen (equal, smaller, faster). State that the check is small and at the ceiling (questions written with the source in mind; lexical overlap with titles helps BM25).
- **Engineering lessons worth a paragraph (local inference, Ch. 2 / demo chapter):** (1) MLX keeps freed GPU buffers in a cache unless a limit is set; a variable-length workload grew to 11 GB and swapped until the 1 GB limit used by the Python backend was added; (2) macOS privacy protection (TCC) blocks an app's access to Desktop/Documents until the user approves, so a local app should keep its data in Application Support; (3) one process can serve generator, verifier and judge, with the judge on the verifier's own base weights by unloading the LoRA adapter (no extra memory).
- **Speed parity Swift vs Python** (same 200 T1 answers as the latency subset, forward pass on the same ids, Release): 3B mean 2.13 s vs 2.04 s in Python; 0.5B 0.343 s vs 0.333 s. The port costs ≈ 4 % at most.
- **Injected-error case study (D30), 3B, 100 answers** (`outputs/demo/casestudy/summary_full.json`, figures `outputs/figures/demo/casestudy_*`): GroundOne flags the injected sentence in 100/100 (by construction of the set: originals accepted by GroundOne, blunt errors, so this shows the mechanics, not recall); the local generative judge (same base, no adapter, B0a) flags 88.5 %; GroundOne false alarms on the other sentences 2.1 %. Error still present: 100 % → 14 % after one rewrite → 14 % after two (the second round adds nothing). Of 14 survivors 13 remain flagged (highlighted by the policy) and 1 is accepted by GroundOne (a miss). **Of 86 removed errors, 75 were removed by deleting the sentence, 10 by restoring the document's value, 1 by rewriting**: precision by deletion (as CoVe), with loss of the correct information for swapped values. Other sentences kept verbatim 97.8 %. GroundOne pass median 1.77 s vs judge 2.33 s (23 tokens; 1.4×). MLX memory with generator + GroundOne 3B: 5.1 GB after loading, 6.2 GB peak. Prompt not tuned after seeing the result (decision left to the author).
- **0.5B variant**: same detection (100 %), but false alarms 16.8 % on correct sentences (81 % kept verbatim) and the 0.5B judge flags only 34.6 % (81 % parsed); survival 9 %; GroundOne pass 0.29 s; memory peak 3.3 GB. Caveat: the set was selected with the 3B.
- **Equal-compute baseline (best-of-3, 60 fresh T1 answers, 3B):** loop accepted by GroundOne 98.3 % (first draft alone 51.7 %), median 7.1 s and 112 generated tokens; best-of-3 sampling (T = 0.7) 61.7 %, 10.0 s, 218 tokens. Acceptance is GroundOne's, and the loop can reach it by deleting sentences: state both.
- **Qualitative library example (to show in the chapter):** "Which post-processing method fixes the miscalibration…": the generator adds "temperature typically between 0 and 1" (wrong: Guo et al. use T > 1 to soften) and two unsupported claims; GroundOne flags the three as not mentioned, the judge marks all four as supported; the loop removes them and the answer shrinks to the one correct sentence — value and limit (deletion) in one example.
- **Rewriting, final design (2026-10-24; the chapter reports only this, no versions — author):** one short request per flagged sentence with the relevant excerpt and an instruction by error type (contradicted: correct from the source, never delete; not stated: rewrite from the source or delete). On a fresh set of 100 injected answers (3B): errors left 9 %; of 91 removed errors 41 restored with the document's value, 1 rewritten, 49 deleted (25 of them fabricated sentences, where deletion is the right repair; 18 invented names, labelled not mentioned); swapped numbers restored 18/25, dates 16/25; 90 % of answers accepted by GroundOne; 3 errors accepted by GroundOne (misses); GroundOne 1.74 s vs judge 2.27 s; rewrite 0.9 s per round. Earlier whole-document prompt (internal control on the same set): 7 restored, 80 deleted — the 3B deletes when offered the option.

## Ch. 7 / Ch. 4 / Ch. 9: latency net of the prefill and prefix caching (D32, 2026-10-26)
- **Why GroundOne's latency grows with K:** not the decisions but the text. In the latency subset the prompt grows from ~550 tokens (K 1–4) to ~1,140 (K ≥ 14); a fit gives s ≈ 0.35 ms × prompt tokens + 0.2 ms × K (0.5B) and 2.2 ms × tokens + 2 ms × K (3B). The judges pay the same prefill plus the decoding of the verdicts (terse ~4 tokens per verdict).
- **Measured split** (`baselines decompose`, results `decompose-05b`, `decompose-3b`; same 200 answers; totals reproduce the published latency within 4 %): GroundOne reading = 97 % of its time (both sizes); deciding 12 ms per answer (0.5B) and 67 ms (3B), i.e. 1.3 and 6.7 ms per sentence; terse judge 30 and 139 ms per sentence, verbose 170 and 1,033. Decision-only speed-up vs terse 33× (30–38) for the 0.5B and 18× (15–20) for the 3B; vs verbose 131× and 125×. Overall stays ~2× (shared prefill). Figure `outputs/figures/benchmarks/latency_split.png`.
- **LoRA overhead seen in the split:** GroundOne's reading is ~10 % slower than the judges' (base weights, no adapter) although its prompt is shorter (887 vs 925 tokens): the unfused adapter. Fusing it would remove it but needs requantisation + recalibration (future work).
- **Prefix caching (exact under causal attention):** prompt order instructions → document → answer, so the KV of the instructions (63 tokens, 7 %) and of the document (65 % of the tokens) can be reused by any later answer on the same document; the answer is ~27 %. Not exclusive to the decision model (the judge prompt also starts with instructions + document): measured for both with the same cache. Implemented in the service (`engine.py`: fixed instructions + LRU of 4 documents; `prefix_cache` field; `GROUNDONE_PREFIX_CACHE=0`) and in the app (verifier and judge, separate caches because the judge runs without the adapter; note in the timing panel).
- **MLX bug found (0.29.3, Python):** `mx.fast.scaled_dot_product_attention` with `mask="causal"` is wrong for some shapes when several queries follow cached keys (e.g. 501 queries after 523 keys: attention error 0.23, logits up to 0.7, 2/342 argmax flips with the 0.5B adapter; max |Δlogit| 4.3 with the 3B). An explicit boolean mask matches a float32 reference. The cached paths use it (`backend.explicit_offset_mask`); cold passes (offset 0) and decoding (one query) never take that path, so all published results are unaffected. After the fix, cached vs cold on 100 answers: max |Δp| 0.014 (0.5B) and 0.005 (3B), 3 and 1 argmax changes out of 1,758, all on near-ties (bf16 rounding). MLX Swift 0.32.3 (newer core) shows no discrepancy (`g1studio sdpa-check`); the Swift conformance test now also checks the cached path: max |Δp| 0.0037, PASS.

## Ch. 8: final rewrite (copy check) and generator 3B vs 7B (D33, 2026-10-26)
- **Rewrite copy check:** explicit "do not return it unchanged" in both prompts; a copy (normalised) gets one retry quoting the copy; a second copy keeps the sentence flagged, not retried later, noted in the panel. 3B case study (set2, 100 answers, `casestudy-g1-3b-b1-set2-final`): copies caught 3 times; surviving errors 8 % after round 1 and 6 % after round 2 (was 10 % / 9 %); accepted by GroundOne 94 % (was 90 %); removed by restoring 42, rewriting 1, deleting 51; survivors 3 still flagged + 3 never flagged (p = 0.93 just above τ; two not scored); per kind: numbers restored 19/25, dates 16/25, names deleted 18 / restored 7, fabricated deleted 25; other sentences verbatim 98.0 %; times G1 1.74 s, judge 2.36 s, rewrite 0.92 s per round; MLX 5.1 GB after load, 6.7 GB peak (was 6.2: the prefix cache keeps up to 16 heads).
- **0.5B rerun (final rewrite):** detection 97/98, false alarms 16.8 %, restored 12, deleted 84, survival 3 %, other sentences verbatim 83.9 %, accepted 81 %.
- **Best-of-3 at equal compute (60 T1 documents, final):** loop accepted 70 % (42/60) vs best-of-3 62 % (37/60), first draft 52 %; loop 6.3 s and 115 tokens vs 7.0 s and 218 (best-of-3 got faster with the prefix cache: same document re-verified per sample).
- **7B generator (Qwen2.5-7B-Instruct 4-bit), selectable in the app:** case study survival 3 % (only the 3 errors GroundOne never flags), accepted 98 %, rewrite 2.1 s/round vs 0.9, MLX peak 9.2 GB vs 6.7. On the 12 library example questions (`outputs/demo/results/examples-gen{3b,7b}.json`): median 276 vs 250 words, generation 17.7 s vs 7.6, GroundOne supported 66 % vs 85 % of sentences (46 vs 21 not mentioned), after one rewrite 2 vs 9 sentences still flagged, 0 vs 1 copies; MLX active 8.5 vs 5.9 GB, peak 9.4 vs 6.9 GB. The 3B stays the default.
- **App memory:** peak 6.2 GB during one question, 6.9 GB after a 12-question session (prefix cache of recent sources).
- **Retrieval determinism fix:** RRF ties broken by row id (Swift dictionary order reordered tied passages between processes and changed the greedy answer).
- **Headline basis for the cache (2026-10-26):** the 1.7–2× speed-up is the first verification (cold; caching the instructions alone leaves it at 1.96× / 1.77× at K ≥ 14). With the document cached (re-verification), at K ≥ 14 the speed-up over the terse LLM judge is 3.6× for the 0.5B (3.5–3.8) and 3.4× for the 3B (3.2–3.4); over all answers 4.8× and 3.1×. Ch. 1, Ch. 9, the thesis summary and both 3-page summaries use the K ≥ 14 basis ("from 1.7–2 to 3.4–3.6").
- **Answer-prefix reuse (2026-10-26, `decompose --cache rewrite`):** the cache also keeps the whole sequence of the last verification; after a rewrite the pass starts at the first changed token and the verdicts of earlier markers are reused (exact under causal attention). Measured on the 200 latency answers by appending ", as reported." to the first, middle or last scored sentence (a stand-in for a rewrite: time depends only on where the change falls). GroundOne, document cached → previous version cached: 0.5B 0.106 s → 0.095 / 0.051 / 0.021 s (1.13× / 2.1× / 5.0×; 2.6× over the three positions), 3B 0.589 s → 0.515 / 0.285 / 0.093 s (1.15× / 2.1× / 6.3×; 2.7×); tokens read 249 → 219 / 104.5 / 8. Terse LLM judge only 1.03–1.13× (0.5B) and 1.07–1.29× (3B): its verdicts follow the whole answer, so any change invalidates all of them and the decoding is repeated. Terse / GroundOne: 4.8× → 12× (11.2–12.9) with the 0.5B, 3.1× → 7.1× (6.6–7.8) with the 3B. Thesis: Ch. 4 (argument), Ch. 7 `tab:results-answer-prefix`, Ch. 8 (re-verification in the app), Ch. 9. Implemented in the service (`engine._score_cached`, `prefix_cache: "answer prefix"`) and the app (`GroundOneModel.lastAnswer`); tests `test_answer_prefix_reuse_equals_one_pass` (Python) and the Swift conformance check (cached vs cold, document + answer prefix: max |Δp| 0.0073 with the 3B, PASS; 0.0186 with the 0.5B, which already fails the cold gate at 0.031; row added to `tab:studio-conformance`).
