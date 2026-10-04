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
- The data is **test-only for training purposes**: the authors say it is "largely test-only" (§3). Do not train GroundOne on it. Use dev only for threshold tuning and model selection.
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
Not stated in the paper or the leaderboard capture. The paper says use is "for research purposes only, consistent with [the datasets'] intended use" (App. C.4). Each constituent dataset keeps its own licence.

## Relevance to GroundOne
- It is the same task framing as GroundOne: per-sentence, binary, document-grounded.
- **Headline protocol**: t = 0.5 on P(supported), BAcc per dataset plus the macro average. Secondary results: dev-tuned thresholds, AUROC and ECE.
- The documents are long: ClaimVerify and WiCE average about 1.6–1.9K length units (likely words, so probably more than 2K tokens). Check that Qwen2.5 inputs fit without truncation, or chunk and take the maximum as MiniCheck does.

## Links
[[MiniCheck]], [[HHEM]], [[AlignScore]], [[RAGTruth]], [[Groundedness Verification]], [[Hallucination Detection]], [[LLM-as-a-Judge]], [[Qwen2.5]], [[GroundOne]]
