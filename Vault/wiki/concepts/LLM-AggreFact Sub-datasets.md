---
type: concept
tags: [concept, benchmark, evaluation, llm-aggrefact, datasets, grounding]
---
# LLM-AggreFact Sub-datasets

Per-sub-dataset reference card for [[LLM-AggreFact]], the main evaluation benchmark of [[GroundOne]]. The headline score is the **unweighted mean balanced accuracy over the 11 sub-datasets** (10 in the MiniCheck paper plus [[RAGTruth]] on the leaderboard). Because the thesis reports per-sub-dataset results, each column needs a short, accurate description. Facts come from the original papers (linked) and from MiniCheck App. C ([[Tang 2024 - MiniCheck]]). Numbers come from our EDA on the **test split** (`Project/EDA`), with lengths in **Qwen2.5 tokenizer** tokens.

## Overview table
| Sub-dataset | Origin paper | Task type | Document | Claim author | Label source | n (test) | Share supported | Doc tokens median / p90 |
|---|---|---|---|---|---|---|---|---|
| AggreFact-CNN | [[Tang 2023 - AggreFact]] | summarization (news) | CNN/DM article | fine-tuned BART / PEGASUS / T5 | inherited from SummEval, FRANK, Polytope, CLIFF (crowd, experts, authors); whole summary | 558 | 0.898 | 560 / 1,059 |
| AggreFact-XSum | [[Tang 2023 - AggreFact]] | summarization (news, extreme) | XSum (BBC) article | fine-tuned BART / PEGASUS / T5 | inherited from Wang'20, CLIFF, Goyal'21, Cao'22; one-sentence summary | 558 | 0.511 | 359 / 729 |
| TofuEval-MediaS | [[Tang 2024 - TofuEval]] | dialogue summarization (topic-focused) | MediaSum interview transcript (~1K words) | GPT-3.5-Turbo, Vicuna-7B, WizardLM-7/13/30B | professional linguists, per sentence, κ = 0.42, plus author review | 726 | 0.763 | 1,025 / 1,178 |
| TofuEval-MeetB | [[Tang 2024 - TofuEval]] | dialogue summarization (topic-focused) | MeetingBank city-council transcript | same 5 LLMs | professional linguists, κ = 0.34, plus author review | 772 | 0.806 | 981 / 1,264 |
| Wice | [[Kamoi 2023 - WiCE]] | fact-checking (citation entailment) | cited web article(s), Common Crawl | **human** (Wikipedia editors) | 5 MTurk workers per subclaim, α = 0.62; partial → unsupported | 358 | 0.310 | 1,286 / 3,658 |
| Reveal | [[Jacovi 2024 - REVEAL]] | reasoning-chain verification (CoT step attribution) | 1 retrieved Wikipedia paragraph (~100 words) | Flan-PaLM-540B, GPT-3 (davinci-003), Flan-UL2-20B | 5 trained annotators, α = 0.49; low-agreement items removed; only "fully attributable" = supported | 1,710 | 0.234 | 112 / 223 |
| ClaimVerify | [[Liu 2023 - Evaluating Verifiability in Generative Search Engines]] | RAG-QA (generative search) | cited webpage(s) | Bing Chat, NeevaAI, perplexity.ai, YouChat | 1 MTurk annotator (34 total), AIS "fully supported"; >82% pairwise agreement on a subset | 1,088 | 0.725 | 1,368 / 4,743 |
| FactCheck-GPT | [[Wang 2024 - Factcheck-Bench]] | fact-checking (atomic claim vs evidence stance) | 1 Google evidence snippet | ChatGPT (GPT-3.5-Turbo), decomposed into atomic claims | 10 in-house experts in pairs, consensus; only "completely support" = supported | 1,566 | 0.240 | 117 / 169 |
| ExpertQA | [[Malaviya 2024 - ExpertQA]] | RAG-QA (long-form, expert domains) | attached evidence passage or webpage | GPT-4 (closed-book, retrieve-and-read, post-hoc), Bing Chat | 1 domain expert (the question author); only "Complete" = supported | 3,702 | 0.803 | 185 / 1,138 |
| Lfqa | [[Chen 2024 - Understanding Retrieval Augmentation for LFQA]] | RAG-QA (long-form, ELI5) | 3–4 retrieved snippets (~100 words each) | WebGPT-175B, GPT-3.5 (davinci-003), Alpaca-7B | 3 MTurk workers, majority, α = 0.71; partial → unsupported | 1,911 | 0.587 | 401 / 547 |
| RAGTruth | [[Niu 2024 - RAGTruth]] | RAG (QA, data-to-text, summarization) | MS MARCO passages, Yelp JSON, CNN/DM news | GPT-3.5/4, Llama-2-7/13/70B-chat, Mistral-7B | 2 trained annotators, span-level, projected to sentences; 91.8% response-level agreement | 16,371 | 0.922 | 606 / 1,110 |

Notes:
- "Partial → unsupported" is the LLM-AggreFact label unification (MiniCheck App. C.2). AggreFact, TofuEval and ClaimVerify keep their own binary labels.
- Dev/test splits: AggreFact, TofuEval, WiCE and ClaimVerify keep their original splits. Reveal, FactCheck-GPT, ExpertQA and Lfqa were split 50/50 by query.
- For RAGTruth's sentence projection and split details, see [[RAGTruth]].

## Grouping by what is being verified
- **Summaries of a fixed document**: AggreFact-CNN/XSum (pre-LLM summarizers; the claim is the whole summary) and TofuEval (LLM-written, sentence level, dialogue input).
- **Retrieve-then-generate answers**: RAGTruth, Lfqa, ClaimVerify, ExpertQA. These are the closest to local RAG.
- **Atomic or step claims vs a single evidence passage**: FactCheck-GPT and Reveal. The contexts are short and most negatives are "evidence is on-topic but does not state it".
- **Human claims vs a cited source**: Wice.

## Implications for GroundOne
- **Length cap.** At a 2,048-token cap most sub-datasets fit easily. The exceptions are **ClaimVerify (p90 4,743)** and **Wice (p90 3,658)**, and the TofuEval and AggreFact-CNN tails are around 1.1–1.3K. Overall 2.4% of LLM-AggreFact test documents exceed 2,048 tokens (EDA report), concentrated in these two sub-datasets.
  - Any truncation changes these two scores.
  - The thesis must choose and state a policy: truncate, chunk and take the maximum score (as WiCE and MiniCheck do), or exclude and log the items.
  - It should report ClaimVerify and Wice with that caveat.
- **Label balance differs widely.** The share supported runs from **0.23 (Reveal) and 0.24 (FactCheck-GPT)** to **0.90 (AggreFact-CNN) and 0.92 (RAGTruth)**.
  - Plain accuracy would reward a constant classifier, which is why the benchmark uses **balanced accuracy** with a single global threshold (0.5).
  - A model trained on RAGTruth-like data (about 90% supported) will be biased towards "supported". That costs most on Reveal, FactCheck-GPT and Wice.
  - Rebalancing or calibrating the training data matters for the macro score.
- **Negatives differ in kind.** In Reveal and FactCheck-GPT most negatives are *irrelevant or insufficient* evidence, i.e. true claims that are not grounded in this passage. In Wice and Lfqa many are *partially* supported. In RAGTruth and TofuEval they are generated hallucinations: contradictions and baseless additions. A strict grounding model (no world knowledge) is right to reject these, but this conflicts with the looser expert labels in ExpertQA.
- **Closest to local RAG**: **RAGTruth** (in-domain, the largest), then **Lfqa** (small retrieved chunk set, about 400 tokens, best agreement, α = 0.71), then **ClaimVerify** and **ExpertQA** (production retrieve-and-generate, but long or noisy evidence). These four should be highlighted as the "RAG subset" alongside the 11-way macro average.
- **Noisy columns**:
  - **ExpertQA** has a single expert annotator with knowledge-aware judgements, and every model scores about 50–61 on it.
  - **AggreFact-CNN** has about 57 negatives in test.
  - **TofuEval** has κ of 0.34–0.42.

  Small differences on these columns should not be over-interpreted. Use paired bootstrap (as MiniCheck does) before claiming wins.
- **Claim granularity varies**: whole summaries (AggreFact), sentences (TofuEval, ClaimVerify, ExpertQA, Lfqa, RAGTruth, Wice), atomic claims (FactCheck-GPT) and CoT steps (Reveal). GroundOne is trained on sentences, so expect weaker transfer on multi-sentence CNN summaries.

## Links
[[LLM-AggreFact]], [[RAGTruth]], [[GroundOne]], [[Groundedness Verification]], [[Datasets for GroundOne]], [[Tang 2024 - MiniCheck]], [[Tang 2024 - LLM-AggreFact Leaderboard]], [[Hallucination Detection]], [[Natural Language Inference]], [[Retrieval-Augmented Generation]]
