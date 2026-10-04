---
type: concept
tags: [system-one, bi-encoder, contrastive-learning, related-work]
---
# CLM (Contrastive Language Models)

**Contrastive Language Models (CLMs)** are a [[System One Models|System One]] design from Stanford University and NVIDIA Research (Kwok, Kang, Suresh, Saad-Falcon, Pavone, Ré, Mirhoseini), published as a **Notion blog post on 2026-09-23** with an open-source inference repo. There is **no peer-reviewed paper**. Released model: **CLM-8B** (`Contrastive-LM/CLM-v0.1-8B`, Apache 2.0).

## Architecture
- **Bi-encoder**: a state encoder and an action (candidate) encoder, each = **frozen Qwen3-8B** (last-token hidden state, normalised) + a trainable ~20M-parameter MLP projection head (4096 → 1536 → 1536 → 512).
- Score = **cosine similarity** between state and candidate embeddings; softmax over candidates = answer distribution. Typed questions (`Noul`, `Choice`, `Score`) are served through a TypeSafe-compatible API by embedding each option's description as a candidate.
- **Training**: bidirectional **InfoNCE** over in-batch state–action pairs; mid-training adds hard negatives to the denominator. Three-stage data recipe: ~60M Nemotron Q&A pairs → ~30M synthetic hard negatives (Gemini 2.5 Flash-Lite) → ~1M agent trajectories with 40% replay.
- **Disaggregation**: state and candidate never attend to each other, so candidate embeddings can be cached; per decision only the new state is encoded. This is the source of the speed advantage when there are many candidates or the candidate set is fixed.

## Evidence (see [[Kwok 2026 - Contrastive Language Models]], [[CLM README]])
| Claim | Evidence quality |
| --- | --- |
| Latency 36–44 ms for 1–1,024 candidates vs Jev 131–579 ms, constrained decoding up to 4.3 s (RTX 4090, 200-token state, 5 trials) | Author measurement, plausible by construction; Jev measured through a remote API |
| Hard-negative mid-training: 52.1% → 69.2% top-1 (~100K held-out questions, 10 hard negatives) | Author measurement on own synthetic data |
| "On par with Jev" on T-Rex, BFCL v4, WikiRacing, Super Mario | Figure only; **contradicted by the repo's own T-Rex files**: agreement with the planner's best move **0.658 vs Jev 0.987** (5 seeds × 60 s), survival equal only because a safety shield intervened 4,883 times for CLM vs 28 for Jev |
| "SOTA" verifier on DeepSWE 81.6% (31/38) and Terminal-Bench 2.1 87.6% (30 tasks) | After task fine-tuning; small task sets, no intervals; Jev used zero-shot |
| Power-law scaling of test InfoNCE loss | Fits only in figures; experiments not in the released branch |

Overall: the **speed** claims are well supported; the **decision-quality parity with Jev** is not supported by the one reproducible comparison.

## Why a bi-encoder is weaker for fine-grained entailment (inference)
*This section is our reasoning, not a result reported by CLM or measured in the thesis.*
- In a bi-encoder the claim and the context are each compressed into one 512-d vector before they interact; the only interaction is a dot product. Entailment depends on token-level alignment (negation, numbers, entities, quantifiers) between a claim and a specific span of the context.
- A cross-encoder / decoder readout (as in [[SemIf]], [[Rizzo-Flow]], GroundOne) lets every claim token attend to every context token across all layers before the decision.
- Consistent indirect evidence: CLM needs a dedicated hard-negative stage for "fine-grained discrimination", and it misses the best T-Rex action ~1/3 of the time even when the option text says "Safe ... Best".
- The bi-encoder's advantage (reusable candidate embeddings) matters little for [[Groundedness Verification]], where each claim is new and there are only two labels; the reusable object there is the **context**, which a decoder readout already shares through the [[KV Cache]].

## Relevance to GroundOne
**Related work only.** Serving requires vLLM + CUDA and Qwen3-8B as a pooling encoder, which does not fit the 16 GB M4 Mac; it is not used as a baseline. It is cited as the third System One family (bi-encoder contrastive scoring) and as an example of why System One claims must be evaluated on decision quality and [[Calibration]], not latency.

## Related
- [[System One Models]], [[Jev]], [[SemIf]], [[Rizzo-Flow]], [[GroundOne]], [[When System One Beats an LLM]]
