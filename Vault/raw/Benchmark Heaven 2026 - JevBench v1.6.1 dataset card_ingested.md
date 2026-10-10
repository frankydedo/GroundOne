Source: https://huggingface.co/datasets/benchmarkheaven/jevbench (revision 47bea8ac8059af6d4265123405a18194ccabd5c6) — retrieved 2026-10-10

---
license: cc-by-4.0
pretty_name: JevBench decision model results
tags:
  - decision-model-benchmark
  - decision-models
  - leaderboard
  - model-evaluation
  - calibration
  - jevbench
  - jev-compatible
  - open-weights
task_categories:
  - text-classification
language:
  - en
size_categories:
  - n<1K
configs:
  - config_name: leaderboard
    data_files:
      - split: train
        path: data/leaderboard.csv
---

# JevBench decision model results

## Scoring method (as of v1.6.1)

JevBench by Benchmark Heaven is a benchmark for AI decision models, including Jev-compatible systems. It measures typed decision accuracy, probability calibration, latency and cost. Maintained by Benchmark Heaven, independently of TypeSafe AI.

[Current open-weights board](https://benchmarkheaven.com/jev-models) · [Hosted API board](https://benchmarkheaven.com/jev-models/api) · [Methodology](https://benchmarkheaven.com/jev-models/methodology) · [Data card](https://benchmarkheaven.com/jev-models/data) · [Benchmark comparison](https://benchmarkheaven.com/decision-model-benchmarks)

Published release: **v1.6.1**, initially published 2026-10-06. [Version permalink](https://benchmarkheaven.com/jev-models/v1.6.1). Published addenda: a6 (2026-10-07), a7 (2026-10-07), a8 (2026-10-07), a11 (2026-10-08), a12 (2026-10-08); amended through 2026-10-08. Latest row measurement: 2026-10-07. This list includes additions embedded in the results artifact; method amendments and board revisions are listed separately on the versioned board. Cite source_sha256 5cd8c1332226ea9c179883d2285c0d8b8cc593ae38f2645197364a7ddd9c83c1 for the exact published bytes. The live board may also include later dated API reruns and presentation revisions.

**Capability Score:** Arithmetic mean of Intelligence and Calibration; ranked models within both official caps. Headline on the open-weights board. Cost cap: USD 0.0646 per 1,000 decisions; adjusted median-latency cap: 1.23 seconds.

**Composite Score:** Weighted harmonic mean of Intelligence, Calibration, Speed and Cost, multiplied by squared penalties when Intelligence is below its configured floor, or Speed or Cost is below 50. Equal 25% weights do not mean an arithmetic average. Option A: weights Calibration 25%, Cost 25%, Intelligence 25%, Speed 25%; Intelligence floor 50. Composite is secondary on open weights and leads the hosted API board.

[Authoritative release manifest](https://benchmarkheaven.com/api/jevbench/manifest) · [Own results JSON](https://benchmarkheaven.com/api/decision-results/jevbench/v1.6.1/json) · [Own results CSV](https://benchmarkheaven.com/api/decision-results/jevbench/v1.6.1/csv). Missing measurements are null, never zero. No third-party benchmark numbers are included.

**Limitations:** finite task coverage; sealed inputs prevent complete independent reruns; hosted endpoint versions can be opaque; cost is modeled from the published basis and latency depends on the runtime and measurement location. Training on the public split must be disclosed. A leaderboard score does not establish reliability on your workload.

**Name disambiguation:** this is JevBench by Benchmark Heaven at benchmarkheaven.com. The [metamorphic coherence benchmark](https://jevbench.github.io/) is a separate project; its consistency scores measure a different property.

Historical releases retain their original scoring definitions and measurement sets. Do not compare scores across method versions as if they were the same experiment.

## Summary

This dataset contains only Benchmark Heaven's system-level JevBench measurements. Each row is one evaluated system with the four axis scores, Capability and Composite scores, rank fields and published cost and latency fields. The stored snapshot CSV schema is preserved; its column names differ from the site's JSON/CSV exports.

The snapshot was generated 2026-10-05, before v1.6.1's final publication timestamp on 2026-10-06 and its later public addenda.


`data/leaderboard.json` carries the stored public feed for this JevBench v1.6.1 snapshot, generated 2026-10-05; the live feed may include later dated additions and presentation changes.

## What is measured

- **Intelligence** — chance-corrected accuracy on the frozen public and sealed tiers.
- **Calibration** — distribution quality of the typed answers a system produces.
- **Speed** — median (p50) latency on a logarithmic scale; self-hosted runs carry a published adjustment.
- **Cost** — USD per 1,000 complete decisions; `price_kind` labels the evidence basis (`estimate` is an estimate, not a measured charge).
- **Capability score / rank** — the headline; rank is present only for systems inside the official caps.
- **Composite score / rank** — weighted harmonic mean of Intelligence, Calibration, Speed and Cost, with the configured squared penalties; equal 25% axis weights are not an arithmetic average. It is secondary on the open-weights board and headlines the hosted API board.

## Columns

| Column | Description |
| --- | --- |
| `revision` | JevBench release this row belongs to. |
| `key` | Stable machine key of the system. |
| `name` | Published system name. |
| `source_url` | Published source or weights link. |
| `listing` | `ranked` (in the ranking) or `listed` (shown, not ranked). |
| `capability_rank` | Capability rank; empty when the system is outside the official caps. |
| `capability_score` | Mean of Intelligence and Calibration (0–100). |
| `capability_eligible` | `true` when inside both official caps. |
| `composite_rank` | Composite rank (empty when not ranked). |
| `composite_score` | Composite score (0–100). |
| `intelligence`, `calibration`, `speed`, `cost_axis` | The four axis scores (0–100). |
| `usd_per_1000_decisions` | Modeled cost per 1,000 complete decisions. |
| `price_kind` | Evidence basis for the cost, e.g. `estimate`. |
| `p50_latency_s_raw` | Measured raw median latency in seconds (before any published adjustment). |

## How to cite

```bibtex
@misc{benchmarkheaven2026jevbench,
  title         = {JevBench: A Benchmark for AI Decision Models},
  author        = {{Benchmark Heaven}},
  year          = {2026},
  howpublished  = {\url{https://benchmarkheaven.com/jev-models}},
  note          = {Static snapshot fetched 2026-10-05, before final v1.6.1 publication on 2026-10-06; source_sha256 5cd8c1332226ea9c179883d2285c0d8b8cc593ae38f2645197364a7ddd9c83c1}
}
```

## Links

- [Live JevBench board](https://benchmarkheaven.com/jev-models)
- [Jev alternatives, compared](https://benchmarkheaven.com/jev-models/alternatives)
- [How to choose a Jev-class model](https://benchmarkheaven.com/jev-models/how-to-choose)
- [Is Jev open source?](https://benchmarkheaven.com/jev-models/open-source-jev)
- [Public results API](https://benchmarkheaven.com/api/jevbench/latest)
- [Submit a system](https://benchmarkheaven.com/submit)
- [Method repository](https://github.com/fstandhartinger/jevbench)

## Update cadence

This stored snapshot is not automatically regenerated when a JevBench release changes.

## Limitations

Aggregates only: no item-level data (no questions, item ids or predictions).
Sealed items are never published. Cost values are modeled per the stated basis
and are not invoices; latency adjustments for self-hosted runs are published
assumptions, not measurements.
