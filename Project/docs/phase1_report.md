# Phase 1 report: datasets v1

Built on 2026-10-05 by `groundone data build` (seed 1234), checked by `groundone data check` (**PASS**) and `groundone data shortcut` (code in `GroundOne/src/groundone/data/`). Files and hashes: `Project/data/processed/v1/manifest.json` (data is gitignored; code and manifest are versioned). It follows the EDA recommendations (`Project/EDA/report/eda_report.md` §3).

## 1. Format (shared by training, evaluation and the engine)

Every item is a document, a numbered answer (one or more sentences), the index of the sentence under test, and one question. Prompts are rendered only by `GroundOne/src/groundone/prompts.py`, so training and inference see identical text. For pair datasets (ANLI, MiniCheck, LLM-AggreFact) the answer has one sentence.

| Question (`qtype`) | Letters | Gold label from the three-way class |
| --- | --- | --- |
| `sup`: is it fully supported? | A yes / B no | A = supported, B = contradicted or not mentioned |
| `three`: supported, contradicted or not mentioned? | A / B / C | direct |
| `strict` rule: anything not stated is an error | A acceptable / B error | A = supported |
| `lenient` rule: only contradictions are errors | A acceptable / B error | A = supported or not mentioned |

Binary-only data (MiniCheck synthetic) gets only the `sup` question. Three-way data (ANLI, RAGTruth) gets one question per row, sampled 30 % `sup`, 30 % `three`, 15 % `strict`, 25 % `lenient` (lenient weighted up because it is the rule that differs from the binary question).

## 2. What was built

| File | Rows | Content |
| --- | --- | --- |
| `train_05b` | 42,910 | ANLI 21,000 (7,000 per class) + MiniCheck 13,990 + RAGTruth 7,920. 14.5 M tokens (mean 338, p90 867). Three-way classes balanced (≈ 9,600 each) |
| `train_3b` | 10,000 | Stratified subset of `train_05b` by source × question (3.4 M tokens) |
| `dev_anli` | 2,489 | Official ANLI dev minus the 711 pairs whose premise is also in ANLI test |
| `dev_ragtruth` | 2,249 sentences (300 answers) | 10 % of RAGTruth train sources, split by `source_id` |
| `dev_minicheck` | 405 | 3 % of MiniCheck documents |
| `test_anli` | 3,200 | Official ANLI test (three-way, balanced) |
| `test_ragtruth` | 19,902 sentences (2,700 answers) | RAGTruth test, quality = good; 18,301 supported / 999 not mentioned / 602 contradicted |
| `test_aggrefact` | 29,320 | LLM-AggreFact test, binary, evaluation only (D18) |

Estimated training time from the Phase 0 probe: **≈ 6–7 h for the 0.5B** on `train_05b` and **≈ 7 h for the 3B** on `train_3b`, i.e. one night each.

## 3. Decisions taken while building

1. **ANLI training pairs** come only from premises that are not in ANLI dev/test (93,480 available; 21,000 sampled, 7,000 per class). This is the size of MiniCheck's ANLI share but not MiniCheck's exact subset, so the comparison with MiniCheck is *approximately* data-matched.
2. **RAGTruth training sentences** are rebalanced (2,700 contradicted, 2,700 not mentioned, 2,600 supported; quality = good only). Each row keeps the whole answer, so training uses the same multi-sentence format as inference.
3. **Token cap 2,048**: 78 RAGTruth rows were longer and were dropped (logged).
4. **Cross-dataset exclusion** (found by the leakage check): one CNN article used by RAGTruth train is also an LLM-AggreFact-CNN test document; its 2 training rows were removed.
5. **ANLI dev cleaned**: the official dev and test share premises by design; for calibration we drop the 711 dev pairs that share a premise with test.

## 4. Leakage check: PASS

- No source document of train or dev appears in any test set (ANLI by premise, RAGTruth by `source_id`, MiniCheck by document).
- No (document, sentence) pair of train or dev appears in any test set.
- No training or dev document appears among LLM-AggreFact test documents.
- Train and dev are disjoint by group within every source.
- Warnings only (not failures): 58 training sentences have the same text as an LLM-AggreFact test claim, with different documents. They are generic Yelp sentences such as "The restaurant offers outdoor seating and takeout options."

## 5. Shortcut check (ANLI, claim-only baseline)

A bag-of-words classifier that sees **only the claim** reaches **0.559** balanced accuracy on held-out ANLI training rows (chance 0.333), but only **0.357 (dev)** and **0.393 (test)**. The surface cues in ANLI train (e.g. 26 % of contradictions contain a negation, against 8–10 % for the other classes) do not hold in dev/test, where the pattern is reversed.

Implication: a model can partly learn these cues from our training data and will be penalised on ANLI test. This is not fixed in v1. ANLI test, being adversarial and cue-reversed, will reveal it. If the fine-tuned model shows a large gap between ANLI training-like data and ANLI test, a v2 can rebalance negations per class.

## 6. Next

Phase 2: the GroundOne engine (batched, from the Phase 0b prototype, reading prompts from `groundone/prompts.py`) and the evaluation harness, then the first 0.5B training run overnight.
