---
type: concept
tags: [lora, qlora, peft, fine-tuning, mlx, training, groundone]
---
# LoRA and QLoRA

## LoRA in one paragraph
**Low-Rank Adaptation** ([[Hu 2022 - LoRA|Hu et al. 2022]]) freezes a pretrained weight matrix $W_0$ and learns an additive low-rank update:
$$h = W_0x + \tfrac{\alpha}{r}\,BAx,\qquad B\in\mathbb R^{d\times r},\;A\in\mathbb R^{r\times k},\;r\ll\min(d,k).$$
$B$ starts at zero, so training starts exactly from the base model. Only $A$ and $B$ are trained, so optimizer state exists only for them. On GPT-3 this cut training VRAM from 1.2 TB to 350 GB and the checkpoint from 350 GB to 35 MB. After training, $BA$ can be **merged** into $W_0$, so there is **no extra inference latency** (§4.1–4.2).

**In plain words:** instead of rewriting the whole model, LoRA learns a small "correction" next to each chosen layer. The correction is tiny to store and can be baked into the weights afterwards.

## QLoRA in one paragraph
**QLoRA** ([[Dettmers 2023 - QLoRA|Dettmers et al. 2023]]) keeps the frozen base in **4-bit** (NF4 + double quantization), dequantizes to BF16 on the fly for each matmul, and backpropagates into LoRA adapters. It adds paged optimizers for memory spikes. Result: a 65B model can be fine-tuned on one 48 GB GPU, and **4-bit QLoRA matches 16-bit LoRA and full fine-tuning** (Table 3).

## What the papers say matters
| Knob | Evidence | Take-away |
|---|---|---|
| **Which modules** | Hu §7.1: under a fixed budget, $W_q{+}W_v$ at r = 4 beats one matrix at r = 8. Dettmers §4/Fig. 2: q/v-only LoRA **could not match** full fine-tuning; "LoRA on all linear transformer block layers are required" | Adapt **all linear layers** (q, k, v, o, gate, up, down) |
| **Rank r** | Hu §7.2: r = 1–8 already match r = 64 on MultiNLI/WikiSQL. Dettmers App. A: with all layers adapted, "LoRA r is unrelated to final performance" (r 8–256) | Small r (8–16) is enough; do not spend memory on rank |
| **α / scale** | Hu §4.1: tuning α ≈ tuning the LR; fix α and tune the LR | Fix scale, sweep LR |
| **Quantized base** | Dettmers: NF4+DQ base matches BF16; the 4-bit 7B base takes about 5 GB | Quantize the frozen base to free memory |
| **Gradient checkpointing** | Dettmers §2: LoRA *input gradients* take 567 MB vs. 26 MB of LoRA weights (7B, batch 1); checkpointing brings them to about 18 MB/sequence | **Activations, not adapters, dominate memory**, so turn checkpointing on |
| **Dropout** | Dettmers App. A: 0.05 helps 7B/13B, not 33B/65B | 0.05 is reasonable for small models |

## Training on a 16 GB M4 (MLX) – checklist
mlx-lm 0.31.3 defaults (in `mlx_lm/lora.py`, checked in the thesis venv): `num_layers=16` (LoRA only on the **last 16 blocks**), `rank=8`, `scale=20.0`, `dropout=0.0`, `grad_checkpoint=False`, `mask_prompt=False`. When no `keys` are given, **every Linear/QuantizedLinear in the selected blocks** gets an adapter (`tuner/utils.py`).
1. **Base precision.** Train on an 8-bit or 4-bit MLX model (MLX affine group quantization, not NF4). This is QLoRA-style training. 0.5B fits easily. For 3B, 8-bit is about 3 GB of weights and 4-bit about 1.7 GB, leaving room for activations.
2. **Coverage before rank.** Following QLoRA §4, try `num_layers = -1`/all (24 blocks for 0.5B, 36 for 3B) before raising the rank. The earlier routing configs (`Project_old/LoRA_Finetuning/LoRA_configs/config_3B_8bit_opt.yaml`) used `lora_layers: 8`, `rank: 8`, `scale: 10`, so an ablation over 8 / 16 / all blocks is the cheapest meaningful experiment. Note that the config's `alpha: 16` key is not an mlx-lm LoRA parameter; mlx-lm uses `scale`.
3. **`--grad-checkpoint`** on for 3B and longer sequences. It trades compute for activation memory.
4. **Batch 1 + gradient accumulation** (as in the existing configs: `batch_size: 1`, `grad_accumulation_steps: 4`) and a `max_seq_length` that covers context + answer + suffix (about 650 tokens for the measured cases).
5. **`--mask-prompt` / loss only on the answer letter.** GroundOne's loss is cross-entropy on the restricted logits at the readout position *(final: three letters A/B/C at every marker, class-weighted; design b)*. The standard LM loss over the prompt would waste capacity and hurt calibration.
6. **Fuse adapters for latency benchmarks** (`mlx_lm.fuse`) so measured latency equals base-model latency (Hu §4.1). Keep unfused adapters if several System One heads share one base.
7. Watch **validation NLL** as well as accuracy. NLL overfitting = overconfidence ([[Calibration]]).

## Relevance to GroundOne
LoRA is how GroundOne turns [[Qwen2.5]] 0.5B/3B into a System One verifier. The merge property means the [[Prefill and Decode]] latency budget does not change after fine-tuning. One base model can host several adapters (verifier, router, ...), swapped cheaply.

## Links
- [[Qwen2.5]], [[Prefill and Decode]], [[KV Cache]], [[Calibration]], [[GroundOne]], [[System One Models]], [[Groundedness Verification]]
- Sources: [[Hu 2022 - LoRA]], [[Dettmers 2023 - QLoRA]], [[Qwen Team 2024 - Qwen2.5 Technical Report]]

## As run in GroundOne (2026-10-10)
Custom MLX loop (not `mlx_lm.lora`): rank 16, α 32 (scale 2.0), dropout 0.05 on **all** linear layers of all blocks; lr 1e-4, cosine with warm-up; token-budget length-bucketed batches; best checkpoint by dev balanced accuracy. 0.5B: all 13,203 answers, 802 steps, 5.5 h, peak 2.6 GB; 3B: 6,500 answers, 403 steps, 12.25 h, peak 5.9 GB. **No gradient clipping**: one 0.5B seed collapsed to a constant predictor and was stopped; the two completed seeds agree ([[Fine-tuning Instability and Seeds]], [[GroundOne Results]]).

## Loading GroundOne adapters outside Python (ingest 2026-10-18)
- MLX Swift LM reads the same `adapter_config.json` + `adapters.safetensors` that mlx-lm writes, wraps quantised layers with `QLoRALinear`, and can fuse or unload an adapter at runtime ([[ml-explore 2026 - mlx-swift-lm LoRA adapters reference]]). Fusing into an 8-bit base re-quantises the weights ([[Apple WWDC 2025 - Explore large language models on Apple silicon with MLX]]), so the demo loads the adapter unfused. Unloading enables one shared base for generator and verifier ([[Demo Application]]).
