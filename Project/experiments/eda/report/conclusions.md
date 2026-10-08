## 1. Summary

The EDA has two parts:
- **Part A** describes the three source datasets of the GroundOne dataset: RAGTruth (training source and test T1), LLM-AggreFact (test T2) and VitaminC (test T3).
- **Part B** describes the dataset built from them (`Project/data/processed/groundone/`, counts in its `DATACARD.md`). It focuses on the properties that shape the experiments and their interpretation.

**Part A: sources**
- **RAGTruth hallucinations are concentrated by task and by generator.**
  - Data-to-text answers are hallucinated about 2–4 times as often as QA or summaries (share of answers with at least one span).
  - Llama-2 and Mistral answers carry most of them; GPT-3.5/4 answers are almost clean.
  - *Baseless* spans (→ not_mentioned) outnumber *Conflict* spans (→ contradicted), and *Subtle Conflict* is very rare (201 spans).
- **LLM-AggreFact sub-datasets differ widely** in document length (median 112–1,368 tokens) and label balance (23–92 % supported).
  - Its macro average weights them equally, although RAGTruth has 56 % of the claims.
  - 2.4 % of its documents exceed the 2,048-token cap and are chunked.
- **VitaminC real test claims are short** (median 18 tokens) and the evidence is one Wikipedia sentence (median 36 tokens).
  - Many claims are numerical: 59 % of supported, 71 % of refuted and 44 % of NEI claims contain a digit.
  - The classes are unbalanced in the release (50 / 29 / 21 %), hence the per-class sample in T3.

**Part B: built dataset**
- **Segmentation.** pysbd with line splitting gives 5 % fewer sentences than the earlier regex splitter (130,381 vs 137,428), mainly because it does not cut decimals.
  - 8.2 % of sentences have no checkable content and are kept as context only.
  - Most of these are headings that introduce a list (6,867); the rest are short fragments (1,982), conversational or refusal formulas (1,055) and citation-only lines (802).
- **Test answers are cleaner than training answers.** In every task, T1 has a lower share of contradicted and not-mentioned sentences than train (e.g. QA contradicted 0.6 % vs 1.6 %). This holds for every generator. Metrics that depend on the base rate (precision, F1 on the minority classes) are therefore not comparable between dev and T1; balanced accuracy and macro recall are.
- **Where the classes come from.**
  - 85 % of contradicted training sentences come from *Evident Conflict* spans alone; *Subtle Conflict* gives only 147.
  - Not-mentioned sentences are 71 % *Evident* and 28 % *Subtle Baseless Info*.
  - The contradicted class is therefore mostly blatant contradictions (wrong numbers, names, facts). Subtle contradictions are barely represented and cannot be evaluated separately.
- **Surface cues exist and must be reported as baselines.**
  - *Word overlap.* The share of a sentence's content words found in the document separates the classes in all three sets (supported 0.64 > contradicted 0.47 > not mentioned 0.40 in T1). On its own it reaches AUROC 0.74 for supported vs not on T1, and 0.70 on VitaminC.
  - *Sentence wording.* A sentence-only classifier reaches a three-way balanced accuracy of 0.66 on Data2txt (chance on QA and Summary). Its strongest not-mentioned cues are Yelp details the business record rarely contains: "100 reviews", "rating google", "wifi", "valet garage", "family owned".
  - A verifier's gain must be measured against these two baselines, per task.

## 2. Consequences for the experiments

1. **Report three baselines that never read the document as a whole:** the majority class, word overlap and sentence-only n-grams. They give the floor against which GroundOne's specialisation is measured, per task.
2. **Use base-rate-independent metrics** (balanced accuracy, macro recall, AUROC) as primary metrics, because the class shares differ between train/dev and T1.
3. **Report results per task and per generator group** (GPT vs open models). The hallucination rate depends strongly on both.
4. **Present the contradicted class as mostly "evident" contradictions.** Claims about subtle contradictions would need data RAGTruth does not provide.
5. **T3 tests the same contradicted vs not-mentioned distinction in a different domain** (Wikipedia, single sentences, many numbers). It is useful precisely because it shares the word-overlap cue but not RAGTruth's Data2txt templates.

## 3. Limitations of this EDA

- Sentence labels depend on the span-to-sentence rule and on the segmentation. Both are validated against LLM-AggreFact's independent labels (98.75 % binary agreement, `DATACARD.md`), but the type (conflict vs baseless) has no published agreement.
- RAGTruth's original labels likely under-mark hallucinations (a 2026 re-annotation of the test split reports 1.68× more hallucinated answers). All class shares above are lower bounds.
- Word overlap is a crude lexical measure (no stemming, no synonyms). It is used as a cue detector, not as a model.
- The test splits were analysed only descriptively. No choice about the data or the model was tuned on them.
