---
type: concept
tags: [concept, hallucination, detection, taxonomy, rag, evaluation]
---
# Hallucination Detection

**Hallucination detection** means deciding whether, and where, generated text contains content that is not supported by a reference. In [[Retrieval-Augmented Generation|RAG]] that reference is the retrieved context. GroundOne addresses the context-grounded, sentence-level version of the problem, which this wiki calls [[Groundedness Verification]].

## What counts as a hallucination
- **Two texts are always needed**: the evidence (the premise or context) and the text being judged (the hypothesis or response). The relation is **asymmetric**: "I visited Iowa" is unsupported by "I visited the US", but the reverse is fine ([[Vectara 2024 - HHEM-2.1-Open model card]]).
- **Context-faithfulness vs world-factuality**:
  - [[Ravi 2024 - Lynx|Lynx]] focuses only on *intrinsic* hallucination, meaning unfaithful to the context. It explicitly leaves factuality against world knowledge out of scope, because user documents may contradict outside knowledge.
  - HHEM and RAGTruth likewise count "**factual but hallucinated**" content (true in the world, absent from the context) as a hallucination.
  - RAGTruth marks these spans `implicit_true` but still labels them hallucinated ([[Niu 2024 - RAGTruth]] §3.4).
  - Note that Lynx uses "intrinsic vs extrinsic" to mean context vs world, while RAGTruth splits the context-based kind further into *conflict* and *baseless*. The terminology is not uniform across papers.
- **RAGTruth taxonomy** (four types, §3.1):
| | Evident | Subtle |
|---|---|---|
| **Conflict** (contradicts the context) | wrong numbers, names | changed meaning or implication |
| **Baseless info** (not in the context) | fabricated details | inferred details, sentiment, norms |

  Baseless info is more frequent than conflict, and subtle types are harder to detect (RAGTruth Fig. 2, Fig. 4). In NLI terms, conflict ≈ *contradiction* and baseless ≈ *neutral* ([[Natural Language Inference]]). This is why both NLI classes map to "unsupported".

## Granularity
| Level | Unit | Example datasets / systems | Metric |
|---|---|---|---|
| Response-level | whole answer | RAGTruth response labels, HaluBench ([[Ravi 2024 - Lynx]]) | P/R/F1, accuracy |
| **Sentence/claim-level** | one sentence vs context | [[LLM-AggreFact]], [[MiniCheck]], **GroundOne** | balanced accuracy, AUROC |
| Atomic-fact-level | decomposed facts | FActScore, FactCheck-GPT (in LLM-AggreFact) | BAcc |
| Span/token-level | character spans | [[RAGTruth]] | char-overlap P/R/F1 |

- Finer granularity is harder. On RAGTruth, the best response-level F1 is 78.7, but the best span-level F1 is only 52.7 ([[Niu 2024 - RAGTruth]] Tables 5–6).
- [[Tang 2024 - MiniCheck|MiniCheck]] found that **atomic-fact decomposition gives no consistent gain** over checking whole sentences, at 2–4× the cost (§7.1). This supports sentence-level checking.
- A sentence-level detector can produce response-level labels: a response is unsupported if any of its sentences is.

## Approaches
1. **NLI / alignment encoders**: a cross-encoder scores a (context, claim) pair.
   - Examples: [[AlignScore]] (RoBERTa-L 355M), [[HHEM]] (flan-t5-base derived), SummaC, T5-NLI-Mixed.
   - Long contexts are handled by chunking and taking the maximum score.
   - They are cheap and give a probability, but most have 512-token limits and are weaker on LLM-generated text.
2. **Small specialized checkers trained on targeted data**: [[MiniCheck]] (Flan-T5-L 770M, RoBERTa and DeBERTa), Bespoke-MiniCheck-7B, FactCG. These reach the level of frontier LLMs on [[LLM-AggreFact]] (about 75 BAcc against about 77 for the best model).
3. **Prompted LLM judges** ([[LLM-as-a-Judge]]): GPT-4 and Claude are prompted to label or extract hallucinated spans.
   - They are strong but expensive. GPT-4 costs about $107 for LLM-AggreFact versus $0.24 for MiniCheck-FT5 ([[Tang 2024 - MiniCheck]] Tables 3–4).
   - As span extractors they have poor precision: GPT-4-turbo has 18.4 span precision on RAGTruth.
4. **Fine-tuned generative detectors**:
   - [[Ravi 2024 - Lynx|Lynx]] is Llama-3 8B/70B, producing reasoning plus a PASS/FAIL verdict.
   - The RAGTruth authors' Llama-2-13B generates the hallucinated spans as output.
   - These are accurate in-distribution, but they decode many tokens and need output parsing (Llama-2-13B-chat was parsable on only about 3% of HaluBench before fine-tuning).
5. **Self-consistency / uncertainty**: SelfCheckGPT samples extra responses, and other methods use token entropy. These do not need the context but perform worse in RAG: SelfCheckGPT gets 58.8 F1 on RAGTruth.
6. **Single-pass logit readout ([[System One Models|System One]]; GroundOne)**: a decoder LLM fine-tuned with [[LoRA]] reads P(answer letter) after one forward pass. It sits between families 2 and 4: it has the capacity of a decoder and its long context, with the cost and calibrated-probability interface of a classifier ([[When System One Beats an LLM]]).

## Open issues relevant to the thesis
- **Benchmarks disagree.** HHEM-2.1 matches GPT-4 on the vendor's RAGTruth-QA numbers, yet is about 4 points below GPT-4 on LLM-AggreFact.
- **Label definitions differ** across datasets (strict RAG vs world knowledge; how `implicit_true` and partial support are treated). Report these choices explicitly.
- **Calibrated scores are rarely evaluated.** All the sources above report BAcc, F1 or accuracy, and none reports ECE. This is a gap GroundOne can fill ([[Calibration]], [[Expected Calibration Error]]).

## Sources
[[Niu 2024 - RAGTruth]], [[Tang 2024 - MiniCheck]], [[Tang 2024 - LLM-AggreFact Leaderboard]], [[Zha 2023 - AlignScore]], [[Vectara 2024 - HHEM-2.1-Open model card]], [[Ravi 2024 - Lynx]], [[Nie 2020 - Adversarial NLI]]. Related: [[GroundOne]], [[Rizzo-Flow]], [[RAG Evaluation Frameworks]].
