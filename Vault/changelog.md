# Changelog

## [2026-09-22] ingest | jev_simone_rizzo.txt
- Ingested Simone Rizzo's video transcript on Jev and System One Models.
- Created source page `jev_simone_rizzo`.
- Created concept pages: `Jev`, `System One Models`, `Reinforcement Learning with Calibrated Decisions`.
- Updated `index.md`.

## [2026-09-22] ingest | jev_video_description.txt
- Ingested YouTube video description.
- Created source page `JEV Video Description`.
- Created concepts: `TypeSafe AI`, `Jevlike`, `SemIf`.
- Updated `System One Models` and `Reinforcement Learning with Calibrated Decisions` with new terminology.
- Updated `index.md`.

## [2026-09-22] ingest | Jev’s Architecture Unmasked.md
- Ingested Archer Hume's deep dive article.
- Created source page `Jevs Architecture Unmasked`.
- Created concepts: `Mixture of Experts`, `KV Cache`.
- Updated `Jev` with architectural inferences (Shared KV Cache, Sparse MoE, Listwise Processing).
- Updated `index.md`.

## [2026-09-23] ingest | multiple jev sources
- Ingested three Jev sources: Che cos'è Jev, Introducing System One Models, and What is Jev.
- Created source pages: `Che cos'e Jev Spiegazione`, `Introducing System One Models and Jev`, `What Is Jev A Guide to TypeSafe AI`.
- Created concept page: `LangChain`.
- Updated concept pages: `Jev`, `TypeSafe AI`.
- Updated `index.md`.

## [2026-09-28] ingest | BFCL files
- Ingested Berkeley Function Calling Leaderboard V4 and Datasets at Hugging Face.
- Created source pages: `Berkeley Function Calling Leaderboard V4`, `Hugging Face Datasets BFCL`.
- Created concept pages: `Function Calling`, `Berkeley Function Calling Leaderboard`.
- Updated `index.md`.

## [2026-10-01] ingest | Can Jev replace your LLM judge? Evaluating quality, cost, and latency.md
- Ingested MLflow blog post by Yuki Watanabe.
- Created source page: `Can Jev replace your LLM judge`.
- Created concept page: `LLM-as-a-Judge`.
- Updated concept page: `Jev`.
- Updated `index.md`.

## [2026-10-04] query | Quando un System One è vantaggioso rispetto a un LLM?
- Synthesized wiki concepts plus project material (SemIf RESULTS, LoRA v1 results, expected_results) into a new page.
- Created concept page: `When System One Beats an LLM`.
- Updated concept pages: `System One Models`, `Jev`.
- Updated `index.md`.

## [2026-10-05] ingest | 25 sources for the GroundOne thesis (papers, model cards, System One repos)
- Downloaded and verified 21 papers and 4 web/repo documents into `raw/` (citations checked against arXiv / ACL Anthology / AAAI).
- Created 37 source pages: RAG and verification (Lewis, RAGTruth, MiniCheck, LLM-AggreFact leaderboard, AlignScore, HHEM card, Lynx, RAGAS, ARES, Self-RAG, Zheng LLM-as-a-Judge, ANLI, MNLI), calibration (Naeini, Guo, Kadavath, Tian, Geifman), models/inference (LoRA, QLoRA, Qwen2.5, Pope, PagedAttention), System One (CLM blog + README, Rizzo-Flow README + training, SemIf README + RESULTS).
- Created concept pages: `GroundOne`, `Retrieval-Augmented Generation`, `RAG Evaluation Frameworks`, `Hallucination Detection`, `Groundedness Verification`, `Natural Language Inference`, `LLM-AggreFact`, `RAGTruth`, `MiniCheck`, `HHEM`, `AlignScore`, `Calibration`, `Expected Calibration Error`, `Selective Prediction`, `LoRA`, `Qwen2.5`, `Prefill and Decode`, `CLM`, `Rizzo-Flow`.
- Updated: `LLM-as-a-Judge`, `KV Cache`, `SemIf` (OpenJav → OpenJev), `System One Models` (taxonomy), `When System One Beats an LLM` (GroundOne hypotheses replace routing ones; paths fixed).
- Renamed processed raw files with `_ingested` and updated references.

## [2026-10-05] lint | vendor claims, archived routing context
- `Jev`, `Jev Input and Output Format`: speed/cost/calibration figures marked as vendor claims; architecture marked as third-party inference.
- `Mixture of Experts`: MoE in Jev marked as Archer Hume's inference.
- `Function Calling`, `Berkeley Function Calling Leaderboard`: marked as archived context of the abandoned tool-routing experiment.
- `index.md` reorganised around the thesis.

## [2026-10-05] ingest | dataset sources and GroundOne EDA (Phase 1a)
- Added and verified 17 sources in `raw/`: dataset cards (ANLI, LLM-AggreFact, MiniCheck C2D/D2C, RAGTruth), RAGTruth origin sources (MS MARCO, See 2017 and Hermann 2015 for CNN/DM, Yelp Open Dataset), the 8 papers behind LLM-AggreFact's sub-datasets; plus the project's own EDA report.
- Created 18 source pages and concept pages `ANLI`, `MiniCheck Synthetic Data`, `Datasets for GroundOne` (synthesis), `LLM-AggreFact Sub-datasets`.
- Updated `RAGTruth` (EDA findings) and `LLM-AggreFact` (licence: evaluation only, no training or fitting on any split; sub-datasets; RAGTruth-subset overlap).
- Renamed processed raw files with `_ingested`; updated `index.md` (new Data section).

## [2026-10-06] ingest | VitaminC; final dataset choice
- Added `raw/Schuster 2021 - VitaminC_ingested.pdf` (arXiv 2103.08541) and `raw/Dataset card - VitaminC_ingested.md` (HF card, CC BY-SA 3.0).
- Created source page `Schuster 2021 - VitaminC` and concept page `VitaminC` (test T3 only).
- Updated `Datasets for GroundOne`: final choice (RAGTruth = only training source; tests RAGTruth, LLM-AggreFact, VitaminC), expected sizes, and the earlier EDA analysis marked as superseded.
- Updated `RAGTruth` (final role, reliability caveats, segmentation findings); marked `ANLI` and `MiniCheck Synthetic Data` as not used.

## [2026-10-06] ingest | EDA of the final GroundOne dataset
- Added `raw/GroundOne 2026 - EDA report (dataset)_ingested.md` and source page `GroundOne 2026 - EDA report (dataset)`.
- Marked `GroundOne 2026 - EDA report` (Phase 1a, four-question design) as superseded.
- Updated `Datasets for GroundOne` (EDA consequences) and `index.md`.

## [2026-10-10] lint | full health check against the project state of 2026-10-10
- Project pages were stale (frozen at the 2026-10-06 dataset choice). Rewrote [[GroundOne]]; created [[GroundOne Results]]; added the outcome of H1–H4 to [[When System One Beats an LLM]] (H2 "≈ 0 gain vs single-token generation" refuted by control B2).
- Updated with measured results and marked superseded statements (nothing deleted): [[Datasets for GroundOne]] (actual sizes; ANLI rules void), [[LLM-AggreFact]] (dev not used, D18; T2 results), [[RAGTruth]], [[VitaminC]], [[MiniCheck]], [[HHEM]], [[LoRA]] (as run; no gradient clipping), [[Qwen2.5]] (spaced-letter finding), [[Natural Language Inference]], [[AlignScore]], [[ANLI]], [[Groundedness Verification]] (D18; GroundOne rows in the reference table), [[Jev]] (links to its source pages).
- Fixed the only broken link (`[[Archer Hume]]` in a frontmatter); added the missing `**Raw file**` pointer to nine older source pages; fixed two stale lines in [[GroundOne 2026 - EDA report]].

## [2026-10-10] ingest | 22 sources for the thesis update
- **Readout, confidence, statistics, stability** (11): Wang 2024, Zheng 2024, Zhao 2021, Xiong 2024, Koehn 2004, Berg-Kirkpatrick 2012, Dror 2018, Dodge 2020, Mosbach 2021, Pascanu 2013, Willard 2023. New concepts: [[Letter-Token Readout]], [[Verbalised vs Logit Confidence]], [[Statistical Significance and Bootstrap]], [[Fine-tuning Instability and Seeds]], [[Constrained Decoding]]. Updated [[Calibration]], [[LLM-as-a-Judge]], [[System One Models]], [[Selective Prediction]], [[Expected Calibration Error]].
- **Local inference, energy, hallucination** (11): Patel 2024 (Splitwise), Samsi 2023, Luccioni 2024, Alizadeh 2024, Gunter 2024, MLX README, llama.cpp README, Apple M4 MacBook Pro tech specs, Laban 2022 (SummaC), Min 2023 (FActScore), Huang 2023 (survey). New concepts: [[On-Device Inference]], [[Energy of LLM Inference]], [[Apple Silicon and MLX]]. Updated [[Prefill and Decode]], [[KV Cache]], [[Hallucination Detection]], [[Groundedness Verification]], [[Rizzo-Flow]], [[Retrieval-Augmented Generation]].
- Finding raised during ingest: GroundOne's optimiser is MLX `AdamW` with its default `bias_correction=False`; with Mosbach 2021 this is a second plausible cause of the collapsed seed (recorded in `Project/docs/thesis_notes.md`).
- Raw files renamed `_ingested`; `index.md` updated (new sections: evaluation methodology, local inference).

