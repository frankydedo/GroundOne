---
type: source
author: "Luyu Gao, Zhuyun Dai, Panupong Pasupat, Anthony Chen, Arun Tejasvi Chaganty, Yicheng Fan, Vincent Y. Zhao, Ni Lao, Hongrae Lee, Da-Cheng Juan, Kelvin Guu (CMU, Google Research, UC Irvine)"
date: 2023
venue: "ACL 2023, Long Papers, pp. 16477–16508 (arXiv 2210.08726; the raw file is arXiv v3 and page 1 does not state the venue)"
url: "https://arxiv.org/abs/2210.08726"
tags: [source, paper, attribution, post-hoc-editing, revision, retrieval, verify-and-revise, hallucination]
---
# Gao 2023 – RARR: Researching and Revising What Language Models Say, Using Language Models

**Raw file**: `raw/demo/Gao 2023 - RARR, Researching and Revising What Language Models Say (arXiv 2210.08726)_ingested.pdf`

## Overview
RARR (Retrofit Attribution using Research and Revision) is a **post-hoc** pipeline that sits after any text generator. It *researches* the generated passage by producing verification queries and retrieving web evidence, then *revises* the passage so that it agrees with the evidence. It also returns an **attribution report** of at most 5 evidence snippets. The paper defines the task of **Editing for Attribution** and evaluates it on two axes, attribution and **preservation**. It shows that earlier editors buy attribution by rewriting or truncating the text, while RARR improves attribution and keeps the original intent over 90% of the time (§2, §5.3, Table 1).

## Key Insights
1. **Pipeline (§3, Fig. 2).** (a) *Query generation*: PaLM 540B with 6-shot prompts, sampled 3 times, writes questions that together cover the passage. (b) *Retrieval*: Google Search, top 5 pages, 4-sentence sliding-window snippets, re-ranked by a T5-large relevance model, keeping the top 1 per query. (c) *Agreement model*: a chain-of-thought prompt decides whether the passage and the evidence imply the same answer to each query. (d) *Edit model*: runs **only on disagreement** and first names the span to change, then rewrites minimally. Edits longer than 50 characters or 0.5× the text length are rejected (footnote 3).
2. **Feedback source: external evidence, judged by a prompted LLM.** Retrieval supplies the evidence and the same LLM, prompted differently, judges agreement. Detection is per query and evidence pair, so it is localised, close to claim level. The loop runs **once over all retrieved (query, evidence) pairs**, not over repeated generate-verify rounds.
3. **Metrics (§2).** Attribution is a sentence-level extension of AIS (human). The automatic version, auto-AIS, takes for each sentence the maximum NLI entailment probability over the evidence and averages over sentences (Eq. 2). Preservation is intent preservation (human) times a Levenshtein similarity (Eq. 3–4). The two are combined into a harmonic mean, F1_AP.
4. **Results (Table 1).** On PaLM outputs for NQ, RARR raises AIS from 35.4 to 43.4 with preservation 83.1 (F1_AP 57.0). EFEC reaches higher AIS (48.3), but its preservation is only 10.4 (F1_AP 17.1), because it often collapses the passage into one sentence (§6.1). On SQA and QReCC, RARR's F1_AP is 45.9 and 41.5. Attribution improves by up to 13 points absolute while changing only 10–20% of the text.
5. **The gate matters (Table 2, Fig. 8).** Removing the agreement model, so that every piece of evidence triggers an edit, lowers preservation (NQ Lev 89.6 → 82.6) and F1_AP (68.1 → 62.8) and introduces unsupported edits. RARR leaves 90% of already well-attributed inputs (pre-edit AIS > 0.9) unedited (§6.1).
6. **Failure modes (§6.1, Fig. 7).** Misleading evidence causes wrong edits, for example a later re-run channel (MeTV) replacing the original broadcaster (NBC). After a fixed claim in a reasoning chain, the dependent later steps are not updated. Downstream SQA accuracy drops slightly, by up to 2.6 points (Fig. 9).
7. **Limitations (§8–9).** RARR tends to **keep** claims it cannot attribute rather than delete them. Its attribution is permissive: a claim counts as attributed if *any* source supports it, and conflicting evidence is not handled. Attribution does not imply correctness. The system is computationally costly because every stage prompts a 540B LLM, and the authors suggest distilling it into a smaller model. Partially attributed output should be shown as such to avoid misleading readers.

## Relevance to GroundOne
- **Closest precedent for "detect, then repair only what is flagged".** RARR's agreement gate followed by a minimal edit is structurally the demo's loop: GroundOne flags sentences, and the generator rewrites only the flagged ones. RARR's ablation (Table 2) is direct evidence that **gating edits on a verifier** limits over-editing. In the demo, GroundOne replaces RARR's prompted agreement model with a single forward pass of a fine-tuned verifier ([[Verify-and-Revise Loops]]).
- **Preservation must be measured, not only pass rate.** The attribution–preservation trade-off (EFEC) warns that a revise loop judged only by "fraction of sentences now supported" rewards deleting or watering down content. The demo's evaluation should report a preservation measure, for example Levenshtein similarity or sentences dropped, next to the verified-pass rate.
- **Three-way verdicts address a stated gap.** RARR has no notion of *contradicted* versus *unattributable* and keeps unattributable claims. GroundOne's split between contradicted and not mentioned lets the policy treat them differently, for example rewriting contradictions but only highlighting unsupported additions, and flagging rather than silently keeping unsupported content ([[Guardrails and Policies]]).
- **Different setting.** RARR retrieves fresh web evidence *after* generation (open-world attribution). GroundOne verifies against the document the RAG pipeline already retrieved (closed-book groundedness). In the demo the evidence is fixed and local, so no web search is needed, which fits the locality pillar ([[Groundedness Verification]], [[On-Device Inference]]).
- **The cost the authors flag is what GroundOne addresses.** RARR calls a 540B LLM for every query, agreement check and edit, and the authors themselves propose a smaller distilled model. GroundOne is that kind of component for the detection step.

## Links
- Concepts: [[Verify-and-Revise Loops]], [[Groundedness Verification]], [[Hallucination Detection]], [[Retrieval-Augmented Generation]], [[Natural Language Inference]], [[Guardrails and Policies]], [[Demo Application]]
- Related sources: [[Madaan 2023 - Self-Refine, Iterative Refinement with Self-Feedback (arXiv 2303.17651)]], [[Gou 2024 - CRITIC, LLMs Can Self-Correct with Tool-Interactive Critiquing (arXiv 2305.11738)]], [[Liu 2023 - Evaluating Verifiability in Generative Search Engines]], [[Min 2023 - FActScore]]
