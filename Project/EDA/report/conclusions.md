## 1. Summary

Four datasets were analysed: **ANLI** and **RAGTruth** in depth, **MiniCheck synthetic data** and **LLM-AggreFact** more briefly. The question was which dataset can serve which experiment of the thesis (X1–X7 below). Main findings:

1. **No single dataset covers everything.** ANLI is the only source with balanced, human three-way labels (supported / contradicted / not mentioned), so it carries the three-way question and the rules. RAGTruth is the only source of real multi-sentence RAG answers over a shared context, so it carries the K-decisions experiment and in-domain training. LLM-AggreFact is the benchmark that makes our numbers comparable with published ones.
2. **The LLM-AggreFact "RAGTruth" subset is RAGTruth itself.** Its dev part consists of sentences from the RAGTruth *train* split (14,046 of 15,340 matched) and its test part of sentences from the RAGTruth *test* split (14,942 of 16,371). Training on RAGTruth train is therefore safe for the LLM-AggreFact **test** set. LLM-AggreFact itself may only be used for evaluation (licence / gating condition), so none of its splits is used for calibration or model selection. RAGTruth test and LLM-AggreFact-RAGTruth test are the same data and must not be counted twice.
3. **Our sentence labels for RAGTruth are reliable.** On 29,191 sentences matched with LLM-AggreFact's own labels, our span-derived binary label agrees in **98.6 %** of cases. All 419 disagreements go the same way: we say "unsupported", LLM-AggreFact says "supported". They are not explained by the `implicit_true` / `due_to_null` flags; the likely cause is a different overlap rule or segmentation. We use LLM-AggreFact's labels for binary evaluation (comparability) and our labels where only we have them (three-way classes).
4. **Contradictions are rare in RAG answers, except in Data2txt.** At sentence level RAGTruth train has 105,572 supported, 8,077 not-mentioned and 4,658 contradicted sentences, and 77 % of the contradiction spans come from Data2txt (Yelp records as JSON). In the QA test split only 0.5 % of sentences are contradicted. A three-way test on RAGTruth QA alone would be meaningless; ANLI is needed.
5. **ANLI reuses documents across splits.** Each premise has ~16 hypotheses on average, and 98.6 % (dev) / 98.9 % (test) of the dev/test premises also occur in train with other hypotheses. For a clean test of whether rules generalise, the ANLI training subset should exclude those premises: **93,480 train pairs remain** (24,455 contradiction, 38,604 neutral, 30,421 entailment), far more than needed.
6. **ANLI has a shortcut in train that is reversed in dev/test.** In the train split 25 % of contradiction hypotheses contain a negation word, against 8–11 % for the other classes. In dev and test the pattern is reversed: contradictions contain *fewer* negations (8–9 %) than supported claims (15–16 %), a consequence of ANLI's adversarial collection. A model that learns "negation → contradicted" from train is penalised on dev/test. Not-mentioned claims also share fewer words with the premise (median overlap 0.50 vs 0.64–0.67). Phase 1 should run a claim-only baseline and, if needed, rebalance negations in the training subset.
7. **Lengths and the training cap.** Median document length: ANLI 73 tokens, MiniCheck 186, RAGTruth QA 308, RAGTruth Summary 552, LLM-AggreFact test 530 (but ClaimVerify and Wice reach a p90 of 3,600–4,700 tokens). For RAGTruth, 22 % of full prompts (context + answer) exceed 1,024 tokens and only 1 % exceed 2,048. **A 2,048-token cap keeps 99 % of RAGTruth; 1,024 would drop a fifth of it**, mostly Summary and Data2txt.
8. **K is naturally high in RAGTruth.** Median sentences per answer: 9 (Data2txt), 6 (QA), 5 (Summary); 45 % of answers have K ≥ 8. With three questions per sentence, K = 15–27 per answer is realistic, exactly the regime where Phase 0b measured a 2–6× gain.
9. **RAGTruth is clean between its splits** (no source document is in both train and test) and has 173 responses flagged as `incorrect_refusal` or `truncated` that should be dropped.
10. **No overlap** was found between MiniCheck synthetic data or ANLI and LLM-AggreFact (documents or claims).

## 2. Usability of each dataset per experiment

✅ suitable · ⚠️ usable with care · ❌ not suitable

| Experiment | ANLI | RAGTruth | MiniCheck synthetic | LLM-AggreFact |
| --- | --- | --- | --- | --- |
| **X1** Binary groundedness, training (RQ1) | ✅ the MiniCheck "hard ANLI" subset; filter premises seen in dev/test; the train-only negation shortcut must be checked | ✅ in-domain; sentence level; ~90 % supported, so rebalance; drop refusals/truncated | ✅ the core of the MiniCheck recipe (14,395 pairs); makes the comparison with MiniCheck data-matched | ❌ evaluation only (its dev RAGTruth part *is* RAGTruth train) |
| **X2** Binary evaluation comparable with published results (RQ1, plain task of RQ5) | ⚠️ dev/test usable as a secondary, non-RAG check | ✅ test split, but it **is** the LLM-AggreFact-RAGTruth test; report once, with LLM-AggreFact labels | ❌ training data | ✅ **primary benchmark** (test, 11 sub-datasets, macro balanced accuracy, threshold 0.5); long documents in ClaimVerify/Wice need the 2,048 cap or chunking, stated |
| **X3** K decisions over one shared context (RQ2) | ⚠️ several hypotheses per premise give a synthetic K, but contexts are tiny (~75 tokens) | ✅ **the natural set**: real answers, median K 5–9, contexts 300–700 tokens | ❌ ~2 claims per document | ⚠️ only its RAGTruth part has several claims per document (same data as RAGTruth) |
| **X4** Three-way question (RQ5) | ✅ **primary**: human three-way labels, balanced dev/test (1/3 each) | ⚠️ train usable (8,077 not mentioned, 4,658 contradicted, mostly Data2txt); test too skewed (602 contradicted, almost none in QA); report per task | ❌ binary only | ❌ binary only |
| **X5** Rules in the prompt, strict vs lenient (RQ5) | ✅ **primary**: rule labels derived from three-way labels, balanced, so the two rules differ on ~1/3 of items | ⚠️ the rules differ only on not-mentioned sentences (~4–7 %); informative mainly on Data2txt; the `implicit_true` flag (2,012 sentences) allows a third rule ("true world knowledge is acceptable") | ❌ | ❌ |
| **X6** Calibration: dev for temperature, test for ECE (RQ3) | ✅ dev for temperature (three-way and rules), test for evaluation | ✅ dev carved from train **by source_id** (no source crosses splits) | ⚠️ could provide a dev slice, but synthetic | ❌ **evaluation only by licence** (no fitting of temperature or thresholds on it; its RAGTruth dev part is also RAGTruth train) |
| **X7** Demo realism (local RAG) | ❌ single sentences, Wikipedia | ✅ **QA** (MS MARCO questions, 3 retrieved passages, ~300 tokens) is closest to the demo; Summary acceptable; Data2txt (JSON) unlike the demo | ❌ | ❌ |

## 3. Recommendations for Phase 1 (data)

1. **Training mix (binary + three-way + rules), first proposal:**
   - MiniCheck synthetic, all 14,395 pairs (binary).
   - ANLI train, the ~21K MiniCheck hard subset, restricted to premises **not** in ANLI dev/test (three-way labels kept, so the same pairs also feed the three-way question and the rules).
   - RAGTruth train, sentence level, quality = good, rebalanced (e.g. all not-mentioned and contradicted sentences plus an equal number of supported ones), each answer used as a shared context so that training matches the K-question inference format.
   - Size to be fixed against the training budget: ≈35K for the 0.5B (≈ 3–4 h) and a ~10K subset for the 3B (one night).
2. **Length cap 2,048 tokens** (keeps 99 % of RAGTruth); log every excluded item.
3. **Splits:** RAGTruth dev carved from train by `source_id`; ANLI dev for temperature and threshold, ANLI test held out; LLM-AggreFact test held out; LLM-AggreFact is evaluation-only by licence (no training, no fitting on dev).
4. **Labels:** binary evaluation on RAGTruth with LLM-AggreFact's labels; our span-derived three-way labels for X4/X5, with the 98.6 % agreement reported.
5. **Checks to add to the build:** the leakage check (§5.3 of the plan) must also compare against LLM-AggreFact test claims; a claim-only baseline for the ANLI negation shortcut (present in train, reversed in dev/test).
6. **Report per RAGTruth task** (QA / Summary / Data2txt): they differ in format (JSON vs text), hallucination rate (18 % vs 64 % of test answers) and contradiction rate.

## 4. Limitations of this EDA

- Sentence splitting is rule-based (the Phase 0 splitter); 6 % of RAGTruth spans cross a sentence boundary and are assigned to every sentence they touch.
- Token counts use the Qwen2.5 tokenizer without the chat template (~60 extra tokens per prompt).
- Context-vs-source matching for LLM-AggreFact documents found only 27 % exact matches with RAGTruth sources (formatting differs); the overlap conclusion relies on claim (sentence) matching, which is exact for 92 % of the subset.
