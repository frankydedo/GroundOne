---
title: "Hardware Corner 2025 - How fast is the AI Max+ 395 for LLM inference"
url: https://www.hardware-corner.net/how-fast-ai-max-395-llm-20250317/
published: 2025-03-17
accessed: 2026-10-11
extracted_with: trafilatura 2.3.1
---

# How Fast Will a Ryzen AI MAX+ 395 (Strix Halo) System Be for LLM Inference?

AMD’s [Ryzen AI MAX+ 395](https://www.amd.com/en/products/processors/laptop/ryzen/ai-300-series/amd-ryzen-ai-max-plus-395.html) **(Strix Halo)** brings a unique approach to local AI inference, offering a massive memory allocation advantage over traditional desktop GPUs like the RTX 3090, 4090, or even the upcoming 5090. While initial benchmarks suggest that **running a 70B model at 3 tokens per second isn’t very practical**, Strix Halo’s real strength may lie in handling **smaller but still powerful models**, making it a viable alternative to high-end GPU-based setups.

## Performance Expectations

With the ability to allocate **up to 96GB of system memory to the GPU in Windows** and **110GB in Linux**, Strix Halo can load significantly larger models than consumer GPUs capped at **24GB–48GB of VRAM**. This means it could be a much better solution for running **32B models**, which are more practical for fast local inference.

For users working with models like **DeepSeek-V2.5 238B in Q3 or Mistral 123B Q6**, it remains uncertain how well Strix Halo will handle them. However, for models in the **7B–32B range**, Strix Halo’s large memory capacity could make it an excellent choice for efficiency and usability. For example [RTX 3090 GPU can run QwQ 32B with around 20 tokens per second](https://www.hardware-corner.net/guides/qwq-llm-rtx-3090-benchmark/).

## Benchmark Comparisons

A recent review of a **Chinese mini PC prototype (AXB35-2)** featuring Strix Halo with **128GB of memory** provided insight into its real-world performance. Running **DeepSeek R1 Distil Llama-70B Q8**  on **LM Studio 0.3.9** with a **2K context** in Windows (without Flash Attention), the system achieved **\~3 tokens per second**.

For comparison, an **Apple MacBook Pro M4 MAX (40-core GPU, 128GB RAM)** running the same model achieved:

- **5.46 tokens/sec** (GGUF format, no Flash Attention)
- **6.29 tokens/sec** (MLX format, 2K context)
- **5.59 tokens/sec** (MLX, 8K context)
- **6.31 tokens/sec** (MLX, 13K context)

Apple’s **M3 Ultra (Mac Studio)** with **512GB of unified memory and 800GB/s bandwidth** remains a powerful contender, but the flexibility and affordability of Strix Halo could make it a more practical choice for many users.

A traditional desktop system with an RTX 4090 or even the upcoming 5090 will have higher raw processing power, but with only **24GB or 48GB of VRAM**, they struggle with models requiring large memory allocations. Strix Halo’s **ability to load entire models into memory** without offloading to slower storage could make it more efficient for many AI tasks.

Additionally, for **laptop or mini PC users**, Strix Halo eliminates the need for an expensive, power-hungry discrete GPU while still delivering **usable performance for mid-to-large models**.

## Final Thoughts

While early benchmarks show limitations in handling massive 70B+ models at usable speeds, **smaller models up to 32B** could benefit greatly from Strix Halo’s **high memory capacity and integrated efficiency**. Until more systems are available and further testing is conducted, we can’t say for certain how it will perform with the largest models, but for AI enthusiasts looking for a compact and memory-rich alternative to high-end GPUs, **Strix Halo could be a compelling option.**

No comments yet.
