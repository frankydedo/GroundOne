---
type: concept
tags: [architecture, ai]
---
# System One Models

**System One Models** are a new paradigm of AI architectures defined by [[TypeSafe AI]]. They are designed for fast, intuitive, and immediate decision-making, taking structured decisions that software can use directly, in contrast to the slower, reasoning-heavy text generation of traditional LLMs.

The name likely draws inspiration from Daniel Kahneman's "Thinking, Fast and Slow", where "System 1" is fast, automatic, and intuitive.

## Characteristics
- **No Text Generation**: They do not generate tokens sequentially. Instead, they output structured, primitive data types (Booleans, Scores, Choices) instantly.
- **High Speed & Low Latency**: By skipping the autoregressive generation phase, they process information in milliseconds.
- **Fixed Task Outputs**: They return classification, scoring, or binary decisions over an answer set fixed at call time, based on an input state and instructions. Whether this needs a dedicated output head depends on the implementation (see taxonomy below).

## When to Use Them
They win on closed-form decisions (boolean/score/choice) that are frequent, latency-sensitive and need no rationale; they lose on open-ended generation, reasoning and explanations. See [[When System One Beats an LLM]] for the full analysis and evidence.

## Taxonomy of System One implementations
All known implementations share the contract (state + runtime question + closed answer set → probabilities, no free text) but differ in *how* the probabilities are produced.

| Family | How the decision is read | Examples | State–candidate interaction | Main strength / weakness |
| --- | --- | --- | --- | --- |
| **(a) Proprietary readout head** | Decoder backbone truncated before the LM head + a dedicated output head; shared state in the KV cache, listwise options | [[Jev]] (architecture **inferred** from probing in [[Jevs Architecture Unmasked]], not disclosed) | Full (cross-attention through the decoder) | Best published quality (e.g. 0.883 on the TypeSafe subset, 0.727 on typed-decisions); closed, hosted, calibration claims not independently verified |
| **(b) LM-head logit readout of answer letters** | Prompt as multiple choice; one forward pass; softmax over the logits of the option letters/tokens at the answer position; state prefix shared across questions | [[SemIf]] (frozen Qwen3.5-4B), [[Rizzo-Flow]] (Spark-X2.5 + [[LoRA]] soft-CE fine-tune), **[[GroundOne]]** ([[Qwen2.5]] 0.5B/3B + LoRA, A/B/C = supported / contradicted / not mentioned; *earlier 2-way A/B plan superseded*) | Full | Open, runs locally, trainable with ordinary LoRA; position bias and raw miscalibration unless fine-tuned/temperature-scaled |
| **(c) Bi-encoder contrastive scoring** | State and each candidate embedded separately (frozen LLM + projection heads), cosine similarity, softmax | [[CLM]] (frozen Qwen3-8B, InfoNCE) | Only a final dot product | Very fast with many/reusable candidates (cached embeddings); weaker decision quality on the one reproducible comparison (T-Rex agreement 0.658 vs Jev 0.987) and, by inference, on fine-grained entailment |

Notes:
- Families (a) and (b) are close: both are "one prefill, read a distribution at the end". The difference is whether the distribution comes from a new trained head or from the existing LM head restricted to answer tokens. (b) is what a "single-token logit readout" baseline means in [[When System One Beats an LLM]].
- Family (c) trades interaction for caching. For [[Groundedness Verification]], where the reusable object is the retrieved context and each claim is new, (b) gets the reuse via the [[KV Cache]] without giving up interaction.
- Family (b) is described in detail, with its biases and corrections, in [[Letter-Token Readout]].

## Readout is not generation (GroundOne control B2)
*Correction to an earlier assumption: "a single-token logit readout is the same computation as generating one token" holds only for the forward pass, not for the decision.*
- A family-(b) System One takes the argmax over the **admissible** answer tokens only. A one-token generator takes the argmax over the **whole vocabulary**. In zero-shot systems ([[SemIf]], [[Rizzo-Flow]], GroundOne's untrained B1) the two roughly agree, because the model already tends to answer with the letter.
- After fine-tuning with a loss restricted to the answer letters, they decouple. In GroundOne the three readout letters hold only about 4–5 % of the probability mass at the " Verdict:" markers; left free, the model would write the spaced letter " A".
- **B2** keeps GroundOne's weights and single pass but decides by the full-vocabulary token. T1 three-way falls from 0.769 to 0.521 for the 0.5B (24.7 % format failures) and from 0.832 to 0.761 for the 3B (1.2 % failures). Bootstrap: +0.248 [+0.228, +0.269] and +0.071 [+0.059, +0.083] for the readout.
- **Implication for the definition.** A System One's advantage does not come from "generating one token instead of many", but from **not generating at all**. It asks a closed question, runs one pass and scores the admissible options. The restriction is itself a source of accuracy and format robustness, and matters more the smaller the model. The restricted readout is constrained decoding of length one ([[Constrained Decoding]]). Its probabilities are conditional on the answer being one of the options, so they need [[Calibration]] (see also [[Verbalised vs Logit Confidence]]).
- Related evidence: first-token answers and text answers of zero-shot instruction-tuned models disagree heavily ([[Wang 2024 - My Answer is C (first-token probabilities vs text answers)]]). Letter readouts carry option-ID token bias ([[Zheng 2024 - LLMs Are Not Robust Multiple Choice Selectors]]).

## Example Models
- [[Jev]]: A prominent example of a System One Model created by a team of ex-OpenAI researchers (family a).
- [[SemIf]], [[Rizzo-Flow]]: open reproductions of the interface (family b).
- [[Jevlike]]: another open reproduction (implementation not yet ingested, family unclassified).
- [[CLM]]: contrastive bi-encoder from Stanford/NVIDIA (family c).
