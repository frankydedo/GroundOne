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

## Relevance to GroundOne
- It is the most realistic RAG evaluation available: the errors are natural, the generators are modern, and the subtle "baseless info" cases are exactly what a strict verifier must catch.
- **Training use**: RAGTruth train gives in-domain negatives that NLI data lacks. Watch for leakage, since the [[LLM-AggreFact]] RAGTruth column likely comes from the RAGTruth test split. Its provenance is not stated in the sources.
- Report per task (QA vs data-to-text vs summarization). Data-to-text, with JSON input and a 68.6% hallucination rate, behaves very differently from the other two.

## Links
[[Niu 2024 - RAGTruth]], [[Hallucination Detection]], [[Groundedness Verification]], [[LLM-AggreFact]], [[HHEM]], [[MiniCheck]], [[Ravi 2024 - Lynx]], [[GroundOne]]
