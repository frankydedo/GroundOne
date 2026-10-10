Source: https://huggingface.co/FluidInference/d1-omni-600m-coreml (revision 8ae382b1f2e5b9b7e33008515a40df4ecdfcebdb) — retrieved 2026-10-10

---
license: other
license_name: lfm1.0
license_link: LICENSE
base_model: LiquidAI/d1-omni-600M
library_name: coreml
pipeline_tag: text-classification
tags:
- coreml
- apple-silicon
- neural-engine
- decision-model
- liquid
- lfm2.5
- moderation
---

# d1-omni-600M · Core ML

Core ML conversion of the text path of Liquid AI's [d1-omni-600M](https://huggingface.co/LiquidAI/d1-omni-600M)
(revision `02b55d70`): the LFM2.5 encoder trunk plus the decision head, answering typed questions (yes/no, choice,
score) in one forward pass with zero generated tokens. The vision and audio encoders are not included.

Swift runtime and demos: [FluidUse](https://github.com/FluidInference/FluidUse) (`D1OmniManager`, `D1OmniModelStore`,
`ModerationDemo`).

## Files

| file | |
|---|---|
| `d1-omni-text.mlpackage` | one fp16 multifunction package (729 MB, weights shared) |
| `tokenizer.json`, `config.json` | upstream tokenizer and config (calibration temperatures) |
| `LICENSE` | LFM Open License v1.0 |

Functions are named `L{tokens}_K{options}_B{batch}`: `L64/L128/L256_K2_B1` and `_B8` (yes/no, one or eight questions
per call) and `L128/L256_K8_B1` (up to eight options). Inputs: `input_ids`, `attention_mask` (B, L), `marker_pos`,
`marker_mask` (B, K), `qtype` (B,), all int32. Output `logits` (B, K): divide by the temperature in
`config.json` and softmax over the used marker slots (a yes/no reads as [no, yes]). Prompt layout follows upstream
`prompt.py`.

## Conversion notes

- The trunk and head were rewritten with traceable ops; wrapper vs PyTorch max |Δp| 7.7e-6.
- The Neural Engine's fused `silu` is about 1.4% off, which compounded over 16 SwiGLU MLPs (41 of 492 Snake decisions
  flipped vs PyTorch). SiLU is written as `x * 0.5 * (1 + tanh(x / 2))`, the same function, which the Neural Engine
  computes accurately: 2 of 492 flips, max |Δp| 0.017.
- 99.1% of ops run on the Neural Engine (1,140 of 1,150); the rest are casts, the padding mask and the embedding lookup.

## Results (Apple M5 Pro)

Toxicity on 5,000 Civil Comments test comments (CC0; clear labels: rater toxicity 0 or ≥ 0.5; prompt ≤ 256 tokens),
question "Is this comment toxic?" with the Civil Comments annotators' definition of toxic, flagged at P(toxic) ≥ 0.8:

| | |
|---|---|
| agreement with human labels | 95.4% (toxic recall 67.8%, precision 82.4%) |
| flags that differ from PyTorch | 0 of 5,000 |
| Neural Engine only (1 per call) | 102 comments/s |
| GPU only (8 per call) | 215 comments/s |
| Neural Engine + GPU together | 267 comments/s |

Single question on the Neural Engine: about 4.6 ms at 64 tokens, 6.6 ms at 128.

## License

The weights are Liquid AI's, under the [LFM Open License v1.0](LICENSE): free to use and redistribute, but commercial
use is not licensed for entities with $10M or more in annual revenue.

