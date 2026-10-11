---
title: "PremAI 2026 - LLM quantization guide, GGUF vs AWQ vs GPTQ vs bitsandbytes"
url: https://blog.premai.io/llm-quantization-guide-gguf-vs-awq-vs-gptq-vs-bitsandbytes-compared-2026
published: 2026-03-17
accessed: 2026-10-11
extracted_with: trafilatura 2.3.1
---

# LLM Quantization Guide: GGUF vs AWQ vs GPTQ vs bitsandbytes Compared (2026)

## On this page

A 70B parameter model in FP16 takes 140GB of memory. Most people don't have that kind of hardware.

Quantization solves this by compressing weights from 16-bit floats to 4-bit integers, shrinking models by 75% with surprisingly little quality loss. A Llama 3 70B that normally requires multiple A100s can run on a single RTX 4090 after quantization.

But the method matters. GGUF, AWQ, GPTQ, and bitsandbytes take different approaches, each optimized for different hardware and use cases:

- **GGUF**: Best for CPU/Ollama, retains 92% quality at Q4\_K\_M
- **AWQ**: Fastest on vLLM (741 tok/s with Marlin kernel)
- **GPTQ**: Mature GPU option, extensive pre-quantized model library
- **bitsandbytes**: Only option that supports training (QLoRA)

This guide covers how each method works, when to use which, and how to create your own quantized models.

## The Theory: What Quantization Actually Does

Neural network weights are typically stored as 16-bit or 32-bit floating-point numbers. Each weight might be something like 0.0023847 or -1.7632. Quantization maps these continuous values to a smaller set of discrete values.

The simplest approach: divide the weight range into 16 buckets (for 4-bit), assign each weight to its nearest bucket, and store the bucket index instead of the full value.

The math:

```
quantized_value = round((original_weight - min_value) / scale)
scale = (max_value - min_value) / (2^bits - 1)
```
A 4-bit integer can represent 16 different values (0-15). To reconstruct the original weight during inference, you reverse the process: `reconstructed = quantized_value * scale + min_value`.

This introduces error. The reconstructed value won't exactly match the original. The art of quantization is minimizing this error for the weights that matter most.

Simple rounding destroys model quality. A 7B model naively quantized to 4-bit produces garbage. The methods below use smarter approaches.

## GGUF: The CPU-Friendly Format

GGUF (GPT-Generated Unified Format) is a file format created by the llama.cpp project. It's designed for efficient inference on CPUs and Apple Silicon, with optional GPU offloading.

GGUF isn't a single quantization algorithm. It's a container format that supports multiple quantization schemes, all developed by Georgi Gerganov and contributors to llama.cpp.

### How GGUF Quantization Works

GGUF uses block-wise quantization with mixed precision. The model is divided into blocks of weights. Each block gets its own scale factor stored alongside the quantized values.

The naming convention tells you what you're getting:

- **Q4\_0**: 4-bit quantization, simple scheme, \~4.34 bits per weight
- **Q4\_K\_M**: 4-bit with k-quant, medium quality, \~4.58 bits per weight
- **Q5\_K\_M**: 5-bit with k-quant, medium quality, \~5.69 bits per weight
- **Q8\_0**: 8-bit quantization, near-lossless, \~8.5 bits per weight
- **IQ4\_XS**: 4-bit i-quant, extra small, importance matrix optimized

The "K" variants use k-quant, which applies different bit depths to different layers based on their sensitivity. Attention layers might get more bits than feed-forward layers. The "I" variants use importance matrices to guide which weights get higher precision.

### Quality Retention

Based on benchmarks across multiple sources:

- **Q8\_0**: \~99% of FP16 quality
- **Q5\_K\_M**: \~97% of FP16 quality
- **Q4\_K\_M**: \~92% of FP16 quality
- **Q3\_K\_M**: \~85% of FP16 quality
- **Q2\_K**: \~70% of FP16 quality (significant degradation)

Q4\_K\_M is the sweet spot for most users. You get 3-4x size reduction with minimal quality loss.

### When to Use GGUF

GGUF excels when:

- Running on CPU or Apple Silicon (M1/M2/M3)
- Using Ollama, LM Studio, or llama.cpp directly
- Needing hybrid CPU/GPU inference (partial layer offloading)
- Distributing models as single, self-contained files

GGUF is less ideal for:

- Pure GPU inference where speed matters most (AWQ/GPTQ are faster)
- Integration with vLLM (GGUF has overhead in vLLM, \~93 tok/s vs 741 tok/s for AWQ with Marlin)
- Production serving at scale

For [self-hosted LLM deployments](https://www.premai.io/blog/self-hosted-llm-guide) on consumer hardware, GGUF is often the right choice.

## AWQ: Activation-Aware Weight Quantization

AWQ was developed by MIT researchers and takes a fundamentally different approach: not all weights matter equally.

### How AWQ Works

The key insight is that less than 1% of weights are "salient" — they contribute disproportionately to model outputs. AWQ identifies these weights by observing activations during a calibration pass.

The algorithm:

1. Run calibration data through the model
2. Measure which weights produce the largest activation magnitudes
3. Protect salient weights with higher precision or skip quantization entirely
4. Quantize the remaining 99%+ of weights to 4-bit

This selective approach preserves model behavior better than uniform quantization. AWQ also applies scaling factors to reduce the dynamic range of weights before quantization, making them easier to represent with fewer bits.

### The Marlin Kernel Advantage

AWQ by itself doesn't guarantee speed. The inference kernel matters enormously.

Benchmark data from JarvisLabs on Qwen2.5-32B with H200:

| Method | Throughput | Quality (Pass@1) | 
|---|---|---|
| FP16 Baseline | 461 tok/s | 56.1% | 
| AWQ (no Marlin) | 67 tok/s | 51.8% | 
| AWQ + Marlin | 741 tok/s | 51.8% | 
| GPTQ + Marlin | 712 tok/s | 46.3% | 

AWQ without an optimized kernel is actually slower than FP16. With the Marlin kernel, it's 1.6x faster than baseline while retaining 92% of code generation accuracy.

This is why kernel support matters when choosing quantization formats.

### When to Use AWQ

AWQ excels when:

- Using vLLM with Marlin kernel support
- Prioritizing inference speed on NVIDIA GPUs (Turing or newer)
- Serving production workloads where throughput matters
- Working with instruction-tuned or chat models (AWQ was optimized for these)

AWQ is less ideal for:

- CPU inference (no support)
- Training or fine-tuning (weights are compressed, not trainable)
- Older GPUs without kernel support

## GPTQ: GPU-Optimized Post-Training Quantization

GPTQ (Generative Pre-trained Transformer Quantization) was one of the first methods to compress LLMs to 4-bit while maintaining quality. It uses second-order information (the Hessian matrix) to minimize quantization error.

### How GPTQ Works

GPTQ quantizes weights layer by layer, compensating for errors as it goes:

1. Select the next weight to quantize
2. Calculate the optimal quantized value considering accumulated error
3. Adjust remaining un-quantized weights to compensate
4. Repeat until all weights are quantized

The "second-order" aspect means GPTQ considers how weights interact, not just their individual values. This produces better results than naive round-to-nearest.

GPTQ requires calibration data to compute the Hessian information. Typically a few hundred samples from a dataset like WikiText or C4.

### GPTQ Performance

From the same JarvisLabs benchmarks:

- **Throughput**: 712 tok/s with Marlin (vs 741 for AWQ)
- **Quality**: 46.3% Pass@1 on HumanEval (vs 51.8% for AWQ)
- **Perplexity**: 6.90 (vs 6.84 for AWQ, 6.56 baseline)

GPTQ is slightly slower and shows more quality degradation than AWQ in these tests, particularly on code generation tasks. However, differences are small enough that your mileage may vary depending on model and use case.

### When to Use GPTQ

GPTQ makes sense when:

- Your toolchain already supports GPTQ (ExLlama, Text Generation Inference)
- You need pre-quantized models (TheBloke has extensive GPTQ collections)
- Using pure GPU inference

GPTQ is less ideal for:

- New deployments where AWQ is an option (AWQ generally matches or beats GPTQ)
- CPU inference (GPU-only)

## bitsandbytes: Dynamic Quantization for Training

bitsandbytes takes a different approach entirely. Rather than pre-quantizing models to a file format, it quantizes on-the-fly during model loading and supports training through quantized weights.

### How bitsandbytes Works

bitsandbytes provides two main quantization modes:

**LLM.int8()** (8-bit): Uses vector-wise quantization with mixed-precision decomposition. It identifies outlier features in activations and processes them in FP16 while quantizing the rest to INT8.

**NF4** (4-bit): Uses NormalFloat4, a data type designed for normally-distributed weights. Instead of uniform buckets, NF4 uses quantiles of a normal distribution, better matching typical weight distributions.

Key features:

- **Double quantization**: Quantizes the quantization constants themselves, saving an additional 0.4 bits per parameter
- **Nested quantization**: Applies multiple quantization layers for extreme compression
- **Training support**: Enables QLoRA, which fine-tunes 4-bit models by training small adapter layers

### QLoRA: The Training Advantage

bitsandbytes enables QLoRA (Quantized Low-Rank Adaptation), which lets you fine-tune massive models on consumer GPUs:

- Load base model in 4-bit (NF4)
- Add small trainable LoRA adapters in FP16
- Train only the adapters (0.1-1% of parameters)
- Merge adapters back into base model

A 65B model that normally requires hundreds of GB for training can be fine-tuned on a single 48GB GPU with QLoRA.

```
from transformers import BitsAndBytesConfig
config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True,
    bnb_4bit_compute_dtype=torch.bfloat16
)
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-3-70b",
    quantization_config=config
)
```
### bitsandbytes Performance

From JarvisLabs benchmarks:

- **Throughput**: 168 tok/s (slower than AWQ/GPTQ, but no pre-quantization needed)
- **Quality**: 51.8% Pass@1 (matches AWQ)
- **Perplexity**: 6.67 (best quality retention of all methods tested)

bitsandbytes preserves quality better than other methods but runs slower because quantization happens dynamically rather than being pre-computed.

### When to Use bitsandbytes

bitsandbytes excels when:

- Fine-tuning models with QLoRA
- Loading models without pre-quantized weights available
- Prioritizing quality over inference speed
- Using Hugging Face Transformers ecosystem

bitsandbytes is less ideal for:

- Production serving (pre-quantized AWQ/GPTQ are faster)
- CPU inference (GPU-only currently)

For teams running [fine-tuning workflows](https://docs.premai.io/finetuning/overview?ref=premai.io), bitsandbytes with QLoRA is often the most practical approach.

## Head-to-Head Comparison

| Feature | GGUF | AWQ | GPTQ | bitsandbytes | 
|---|---|---|---|---|
| **Best for** | CPU/Ollama | vLLM production | GPU inference | Training | 
| **Quality retention** | 92% (Q4\_K\_M) | 95% | 90% | 95%+ | 
| **Speed (vLLM)** | 93 tok/s | 741 tok/s | 712 tok/s | 168 tok/s | 
| **CPU support** | Yes | No | No | No | 
| **Training support** | No | No | No | Yes (QLoRA) | 
| **Pre-quantized models** | Many | Growing | Many | N/A | 
| **Calibration required** | Optional | Yes | Yes | No | 

## Creating Your Own GGUF Quants

The most common reason to create your own quants: you've fine-tuned a model and need to deploy it efficiently.

### Setup

```
# Clone llama.cpp
git clone https://github.com/ggml-org/llama.cpp
cd llama.cpp
# Build
cmake -B build
cmake --build build --config Release
# Install Python dependencies
pip install -r requirements.txt
```
### Convert to GGUF

```
# Convert HuggingFace model to GGUF FP16
python convert_hf_to_gguf.py /path/to/your/model \
    --outfile model-f16.gguf \
    --outtype f16
```
### Quantize

```
# Basic Q4_K_M quantization
./build/bin/llama-quantize model-f16.gguf model-q4_k_m.gguf Q4_K_M
```
For better quality at aggressive quantization levels (IQ3, IQ2), use an importance matrix:

```
# Generate importance matrix from calibration data
./build/bin/llama-imatrix \
    -m model-f16.gguf \
    -f calibration-text.txt \
    --chunk 512 \
    -o imatrix.dat
# Quantize with importance matrix
./build/bin/llama-quantize \
    --imatrix imatrix.dat \
    model-f16.gguf \
    model-iq4_xs.gguf \
    IQ4_XS
```
The importance matrix tells the quantizer which weights matter most, improving quality for extreme compression.

### Test Your Quant

```
# Run perplexity test
./build/bin/llama-perplexity \
    -m model-q4_k_m.gguf \
    -f wikitext-2-raw/wiki.test.raw
# Test inference
./build/bin/llama-cli \
    -m model-q4_k_m.gguf \
    -p "The capital of France is" \
    -n 50
```
Lower perplexity is better. Compare against your FP16 baseline to measure quality loss.

## Creating AWQ Quants

AWQ quantization requires GPU and calibration data.

### Setup

```
pip install autoawq transformers
```
### Quantize

```
from awq import AutoAWQForCausalLM
from transformers import AutoTokenizer
model_path = "your-model-path"
quant_path = "your-model-awq"
quant_config = {
    "zero_point": True,
    "q_group_size": 128,
    "w_bit": 4,
    "version": "GEMM"
}
# Load model
model = AutoAWQForCausalLM.from_pretrained(
    model_path,
    low_cpu_mem_usage=True,
    use_cache=False
)
tokenizer = AutoTokenizer.from_pretrained(model_path)
# Quantize (uses default calibration data)
model.quantize(tokenizer, quant_config=quant_config)
# Save
model.save_quantized(quant_path)
tokenizer.save_pretrained(quant_path)
```
Quantization takes 10-15 minutes for 7B models, around an hour for 70B models. GPU memory peaks at roughly 1.5x the model size during quantization.

### Custom Calibration Data

For domain-specific models, use your own calibration data:

```
# Prepare calibration samples
calibration_data = []
for example in your_dataset:
    text = tokenizer.apply_chat_template(
        example["messages"],
        tokenize=False
    )
    calibration_data.append(text)
# Quantize with custom data
model.quantize(
    tokenizer,
    quant_config=quant_config,
    calib_data=calibration_data
)
```
Using domain-relevant calibration data improves quality for your specific use case.

### Run with vLLM

```
from vllm import LLM, SamplingParams
llm = LLM(
    model="your-model-awq",
    quantization="awq"
)
outputs = llm.generate(
    ["Hello, my name is"],
    SamplingParams(temperature=0.8, max_tokens=100)
)
```
## Choosing the Right Method

**Use GGUF when:**

- Running locally with Ollama or LM Studio
- Deploying on CPU or Apple Silicon
- Need single-file distribution
- Want the broadest hardware compatibility

**Use AWQ when:**

- Deploying with vLLM in production
- Maximizing throughput on NVIDIA GPUs
- Serving chat or instruction models

**Use GPTQ when:**

- Pre-quantized GPTQ models are available and AWQ isn't
- Using ExLlama or other GPTQ-native tooling

**Use bitsandbytes when:**

- Fine-tuning with QLoRA
- Need to load models without pre-quantized versions
- Quality is more important than inference speed

For production deployments, the decision often comes down to your inference stack. If you're using [vLLM for serving](https://docs.premai.io/guides/general/serve-models-to-vllm?ref=premai.io), AWQ with Marlin is typically fastest. If you're using Ollama or llama.cpp, GGUF is the native format.

## Quality vs Speed: Making the Tradeoff

Every quantization method trades precision for efficiency. The question is how much quality you can afford to lose.

**Quality-critical applications** (medical, legal, financial):

- Start with Q5\_K\_M (GGUF) or 8-bit
- Test thoroughly on your specific use case
- Consider bitsandbytes for best quality retention
- The [LLM evaluation benchmarks](https://www.premai.io/blog/llms-evaluation-benchmarks-challenges-and-future-trends/) guide covers how to measure quality

**Speed-critical applications** (real-time chat, high-throughput serving):

- AWQ with Marlin kernel
- Test latency under realistic load
- Monitor quality metrics in production

**Memory-constrained** (consumer GPUs, edge devices):

- GGUF Q4\_K\_M or Q3\_K\_M
- Consider [small language models](https://www.premai.io/blog/small-language-models-slms-for-efficient-edge-deployment/) purpose-built for constrained environments

**Training/fine-tuning:**

- bitsandbytes with NF4 + QLoRA
- See the [fine-tuning guide](https://www.premai.io/blog/enterprise-ai-fine-tuning-from-dataset-to-production-model/) for complete workflows

## Common Issues and Solutions

### "Model quality degraded significantly"

- Try a higher-quality quant (Q5\_K\_M instead of Q4\_K\_M)
- Use importance matrix for GGUF aggressive quants
- Use domain-specific calibration data for AWQ/GPTQ
- Some models are more quantization-sensitive than others

### "AWQ is slower than expected"

- Ensure Marlin kernel is being used (check vLLM logs)
- Verify GPU compute capability is 7.5+ (Turing or newer)
- AWQ without Marlin is slower than FP16

### "GGUF runs slow on GPU"

- Increase `n_gpu_layers` to offload more layers
- Check that CUDA/Metal acceleration is enabled
- Some quant types have more overhead than others

### "Out of memory during quantization"

- AWQ/GPTQ need \~1.5x model size for quantization
- Use `low_cpu_mem_usage=True` flag
- Quantize on a machine with more RAM than your target inference machine

### "Quantized model gives different outputs"

- This is expected. Quantization introduces error
- Run evaluation benchmarks to quantify the difference
- If degradation is unacceptable, use higher precision

## When Quantization Isn't the Answer

Quantization solves one problem: fitting large models into limited memory. But it introduces complexity you might not want to manage.

Consider what you're signing up for:

- **Calibration data selection**: AWQ and GPTQ quality depends on choosing the right calibration samples
- **Format compatibility**: Your quant needs to match your inference stack
- **Quality validation**: Every model needs testing after quantization
- **Re-quantization**: When the base model updates, you quantize again
- **Edge cases**: Quantized models can fail on inputs outside the calibration distribution

For teams focused on building applications rather than managing infrastructure, this overhead adds up.

[Prem](https://www.premai.io/studio?ref=premai.io) handles the model optimization pipeline. You [upload datasets](https://docs.premai.io/datasets/overview?ref=premai.io), [fine-tune models](https://docs.premai.io/finetuning/overview?ref=premai.io) for your domain, and [run evaluations](https://docs.premai.io/evaluations/overview?ref=premai.io) to validate quality. The platform handles optimization for inference without requiring you to become a quantization expert.

The workflow is flexible. Fine-tune on Prem, then export to standard formats if you need to [self-host with vLLM](https://docs.premai.io/guides/general/serve-models-to-vllm?ref=premai.io) or quantize for edge deployment. Or deploy directly through Prem's infrastructure with sub-100ms latency.

For enterprises with [data sovereignty requirements](https://www.premai.io/blog/what-is-a-private-ai-platform), Prem deploys to your AWS VPC or on-premise. You get managed infrastructure without sending data to third parties.

The right choice depends on your team. If you have MLOps expertise and specific optimization requirements, quantize yourself. If you'd rather focus on your application, let the platform handle model optimization.

## The Future of Quantization

Several trends are shaping where quantization is heading:

**FP8 quantization** is gaining traction on newer GPUs (H100, Ada Lovelace). It offers a middle ground between FP16 and INT8 with better quality retention.

**1-bit and 2-bit models** like BitNet are being explored, though they typically require training-aware quantization rather than post-training compression.

**Adaptive quantization** that adjusts precision based on input is an active research area. Some tokens might need full precision while others can tolerate aggressive compression.

For now, 4-bit post-training quantization with AWQ or GGUF Q4\_K\_M represents the practical sweet spot for most deployments.

## FAQ

### Does quantization affect fine-tuning?

You can't directly fine-tune pre-quantized weights (GGUF, AWQ, GPTQ). Use bitsandbytes with QLoRA to train adapters on a 4-bit base model, then merge adapters back. Alternatively, fine-tune in full precision and quantize afterward.

### Which has better quality, GGUF or AWQ?

Both retain about 92-95% of FP16 quality at 4-bit. GGUF Q4\_K\_M shows 6.74 perplexity vs AWQ's 6.84 in JarvisLabs benchmarks, but differences are minimal. Choose based on your inference stack, not quality expectations.

### Can I convert between formats?

Not directly. GGUF, AWQ, and GPTQ store weights differently and can't be converted without quality loss. Start from FP16 weights and quantize to your target format.

### What's the minimum GPU for AWQ/GPTQ?

Compute capability 7.5+ (Turing architecture: RTX 2000 series, T4, and newer). Older GPUs won't have optimized kernel support.

### How do I know if my quant is good enough?

Run perplexity tests against a held-out dataset. Compare against your FP16 baseline. A perplexity increase of 5-10% is typical for Q4. Beyond 20%, you may notice quality issues in practice.

### Should I use imatrix for all GGUF quants?

Only necessary for aggressive quants (Q3 and below, IQ2, IQ3). For Q4\_K\_M and higher, default quantization works well.

### When should I skip quantization entirely?

If you're spending more time on quantization than on your actual application, consider managed infrastructure instead. Platforms like Prem handle model optimization automatically. Quantize yourself when you have specific hardware constraints or need maximum control over the inference stack.
