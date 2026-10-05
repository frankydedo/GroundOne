---
type: concept
tags: [concept, dataset, nli, adversarial, training-data, three-way, rules]
---
# ANLI (Adversarial NLI)

**ANLI** is a three-way [[Natural Language Inference]] dataset (entailment / neutral / contradiction) collected adversarially by Facebook AI Research ([[Nie 2020 - Adversarial NLI]], ACL 2020; card: [[Dataset card - ANLI]]). In [[GroundOne]] it is the **only source of balanced, human-labelled three-way data**, so it carries the three-way question and the strict/lenient rules. The general comparison with MultiNLI and the evidence on how useful NLI data is for grounding are on [[Natural Language Inference]]; this page does not repeat them.

## Origin and collection
- **HAMLET** (human-and-model-in-the-loop): a writer gets a premise and a target label and writes a hypothesis that should fool the current model; fooling examples are verified by other humans; the model is retrained for the next round. Three rounds:
  - **R1**: BERT-Large adversary; premises are 250–600-character **Wikipedia** passages (via HotpotQA).
  - **R2**: RoBERTa ensemble; new Wikipedia premises.
  - **R3**: stronger RoBERTa ensemble; Wikipedia plus news, fiction, spoken text, WikiHow and RTE5. "Wikipedia premises" is therefore exact only for R1–R2.
- **Train contains unverified and model-correct examples**; dev and test contain only verified, model-fooling examples and are balanced by label ([[Nie 2020 - Adversarial NLI]]).

## Sizes and labels
| Round | Train | Dev | Test |
|---|---|---|---|
| R1 | 16,946 | 1,000 | 1,000 |
| R2 | 45,460 | 1,000 | 1,000 |
| R3 | 100,459 | 1,200 | 1,200 |
| **Total** | **162,865** | **3,200** | **3,200** |

- **Train label balance** E/N/C = 52,111 / 68,789 / 41,965 (neutral-heavy, especially in R2/R3). Dev and test are balanced, about 1/3 each ([[Nie 2020 - Adversarial NLI]]).
- Fields: `uid`, `premise`, `hypothesis`, `label`, `reason` (annotator explanation; filled for 16 % of pairs in our EDA).
- **Licence: CC BY-NC 4.0** ([[Dataset card - ANLI]]). Non-commercial research use, including fine-tuning, is allowed with attribution.

## EDA findings (GroundOne Phase 1a)
From [[GroundOne 2026 - EDA report]] (Qwen2.5 tokens):
- **Short documents**: premise median 74 tokens (p90 106, max 333); hypothesis median 11 (p90 20). An order of magnitude shorter than RAG contexts.
- **Premise reuse**: 10,761 unique premises, **~16 hypotheses per premise** (15.73). **98.6 % of dev and 98.9 % of test premises also appear in train** with other hypotheses.
  - Consequence: to test whether rules *generalise*, the training subset must exclude dev/test premises. **93,480 train pairs remain** (24,455 contradiction / 38,604 neutral / 30,421 entailment), far more than needed.
- **Negation shortcut, reversed across splits**: in train, 25 % of contradiction hypotheses contain a negation word vs 8–11 % for the other classes. In dev/test, contradictions contain *fewer* negations (8–9 %) than supported claims (15–16 %). The report attributes this to the adversarial collection. A model that learns "negation → contradicted" from train is penalised on dev/test.
- **Overlap shortcut**: not-mentioned claims share fewer words with the premise (median overlap 0.50 vs 0.64–0.67).
- **No overlap** with [[LLM-AggreFact]] premises.

## Role in GroundOne
- **Mapping**: entailment → *supported*, neutral → *not mentioned*, contradiction → *contradicted*. For the binary task, neutral + contradiction → unsupported (MiniCheck's mapping).
- **X1 training**: the ~21K MiniCheck "hard" subset ([[MiniCheck Synthetic Data]] recipe), restricted to premises not in dev/test, three-way labels kept.
- **X4 three-way question**: primary dataset (balanced human labels; RAGTruth test has almost no contradictions in QA).
- **X5 rules**: rule labels are derived from three-way labels. Strict = only entailment is acceptable; lenient = only contradiction is an error. Because the classes are balanced, the two rules disagree on about 1/3 of items (all the neutral ones).
- **X6 calibration**: dev for temperature/threshold, test held out.
- **Checks**: a claim-only (hypothesis-only) baseline and, if needed, rebalancing negations in the training subset.
- **Not suitable** for X7 (single short Wikipedia-style paragraphs) and only a weak synthetic X3 (many hypotheses per tiny premise).

## Links
[[Natural Language Inference]], [[Nie 2020 - Adversarial NLI]], [[Dataset card - ANLI]], [[GroundOne 2026 - EDA report]], [[Datasets for GroundOne]], [[MiniCheck]], [[MiniCheck Synthetic Data]], [[RAGTruth]], [[GroundOne]]
