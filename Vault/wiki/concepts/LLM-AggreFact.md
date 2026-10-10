---
type: concept
tags: [concept, benchmark, fact-checking, grounding, evaluation, sentence-level]
---
# LLM-AggreFact

**LLM-AggreFact** is a benchmark for **fact-checking LLM output against grounding documents**. It was introduced with [[MiniCheck]] ([[Tang 2024 - MiniCheck]], EMNLP 2024) and is maintained as a leaderboard at llm-aggrefact.github.io ([[Tang 2024 - LLM-AggreFact Leaderboard]]). It is GroundOne's main sentence-level benchmark.

## Composition
- **Paper version**: 10 datasets. **Leaderboard version**: 11 datasets, adding **RAGTruth** as a column.
- Every dataset contains **human-annotated (document, claim, label)** tuples. The claims are mostly LLM-generated, without injected errors; WiCE uses human-written Wikipedia claims. Synthetic-error datasets were **excluded** (HaluEval, SummEdits), and FActScore was excluded because of a mismatch between the evidence annotators used and the evidence models retrieved (App. C.3).

| Setting | Dataset | Content |
|---|---|---|
| Fixed-doc | AggreFact CNN / XSum (SOTA subset) | news summaries from fine-tuned summarizers |
| Fixed-doc | TofuEval MediaS / MeetB | topic-focused dialogue summaries by LLMs |
| Retrieve-then-generate | ClaimVerify, LFQA, ExpertQA | generative search / long-form QA sentences |
| Post-hoc grounding | REVEAL, FactCheck-GPT, ExpertQA | reasoning-chain sentences; decontextualized atomic facts |
| Human claims | WiCE | Wikipedia claims vs cited pages |
| (leaderboard) | RAGTruth | see [[RAGTruth]] |

## Splits and sizes (paper version, App. C, Table 11)
| Dataset | Dev | Test | Avg doc len* | % unsupported (test) |
|---|---|---|---|---|
| AggreFact-CNN | 459 | 558 | ~560 | 10% |
| AggreFact-XSum | 777 | 558 | ~370 | 49% |
| TofuEval-MediaS | 1,800 | 726 | ~950 | 24% |
| TofuEval-MeetB | 1,607 | 772 | ~920 | 19% |
| WiCE | 349 | 358 | ~1,650 | 69% |
| REVEAL | 1,656 | 1,710 | ~100 | 77% |
| ClaimVerify | 1,093 | 1,088 | ~1,850 | 27% |
| FactCheck-GPT | 1,537 | 1,566 | 100 | 76% |
| ExpertQA | 3,773 | 3,702 | ~500 | 20% |
| LFQA | 2,029 | 1,911 | ~380 | 41% |
| **Total** | **~15.1K** | **~12.9K** ("13K", Table 3) | | |

*Average document length as given in Table 11. The unit is not restated there; Table 1 of the same paper uses NLTK word counts.

- **Yes, there is a dev set.** AggreFact, TofuEval, WiCE and ClaimVerify keep their original validation and test splits. REVEAL, FactCheck-GPT, ExpertQA and LFQA were split 50/50, with no query shared between dev and test (§4.1).
- The sizes of the RAGTruth subset on the leaderboard are **not stated** in the available sources.
- The data is **test-only for training purposes**: the authors say it is "largely test-only" (§3). Do not train GroundOne on it. *(Superseded by D18: GroundOne uses no split of LLM-AggreFact for threshold tuning, calibration or model selection; see the licence note below.)*
- **Label unification (App. C.2)**: the binary labels of AggreFact, TofuEval and ClaimVerify are kept as they are. Elsewhere, only *supported / fully attributable / completely support / complete* map to supported, and **partial support is mapped to unsupported**.

## Protocol
- **Metric**: balanced accuracy per dataset. The leaderboard "Average" is the unweighted mean over datasets.
- **Threshold**: **no per-dataset threshold tuning**. A fixed midpoint (0.5) is used, deliberately, to measure zero-shot deployability (§4.1). Threshold-tuned results are in App. B.1 (Table 7) and are qualitatively similar.
- **LLM judges**: zero-shot with a prompt adapted from Luo et al. (2023), temperature 0 (App. E.1).
- **Significance**: paired bootstrap, 1,000 runs, p < 0.05 (Table 2 caption).

## Known numbers
See [[Groundedness Verification#Reference numbers (LLM-AggreFact average BAcc)]] and [[Tang 2024 - LLM-AggreFact Leaderboard]]. Highlights:
- Top entry is Bespoke-MiniCheck-7B at 77.4.
- MiniCheck-FT5 scores 75.0 on the leaderboard and 74.7 in the paper.
- HHEM-2.1-open 71.8, AlignScore 70.5.
- **Qwen2.5-0.5B-Instruct 64.2** and Qwen2.5-7B-Instruct 72.8.
- Per-dataset ceiling: **ExpertQA is about 50–61** for every model.

## Licence
Not stated in the paper or the leaderboard capture. **Update**: the Hugging Face card states CC BY-ND 4.0 and an evaluation-only condition; see "Access condition and licence (dataset card)" below. The paper says use is "for research purposes only, consistent with [the datasets'] intended use" (App. C.4). Each constituent dataset keeps its own licence.

## Relevance to GroundOne
- It is the same task framing as GroundOne: per-sentence, binary, document-grounded.
- **Headline protocol**: t = 0.5 on P(supported), BAcc per dataset plus the macro average. Secondary results: dev-tuned thresholds, AUROC and ECE.
- The documents are long: ClaimVerify and WiCE average about 1.6–1.9K length units (likely words, so probably more than 2K tokens). Check that Qwen2.5 inputs fit without truncation, or chunk and take the maximum as MiniCheck does.

## Access condition and licence (dataset card)
From [[Dataset card - LLM-AggreFact]] (gated dataset):
- **"This resource is permitted for use as an evaluation benchmark. Data in the benchmark should not be used in pretraining or fine-tuning any NLP models."** Access requires accepting this condition.
- Licence field: **CC BY-ND 4.0**.
- Released sizes: **dev 30,420, test 29,320**. Fields: `dataset`, `doc`, `claim`, `label`, `contamination_identifier` (64-character string for contamination detection).
- For GroundOne: **evaluation only, no training or fine-tuning on any split.** Nothing is fitted on it either: no temperature, threshold or model selection on any split (plan decision D18, 2026-10-05); dev is at most a sanity check.

## The 11 sub-datasets (GroundOne Phase 1a EDA)
Test split, measured by [[GroundOne 2026 - EDA report]] in Qwen2.5 tokens (the paper table above uses a different length unit). Details per dataset: [[LLM-AggreFact Sub-datasets]].

| Sub-dataset | n (test) | supported | doc tokens p50 | doc tokens p90 | claim tokens p50 |
|---|---|---|---|---|---|
| AggreFact-CNN | 558 | 89.8 % | 560 | 1,059 | 67 |
| AggreFact-XSum | 558 | 51.1 % | 359 | 729 | 27 |
| ClaimVerify | 1,088 | 72.5 % | 1,368 | 4,743 | 23 |
| ExpertQA | 3,702 | 80.3 % | 185 | 1,138 | 30 |
| FactCheck-GPT | 1,566 | 24.0 % | 117 | 169 | 14 |
| LFQA | 1,911 | 58.7 % | 401 | 547 | 25 |
| RAGTruth | 16,371 | 92.2 % | 606 | 1,110 | 23 |
| REVEAL | 1,710 | 23.4 % | 112 | 223 | 13 |
| TofuEval-MediaS | 726 | 76.3 % | 1,025 | 1,178 | 22 |
| TofuEval-MeetB | 772 | 80.6 % | 981 | 1,264 | 23 |
| WiCE | 358 | 31.0 % | 1,286 | 3,658 | 31.5 |

- The counts sum to the card's 29,320 test rows. Without RAGTruth, test has 12,949 and dev 15,080 rows, consistent with the paper's ~12.9K / ~15.1K (derived by subtraction).
- RAGTruth is **56 % of the test rows** but weighs 1/11 in the macro-averaged balanced accuracy.
- Overall test document median 530 tokens; **2.4 % of test documents exceed 2,048 tokens** (mostly ClaimVerify and WiCE). This answers the length question in "Relevance to GroundOne": a 2,048 cap or chunking is needed only for a small tail, and the handling must be stated.
- No overlap with [[MiniCheck Synthetic Data]] (documents or claims) or [[ANLI]] premises.

## RAGTruth-subset overlap (GroundOne Phase 1a EDA)
- The RAGTruth sub-dataset has 31,711 claims (dev 15,340, test 16,371). By sentence matching: **dev comes from RAGTruth train** (14,046 matched) and **test from RAGTruth test** (14,942 matched); 359 ambiguous, 2,364 unmatched. The card confirms a random sample of RAGTruth train was put in the validation set.
- Consequences: training on RAGTruth train is safe for LLM-AggreFact **test**; the RAGTruth part of LLM-AggreFact **dev** must not be used for calibration or model selection; RAGTruth test and LLM-AggreFact-RAGTruth test are the same data and are reported once.
- Labels agree with our span-derived RAGTruth sentence labels on 98.6 % of 29,191 matched sentences. See [[RAGTruth]] and [[Datasets for GroundOne]].

## Links
[[MiniCheck]], [[HHEM]], [[AlignScore]], [[RAGTruth]], [[Groundedness Verification]], [[Hallucination Detection]], [[LLM-as-a-Judge]], [[Qwen2.5]], [[GroundOne]], [[LLM-AggreFact Sub-datasets]], [[Dataset card - LLM-AggreFact]], [[Datasets for GroundOne]], [[GroundOne 2026 - EDA report]]

## GroundOne results on T2 (2026-10-10)
Macro balanced accuracy over the 11 sub-datasets at threshold 0.5 / RAG subset: GroundOne 0.5B 70.1 / 74.4 (run 2: 71.5 / 74.3), GroundOne 3B **74.8 / 76.9**, [[MiniCheck]]-RoBERTa 74.0 / 74.6 (our run reproduces its published score), [[Rizzo-Flow]] 4B 61.5 on its 1,093-item subsample; published zero-shot Qwen2.5-7B 72.8. The 3B vs MiniCheck macro difference is **not significant** (+0.8 [−0.5, +2.1]); on the RAG subset it is (+2.4 [+1.4, +3.3]). Single sub-datasets move by up to 10 points between two seeds, so per-dataset differences under ≈ 5 points are not interpreted. See [[GroundOne Results]], [[VitaminC]].
