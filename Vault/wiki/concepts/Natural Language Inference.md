---
type: concept
tags: [concept, nli, entailment, training-data, groundedness]
---
# Natural Language Inference

**Natural Language Inference (NLI)**, also called recognizing textual entailment, asks for the relation between a **premise** and a **hypothesis**. There are three labels:
- **entailment**: the hypothesis is definitely true given the premise.
- **neutral**: it might be true.
- **contradiction**: it is definitely false.

Groundedness checking is NLI applied with the retrieved context as premise and an answer sentence as hypothesis ([[Groundedness Verification]]). Most encoder hallucination detectors are NLI models or their descendants ([[Hallucination Detection]]).

## Datasets relevant to GroundOne
| | **MultiNLI** ([[Williams 2018 - MultiNLI Broad-Coverage Challenge Corpus]]) | **ANLI** ([[Nie 2020 - Adversarial NLI]]) |
|---|---|---|
| Size | 392,702 train / 20,000 dev / 20,000 test (433k total) | 162,865 train / 3,200 dev / 3,200 test |
| Premise | single sentence, mean 22.3 tokens | multi-sentence passage (A1/A2: 250–600 characters of Wikipedia; A3 adds news, fiction, spoken, WikiHow, RTE) |
| Collection | crowdworkers write E/N/C hypotheses for 10 genres | adversarial human-and-model-in-the-loop, 3 rounds (HAMLET) |
| Label balance | balanced by construction | train E/N/C 52,111 / 68,789 / 41,965; dev and test balanced |
| Label quality | dev/test 5-way validated; 1.8% without a gold label (`-`, exclude) | dev/test verified; **train includes unverified examples** |
| Test labels | **hidden** (Kaggle), so use dev-matched/mismatched | released |
| Licence (as stated) | OANC permissive; some fiction CC BY-SA 3.0 / CC BY 3.0 / public domain; "may be modified and redistributed" | **not stated in paper** (repo: github.com/facebookresearch/anli) |
| Difficulty | ESIM about 72% (2018); RoBERTa about 91% dev | RoBERTa (all data) 53.7% on ANLI test |

## Mapping NLI to supported / unsupported
- **entailment → supported**
- **neutral → unsupported** (baseless information, i.e. not in the context)
- **contradiction → unsupported** (conflict with the context)

This is MiniCheck's mapping for ANLI ([[Tang 2024 - MiniCheck]] §3.3). It matches the [[RAGTruth]] taxonomy, where *baseless* ≈ neutral and *conflict* ≈ contradiction. After mapping, both datasets are about 1/3 supported, so plan class weighting or rebalancing. [[AlignScore]] instead keeps the 3-way head and scores with P(ALIGNED). Its ablation found the 3-way head better than a binary head (Fig. 3). GroundOne could also train on 3 answer letters and sum the two non-entailment probabilities. That is an option, not something the sources tested for decoders.

## Evidence on how useful NLI data is for grounding
- **ANLI helps in moderation.** MiniCheck uses a **21K subset of ANLI examples that fooled the models** together with 14K synthetic examples. "Training on more of ANLI was not effective" (§3.3). The ANLI subset alone reaches only 59.9 average BAcc on [[LLM-AggreFact]], against 74.7 with the synthetic data (Table 6).
- **FT5-ANLI-L** (Flan-T5-L on the full 163K ANLI) scores 61.4 on LLM-AggreFact without threshold tuning. MiniCheck-FT5, the same backbone with better data, scores 74.7 (Table 2).
- **Short-premise NLI can hurt.** [[AlignScore]]'s ablation shows that *removing* NLI data (SNLI, MNLI, ANLI, DocNLI) improved performance on most benchmarks. The authors attribute this to short premises (Fig. 5).
- T5-NLI-Mixed (11B, trained on many NLI sets) is near the bottom of LLM-AggreFact at 61.1 on the leaderboard. Model size does not make up for a mismatch between the training data and the task.
- Hypothesis-only artefacts are strong in SNLI and MNLI and weaker in ANLI ([[Nie 2020 - Adversarial NLI]] Table 6). This is another reason to prefer ANLI.

## Implications for GroundOne training data *(superseded 2026-10-06: GroundOne trains on RAGTruth only, D21; ANLI and MiniCheck data are not used; nothing is selected on LLM-AggreFact, D18)*
1. Use the **ANLI hard subset** (or all rounds, downweighted) as the NLI component, mapped to binary.
2. Use MNLI at most as a warm-up or auxiliary source, given its single-sentence premises.
3. Add long-context, LLM-style data, either [[MiniCheck]]'s C2D/D2C synthetic data or the [[RAGTruth]] training split, which is what moves performance on LLM-AggreFact.
4. Keep NLI dev sets as in-domain sanity checks, but select models on LLM-AggreFact dev and a RAGTruth dev split carved from train.

## Links
[[Groundedness Verification]], [[Hallucination Detection]], [[MiniCheck]], [[AlignScore]], [[HHEM]], [[RAGTruth]], [[LLM-AggreFact]], [[LoRA]], [[Qwen2.5]]

## Related
- Final data choice: [[Datasets for GroundOne]]; the three-way NLI-style labels survive as GroundOne's classes (supported / contradicted / not mentioned), tested out of domain on [[VitaminC]].
