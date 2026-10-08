# GroundOne dataset: data card

Built by `groundone data build` on 2026-10-06, following `Project/docs/dataset_plan.md` v2.0.
- Numbers: `build_report.json`, `leakage_report.json`, `shortcut_report.json`.
- Hashes: `manifest.json`; `tests_frozen.json` once the tests are frozen.
- Figures: `Project/outputs/figures/dataset/`.

## Task
For each sentence of an LLM answer, given the retrieved document, one decision among three classes:
- *supported*: everything the sentence states is said or directly implied by the document;
- *contradicted*: some part conflicts with the document;
- *not_mentioned*: it adds information the document neither contains nor contradicts.

A sentence with both a conflicting and an unverifiable part is *contradicted*.

**K** is the number of scored sentences of the answer. Sentences without checkable content (greetings, list headings ending with a colon, citation-only lines, refusal formulas, fewer than two words) stay in the answer as context with label `null`.

## Contents

| File | Role | Source | Records | Decisions | supported | contradicted | not_mentioned |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `train.jsonl` | training | RAGTruth train split | 13,203 answers | 90,795 | 79,898 | 4,039 | 6,858 |
| `dev.jsonl` | selection, calibration | RAGTruth train split, 10 % of sources | 1,468 answers | 9,996 | 8,827 | 410 | 759 |
| `test_ragtruth.jsonl` | **T1** | RAGTruth official test split | 2,647 answers | 17,284 | 15,745 | 584 | 955 |
| `test_aggrefact.jsonl` | **T2** (evaluation only) | LLM-AggreFact test | 29,320 pairs | 29,320 | 22,832 | 6,488 *unsupported* (binary) | |
| `test_vitaminc.jsonl` | **T3** | VitaminC test, real revisions | 3,000 pairs | 3,000 | 1,000 | 1,000 | 1,000 |


**RAGTruth answers.**
- Mean K: 6.88 in train and 6.53 in T1; maximum 28.
- Answers with K ≥ 14: 573 in train and 106 in T1.
- Train is 10.88 M tokens (document + answer, Qwen2.5 tokenizer).

**T1 answers by K band:**
| K band | Answers |
| --- | --- |
| 1–4 | 756 |
| 5–8 | 1,288 |
| 9–13 | 497 |
| ≥ 14 | 106 |

**T1 by task:** QA 870, Summary 877, Data2txt 900 answers.

**Cells with fewer than 30 minority-class sentences** (results there are marked as indicative):
- *contradicted* in every QA band, Data2txt 1–4 and ≥ 14, and Summary 9–13;
- *not_mentioned* in Data2txt 1–4 and Summary 9–13.

## Sources and licences
- **RAGTruth** (Niu et al., ACL 2024; MIT).
  - Answers of 6 LLMs to QA (MS MARCO), news summarisation (CNN/DM and recent news) and data-to-text (Yelp) prompts.
  - Character spans annotated by two trained annotators, with a third review on disagreement. Agreement: 91.8 % per answer, 78.8 % per span; none is reported for the hallucination type.
- **LLM-AggreFact** (Tang et al., 2024; CC BY-ND 4.0, gated).
  - 11 human-labelled fact-checking datasets, binary labels.
  - Evaluation only: never used for training, calibration or selection.
- **VitaminC** (Schuster et al., NAACL 2021; CC BY-SA 3.0).
  - Claims written by 70 trained annotators against real Wikipedia revisions; Fleiss κ = 0.71.
  - Real test split: 17,306 / 9,907 / 7,268 (SUPPORTS / REFUTES / NEI). Sampled to 1,000 per class with seed 1234.

## Construction
1. **Segmentation** (`groundone/data/segment.py`, also used at inference):
   - line breaks first, then pysbd within each line;
   - leading list markers ("3. ", "* ") are removed;
   - the checkable-content rule is written a priori. It was adjusted twice, for formatting only:
     - list markers and citation-only lines, after check C2 on T1 showed them as the main source of mismatches with LLM-AggreFact;
     - conversational formulas seen in the training data (e.g. "Sure, I can help you with that!").
   - No label was changed.
2. **RAGTruth labels.** A scored sentence is *contradicted* if it overlaps a Conflict span, *not_mentioned* if it overlaps only Baseless spans, and *supported* otherwise. `implicit_true` spans stay *not_mentioned*.
   - 27 of 14,226 spans (0.19 %) touch no scored sentence.
3. **Exclusions** (counts in `build_report.json` → `ragtruth_dropped`):
   - answers flagged `incorrect_refusal` or `truncated`;
   - answers with no scored sentence;
   - answers over 2,048 tokens: 23 in T1, 7 in dev, 152 in train;
   - training and dev answers whose document is in LLM-AggreFact test: one CNN article, 6 answers.
4. **Splits.**
   - RAGTruth test is T1.
   - RAGTruth train sources are shuffled with seed 1234: 10 % go to dev and the rest to train, by `source_id`.
5. **VitaminC.** Detokenised ("UK ." → "UK."). Some evidence texts contain artefacts of the source (e.g. "doesn'thave").

## Reliability checks (before freezing)
| Check | Result |
| --- | --- |
| C1 label provenance | all test labels are human annotations of the published datasets |
| C2 segmentation vs LLM-AggreFact's own RAGTruth claims | **pass**: 96.3 % of its claims are among our scored sentences; 8.5 % of our scored sentences are absent from it (mostly sentences its undocumented "check-worthiness" filter removed, or different boundaries) |
| C3 label derivation vs LLM-AggreFact's independent labels | **pass**: 98.75 % agreement on 15,492 matched sentences; all 193 disagreements are "ours not supported / theirs supported" |
| C4 coverage | table above; small cells flagged |
| C5 reference baselines | MiniCheck-RoBERTa on the unchanged T2: 74.0 (published 73.5). Majority-class and random three-way balanced accuracy: 0.333 |
| Leakage | **pass**: no group, document or (document, sentence) pair of dev or train appears in a test set. 788 train and 82 dev sentence strings also occur in tests with different documents (template sentences such as "The business has a rating of 4.0 stars.") |

## Known limitations
- **Sentence-only shortcut.** A bag-of-words classifier that sees only the sentence reaches a three-way balanced accuracy of:
  - 0.545 on dev and 0.570 on T1 (chance 0.333);
  - **0.656 on Data2txt**, but 0.358 on QA and 0.353 on Summary;
  - 0.331 on T3, where the contrastive design removes the cue.

  In data-to-text, some sentence types (opening hours, amenities, ratings) are often hallucinated, so part of that task can be guessed without reading the document. GroundOne must be compared with this baseline per task.
- **Word overlap.** The share of a sentence's content words found in the document alone gives AUROC 0.74 (supported vs not) on T1 and 0.70 on T3 (EDA, `Project/experiments/eda/report/eda_report.md`).
- **T1 is cleaner than train.** It has a lower share of contradicted and not-mentioned sentences in every task and for every generator.
- **Contradicted ≈ evident contradictions.** 85 % of contradicted training sentences come from *Evident Conflict* spans only.
- **Imbalance.** RAGTruth is about 89 % *supported*; *contradicted* is 3–4 %, mostly from Data2txt.
- **Label completeness.** A 2026 re-annotation of the RAGTruth test split (RT4CHART) reports 1.68× more hallucinated answers than the original labels. T1 likely under-counts the minority classes. The three-way claim is also tested on T3.
- **T3 is out of domain.** Single Wikipedia sentences, K = 1, about half numerical. GroundOne is not trained on it.
- **Pre-training contamination** of Qwen2.5 with these public datasets cannot be excluded.
