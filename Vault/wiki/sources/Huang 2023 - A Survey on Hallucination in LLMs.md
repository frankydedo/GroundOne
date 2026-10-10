---
type: source
author: "Lei Huang, Weijiang Yu, Weitao Ma, Weihong Zhong, Zhangyin Feng, Haotian Wang, Qianglong Chen, Weihua Peng, Xiaocheng Feng, Bing Qin, Ting Liu"
date: 2023
venue: "ACM Transactions on Information Systems (TOIS), doi 10.1145/3703155; arXiv 2311.05232 (2023; ingested PDF is v2, Nov 2024)"
url: "https://arxiv.org/abs/2311.05232"
tags: [source, paper, survey, hallucination, taxonomy, faithfulness, factuality, detection, rag]
---
# Huang 2023 – A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions

**Raw file**: `raw/Huang 2023 - A Survey on Hallucination in LLMs_ingested.pdf`

## Overview
A broad survey (Harbin Institute of Technology, Huawei) of hallucination in LLMs. It proposes an LLM-specific **taxonomy** (§2.3), analyses **causes** across data, training and inference (§3), reviews **detection methods and benchmarks** (§4) and **mitigation** (§5), and devotes a section to **hallucinations in retrieval-augmented generation** (§6). Venue: the PDF carries the ACM TOIS reference format and DOI 10.1145/3703155 (its volume/issue fields "Vol. 1, No. 1, January 2024" look like template placeholders, so cite TOIS with the DOI and verify the volume).

## Key Insights
1. **Classic split (§2.3).** In NLG, *intrinsic* hallucinations conflict with the source; *extrinsic* ones cannot be verified from the source (neither supported nor contradicted).
2. **LLM taxonomy (§2.3.1–2.3.2, Table 1).**
   - **Factuality hallucination**: discrepancy with verifiable real-world facts, either *factual contradiction* or *factual fabrication*.
   - **Faithfulness hallucination**: divergence from the user's input or lack of self-consistency, split into *instruction inconsistency*, **context inconsistency** (output unfaithful to the provided context) and *logical inconsistency*.
3. **Causes (§3).** Data (misinformation, knowledge boundaries, poor alignment data), training (pre-training, SFT beyond the knowledge boundary, RLHF sycophancy), inference (sampling randomness, over-confidence, softmax bottleneck, reasoning failures).
4. **Faithfulness detection families (§4.1.2, Fig. 3).** (1) **Fact-based** overlap (n-grams, entities, relation triples); (2) **classifier-based** (NLI or synthetic-data classifiers; the survey notes the NLI granularity mismatch and cites [[Laban 2022 - SummaC|SummaC]]'s sentence-pair aggregation as a fix); (3) **QA-based** (generate questions, compare answers); (4) **uncertainty-based** (entropy, log-probability); (5) **LLM-based judgement**, with a binary verdict or a k-point Likert scale, via direct, chain-of-thought or in-context prompting, optionally with explanations.
5. **Factuality detection (§4.1.1).** Fact-checking by *external retrieval* (e.g. [[Min 2023 - FActScore|FActScore]]'s atomic facts) or *internal checking* (e.g. Chain-of-Verification), plus uncertainty estimation.
6. **RAG still hallucinates (§6).** Two sources: **retrieval failure** (§6.1: queries, sources, retriever) and the **generation bottleneck** (§6.2): noisy context, context–knowledge conflicts, insufficient use of long contexts, and missing **contextual alignment** (source attribution, faithful decoding such as context-aware decoding).

## Relevance to GroundOne
- **Where GroundOne sits in the taxonomy.** GroundOne detects **faithfulness hallucinations of the context-inconsistency type**: whether each answer sentence is supported by the retrieved document. It does not judge factuality against world knowledge ([[Hallucination Detection]], [[Groundedness Verification]]).
- **Three classes map onto the classic split.** *Contradicted* ≈ intrinsic hallucination (conflicts with the source); *not mentioned* ≈ extrinsic hallucination (unverifiable from the source); *supported* = faithful.
- **Which detection family.** GroundOne is a classifier-based detector built from a decoder LLM: it is fine-tuned like family (2) but keeps the long context of family (5), and replaces the judge's generated verdict with a restricted logit readout. Unlike family (5), it produces no explanation; unlike family (4), its probabilities are trained for the decision and calibrated ([[System One Models]], [[LLM-as-a-Judge]]).
- **Motivation for post-hoc verification in RAG.** §6 is a citable argument that retrieval alone does not remove hallucinations, which justifies a verifier placed after the generator ([[Retrieval-Augmented Generation]]).

## Links
- Concepts: [[Hallucination Detection]], [[Groundedness Verification]], [[Retrieval-Augmented Generation]], [[Natural Language Inference]], [[LLM-as-a-Judge]], [[Calibration]]
- Related sources: [[Laban 2022 - SummaC]], [[Min 2023 - FActScore]], [[Niu 2024 - RAGTruth]], [[Asai 2024 - Self-RAG]], [[Ravi 2024 - Lynx]], [[Tang 2024 - MiniCheck]]
