# Thesis notes: findings and arguments to reuse when writing

A running record of results, explanations and arguments that came up during the experiment, organised by thesis chapter.
Every number points to its source file.

**Rules:**
- Add an entry whenever a result or insight appears; never delete one, mark it superseded instead.
- English, short and factual. The thesis prose is written later from these notes.
- Raw logs and status are in `Phases&ToDos.md`; this file keeps what the thesis needs.

---

## Ch. 2 / Ch. 7: what "working in RAG" means (2026-10-07)

- A RAG check and a generic (source, claim) check are formally the same task: does the document support the sentence? What differs is the **distribution**, and a fine-tuned verifier learns the distribution.
- **Who writes the claim.**
  - In RAG an LLM writes it right after reading the source. Sentences reuse many words of the document and are mostly correct (≈ 90 % supported in RAGTruth). Errors are LLM-typical: fabricated details (baseless) more often than contradictions, swapped numbers or names, intrusions of world knowledge.
  - In fact-verification datasets (VitaminC, FEVER) humans write the claims adversarially: minimal edits, numeric comparisons ("more than 23.5 million"), paraphrases that avoid the source's words.
- **Context.** In RAG a sentence sits inside a multi-sentence answer (coreference, discourse), and the document is long: several retrieved passages, or structured data (JSON) in data-to-text.
- **Error forms.** In RAGTruth "contradicted" is mostly *evident* conflicts (85 % of contradicted training sentences come from Evident Conflict spans), concentrated in data-to-text.
- **Claim scope for the thesis.** GroundOne is a verifier of *LLM-written text grounded on a source*, not a universal fact checker. Specialisation is the point of the thesis, not a weakness to hide.

## Ch. 4: data (see also `data/processed/groundone/DATACARD.md`, `EDA/report/eda_report.md`)

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

Setup: 0.5B, design (b), all training answers, 802 steps (accumulation 4, ≈ 16 answers per step), 5.4 h on the M4. Best dev checkpoint at step 600. Sources: `results/g1-05b-b1/{t1,t2,t3}/metrics.json`, `models/g1-05b-b1/train_log.jsonl`, `figures/training-g1-05b-b1/`.

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
