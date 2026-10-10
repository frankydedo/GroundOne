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

## [2026-10-10] ingest | Hugging Face decision-models tag (12 sources)
- **Sources** (12 pages): papers Deußer 2026 (Jev on 37 datasets), Nandakishore 2026 (Laya reproduction and calibration), Azizi 2026 (labels override definitions; three readouts on Qwen2.5), Robles-Fernández 2026 (Sciev manuscript); model cards Laya, Sciev; dataset cards DecideBench, JevBench v1.6.1 (+ leaderboard CSV), morrenhale Jev vs Laya vs Julia-1 (+ results JSON), Laya Formatting Fragility, Core AI on M4 Max, tasksource-jev-typed-decisions. The two data files are cited from their card pages, not given pages of their own.
- **New concepts:** [[Laya]], [[Decision-Model Benchmarks]], [[Hugging Face decision-models Tag]].
- **Updated (appended, superseded statements marked):** [[System One Models]] (families d: encoder + per-option marker head, e: diffusion backbone + typed heads; meanings of "one forward pass"), [[Jev]] (independent evaluations; the "no public calibration measurement" note marked superseded), [[Rizzo-Flow]] (training-data lineage: procedural-typed-decisions, not tasksource-jev-typed-decisions), [[Calibration]] (calibration is not intrinsic; dev-fitted thresholds), [[On-Device Inference]] (Core AI M4 Max measurements, re-prefill cost), [[Letter-Token Readout]] (Azizi 2026), [[When System One Beats an LLM]] (four evidence rows and a critical reading).
- **Findings raised during ingest:** (1) on LLM-AggreFact, with the same split and metric but a different prompt, Jev (78.6) and a zero-shot Qwen3.8-27B letter readout (76.9) are above GroundOne 3B (74.8); the thesis T2 claim must cite this. (2) Laya's "one forward pass" is one sequence per question, so there is no shared context. (3) Laya-card numbers are internally inconsistent (Jev ECE 0.144 vs 0.246; post-temperature vs raw), and the typed-decisions checkpoint is under-confident, not over-confident. (4) Provenance conflict on typed-decisions ("official TypeSafe/Julia suite" vs "independent of TypeSafe"). (5) The independence of Nandakishore 2026 rests on the author's statement only (the surname is close to the Laya developer's handle).
- Raw files renamed `_ingested` (14 files, including the CSV and JSON); `index.md` updated (System One section, new Sources subsection).

## [2026-10-10] ingest | Hugging Face decision-model tag (survey + 15 sources)
- **Survey.** Full listing of the singular `decision-model` tag (1,529 models, 610 authors; 862 created in September, 665 in October 2026) saved as raw data; 60+ model cards, code files, configs and the Decision Index data reviewed; 18 arXiv ids resolved (3 kept).
- **Sources (15 pages):** model cards Cloudflare Clef (+ blog posts + head code), Liquid AI d1-3B (+ d1-omni-600M card + readout code), Perplexity pplx-decider-v1.1-27b (+ decision_config, training config, data manifest), Vela 2.0 9B (KR Labs + vLLM-SR; + EVALUATION, TRAINING), Strands decider 2B (Amazon mirror), Kev-4B, uratori-ja-4b; on-device mlx-community clef-flash-4bit, FluidInference d1-omni Core ML, llama.cpp PR 29818; leaderboard multimodalart Jev Decision Index (README + methodology, results and board JSON); papers Li 2026 (JEV-as-a-Judge), Guo 2026 (Just Ask Jev), Deka 2026 (SBERT2S1); the tag listing JSON.
- **New concept:** [[Decision-Model Landscape (Hugging Face, 2026)]] (tag size and composition, families, catalogue with evidence grades, groundedness models, on-device ports, definition changes, red flags).
- **Updated (appended; superseded statements marked):** [[Hugging Face decision-models Tag]] (the singular tag is the big one), [[System One Models]] (industry entrants; family (a) no longer closed-only; five meanings of "one pass"), [[Groundedness Verification]], [[Hallucination Detection]] ("calibration rarely evaluated" partly superseded), [[RAGTruth]] (response-level rows), [[Decision-Model Benchmarks]] (Decision Index, RLCDAlignBench, JEV-as-a-Judge rows; self-reported numbers; "none measures" refined), [[When System One Beats an LLM]] (three evidence rows, point 5), [[On-Device Inference]], [[Apple Silicon and MLX]], [[Calibration]], [[Selective Prediction]] (lower-bound threshold rule), [[Reinforcement Learning with Calibrated Decisions]], [[Jev]], [[Letter-Token Readout]], [[LLM-as-a-Judge]], [[Fine-tuning Instability and Seeds]] (seed soups).
- **Findings raised during ingest:** (1) the Decision Index contains response-level RAGTruth for 70 decision models: no entrant under 1B beats chance meaningfully (best 0.553 vs 0.518), all ≥ 15B exceed 0.6; Jev 0.765, best 0.803; Clef 79.4 and Vela 9B 0.774 in their own runs. GroundOne's T1 covers 2,647 of the same 2,700 responses, so a response-level F1 for GroundOne is computable and would place it on this scale (specialist vs zero-shot). (2) pplx-decider and Strands train on VitaminC (and pplx on WiCE), so they are contaminated baselines for T3/T2. (3) Liquid's d1-3B is a letter readout with tree-shared state at 3B, the closest industrial analogue of GroundOne; Clef is the first open decoder + joint-head (family a) model. (4) Two academic papers show calibration is workload-relative (Jev per-benchmark ECE 0.168 vs pooled 0.047; temperature transfer fails) and recommend locally validated, lower-bound thresholds; the open RLCD recipe trails cross-entropy and gives no calibration gain after temperature scaling. (5) Red flags: likes and downloads concentrated in three repositories (54 % of likes; 60 % of downloads from one uploader), "JEV"-named distillation students reporting teacher-agreement metrics, LLM-written self-built evaluation sets.
- Raw files renamed `_ingested` (25 files, including JSON data files and the Clef code file); `index.md` updated (System One ecosystem line and a new Sources subsection). All `raw/` references and wiki links checked: none broken.
