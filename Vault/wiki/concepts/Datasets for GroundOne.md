---
type: concept
tags: [concept, synthesis, dataset, groundone, data-plan, leakage, licence]
---
# Datasets for GroundOne

Synthesis of where [[GroundOne]]'s data comes from, how the datasets differ, and which dataset serves which experiment. Main evidence: [[GroundOne 2026 - EDA report]] (Phase 1a, 2026-10-05), plus the dataset cards and papers linked below. The source of truth for the final plan remains `Project/docs/implementation_plan.md`.

## Where each dataset comes from
- **[[ANLI]]**: adversarial NLI, written by crowdworkers to fool BERT/RoBERTa over Wikipedia (and, in R3, other genres) premises ([[Nie 2020 - Adversarial NLI]], [[Dataset card - ANLI]]).
- **[[RAGTruth]]**: responses of 6 LLMs (GPT-3.5/4, Llama-2 7/13/70B, Mistral-7B) to RAG prompts, with span-level human labels ([[Niu 2024 - RAGTruth]], [[Dataset card - RAGTruth README]]). Its contexts come from three upstream corpora:
  - **QA**: MS MARCO questions (real Bing queries) with 3 retrieved web passages ([[Nguyen 2016 - MS MARCO]]).
  - **Summary**: CNN/Daily Mail articles ([[Hermann 2015 - Teaching Machines to Read and Comprehend]], non-anonymised as in [[See 2017 - Get To The Point]]) plus recent news.
  - **Data2txt**: Yelp business records and reviews as JSON ([[Yelp Open Dataset]]).
- **[[MiniCheck Synthetic Data]]** (C2D/D2C): GPT-4-generated claim/document pairs from Wikipedia claims and Google News articles ([[Tang 2024 - MiniCheck]], [[Dataset card - MiniCheck C2D-D2C]]).
- **[[LLM-AggreFact]]**: aggregation of 11 human-annotated fact-checking datasets, including a converted RAGTruth ([[Dataset card - LLM-AggreFact]], [[LLM-AggreFact Sub-datasets]]).

## How they differ
| | ANLI | RAGTruth | MiniCheck synthetic | LLM-AggreFact |
|---|---|---|---|---|
| Size | 162,865 / 3,200 / 3,200 pairs | 17,790 responses (15,090 train / 2,700 test); 138,239 sentences | 14,395 pairs | dev 30,420 / test 29,320 claims |
| Text producer | crowdworkers (adversarial) | 6 LLMs in RAG | GPT-4 | mostly LLMs (WiCE: humans) |
| Labels | human, 3-way | human character spans (4 types) → derived sentence labels | binary, from construction | human, binary (partial = unsupported) |
| Label balance | train neutral-heavy; dev/test 1/3 each | ~90 % supported sentences | 58 % (C2D) / 35 % (D2C) supported | varies 23–92 % supported per sub-dataset |
| Median document (Qwen tokens) | 73 | QA 308, Summary 552, Data2txt ~685 | 186–188 | 530 (test; p90 up to 4.7K) |
| Claims per document | ~16 hypotheses per premise | median K 5–9 sentences per answer | 2.34 | ~1 except RAGTruth part |
| Licence / use | CC BY-NC 4.0 | not stated | MIT | CC BY-ND 4.0; **evaluation only** |

Label-scheme note: only ANLI has human three-way labels; RAGTruth's three-way sentence classes (supported / not mentioned / contradicted) are our derivation from span types (Baseless → not mentioned, Conflict → contradicted).

## Final choice (2026-10-06)
The task was redefined: one three-way decision per answer sentence, with K = the number of sentences (plan decision D20). The dataset was then cut to the strict minimum (D21). The source of truth is `Project/docs/dataset_plan.md`.

| Dataset | Use | Why |
|---|---|---|
| **[[RAGTruth]]** | **only training source**; dev (10 % of train sources, by `source_id`); test **T1** | It *is* the task: real RAG answers with natural K and span labels that separate conflict from baseless information |
| **[[LLM-AggreFact]]** | test **T2** only (evaluation only by licence) | External, leaderboard-comparable binary benchmark |
| **[[VitaminC]]** | test **T3** only (real test split, stratified sample) | Independent, reliable check of contradicted vs not mentioned (κ = 0.71), since RAGTruth reports no agreement on the hallucination type |

**EDA of the final dataset:** [[GroundOne 2026 - EDA report (dataset)]]. Key consequences:
- word overlap alone gives AUROC 0.74 on T1;
- the sentence-only cue is limited to Data2txt;
- T1 is cleaner than train;
- contradicted is mostly evident contradictions.

**Dropped:**
- [[ANLI]]: adversarial, short premises, far from RAG.
- [[MiniCheck Synthetic Data]]: binary only. Accepted cost: probably a lower LLM-AggreFact score outside the RAG sub-datasets. *Measured (2026-10-10):* the 3B reaches 74.8 macro, on par with MiniCheck-RoBERTa (74.0, difference not significant); the 0.5B reaches 70.1 and is 7–9 points below the encoder on the non-RAG sub-datasets ([[GroundOne Results]]).
- Verified but not adopted: ANAH, Trivia++, RAGBench. Rejected outright: HaluBench (contains RAGTruth test answers), ANAH-v2 (model-generated labels).

**Actual sizes (built and frozen 2026-10-07; data card `Project/data/processed/groundone/DATACARD.md`):**

| Split | Answers / pairs | Decisions | contradicted | not mentioned |
|---|---|---|---|---|
| train | 13,203 answers | 90,795 | 4,039 | 6,858 |
| dev | 1,468 answers | 9,996 | 410 | 759 |
| T1 test | 2,647 answers | 17,284 | 584 | 955 |
| T2 test | 29,320 pairs | 29,320 (binary: 6,488 unsupported) | – | – |
| T3 test | 3,000 pairs | 3,000 | 1,000 | 1,000 |

Checks: no leakage by group (RAGTruth source, document hash); label agreement with LLM-AggreFact's independent RAGTruth labels 98.75 % on the final segmentation; segmentation with pysbd + checkable-content rule (C2 passes at 96.3 %).

*Superseded pre-build estimate* (regex splitter; the final segmenter will be pysbd plus a rule that excludes sentences without checkable content, expected to remove about 10–20 % of sentences, mostly *supported*):

| Split | Answers | Sentence labels | contradicted | not mentioned | Tokens |
|---|---|---|---|---|---|
| train | ~13,300 | ~105K (≈ 85–95K after filtering) | ~4,200 | ~7,200 | ~10.7 M |
| dev | ~1,500 | ~11.6K | ~450 | ~800 | ~1.0 M |
| T1 test | 2,675 | 19.9K (≈ 16K after filtering) | 602 | 999 | ~2.0 M |
| T2 test | – | 29,320 pairs | – | – | – |
| T3 test | – | ~3,000 pairs | ~1,000 | ~1,000 | – |

## Earlier analysis (EDA, 2026-10-05): which dataset could serve which experiment
Kept for reference. It was written for the earlier four-question design, and the final choice above supersedes it.

From the EDA report §2. ✅ suitable · ⚠️ usable with care · ❌ not suitable.

| Experiment | ANLI | RAGTruth | MiniCheck synthetic | LLM-AggreFact |
|---|---|---|---|---|
| **X1** Binary groundedness, training (RQ1) | ✅ the MiniCheck "hard ANLI" subset; filter premises seen in dev/test; check the train-only negation shortcut | ✅ in-domain, sentence level; ~90 % supported, so rebalance; drop refusals/truncated | ✅ core of the MiniCheck recipe (14,395 pairs); makes the comparison with MiniCheck data-matched | ❌ evaluation only (its dev RAGTruth part *is* RAGTruth train) |
| **X2** Binary evaluation comparable with published results (RQ1, plain task of RQ5) | ⚠️ dev/test as a secondary, non-RAG check | ✅ test split, but it **is** the LLM-AggreFact-RAGTruth test; report once, with LLM-AggreFact labels | ❌ training data | ✅ **primary benchmark** (test, 11 sub-datasets, macro balanced accuracy, threshold 0.5); ClaimVerify/WiCE need the 2,048 cap or chunking, stated |
| **X3** K decisions over one shared context (RQ2) | ⚠️ synthetic K from several hypotheses per premise, but contexts ~75 tokens | ✅ **the natural set**: real answers, median K 5–9, contexts 300–700 tokens | ❌ ~2 claims per document | ⚠️ only its RAGTruth part has several claims per document (same data as RAGTruth) |
| **X4** Three-way question (RQ5) | ✅ **primary**: human three-way labels, balanced dev/test | ⚠️ train usable (8,077 not mentioned, 4,658 contradicted, mostly Data2txt); test too skewed (602 contradicted, almost none in QA); report per task | ❌ binary only | ❌ binary only |
| **X5** Rules in the prompt, strict vs lenient (RQ5) | ✅ **primary**: rule labels derived from three-way labels; rules differ on ~1/3 of items | ⚠️ rules differ only on not-mentioned sentences (~4–7 %), mainly Data2txt; `implicit_true` (2,012 sentences) allows a third rule ("true world knowledge is acceptable") | ❌ | ❌ |
| **X6** Calibration: dev for temperature, test for ECE (RQ3) | ✅ dev for temperature (three-way and rules), test for evaluation | ✅ dev carved from train **by `source_id`** | ⚠️ could give a dev slice, but synthetic | ❌ evaluation only by licence: no temperature or threshold fitted on it (D18) |
| **X7** Demo realism (local RAG) | ❌ single short paragraphs | ✅ **QA** (MS MARCO question, 3 passages, ~300 tokens) closest to the demo; Summary acceptable; Data2txt (JSON) unlike the demo | ❌ | ❌ |

## Hard rules
1. **LLM-AggreFact-RAGTruth dev = RAGTruth train.** Measured: 14,046 of its 15,340 dev claims match RAGTruth *train* sentences. Never use the RAGTruth part of LLM-AggreFact dev for calibration, threshold or model selection when training on RAGTruth train.
2. **RAGTruth test = LLM-AggreFact-RAGTruth test.** Measured: 14,942 of 16,371 test claims match RAGTruth *test* sentences. Report it **once**, using LLM-AggreFact's labels for binary results (our span-derived labels agree on 98.6 % of 29,191 matched sentences; all 419 disagreements are "ours unsupported, theirs supported").
3. **2,048-token cap** on the full prompt (context + answer): keeps 99 % of RAGTruth (1,024 would drop ~22 %). Affects 2.4 % of LLM-AggreFact test documents. Log every excluded or chunked item and state the handling in the thesis.
4. **ANLI premise filtering**: exclude from training every premise that also appears in ANLI dev/test (98.6 % / 98.9 % of them do). 93,480 train pairs remain.
5. **LLM-AggreFact licence: evaluation only.** The gated card states the data "should not be used in pretraining or fine-tuning any NLP models" (licence CC BY-ND 4.0). No LLM-AggreFact example, dev included, enters training.
6. **Splits**: RAGTruth dev carved from train **by `source_id`** (RAGTruth train/test already share no source); ANLI dev for temperature/threshold, ANLI test held out; LLM-AggreFact test held out.
7. **Hygiene**: drop the 173 RAGTruth responses flagged `incorrect_refusal` / `truncated`; extend the leakage check to LLM-AggreFact test claims; run a claim-only baseline on ANLI (negation shortcut present in train, reversed in dev/test).
8. **Report RAGTruth per task** (QA / Summary / Data2txt): they differ in format (text vs JSON), hallucination rate (test: 18 % / 23 % / 64 % of answers) and contradiction rate.

## Proposed training mix (EDA recommendation, superseded by the final choice above)
- MiniCheck synthetic, all 14,395 pairs (binary).
- ANLI ~21K hard subset, premises not in dev/test, three-way labels kept (feeds binary, three-way and rules).
- RAGTruth train, sentence level, quality = good, rebalanced (all not-mentioned and contradicted sentences plus an equal number of supported), each answer used as a shared context to match the K-question inference format.
- Budget: ≈35K examples for 0.5B (≈3–4 h), ~10K subset for 3B (one night).

## Links
[[GroundOne]], [[GroundOne 2026 - EDA report]], [[ANLI]], [[RAGTruth]], [[MiniCheck Synthetic Data]], [[LLM-AggreFact]], [[LLM-AggreFact Sub-datasets]], [[VitaminC]], [[Schuster 2021 - VitaminC]], [[Natural Language Inference]], [[MiniCheck]], [[Calibration]], [[Selective Prediction]], [[Nguyen 2016 - MS MARCO]], [[Hermann 2015 - Teaching Machines to Read and Comprehend]], [[See 2017 - Get To The Point]], [[Yelp Open Dataset]]

## Update 2026-10-10
- The rules that referred to [[ANLI]] (premise filtering, ANLI dev for the temperature, the ANLI claim-only baseline) no longer apply: ANLI is not used. Calibration and the served threshold are fitted on the RAGTruth dev split; [[LLM-AggreFact]] is never used for fitting (D18).
- Results on these splits: [[GroundOne Results]]. Surface cues measured on the final data: word overlap AUROC 0.737 (T1) / 0.698 (T3); a sentence-only classifier reaches 0.570 three-way on T1.
