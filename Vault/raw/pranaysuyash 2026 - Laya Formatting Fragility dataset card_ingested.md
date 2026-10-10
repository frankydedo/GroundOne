Source: https://huggingface.co/datasets/pranaysuyash/laya-formatting-fragility (revision 8e2e05382cdf3e264040f4fe6e7ede6e80c798f8) — retrieved 2026-10-10

---
license: apache-2.0
task_categories:
- text-classification
tags:
- decision-models
- formatting-sensitivity
- benchmark
- laya
- agentjev
- typed-decisions
size_category:
  small
pretty_name: Laya Formatting Fragility
---

# Laya Formatting Fragility — a perturbation suite for typed decision models

Small decision models ("decide, don't chat" — Laya, AgentJev and friends)
return typed answers with probabilities in milliseconds. Their answers can
be **sensitive to formatting**: option key names, option order, and state
phrasing change results even when the situation and the gold answer are
identical. Vendor benchmarks don't measure this. This dataset does.

Every row pair differs in exactly one formatting axis; the gold label never
changes. Any model that answers differently across a pair is being driven
by format, not meaning.

## Construction

480 rows = 40 hand-written unambiguous base cases × 12 format variants.

| family | task | classes/levels | rows |
|---|---|---|---|
| `news_topic` | choice | world / sports / technology / finance | 120 |
| `support_department` | choice | billing / technical / account / feedback | 120 |
| `urgency` | score (0–3) | not urgent → critical | 120 |
| `safety_gate` | noul (yes/no) | destructive-or-irreversible? | 120 |

Perturbation axes per base case:

- **phrasing** — `p0`/`p1`/`p2`: three surface forms of the same situation
- **order** — criteria/options in `forward` vs `reversed` insertion order
- **key_variant** — `semantic` option keys vs `abstract` aliases (`A1..An`,
  `L0..L3`); for `safety_gate` noul rows, two question phrasings (`q0`/`q1`)

Labels are hand-assigned and deliberately unambiguous: this suite measures
formatting sensitivity, not capability.

Row schema: `base_id, family, task_type, phrasing, order, key_variant,
state, questions (JSON string in decision-model request shape), gold
(JSON string: {label, options})`.

## Measured results (2026-09-22/23, corrected harness v2)

Flip rates compare answers **by option position within each row's own
criteria** (semantic names and abstract aliases are different label
spaces; raw-string comparison overstates flips — see correction note).

| metric | laya 0.3.5 | AgentJev-0.6B | jev-1.13.0 (hosted) |
|---|---|---|---|
| overall accuracy | 72.7% | 72.5% | **90.2%** |
| baseline slice (p0, forward, semantic) | 75.0% | 82.5% | **95.0%** |
| **order flip rate** (forward ↔ reversed) | **22.5%** | **0.0%** | 2.9% |
| accuracy, forward vs reversed | 68.3% / 77.1% | 72.5% / 72.5% | 90.8% / 89.6% |
| **key-rename flip rate** (position-based) | **32.8%** | **20.0%** | 8.3% |
| accuracy, semantic vs abstract keys | 73.9% / 64.4% | 71.1% / 70.0% | 93.9% / 86.7% |
| phrasing flip rate (p0 ↔ p1) | 15.0% | 23.7% | 3.7% |
| latency p50, 1 question | 20.4 ms | 26.2 ms | 863 ms (network) |
| runs where | fully offline | fully offline | hosted API |

Readings:

- **The hosted generalist is also the most format-stable** — Jev flips on
  2.9–8.3% of pairs across all three axes and leads accuracy on these
  clear-cut tasks by 17+ points. The locals' case rests on latency, cost,
  offline operation, and fine-tunability — not zero-shot quality.
- **Order sensitivity is architecture-dependent.** AgentJev's candidate
  head is permutation-equivariant and the suite verifies it exactly:
  0.0% order flips, identical accuracy in both orders. Laya is genuinely
  order-sensitive (22.5% of answers move; reversed order is actually
  *more* accurate for it, +8.8 points — a position bias, not noise).
- **Key renames matter less than raw-string comparisons suggest — when
  options carry descriptions.** With descriptions present, position-based
  flips are 8–33% and accuracy drops are mild (−9.5 pts Laya, −1.1 pts
  AgentJev, −7.2 pts Jev). Community reports of below-chance collapse
  under abstract keys (e.g. `R1…R5`) likely involve options *without*
  descriptions, where the key is the only signal. The description is the
  load-bearing text.
- **Phrasing sensitivity varies widely** (3.7% hosted vs 15–24% local).

## Correction note (2026-09-22, harness v2)

The first published run used two faulty comparisons: (a) score-row answers
were mapped through the forward key list instead of the row's own (possibly
reversed) criteria order, and (b) key-rename flip rates compared raw answer
strings across different label spaces. Corrected figures above supersede
the first card (which reported laya overall 66.7%, order flip 21.7%, key
flip 87.2%). Accuracy per row was always scored in its own key space and
row-level data is unchanged; only the aggregate order/key metrics changed.
The harness now resolves answers to canonical option positions.

## Usage

```bash
python generate_dataset.py            # regenerate data/fragility_test.jsonl (deterministic)
python probe_harness.py --model laya  # run + print the metrics table
```

Implement the small adapter in `probe_harness.py`
(`predict(state, questions_json) -> (answer, confidence)`) to benchmark
any other typed decision engine on the identical rows — a hosted-engine
stub is included and intentionally unimplemented (no credentials in code).
`laya_fragility_kaggle_demo.ipynb` runs the suite end to end.

## Provenance

Created during an independent head-to-head evaluation of Laya vs hosted
decision models, where formatting sensitivity was first measured on private
fixtures; this dataset re-expresses it synthetically. AgentJev numbers
measured against its local serving path (`jev_service.server`, shared-prefix
runtime, temperatures bundled with its release).

## License

Apache-2.0 (matches the Laya base model).
