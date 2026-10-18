---
type: source
author: "Shehzaad Dhuliawala, Mojtaba Komeili, Jing Xu, Roberta Raileanu, Xian Li, Asli Celikyilmaz, Jason Weston (Meta AI, ETH Zürich)"
date: 2024
venue: "Findings of ACL 2024 (arXiv 2309.11495; the raw file is arXiv v2, Sep 2023, and page 1 states no venue)"
url: "https://arxiv.org/abs/2309.11495"
tags: [source, paper, hallucination, self-verification, verification-questions, verify-and-revise, prompting]
---
# Dhuliawala 2024 – Chain-of-Verification Reduces Hallucination in Large Language Models

**Raw file**: `raw/demo/Dhuliawala 2024 - Chain-of-Verification Reduces Hallucination in LLMs (arXiv 2309.11495)_ingested.pdf`

## Overview
Chain-of-Verification (CoVe) has one LLM (i) draft a response, (ii) **plan verification questions** about the draft's factual claims, (iii) **answer them independently** of the draft, and (iv) write a final revised response that takes the answers into account (§3, Fig. 1). Every step uses the same base model (Llama 65B, few-shot). **No retrieval or tool is used**: the model checks itself, but the checking is set up so that it cannot simply copy its own hallucinations. CoVe raises precision on list questions and FactScore on biographies, at the cost of many extra generations.

## Key Insights
1. **Four steps and four execution variants (§3.3).** *Joint*: plan and answer in one prompt. *2-step*: questions are answered in a prompt that does not contain the draft. *Factored*: each question is answered in its own prompt, without the draft. *Factor+revise*: adds one explicit cross-check prompt per question that compares each answer with the draft. Verification questions are free-form, not templated.
2. **Feedback source: the same model, isolated from its draft.** The key idea is attention control. When the answers can see the draft (joint), the model tends to repeat its hallucinations. Factored execution avoids this, and factored and 2-step beat joint on every task (§4.3).
3. **Results.** Wikidata list questions (Table 1): precision 0.17 (few-shot) → 0.36 (2-step), with hallucinated entities per answer 2.95 → 0.68 and correct ones 0.59 → 0.38. Closed-book MultiSpanQA (Table 2): F1 0.39 → 0.48. Biographies (Table 3): FactScore 55.9 → 60.8 (joint) → 63.7 (factored) → 71.4 (factor+revise), with average facts per biography dropping from 16.6 to 12.3. CoVe on Llama 65B surpasses ChatGPT (58.7) and PerplexityAI (61.6) on FactScore. PerplexityAI still wins on very rare facts, where retrieval is essential (Fig. 2).
4. **Short questions are answered better than long-form claims (§4.3).** On Wikidata, only about 17% of the entities in the baseline lists are correct, but about 70% of the individual verification questions are answered correctly. Decomposing a claim into atomic checks is what makes self-verification work here.
5. **Yes/no verification is worse (Table 4).** Open questions beat yes/no questions in the factored setting, and the model "tends to agree with facts in a yes/no question format whether they are right or wrong". Model-generated questions also beat rule-based templates.
6. **Precision rises, coverage falls.** Gains come largely from **removing** content: fewer positives on Wikidata, fewer facts in biographies. Instruction tuning (Llama 2 Chat) and CoT do not reduce hallucination on these tasks.
7. **Costs and limitations (§6).** CoVe reduces hallucinations but does not remove them. It covers only directly stated factual errors, not reasoning errors or opinions. It costs more compute because it generates more tokens: the factored variant needs one prompt per verification question, plus one cross-check per question for factor+revise, though these can be batched. Its ceiling is the model's own knowledge, and tool use is left to future work.

## Relevance to GroundOne
- **Generative verification, in contrast to System One verification.** CoVe verifies by *generating*: questions, then answers, then cross-checks, then a rewrite, so its cost grows with the number of claims in generated tokens. [[GroundOne]] verifies all K sentences of an answer in one forward pass with no generated tokens. This is the clearest example of the generative verification cost that a [[System One Models|System One]] verifier avoids ([[Prefill and Decode]], [[LLM-as-a-Judge]]).
- **Closed-book versus grounded.** CoVe checks facts against the model's parametric memory and admits that its ceiling is what the model knows. In RAG, the reference is the retrieved document, so the right question is groundedness against the source, not world knowledge. That is GroundOne's task ([[Groundedness Verification]], [[Retrieval-Augmented Generation]]).
- **Design lessons that transfer to the demo loop.** (a) Per-claim, atomic checking works better than judging a long text as a whole, which supports per-sentence verdicts. (b) The verifier should not be biased by the generator's own context. In the demo, the verifier is a different, separately trained model that sees only document and answer, which is the strongest form of "factored" independence. (c) Yes/no prompts to a generative judge invite agreement bias, one reason to prefer a trained three-way classifier over a prompted yes/no check, such as the fact-checking rail in [[Rebedea 2023 - NeMo Guardrails, Controllable and Safe LLM Applications (arXiv 2310.10501)|NeMo Guardrails]].
- **Precision by deletion.** CoVe's gains partly come from dropping content. The demo should report how much content a revise loop removes, not only how much of what remains is supported (see the preservation metric in [[Gao 2023 - RARR, Researching and Revising What Language Models Say (arXiv 2210.08726)|RARR]]).

## Links
- Concepts: [[Verify-and-Revise Loops]], [[Hallucination Detection]], [[LLM-as-a-Judge]], [[Groundedness Verification]], [[System One Models]], [[Demo Application]]
- Related sources: [[Min 2023 - FActScore]], [[Madaan 2023 - Self-Refine, Iterative Refinement with Self-Feedback (arXiv 2303.17651)]], [[Huang 2024 - Large Language Models Cannot Self-Correct Reasoning Yet (arXiv 2310.01798)]], [[Gou 2024 - CRITIC, LLMs Can Self-Correct with Tool-Interactive Critiquing (arXiv 2305.11738)]]
