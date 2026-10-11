---
type: concept
tags: [hugging-face, decision-models, system-one, ecosystem, evidence-quality]
---
# Hugging Face decision-models Tag

**What it is.** `decision-models` is a Hugging Face Hub tag for [[System One Models|System One / decision models]] and the datasets that evaluate or train them: models that take a state and typed questions and return probabilities over a closed answer set, without generating text. According to the survey of 2026-10-10 that prompted this ingest, Hugging Face introduced it in 2026. The dated uploads ingested here are from September–October 2026, after [[Jev]]'s release in September 2026. No ingested raw file documents when or by whom the tag was created.

**What is under it (ingested 2026-10-10).**
- Benchmarks and results: [[Yong 2026 - DecideBench dataset card|DecideBench]], [[Benchmark Heaven 2026 - JevBench v1.6.1 dataset card|JevBench v1.6.1]], [[morrenhale 2026 - Decision benchmark Jev vs Laya vs Julia-1 dataset card|morrenhale's Jev vs Laya vs Julia-1]], [[pranaysuyash 2026 - Laya Formatting Fragility dataset card|Laya Formatting Fragility]], [[mlboydaisuke 2026 - Decision models on Core AI (JevBench public231) dataset card|Core AI runs on an M4 Max]].
- Training data: [[Sileo 2026 - tasksource-jev-typed-decisions dataset card|tasksource-jev-typed-decisions]].
- Models: [[Robles-Fernandez 2026 - Sciev model card|Sciev]] (diffusion backbone + typed heads). The [[Laya]] card uses related tags (`system-one`, `calibrated-decisions`) but not `decision-models` itself.
- Synthesis of the benchmarks: [[Decision-Model Benchmarks]].

**Evidence-quality caveats.**
- **Mostly individual uploads.** Several benchmark cards come from single Hugging Face users, not institutions. They are useful when they publish manifests and predictions (morrenhale, Core AI), weak when they publish aggregates only.
- **LLM-written material.** DecideBench's items were all written by Claude, with labels checked by other models.
- **Harness errors happen.** The fragility suite's first release overstated Laya's key-rename flips (87.2 % vs a corrected 32.8 %).
- **Vendor and third-party numbers are mixed on cards.** The Laya card compares its post-temperature ECE with Jev numbers it did not measure, and its 0.766 comes from a checkpoint trained on that benchmark's training split.
- **Popularity is not evidence.** The caller's survey reports hype signals (rapid likes and stars for Laya). No ingested file gives these counts, so none are recorded here. Independent results on Laya (0.590 morrenhale, 59.8 % DecideBench, JevBench intelligence 1.79) are weak.
- **Peer review is rare.** The arXiv papers (Deußer, Nandakishore, Azizi) are preprints from late September and early October 2026; Sciev's manuscript is not on arXiv.

**Relevance to GroundOne.** The tag is the ecosystem GroundOne would be published into. It also shows the gap the thesis fills: none of these benchmarks measures sentence-level groundedness of RAG answers ([[Decision-Model Benchmarks]]).

## The singular `decision-model` tag is the big one (ingest 2026-10-10, second pass)
*Correction: this page describes the plural tag `decision-models`. The main ecosystem tag is the singular **`decision-model`**, which held 1,529 models from 610 authors on 2026-10-10 (API: `api/models?filter=decision-model`; the web filter is `?other=decision-model`).* The "What is under it" list above covers only the plural tag and should not be read as the model side of the ecosystem: under the singular tag sit Cloudflare Clef, Liquid AI d1, Perplexity pplx-decider, Strands decider, vLLM-SR Decision/Vela, Kev and hundreds of community fine-tunes and quantisations. The survey, catalogue, on-device ports and red flags are in **[[Decision-Model Landscape (Hugging Face, 2026)]]**; the raw listing is [[Hugging Face 2026 - decision-model tag listing (2026-10-10)]]. The community leaderboard used by most cards is the [[multimodalart 2026 - Jev Decision Index (Hugging Face Space)|Decision Index]].
- *Superseded statement:* "none of these benchmarks measures sentence-level groundedness of RAG answers" still holds for *sentence-level*, but the Decision Index does measure **response-level RAGTruth** for 70 entrants ([[Decision-Model Benchmarks]]).

## Links
[[System One Models]], [[Decision-Model Benchmarks]], [[Decision-Model Landscape (Hugging Face, 2026)]], [[Laya]], [[Jev]], [[GroundOne]]

## Date of introduction (author, 2026-10-11)
- The author reports that Hugging Face officially introduced the `decision-model` tag on **2026-10-09**. The survey listing of 2026-10-10 (1,529 models) was therefore taken one day after; more than half of those models (862) had been created in September 2026, so they were uploaded before the tag existed officially and tagged afterwards. No ingested raw file documents the announcement itself; the thesis states the date on the author's authority and cites the tag listing.

