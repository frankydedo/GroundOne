---
type: concept
tags: [concept, model, fact-checker, baseline, small-model, grounding]
---
# MiniCheck

**MiniCheck** ([[Tang 2024 - MiniCheck]], EMNLP 2024) is a family of small **sentence-level grounding fact-checkers**. Given a (document, sentence) pair, it outputs P(supported). The models are trained on GPT-4-generated synthetic data that forces them to check every fact in a claim and to reason across multiple sentences. It is GroundOne's strongest small-model baseline.

## Variants
| Model | Backbone | Size | Training data | LLM-AggreFact BAcc (paper, no tuning) | Leaderboard |
|---|---|---|---|---|---|
| MiniCheck-RBTA | AlignScore's RoBERTa-L | 355M | 14K synthetic | 72.7 | 73.5 (`lytang/MiniCheck-RoBERTa-Large`) |
| MiniCheck-DBTA | DeBERTa-v3-L | 355M (as given in Table 3) | 14K synthetic + 21K ANLI | 72.6 | 73.1 (`lytang/MiniCheck-DeBERTa-v3-Large`) |
| **MiniCheck-FT5** | Flan-T5-L | **770M** (leaderboard: 0.8B) | 14K synthetic + 21K ANLI | **74.7** (75.1 with dev-tuned thresholds) | **75.0** (`lytang/MiniCheck-Flan-T5-Large`) |
| Bespoke-MiniCheck-7B | not stated in sources | 7B | not stated | – | **77.4** (rank 1; `bespokelabs/Bespoke-Minicheck-7B`) |

## How it works
- **Input**: a document chunk and a claim sentence. **Output**: a score in [0,1]. Decision: supported if the score is above 0.5.
- **Context limit**: documents are chunked at sentence boundaries, about **400 tokens** for RoBERTa and DeBERTa and **500 whitespace tokens for FT5**. The maximum score over chunks is taken (App. E.2). Inputs are effectively limited by the 512-token encoders and T5's training length.
- **Training data**:
  - **C2D** (7,076 examples; synthetic documents built from Wikipedia claims).
  - **D2C** (7,319 examples; real Google News documents chunked, with synthetic claims).
  - A hard **ANLI** subset (21K), with neutral and contradiction mapped to unsupported.
  - Training order: everything except D2C for 2 epochs, then D2C for 1 epoch (App. G).
- **No claim decomposition** and no decontextualization: both were tested and found not to help (§7).

## Strengths and weaknesses (from the paper)
- **Cost**: about $0.24 to label the 13K-example LLM-AggreFact test set, against $107 for GPT-4 (Tables 3–4). That is roughly 400× cheaper.
- **Robust without threshold tuning**: it loses only 0.4 BAcc without tuning (Table 7 vs Table 2).
- **Weaknesses**: no explanations or span localization, English only, no reasoning across separate documents (Limitations).
- **Weak spots**: ExpertQA (59.0) and RAGTruth (78.0 on the leaderboard). The leaderboard's RAGTruth column has the top LLMs at about 84–86.

## How to run (incl. Mac)
- The code is at `github.com/Liyan06/MiniCheck`, and checkpoints are on Hugging Face (IDs above, from the leaderboard).
- MPS and Apple-Silicon support, and the licence of models and synthetic data, are **not stated** in the sources. *(Measured: MiniCheck-RoBERTa runs on PyTorch MPS on the M4; it was the baseline used. Flan-T5 did not fit the memory guard; its published number is used.)*
- Flan-T5-L (770M) should fit in memory on a 16 GB Mac. This is an expectation, not something tested.

## Relevance to GroundOne
- It is the **closest design**: a small, single-score, sentence-level checker. The difference is that GroundOne uses a **decoder** ([[Qwen2.5]] 0.5B/3B with [[LoRA]]) with a **logit readout of answer letters** and a long context window, so it does not need chunking.
- *(Superseded: GroundOne does not reuse the recipe; it trains on RAGTruth only, D21.)* The training recipe is the ANLI hard subset plus C2D/D2C. See [[Natural Language Inference]].
- **Targets** (set before training): the 0.5B model should beat MiniCheck-RBTA/DBTA (about 73); matching FT5 (75.0) would be strong; the 3B could aim for Bespoke-7B (77.4). **Outcome:** on LLM-AggreFact the 0.5B is below RoBERTa (70.1 vs 74.0) and the 3B on par (74.8, n.s.); on RAGTruth (T1) both GroundOne models beat it clearly (AUROC 0.905 / 0.940 vs 0.814).
- **Measure what MiniCheck does not**: ECE and calibration ([[Calibration]], [[Expected Calibration Error]]), and on-device latency ([[When System One Beats an LLM]]).

## Links
[[Tang 2024 - MiniCheck]], [[Tang 2024 - LLM-AggreFact Leaderboard]], [[LLM-AggreFact]], [[AlignScore]], [[HHEM]], [[Groundedness Verification]], [[Hallucination Detection]], [[System One Models]], [[GroundOne]]

## Measured in the thesis (2026-10-10)
MiniCheck-RoBERTa: T1 AUROC 0.814, T2 macro 74.0 (reproduces the published 73.5 within 1.5 points), T3 AUROC **0.968**. VitaminC is in its training lineage (via AlignScore data), so its T3 number is not a transfer result. No latency claim: it was run sentence by sentence without batching on PyTorch MPS. See [[GroundOne Results]], [[VitaminC]], [[RAGTruth]], [[Datasets for GroundOne]].
