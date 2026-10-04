---
type: source
author: "Cheng Niu, Yuanhao Wu, Juno Zhu, Siliang Xu, Kashun Shum, Randy Zhong, Juntong Song, Tong Zhang"
date: 2024
venue: "arXiv:2401.00396v2 (17 May 2024); ACL 2024"
url: https://arxiv.org/abs/2401.00396
tags: [source, paper, dataset, hallucination-detection, rag, benchmark, span-level]
---
# Niu 2024 - RAGTruth

**Raw file**: `raw/Niu 2024 - RAGTruth_ingested.pdf` (16 pages)

RAGTruth is a corpus of about 18,000 responses that LLMs **actually generated** in RAG settings (the hallucinations were not injected), with **span-level** human annotations of hallucinated text. The authors also benchmark the hallucination rates of six generators and several detectors, including a fine-tuned Llama-2-13B. It is the main RAG-specific test set for [[Groundedness Verification]] and one of the 11 datasets in [[LLM-AggreFact]]. Concept page: [[RAGTruth]].

## Overview
- **Tasks (§3.2)**: three RAG-style tasks:
  - **QA**: MS MARCO training questions about daily life, with 3 retrieved passages each.
  - **Data-to-text writing**: Yelp business JSON plus up to 3 reviews, written into an objective overview.
  - **News summarization**: CNN/DailyMail training documents plus recent news.
- **Generators (§3.2)**: GPT-3.5-turbo-0613, GPT-4-0613, Mistral-7B-Instruct, Llama-2-7B/13B/70B-chat (the 70B in 4-bit AWQ). Each input gets one response per model, so 6 responses per instance.
- **Annotation (§3.3)**: annotators are English or Communications graduates from a vendor, paid $25/h, working in Label Studio. Each response is labelled **independently by two annotators**, and a third review resolves large disagreements. Agreement is **91.8% at response level** and **78.8% at span level**.
- **Hallucination taxonomy (§3.1)**: four span types. The "conflict" types are intrinsic and the "baseless" types are extrinsic (see [[Hallucination Detection]]).
  - *Evident Conflict*: a direct contradiction of the context, such as a wrong number or a misspelled name.
  - *Subtle Conflict*: a divergence that changes the contextual meaning, such as swapping in a term with a different implication.
  - *Evident Introduction of Baseless Information*: fabricated details that the context does not support.
  - *Subtle Introduction of Baseless Information*: inferred details, sentiments or norms that cannot be verified from the context.
- **Adaptive-evaluation flags (§3.4)**:
  - `implicit_true`: the span is not in the reference but may be true in the world. It is still labelled a hallucination under the strict RAG definition.
  - `due_to_null`: the model read JSON `null` as "false". 1,928 spans are `implicit_true` (13.5%) and 1,642 are `due_to_null` (11.5%) (Table 10, p.15).

## Key numbers (Table 2, p.6)
| Task | Instances | Responses | Mean context len (words) | Hallucinated responses | % | Spans |
|---|---|---|---|---|---|---|
| QA | 989 | 5,934 | 243 | 1,724 | 29.1% | 2,927 |
| Data-to-text | 1,033 | 6,198 | 354 | 4,254 | 68.6% | 9,290 |
| Summ. (CNN/DM) | 628 | 3,768 | 648 | 1,165 | 30.9% | 1,474 |
| Summ. (recent news) | 315 | 1,890 | 369 | 521 | 27.6% | 598 |
| **Overall** | **2,965** | **17,790** | 381 (max 1,749) | **7,664** | **43.1%** | **14,289** |

Mean response length is 131 words (max 632).

- **Split (§5.2)**: the **test set has 450 instances** (150 per task, chosen at random), which is 2,700 responses at 6 per instance. All the rest is training data. **The paper defines no validation split.**
- **Metrics (§5.3)**: response-level precision, recall and F1, plus span-level precision, recall and F1 computed on **character overlap**.

## Key insights
1. **Even GPT-4-turbo is a weak detector when used as a prompt baseline.** Response-level F1 overall (Table 5, p.7): GPT-3.5-turbo prompt 52.9, GPT-4-turbo prompt 63.4, SelfCheckGPT 58.8, LMvLM 49.4. **Fine-tuned Llama-2-13B scores 78.7** (P 76.9 / R 80.7).
2. **Span level is much harder.** Overall span F1 (Table 6, p.7): GPT-3.5 12.8, GPT-4-turbo 28.3, fine-tuned Llama-2-13B 52.7. GPT-4-turbo's span precision is only 18.4.
3. **Evident hallucinations are easier to catch than subtle ones.** This is shown by span-level recall per type (Fig. 4, p.8).
4. **Baseless information is more common than conflicts**, especially in QA (Fig. 2). Data-to-text has the highest hallucination rate (68.6% of responses), largely because generators mishandle JSON.
5. **The generators differ widely.** Hallucination density is lowest for GPT-4-0613 and highest in number of hallucinated responses for Mistral-7B. Hallucinations tend to come late in QA and summarization responses (Fig. 3).
6. **Detection can reduce hallucinations.** Choosing between two candidate responses with the fine-tuned detector cut the hallucination rate by 21.6–63.2% (Table 7). This is the authors' own measurement.

What was measured and what is claimed: the detector comparisons are the authors' own measurements on their 450-instance test set. The claim that "fine-tuning a small LLM is competitive with GPT-4" rests on a single 13B model trained once for 1 epoch, with full fine-tuning on 4×A100 (§5.1).

## Relevance to GroundOne
- **Label granularity**: the labels are **spans inside the response**, not sentences. To get sentence labels for GroundOne, split each response into sentences and mark a sentence *unsupported* if it overlaps any hallucinated span. This rule is a GroundOne design decision, not something the paper prescribes. Decide explicitly how to treat `implicit_true` spans (strict = unsupported) and `due_to_null` spans.
- **Train/dev/test**: the training portion is 2,515 instances (about 15,090 responses). GroundOne has to **carve its own dev split out of train**, grouped by source instance so that the 6 responses to one context never cross splits.
- **Response-level baselines** are usable as reference points but are not sentence-level: GPT-4-turbo F1 63.4 and fine-tuned Llama-2-13B F1 78.7 (Table 5). The HHEM card reports **balanced accuracy** on RAGTruth-Summ and RAGTruth-QA ([[HHEM]]). [[LLM-AggreFact]] reports BAcc on its own RAGTruth subset ([[Tang 2024 - LLM-AggreFact Leaderboard]]).
- **Context length**: the mean context is 381 words and the maximum 1,749 words. Data-to-text inputs are JSON, so the input format differs from plain-passage RAG.
- **Licence**: not stated in the paper. Check the dataset repository before redistributing derived data.
- **Imbalance**: 43.1% of responses contain a hallucination, but at sentence level the unsupported fraction will be much lower. That makes [[Groundedness Verification|balanced accuracy and AUROC]] more appropriate than plain accuracy.

## Links
- Concepts: [[RAGTruth]], [[Hallucination Detection]], [[Groundedness Verification]], [[Retrieval-Augmented Generation]], [[LLM-as-a-Judge]]
- Related sources: [[Tang 2024 - MiniCheck]], [[Tang 2024 - LLM-AggreFact Leaderboard]], [[Ravi 2024 - Lynx]] (uses the RAGTruth test split inside HaluBench), [[Vectara 2024 - HHEM-2.1-Open model card]]
