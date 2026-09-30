# Training Results - v1 Dataset (Original BFCL Distribution)

This directory contains the results and adapters from the initial training experiments using the v1 dataset (pre-oversampling and pre-system-prompt optimization). 

The dataset distribution at this stage was:
- Total Train: 2,424
- Abstain (Z) Class: ~37%
- Valid Tool Class: ~63%

## Included Experiments

1. **0.5B_model**: Baseline run using `Qwen2.5-0.5B-Instruct-8bit`.
   - Max Seq Length: 1024
   - Result: ~73.03% Accuracy

2. **0.5B_model_opt**: Hyperparameter optimized run for the 0.5B model (Gradient Acc: 4, Cosine Decay, max_seq_length: 512).
   - Result: **86.51% Accuracy**
   - Notes: Strong baseline, extremely fast inference (~166ms/prompt), but heavily bottlenecked on the "Abstain" class (23 false abstains).

3. **3B_4bit_model_opt**: Initial scale-up to 3 Billion parameters, utilizing 4-bit quantization to fit into Apple Silicon 16GB VRAM limit.
   - Max Seq Length: 512
   - Result: **86.18% Accuracy**
   - Notes: Slower inference (~602ms/prompt) and mathematically destroyed precision due to 4-bit compression. Yielded identically the same performance as the 0.5B model (same error breakdown: 19 false abstains).

4. **3B_model_opt**: Full 8-bit precision 3B model (Capping max_seq_length to 512 allowed fitting it into VRAM).
   - Max Seq Length: 512
   - Result: **87.83% Accuracy**
   - Notes: 8-bit precision successfully improved confidence, dropping False Abstains down to 12. Best model on the v1 dataset.

## Error Analysis Insight
Across all models in v1, the model practically never picked the wrong tool (only 6 times out of 304 test cases). 85%+ of all errors were related to deciding *whether* to abstain (`Z`).

This led to the creation of the **v2** dataset, which introduces an aggressive system prompt and oversamples the Abstain class to ~43% to tackle this final boundary.
