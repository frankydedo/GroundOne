---
type: source
author: "Hung-Ting Chen, Fangyuan Xu, Shane Arora, Eunsol Choi"
date: 2024
venue: "COLM 2024"
url: https://arxiv.org/abs/2310.12150
tags: [source, paper, dataset, long-form-qa, retrieval-augmentation, attribution, rag, llm-aggrefact]
---
# Chen 2024 - Understanding Retrieval Augmentation for LFQA

**Raw file**: `raw/Chen 2024 - Understanding Retrieval Augmentation for Long-Form QA (LFQA)_ingested.pdf`

"Understanding Retrieval Augmentation for Long-Form Question Answering" is a controlled study of how retrieved documents change long-form answers. Two variables are varied: the **LM**, with documents fixed, and the **document set**, with the LM fixed. The authors release **SALAD**, a set of sentence-level attribution annotations, which is the **Lfqa** sub-dataset of [[LLM-AggreFact]].

## Overview
- **Questions (§3)**: **ELI5** (Reddit "Explain Like I'm Five"). The WebGPT test set has 271 questions, and **100 random questions** were used for human annotation.
- **Document sets**: each has 3–4 snippets of about 100 words. The sets are:
  - **Human demonstration**: Bing results gathered by WebGPT annotators.
  - **WebGPT retriever**: documents retrieved by the WebGPT model.
  - **Bing Search API**.
  - **Random**: another question's WebGPT documents.

  In a 20-question manual check, the WebGPT, human and Bing sets were sufficient to answer 85%, 50% and 45% of questions respectively.
- **LMs**: **WebGPT (175B)**, **GPT-3.5 (text-davinci-003)** and **Alpaca-7B**. Appendices cover others.
- **SALAD annotation (§5)**: covers six model–document configurations. Each answer sentence is labelled **Supported / Partially Supported / Not Supported** by the reference document set, with the minimal supporting sentences and the unsupported span.
  - For answers generated **without documents**, the WebGPT documents serve as the reference.
- **Annotators**: **Amazon Mechanical Turk**. 10 workers passed the qualification. Pay was $2.5 per example (about $15/h).
- **Agreement**: **3 annotations per sentence**, majority label, with 3.4% of items discarded for lacking a majority. **Krippendorff's α = 0.71**.

## Key results (Table 2)
| Setting | # sent. | Supported | Partial | Not |
|---|---|---|---|---|
| WebGPT + WebGPT docs | 649 | 95% | 2% | 3% |
| GPT-3.5 + WebGPT docs | 659 | 85% | 4% | 11% |
| Alpaca + WebGPT docs | 545 | 61% | 7% | 32% |
| GPT-3.5 + Human docs | 661 | 73% | 7% | 20% |
| GPT-3.5 without docs | 896 | 22% | 8% | 70% |
| Alpaca without docs | 447 | 23% | 6% | 71% |
| **Total** | **3,857** | **59%** | 6% | 35% |

- WebGPT, which was fine-tuned with retrieval, is the most faithful. **Alpaca has ten times more unsupported sentences than WebGPT with the same documents.**
- The **last generated sentence is substantially less attributable** than earlier ones (§6.3).
- Off-the-shelf NLI models are competitive automatic attribution judges, but they trail human agreement by about 15 accuracy points (§7).
- Models can tell random documents from relevant ones: answers with random documents look like answers with no documents.

## How it appears in LLM-AggreFact
- **Claim** = one answer sentence. **Document** = the 3–4 concatenated snippets. Our EDA gives a median of 401 and p90 of 547 Qwen tokens.
- **Label mapping**: only Supported counts as supported. **Partially Supported becomes unsupported** (MiniCheck App. C.2). Our EDA test gives **58.7% supported**, matching the paper's total of 59%.
- The split is 50/50 dev/test (2,029 / 1,911) with no question shared between them. The total of 3,940 is slightly above the paper's 3,857, and the difference is not explained in the sources read.

## Caveats
- About **35% of the sentences (the two "without docs" settings) were generated without seeing the reference document**. They are naturally mostly unsupported, which makes their negatives "off-document" rather than subtle RAG hallucinations. Whether LLM-AggreFact keeps all six configurations is not stated in MiniCheck; the 59% match suggests it does.
- The generators are from 2022–23 (text-davinci-003, Alpaca-7B).

## Relevance to GroundOne
- It is the **closest analogue to local RAG** among the original 10 sub-datasets: an answer is generated from a small set of about 100-word retrieved chunks and each sentence is judged against exactly that context. The context length (about 400 tokens) is typical of a top-k RAG prompt.
- The label balance is moderate (59/41), and the agreement is the highest reported among the sub-datasets (α = 0.71). This makes Lfqa one of the most reliable sub-scores.

## Links
[[LLM-AggreFact]], [[LLM-AggreFact Sub-datasets]], [[Retrieval-Augmented Generation]], [[Groundedness Verification]], [[Natural Language Inference]], [[Liu 2023 - Evaluating Verifiability in Generative Search Engines]], [[Malaviya 2024 - ExpertQA]], [[RAGTruth]], [[GroundOne]]
