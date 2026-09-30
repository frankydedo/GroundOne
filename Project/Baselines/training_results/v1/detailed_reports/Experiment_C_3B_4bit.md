# Training Report: Qwen2.5-3B-Instruct-4bit (LoRA)

## Dataset Details
- **Included Subsets:** `simple`, `multiple`, `live_simple`, `live_multiple`, `irrelevance`, `live_irrelevance` (From Berkeley Function Calling Leaderboard)
- **Format:** Multiple-choice routing (A, B, C...) with Abstain capability (Z).
- **Test Set Size:** 304 samples

## Training Configuration
Due to the strict 16 GB unified memory limit of the Apple Silicon architecture, the model underwent extreme quantization and sequence length truncation to fit the backward pass graph into VRAM.
- **Base Model:** `mlx-community/Qwen2.5-3B-Instruct-4bit` (Weights: ~1.74 GB)
- **Iterations:** 3,000
- **Batch Size:** 1
- **Gradient Accumulation Steps:** 4 (Effective batch size: 4)
- **Max Sequence Length:** 512 tokens
- **Learning Rate:** 1e-4
- **LoRA Parameters:** Rank = 8, Alpha = 16, Layers = 8
- **Peak Memory Usage:** ~4.65 GB

## Side-by-Side Evaluation

| Metric | Base Model (3B 4-bit) | LoRA Finetuned (3B 4-bit) |
|--------|-----------------------|---------------------------|
| **Accuracy** | 78.62% (239/304) | **86.18%** (262/304) |
| **Inference Time** | 168.93s | 183.21s |
| **Latency per prompt** | 555.68 ms | 602.65 ms |

**Absolute Accuracy Improvement:** **+7.57%**

## Conclusion & Next Steps
The 3B model showcases significantly stronger base reasoning than the 0.5B model, achieving a highly respectable 78.62% out of the box without any fine-tuning (surpassing the *fully fine-tuned* 0.5B model which hit 73.03%). 

By applying LoRA, we successfully pushed the accuracy to **86.18%**. 

While this is our best result yet, it falls slightly short of the target 90%+ goal. The aggressive 4-bit quantization inherently destroys some of the base model's precision and reasoning capability. 

Because our peak memory was only 4.65 GB, we have mathematical room to upgrade to the **8-bit** version of this model, which should restore the lost precision and likely push the fine-tuned accuracy over the 90% threshold.
