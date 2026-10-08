# GroundOne dataset plan

Status: v2.3 (2026-10-08). All steps done: the test sets are frozen (2026-10-07, `data/processed/groundone/tests_frozen.json`), and the dataset was validated by training (T1 three-way 0.769 for the 0.5B). Readout design (b) is the default (§8). Simplified to the strict minimum: one training source, three test sets. **Steps 1–3 and 5 of §7 are done** (`Project/data/processed/groundone/DATACARD.md`); the tests await the author's approval to be frozen (step 4). Decisions D20 and D21 are in `implementation_plan.md` §3.

This document specifies how the training, development and test data are built from scratch. Nothing is trained until the test sets of §4 are built, validated and frozen. The thesis (Ch. 4) describes only the dataset produced by this plan.

---

## 1. What the model must learn

**Input:**
- a retrieved document `C`: passages for a question, a news article, or structured data;
- an answer `A` written by an LLM, split into sentences `s_1 … s_K`.

**Output:** for every sentence `s_i`, one decision with three classes and their probabilities.

| Class | Definition | Letter |
| --- | --- | --- |
| supported | everything `s_i` states is said or directly implied by `C` | A |
| contradicted | some part of `s_i` conflicts with `C` | B |
| not_mentioned | `s_i` adds information that `C` neither contains nor contradicts | C |

**Precedence:** a sentence with both a conflicting and an unverifiable part is *contradicted*.

Only the document counts, not the real world. RAGTruth's `implicit_true` spans (true in reality, absent from the document) therefore stay *not_mentioned*.

**K is the number of scored sentences of the answer.** It is the variable on which the System One is compared with generative judges. The central figure of the thesis plots accuracy and latency against K on the same test answers. The speed advantage at high K only matters if accuracy holds at high K. So:
- training must contain long answers and late sentence positions;
- the test set must contain enough answers in every K band.

**Derived outputs:** computed from the three probabilities, never learned separately.
- Binary groundedness: `P(supported)`. This is what the LLM-AggreFact comparison uses.
- Strict rule: flag a sentence if `P(supported) < τ`.
- Lenient rule: flag a sentence if `P(contradicted) > τ`.

## 2. Requirements

| # | Requirement | Why |
| --- | --- | --- |
| R1 | Human labels for every training and test item | No label noise introduced by us or by an LLM; no own annotation needed |
| R2 | Multi-sentence answers with natural K, long answers included (K ≥ 14) | The task and the K experiment |
| R3 | Enough *contradicted* and *not_mentioned* examples | They are 3 % and 5 % of RAGTruth test sentences |
| R4 | Full prompt (document + answer) within 2,048 tokens | Memory on 16 GB; keeps 99 % of RAGTruth |
| R5 | Training licence allows fine-tuning | LLM-AggreFact forbids it (D18) |
| R6 | No document or sentence of any test set reaches dev or train | Earlier projects had leaks |
| R7 | Test sets frozen before training, with hashes | No silent changes after seeing results |
| R8 | As few sources as possible | One label definition, one format, fewer failure points (author's decision) |

## 3. Sources

| Dataset | Licence | Use | Why it is indispensable |
| --- | --- | --- | --- |
| **RAGTruth** (Niu et al., ACL 2024) | MIT | **only training source**; dev; test T1 | It *is* the task. It has real RAG answers from 6 LLMs (QA on MS MARCO, news summarisation, data-to-text on Yelp), natural K, and human span labels that separate *conflict* from *baseless* information |
| **LLM-AggreFact** (Tang et al., 2024) | CC BY-ND 4.0, gated: evaluation only | test T2 | External binary benchmark: numbers comparable with the published leaderboard |
| **VitaminC** (Schuster et al., NAACL 2021) | CC BY-SA 3.0 | test T3 | Independent check of contradicted vs not_mentioned with human labels of known reliability (Fleiss κ = 0.71), because RAGTruth reports no agreement for the hallucination type |

**Dropped:**
- ANLI and MiniCheck synthetic (both on disk);
- ANAH, Trivia++ and RAGBench (verified, not adopted);
- everything else that was screened. The reasons are in the wiki page `Datasets for GroundOne`.

**Accepted cost:** without pair-format training data such as MiniCheck, the LLM-AggreFact score will probably be lower on the sub-datasets far from RAG. The primary LLM-AggreFact number is therefore the RAG subset.

**RAGTruth reliability, stated in the thesis:**
- Two annotators per answer, with a third review on disagreement.
- Agreement is 91.8 % per answer and 78.8 % per span. No figure is reported for the type (conflict vs baseless).
- A 2026 re-annotation of the test split (RT4CHART) reports 1.68× more hallucinated answers. The original labels under-mark hallucinations, so T1 under-counts the minority classes.
- Mitigation: the three-way claim is also tested on T3, and both points go into the threats to validity.

## 4. Test sets (built first, then frozen)

### T1: RAGTruth test, the primary test (in-domain, multi-sentence, K curves)

**Content.** All quality-*good* answers of the official test split: 2,675 answers, 450 sources, 3 tasks. The 173 answers flagged `incorrect_refusal` or `truncated` are dropped.

**Scoring.** Every scored sentence of an answer is a decision. The numbered answer shown to the model is the full answer.

**Labels.**
- Sentence class from span overlap, with the precedence of §1.
- Spans crossing a sentence boundary label every sentence they touch.
- Answers with no span have all sentences *supported*.

**Segmentation.**
- One standard segmenter for test, dev, train and inference: **pysbd**. It is chosen a priori because it is rule-based and handles abbreviations and decimals.
- Agreement with LLM-AggreFact is only reported (C2), never optimised, so nothing is tuned on a test set.
- Measured with the current regex splitter: 76.5 % of its sentences are exactly an LLM-AggreFact claim. Of the rest, about half are fragments from splitting decimals ("rating of 4." + "0 stars"), and the others are sentences without checkable content.

**Sentences without checkable content** ("Sure!", "Elements:", "Based on the provided passages, … is:", refusal formulas):
- They stay in the numbered answer as context but are not decisions: no label, no score, `label: null` in the output JSON.
- They are detected by a short documented rule: no content word, a trailing colon introducing a list, a greeting, or a refusal formula.
- The same rule is applied everywhere.

**Reported metrics.**
- Three-way macro-F1 and per-class recall.
- Binary balanced accuracy at 0.5 and AUROC.
- Strict and lenient rule accuracy.
- All of the above per task and per K band (1–4, 5–8, 9–13, ≥ 14), and per answer (all K sentences correct).
- 95 % CIs by bootstrap over answers.
- Cells with fewer than 30 gold examples of a class (e.g. *contradicted* in QA: 31) are marked as indicative.
- **Baselines that do not read the document as a whole** (EDA, `Project/EDA/report/eda_report.md`), reported per task:
  - majority class;
  - word overlap between sentence and document (AUROC 0.74 for supported vs not on T1);
  - sentence-only n-gram classifier (three-way balanced accuracy 0.66 on Data2txt, chance elsewhere).
- Primary metrics are base-rate independent (balanced accuracy, macro recall, AUROC), because T1 has fewer hallucinations than train/dev in every task.

### T2: LLM-AggreFact test (external, binary)

- **Content.** 29,320 pairs, unchanged, K = 1.
- **Scoring.** `P(supported)` at threshold 0.5. Report the 11-way macro balanced accuracy and the RAG subset (RAGTruth, LFQA, ClaimVerify, ExpertQA) as the primary number.
- **Long documents.** Over the cap, chunk the document and take the maximum over chunks (as MiniCheck does), and report how many items needed it.
- **Overlap with T1.** Its RAGTruth part is the same data as T1, so it is reported separately and not counted twice.

### T3: VitaminC test (three-way, balanced by sampling)

- **Content.** Real (human-written) part of the official test split: 34,481 pairs (17,306 / 9,907 / 7,268). Sampled stratified to **1,000 per class = 3,000 pairs**, with a fixed seed.
- **Mapping.** SUPPORTS → supported, REFUTES → contradicted, NOT ENOUGH INFO → not_mentioned.
- **Purpose.** Contradicted vs not_mentioned with clean, balanced labels.
- **Caveats.**
  - The evidence is a single Wikipedia sentence (K = 1) and about half the claims are numerical.
  - GroundOne is not trained on it, so T3 measures transfer from RAG training data.
  - It supports the three-way claim, not the K claim.

### Reliability checks, run before freezing (no manual annotation)

| Check | Pass criterion | If it fails |
| --- | --- | --- |
| C1 Label provenance | every test label comes from the human annotators of the published dataset | drop the source |
| C2 Segmentation (T1) | ≥ 90 % of LLM-AggreFact RAGTruth claims found exactly among our scored sentences, and ≤ 10 % of our scored sentences absent from LLM-AggreFact (reported, not optimised) | fix rule-level bugs only (e.g. decimals) and document them; also report T1 on the matched subset |
| C3 Label derivation (T1) | our binary label agrees ≥ 97 % with LLM-AggreFact's independent label on matched sentences (earlier: 98.6 %); disagreements listed in the data card | inspect the rule, fix, re-run |
| C4 Coverage | counts per class × task × K band tabulated; cells < 30 flagged | report as indicative |
| C5 Reference baselines | MiniCheck-RoBERTa on T2 within ±1.5 points of its published 73.5; majority and random baselines for T1 and T3 | debug the evaluation code before any GroundOne result |
| C6 Freeze | test files + manifest with SHA-256 committed; evaluation reads only through the manifest; any later change needs a decision-log entry | – |

**When manual annotation would become strictly necessary:** only if C2 or C3 fail and cannot be fixed by rule. In that case a small audit (about 150 T1 sentences) is proposed to the author first.

## 5. Development set

- **Use.** Checkpoint selection and calibration only, never training. Same format as T1.
- **Construction.** 10 % of RAGTruth train sources, held out by `source_id`: about 1,500 answers with all their sentences.
- **Selection metric** (fixed before training): three-way macro-F1 on dev.
- **Calibration.** Fitted on dev: temperature plus bias.

## 6. Training set

**Storage.** One record per answer, independent of the readout design of §8:
```
{id, source, group, task, doc, sentences: [...], labels: [supported|contradicted|not_mentioned|null], meta: {K, model, ...}}
```

**Content.** All remaining RAGTruth train answers (quality *good*, within the 2,048-token cap), full answers, all sentences.
- **Class balance.** About 89 % of labels are *supported*. Balance by loss weighting, or by masking part of the *supported* sentences in the loss, never by cutting answers. The model always sees whole answers.
- **K coverage.** 1,165 training answers have K ≥ 14. Weight them up if the dev set shows a drop at high K.

**Checks.**
- Leakage (R6) against T1–T3, including LLM-AggreFact documents and claims.
- Claim-only shortcut baseline (sees only the sentence) on train and test, to expose label cues.

### Estimated size of the final dataset
Measured on the raw data with the regex splitter, Qwen2.5 tokens, 10 % dev by source. pysbd and the content rule will lower the sentence counts by an estimated 10–20 %, mostly *supported* sentences.

| Split | Entries (answers / pairs) | Sentence labels | contradicted | not_mentioned | Tokens |
| --- | --- | --- | --- | --- | --- |
| train | **13,311 answers** | 104,572 (≈ 85–95K after filtering) | ~4,200 | ~7,200 | 10.7 M |
| dev | 1,486 answers | 11,585 | 445 | 804 | 1.0 M |
| T1 | 2,675 answers | 19,902 (≈ 16K) | 602 | 999 | 2.0 M |
| T2 | 29,320 pairs | 29,320 | binary | binary | – |
| T3 | 3,000 pairs | 3,000 | 1,000 | 1,000 | – |

## 7. Build order and acceptance (target: frozen data by Thu 2026-10-09)

1. **Segmenter and content rule.** Install pysbd and implement the rule. *Accept:* C2 passes.
2. **T1 and T2.** Build, then run C1–C5. *Accept:* all pass; data card section written; figures (class × task × K, token lengths) in `Project/figures/dataset/`.
3. **T3.** Download VitaminC (HF `tals/vitaminc`), sample the real test split, run C1, C4 and C5.
4. **Freeze.** C6: manifest with hashes committed.
5. **Dev and train.** Build from RAGTruth train by `source_id`, then run the leakage and shortcut checks. Write the data card (composition, origin, licence, rationale): it becomes thesis Ch. 4.

**Code.**
- `groundone data build`: `data/build.py` (all sources and checks C2–C5) plus `data/segment.py` (pysbd and the content rule, shared with inference).
- `groundone data check`: `data/leakage.py`.
- `groundone data shortcut`: `data/shortcut.py`.
- `groundone data freeze`: writes `tests_frozen.json`.
- `groundone figures dataset`.

Output goes to `Project/data/processed/groundone/`.

**Results of the first build (2026-10-06).**
- Build time: 45 s.
- C2: 96.3 % / 8.5 %. C3: 98.75 %.
- Leakage: PASS, after excluding one CNN article shared with LLM-AggreFact.
- Sentence-only shortcut: 0.57 on T1. It is driven entirely by Data2txt (0.66); QA and Summary are at chance.
- Train: 13,203 answers, 90,795 decisions, 10.9 M tokens.

## 8. Readout design: (b) is the default, (a) the fallback (author's decision, 2026-10-06)

The dataset is stored per answer, so it serves both designs.

**(b) Default: K readouts in one pass.**
- A marker (" Verdict:") follows every scored sentence, and the letter logits A/B/C are read at the marker in the same forward pass.
- Training: one row per answer carries all its K labels. The loss is the class-weighted cross-entropy at all markers, with each class weighted to contribute equally (supported ≈ 0.38, contradicted ≈ 6.4, not_mentioned ≈ 4.1).
- Inference: one pass for all K decisions, with the output head applied only at the marker positions.
- Costs: the verdict on sentence *i* sees only the document and sentences 1..i, and the untrained model has no meaning for the marker (the untrained baseline B1 stays in format a).
- Prompt version `groundone-v2-marked`.
- Code: `prompts.encode_marked`, `readout.py`, `Backend.score_positions`, `train.py --design b`, `groundone test`.

**(a) Fallback: one question per sentence.**
- The prefix is read once, then K short question suffixes run in one batch. Already implemented.
- Training rows: `groundone data rows` (one row per sentence, class-balanced sample).
- Used only if (b) fails the validation criteria below.

**Validation run (night 2026-10-06/07).** The 0.5B is trained on 9,000 random training answers (about 62K decisions) in design (b), then evaluated on T1, T3 and T2. The dataset is judged useful if all of these hold:
- three-way balanced accuracy on T1 > 0.57 (the sentence-only baseline);
- the same metric clearly above 0.36 on QA and Summary;
- AUROC supported vs not > 0.74 (word overlap);
- no collapse below chance for K ≥ 14;
- all three classes predicted.

## 9. Out of scope
- LLM-AggreFact for anything but evaluation.
- Our own annotation, unless C2 or C3 make it strictly necessary.
- Languages other than English.
- Any training source other than RAGTruth.
