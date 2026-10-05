---
type: source
author: "Ryo Kamoi, Tanya Goyal, Juan Diego Rodriguez, Greg Durrett"
date: 2023
venue: "EMNLP 2023, pp. 7561–7583"
url: https://arxiv.org/abs/2303.01432
tags: [source, paper, dataset, nli, fact-verification, wikipedia, claim-decomposition, llm-aggrefact]
---
# Kamoi 2023 - WiCE

**Raw file**: `raw/Kamoi 2023 - WiCE_ingested.pdf`
**Data**: github.com/ryokamoi/wice

WiCE (**Wi**kipedia **C**itation **E**ntailment) is a textual-entailment dataset built from **natural** pairs of claims and cited evidence: a sentence in a Wikipedia article and the web article(s) it cites. Labels are three-way (supported / partially supported / not supported) and are collected per GPT-3.5-generated **subclaim**. It is the **Wice** sub-dataset of [[LLM-AggreFact]] and the only one whose claims were written by **humans**.

## Overview
- **Base data (§2.3)**: the Wikipedia claims of the SIDE dataset (Petroni et al. 2023). The cited web articles were **re-retrieved from Common Crawl** and split into sentences.
- **Claim-Split (§2.1)**: few-shot **GPT-3.5 (text-davinci-002)** decomposes each claim into subclaims, 3.0 on average.
  - Crowd validation found 92.3% of claims fully covered and 97.7% of subclaims correct. Errors in dev and test were fixed by hand.
  - Claims split into one subclaim, or into more than six, were dropped.
- **Filtering**: a RoBERTa-Large DocNLI model removed claims whose subclaims were all trivially entailed. **Only 16.3% of claims were kept.** This was deliberate, to keep the dataset from becoming adversarial for larger models.
- **Annotation**: MTurk workers who passed a 3-example qualification (23 qualified). **5 workers per dev/test example** and 3 for train. Agreement on entailment: **Krippendorff's α = 0.62** (dev).
- **Claim-level labels (§2.3)**: if every subclaim is SUPPORTED, the claim is SUPPORTED. If every subclaim is NOT-SUPPORTED, the claim is NOT-SUPPORTED. Otherwise it is PARTIALLY-SUPPORTED.
- **Sizes (Table 1)**: claims 1,260 / **349** / **358** (train / dev / test); subclaims 3,470 / 949 / 958.
- **Evidence length**: 119.5 sentences per datapoint × 14.0 tokens per sentence, so **about 1.7K tokens on average**.
- **Label distribution (Table 2, dev)**: claims 33.0% supported, **54.7% partially**, 12.3% not supported. Subclaims 55.8 / 18.2 / 25.9.

## Key insights
- Real claims need **inference** much more often than FEVER or VitaminC claims do (Table 3: 52.8% of WiCE subclaims vs 24% FEVER).
- Evidence is far longer than NLI input limits. **Chunk-level "stretching"** (256-token chunks, max over chunks) beats sentence-level stretching. T5-3B trained on ANLI then WiCE reaches claim F1 72.1 vs **human 83.3** (Tables 4–5).
- Claim-Split also helps off-the-shelf NLI models at test time on other datasets.
- GPT-4 few-shot with oracle retrieval reaches claim F1 61.0 and accuracy 77.0. GPT-3.5 is much worse (Table 8).

## How it appears in LLM-AggreFact
- **Claim** = the original Wikipedia sentence (claim level, 358 test). **Document** = the full cited article(s).
- **Label mapping**: only SUPPORTED counts as supported. **PARTIALLY-SUPPORTED becomes unsupported** (MiniCheck App. C.2). Hence the low supported rate: **31.0%** in our EDA test, consistent with the 33% in the dev distribution.
- **Length (our EDA)**: median **1,286** and p90 **3,658** Qwen tokens. Together with ClaimVerify, it has the longest documents in the benchmark.

## Caveats
- About half of the claims are "partially supported". Collapsing that class to unsupported makes WiCE a test of **strict, all-parts** support. A claim with five correct facts and one uncited detail counts as unsupported.
- Citation noise is the *source* of the negatives. Many unsupported claims may be true but simply not covered by the cited page.
- The documents are web pages with possible boilerplate from Common Crawl.

## Relevance to GroundOne
- It is the hardest length case. Many inputs exceed a **2,048-token cap**, so the thesis must state whether it truncates, chunks and takes the maximum (as WiCE and MiniCheck do), or excludes these items.
- The strict mapping of partial support to unsupported matches GroundOne's binary definition. WiCE is therefore a good test of whether the model can catch a *single* unsupported detail in a long, otherwise correct sentence.

## Links
[[LLM-AggreFact]], [[LLM-AggreFact Sub-datasets]], [[Natural Language Inference]], [[Nie 2020 - Adversarial NLI]], [[Tang 2024 - MiniCheck]], [[Groundedness Verification]], [[GroundOne]]
