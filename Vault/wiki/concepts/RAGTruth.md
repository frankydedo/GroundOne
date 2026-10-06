---
type: concept
tags: [concept, dataset, benchmark, rag, hallucination, span-level, training-data]
---
# RAGTruth

**RAGTruth** ([[Niu 2024 - RAGTruth]]) is a corpus of about 18K responses that LLMs **naturally generated** in [[Retrieval-Augmented Generation|RAG]] settings, with **span-level** human labels for hallucinated content. It is GroundOne's RAG-specific benchmark, and its training portion is a candidate source of in-domain training data. It also appears as a column in [[LLM-AggreFact]] and as a subset of HaluBench ([[Ravi 2024 - Lynx]]).

## Composition
- **Tasks**:
  - QA: MS MARCO with 3 passages per question.
  - Data-to-text: Yelp business JSON plus reviews.
  - News summarization: CNN/DM plus recent news.
- **Generators**: GPT-3.5-turbo-0613, GPT-4-0613, Mistral-7B-Instruct, Llama-2-7B/13B/70B-chat. Each instance has one response per model, so 6 responses per instance.
- **Size**: **2,965 instances, 17,790 responses, 14,289 hallucinated spans**. 43.1% of responses contain at least one hallucination: QA 29.1%, data-to-text 68.6%, summarization about 30% (Table 2).
- **Context length**: mean 381 words, max 1,749. Responses average 131 words, max 632.

## Labels
- **Granularity**: **character spans** inside the response, each with one of 4 types (Evident/Subtle × Conflict/Baseless). See [[Hallucination Detection]].
- **Response label**: hallucinated if the response contains at least one span.
- **No sentence-level labels.** These must be derived, for example by marking a sentence unsupported if it overlaps any span. This rule is a GroundOne choice.
- **Flags**:
  - `implicit_true` (1,928 spans): unsupported by the context but possibly true. Strict RAG counts these as hallucinations.
  - `due_to_null` (1,642 spans): JSON null read as false, labelled as baseless.
- **Quality**: two annotators per response plus a third review. Agreement is 91.8% at response level and 78.8% at span level.

## Splits
- **Test**: 450 instances (150 per task) = 2,700 responses (§5.2).
- **Train**: the remaining 2,515 instances, about 15,090 responses.
- **There is no official dev split.** Create one from train, grouped by instance so that the same context never appears on both sides.
- **Discrepancy**: Lynx/HaluBench describes "the test split that comprised of 900 samples, of which 160 contain hallucinations" (§3.2). The leaderboard's RAGTruth subset sizes are not stated in the sources. Document which version is used.

## Licence
**Not stated** in the paper. Check the official repository before redistributing derived sentence-level labels.

## Known numbers
| System | Metric | Score | Source |
|---|---|---|---|
| Fine-tuned Llama-2-13B | response F1 (overall) | 78.7 | RAGTruth Table 5 |
| GPT-4-turbo prompt | response F1 | 63.4 | RAGTruth Table 5 |
| SelfCheckGPT (GPT-3.5) | response F1 | 58.8 | RAGTruth Table 5 |
| Fine-tuned Llama-2-13B | span F1 | 52.7 | RAGTruth Table 6 |
| HHEM-2.1-Open | BAcc RAGTruth-QA / -Summ | 74.28 / 64.42 | [[Vectara 2024 - HHEM-2.1-Open model card]] (vendor) |
| GPT-4 06-13 zero-shot | BAcc RAGTruth-QA / -Summ | 74.11 / 62.62 | HHEM card |
| Lynx 70B / GPT-4o | accuracy (HaluBench RAGTruth subset) | 80.2 / 84.3 | [[Ravi 2024 - Lynx]] Table 3 |
| Claude-3.5 Sonnet / Bespoke-MiniCheck-7B / MiniCheck-FT5 / AlignScore / HHEM-2.1 / Qwen2.5-0.5B-Instruct | BAcc (LLM-AggreFact column) | 86.1 / 84.0 / 78.0 / 71.7 / 69.9 / 51.6 | [[Tang 2024 - LLM-AggreFact Leaderboard]] |

**Caution**: these figures use different metrics, units (response, sentence or claim) and subsets. Compare only within a row group.

## Role in GroundOne (final, 2026-10-06)
- **The only training source**, plus the dev set (10 % of train sources, by `source_id`) and test **T1** (official test split). See [[Datasets for GroundOne]].
- **Reliability caveats**, to be stated in the thesis:
  - the reported agreement (91.8 % per response, 78.8 % per span) says nothing about the **type** (conflict vs baseless), which is exactly the contradicted vs not mentioned boundary;
  - a 2026 re-annotation of the test split (RT4CHART, arXiv 2603.27752; not ingested) reports 1.68× more hallucinated answers, so the original labels likely under-mark hallucinations.
  - [[VitaminC]] (test T3) gives an independent check of the three-way distinction.
- **Segmentation.** LLM-AggreFact's RAGTruth claims match 76.5 % of the sentences from the regex splitter. Most of the rest are fragments from splitting decimals, or sentences without checkable content ("Sure!", "Elements:"). The final pipeline uses pysbd plus a content rule.

## Relevance to GroundOne
- It is the most realistic RAG evaluation available: the errors are natural, the generators are modern, and the subtle "baseless info" cases are exactly what a strict verifier must catch.
- **Training use**: RAGTruth train gives in-domain negatives that NLI data lacks. Watch for leakage, since the [[LLM-AggreFact]] RAGTruth column likely comes from the RAGTruth test split. Its provenance is not stated in the sources.
- Report per task (QA vs data-to-text vs summarization). Data-to-text, with JSON input and a 68.6% hallucination rate, behaves very differently from the other two.

## EDA findings (GroundOne Phase 1a)
Measured by [[GroundOne 2026 - EDA report]] (Qwen2.5 tokens, rule-based sentence splitter), complemented by the official README ([[Dataset card - RAGTruth README]]). Synthesis and usage rules: [[Datasets for GroundOne]].

**Task sources** (`source` field): QA = **MS MARCO** questions with 3 retrieved web passages ([[Nguyen 2016 - MS MARCO]]); Summary = **CNN/DM** (628 instances; [[Hermann 2015 - Teaching Machines to Read and Comprehend]], [[See 2017 - Get To The Point]]) plus **recent news** (315 instances); Data2txt = **Yelp** business records and reviews as JSON ([[Yelp Open Dataset]]).

**Per task** (responses; share with at least one hallucination; context tokens; K = sentences per answer):

| Task | Train | Test | Hallucinated train | Hallucinated test | Context p50 / p90 | K p50 / p90 |
|---|---|---|---|---|---|---|
| QA | 5,034 | 900 | 31.1 % | 17.8 % | 308 / 475 | 6 / 13 |
| Summary | 4,758 | 900 | 31.1 % | 22.7 % | 552 / 1,297 | 5 / 9 |
| Data2txt | 5,298 | 900 | 69.4 % | 64.3 % | 685 / 965 | 9 / 14 |

- **By generator** (share of responses hallucinated): GPT-3.5 13.5 %, GPT-4 13.7 %, Llama-2-70B 47.0 %, Llama-2-13B 56.6 %, Llama-2-7B 61.8 %, Mistral-7B 65.9 %.
- **Span types** (14,289): Evident Baseless Info 6,237; Evident Conflict 5,324; Subtle Baseless Info 2,527; Subtle Conflict 201. Flags: `implicit_true` 1,928, `due_to_null` 1,642. 6.1 % of spans cross a sentence boundary. The README attributes 9,290 spans (65 %) to Data2txt.
- **Sentence-level classes** (derived from spans; 138,239 sentences): train 105,572 supported / 8,077 not mentioned / 4,658 contradicted; test 18,331 / 999 / 602. **77 % of contradiction spans come from Data2txt**; in QA test only 0.5 % of sentences are contradicted. `implicit_true` covers 2,012 sentences.
- **K distribution**: median 9 (Data2txt), 6 (QA), 5 (Summary); 45 % of answers have K ≥ 8.
- **Lengths**: 22 % of full prompts (context + answer) exceed 1,024 tokens, 1 % exceed 2,048. A 2,048 cap keeps 99 %.
- **Quality flags**: 17,617 good, 144 `incorrect_refusal`, 29 `truncated` (drop the 173).
- **Splits are clean**: no `source_id` in both train and test.
- **Overlap with [[LLM-AggreFact]]** (resolves the "Splits" discrepancy and the leakage caveat above): the LLM-AggreFact RAGTruth subset has 31,711 claims (dev 15,340, test 16,371). 14,046 dev claims match RAGTruth **train** sentences and 14,942 test claims match RAGTruth **test** sentences (359 ambiguous, 2,364 unmatched). So LLM-AggreFact-RAGTruth test = RAGTruth test (report once) and its dev = RAGTruth train (do not use it for calibration or selection). The LLM-AggreFact card confirms that a random sample of RAGTruth train was put in its validation set and that "non-checkworthy claims" were removed ([[Dataset card - LLM-AggreFact]]).
- **Label agreement 98.6 %** between our span-derived binary sentence labels and LLM-AggreFact's labels (29,191 sentences). All 419 disagreements are "ours unsupported, AggreFact supported" and are not explained by the `implicit_true` / `due_to_null` flags (likely a different overlap rule or segmentation; not verified). Plan: LLM-AggreFact labels for binary evaluation, our labels for the three-way classes.
- **Licence**: still not stated in the README.

## Links
[[Niu 2024 - RAGTruth]], [[Hallucination Detection]], [[Groundedness Verification]], [[LLM-AggreFact]], [[HHEM]], [[MiniCheck]], [[Ravi 2024 - Lynx]], [[GroundOne]], [[Datasets for GroundOne]], [[GroundOne 2026 - EDA report]], [[Dataset card - RAGTruth README]], [[ANLI]]
