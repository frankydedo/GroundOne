# Expected Benchmark Results & Hypotheses

This document outlines the theoretical expectations and hypotheses for the unified benchmarking suite comparing three architectural paradigms for tool routing: **LightningRoute O(1)**, **LLM-Based Generative O(L)**, and **Rizzo-Flow O(N)**.

## 1. Latency Expectations

### Asymptotic Scaling with Tool Numerosity
* **LightningRoute (O(1) Logit Extraction):** 
  * **Hypothesis:** Latency will remain virtually constant (flat line) across all tool buckets (1-5 to 21-25 tools). 
  * **Why:** The approach relies on a single forward pass over the prompt. While the prompt length $L$ increases slightly with more tools, the compute overhead of prefill phase scaling is minimal compared to autoregressive decoding. Time spent is dominated by a single constant-time matrix multiplication.
* **LLM-Based Router (O(L) Generative):**
  * **Hypothesis:** Latency will be strictly higher than LightningRoute and will scale slightly upwards as tool numerosity increases. 
  * **Why:** The system incurs the Time-To-First-Token (TTFT) overhead plus the sequential decode time of generating the output tokens (even just 1-2 tokens). As the context window $L$ grows with more tools, KV-cache lookup and attention computation during generation will slightly degrade performance.
* **Rizzo-Flow (O(1) Evaluative via Choice):**
  * **Hypothesis:** Latency will be practically identical to LightningRoute, scaling as O(1) and remaining flat across tool buckets.
  * **Why:** When mapping tools to Rizzo-Flow's `ChoiceQuestion` primitive, Rizzo-Flow dynamically compiles the options into a single multiple-choice prompt (assigned to letters A, B, C...). It executes a single forward pass and extracts the logits, exactly like LightningRoute. The only difference should be negligible overhead from parsing complex schemas and general-purpose REST API layers.

### Scaling with Model Parameters (0.5B vs 3B vs 7B)
* **Hypothesis:** Latency will increase proportionally with the number of parameters across both LightningRoute and LLM-Based routers.
* **0.5B:** Ultra-low latency (expected <20ms for O(1)).
* **3B:** Balanced performance, optimal for edge/local deployments.
* **7B:** Highest latency, expected to hit the memory bandwidth limits of the Apple Silicon unified memory.

## 2. Accuracy Expectations

### Base vs. Fine-Tuned Models
* **LLM Base Models:** 
  * **Hypothesis:** Base models will demonstrate high variance in accuracy and may struggle to strictly adhere to the structural constraints (outputting only a single tool name/letter). Accuracy will likely degrade significantly on large tool buckets (context confusion).
* **LLM Fine-Tuned Models:**
  * **Hypothesis:** Will achieve near-perfect instruction following and high routing accuracy. This represents the absolute "Generative Upper Bound" for our specific dataset.
* **LightningRoute:**
  * **Hypothesis:** Accuracy will closely mirror the LLM Fine-Tuned models. Since logit extraction forces the output into a constrained probability space (A-Z), it bypasses token hallucinations completely. It is expected to maintain robust accuracy even at 7B parity, without the generative time penalty.
* **Rizzo-Flow Native:**
  * **Hypothesis:** Expected to serve as the algorithmic upper bound for accuracy. By performing granular O(N) evaluation, it minimizes context-window crowding, potentially outperforming 7B models on buckets with 20+ tools, but at an unacceptable latency cost for real-time systems.

## 3. Predicted Percentile Distributions (p50, p90, p99)

* **LightningRoute:** Will exhibit incredibly tight distributions. p99 should be very close to p50 because there is no variance introduced by variable-length autoregressive decoding.
* **LLM-Based:** Will exhibit wider distributions. p99 will skew higher due to occasional verbose generation (hallucinating explanations before the tool name) or KV-cache memory constraints.
* **Rizzo-Flow:** Will exhibit the same tight distribution as LightningRoute, with only minor absolute latency differences due to Python API overhead.

## Summary Conclusion
If the hypotheses hold, the final scatter plot (Latency vs. Tool Numerosity) will demonstrate that **LightningRoute and Rizzo-Flow (System 1 Architectures)** provide completely flat, O(1) latency across all tool buckets. In contrast, the **O(L) Generative models** will have higher base latency that scales upwards as prompt size increases. LightningRoute and Rizzo-Flow will prove that we can achieve the high accuracy of a fine-tuned generative LLM without paying the autoregressive decode penalty!
