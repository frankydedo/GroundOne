---
type: concept
tags: [inference, latency, prefill, decode, kv-cache, system-one, groundone]
---
# Prefill and Decode

## The two phases of LLM inference
Every request to a decoder-only LLM runs in two phases ([[Pope 2023 - Efficiently Scaling Transformer Inference|Pope et al. 2023]] §2; [[Kwon 2023 - PagedAttention vLLM|Kwon et al. 2023]] §2.2):

| | **Prefill** (prompt phase) | **Decode** (generation phase) |
|---|---|---|
| What | process all $L_{input}$ prompt tokens and fill the [[KV Cache]] | generate output tokens one at a time, each a full forward pass |
| Parallelism | all tokens in **one** forward pass (matrix–matrix) | **sequential** loop of $L_{gen}$ passes (matrix–vector at batch 1) |
| Bottleneck | **compute-bound** (FLOPs; about 2N FLOPs per token) | **memory-bandwidth-bound**: all weights (+ KV cache) are read from memory for every token |
| Hardware efficiency | high: PaLM 540B prefill at 43% MFU (batch 1) to 76% (batch 512) | low: 14% MFU (batch 64) for PaLM 540B (Pope Table 2) |
| Latency shape | grows about linearly with prompt length, but cheap per token | fixed cost **per generated token**; dominates single-request latency (Kwon §2.2) |

**In plain words:** reading is fast because the GPU or Neural Engine can read all prompt tokens at once. Writing is slow because each new word needs the whole model to be loaded from memory again, one word at a time. Pope's PaLM 540B example: prefill of **2048 tokens takes 0.29 s**, while **generating 64 tokens takes 1.82 s** (Table 2).

## Why a System One saves only decode
A [[System One Models|System One]] model, like a generative judge, must still **read** the context and the answer, so prefill is unavoidable. What it removes is the **decode loop**. It returns a probability from the logits of one forward pass instead of writing a verdict, a JSON object or a rationale ([[Jevs Architecture Unmasked|Hume]], [[Jev]]). So:
- the **gain grows with the number of generated tokens it replaces** ($n$) and with the **number of decisions on the same context** ($K$);
- for **one decision answered with one token** ($K=1, n=1$), a generative LLM costs the same: prefill + one step. There is no System One advantage, which is why GroundOne targets sentence-level verification ($K$ sentences per answer) and not single-label routing. See [[When System One Beats an LLM]] and [[GroundOne]].

## Cost model
Let $S$ = shared prefix (context + answer) tokens, $K$ = sentences to verify, $n$ = tokens a generative judge writes per sentence, $t_{dec}$ = time per decode step, and $t_{suffix}$ = time for one forward pass over a short per-sentence suffix (about 10–30 tokens) on top of the cached prefix.
$$T_{gen}\;\approx\;\mathrm{prefill}(S) + K\cdot n\cdot t_{dec}$$
$$T_{S1}\;\approx\;\mathrm{prefill}(S) + K\cdot t_{suffix}$$
Assumptions: both reuse the prefix cache (a fair baseline). The judge's per-sentence question prefill is absorbed into $t_{dec}$. At batch 1, a short suffix pass is weight-load-bound like a decode step, so $t_{suffix}\approx t_{dec}$ to a few $t_{dec}$. Then
$$\frac{T_{gen}-\mathrm{prefill}(S)}{T_{S1}-\mathrm{prefill}(S)}\approx\frac{n\,t_{dec}}{t_{suffix}}\;\approx\;n \text{ (order of magnitude)}.$$
If the generative baseline does **not** reuse the prefix (a new prompt per sentence), $T_{gen}\approx K\cdot\mathrm{prefill}(S)+K n t_{dec}$ and the gap widens further. Possible extension: score all $K$ suffixes in **one batched pass** against the shared prefix (Jev-style parallel branches), giving $T_{S1}\approx\mathrm{prefill}(S)+t_{batch}(K)$.

*Update 2026-10-10.* The formula for $T_{S1}$ above describes **design (a)** (shared prefix + one question suffix per sentence), now the fallback. The default **design (b)** writes a short marker " Verdict:" after each of the $K$ sentences and reads all verdicts from **one** forward pass over the answer, so
$$T_{S1}^{(b)}\;\approx\;\mathrm{prefill}(S + K\,m)$$
where $m$ is the marker length (a few tokens). There is no per-sentence suffix pass and no decode step; the whole cost is one compute-bound prefill. Measured: design (b) is 1.4–1.5× faster than design (a) at K ≥ 14 on the same runtime.

## Thesis preliminary measurement (own, not from a paper)
> **Preliminary measurement by the thesis author**, MLX, 8-bit weights, MacBook Pro M4 16 GB, batch 1. To be repeated with the final benchmark harness (p50/p90/p99, warm-up, several runs).

| Model | Prefill 242 tok | Prefill 441 tok | Prefill 637 tok | Decode |
|---|---|---|---|---|
| Qwen2.5-0.5B | 86 ms | 152 ms | 211 ms | ≈ 7 ms/token |
| Qwen2.5-3B | 544 ms | 941 ms | 1362 ms | ≈ 37–42 ms/token |

Derived (arithmetic on the numbers above):
- Prefill throughput: 0.5B ≈ 0.33–0.36 ms/token (about 2.8–3.0k tok/s). 3B ≈ 2.1–2.25 ms/token (about 450–470 tok/s). Prefill is close to linear in length over this range.
- **One decode step ≈ prefilling about 17–21 tokens** for both sizes. 0.5B: 7 / 0.34 ≈ 20. 3B: 37–42 / 2.15 ≈ 17–20.
- Decode rate: 0.5B ≈ 140 tok/s; 3B ≈ 24–27 tok/s.
- Sanity check against memory bandwidth (approximate; ~~the M4 bandwidth is an Apple spec of about 120 GB/s and is not taken from the wiki sources~~ *superseded 2026-10-10: the 120 GB/s figure is now cited from [[Apple 2024 - MacBook Pro 14-inch M4 tech specs]]; see [[Apple Silicon and MLX]]*): 8-bit weights are about 0.5 GB for 0.5B and about 3.3 GB for 3B, giving lower bounds of about 4 ms and about 27 ms per token. The measured 7 ms and 37–42 ms fit decode being **memory-bound** with overhead.

**Illustrative example** ($S$ = 637, $K$ = 5 sentences; $t_{suffix}$ is an *assumption* ≈ 10 ms for 0.5B and ≈ 50 ms for 3B, still to be measured). *Superseded 2026-10-10: GroundOne now uses design (b), one pass per answer, and the measured latencies are in the section "GroundOne measured latency and energy" below. The example is kept as the original reasoning.*
| Scenario | 0.5B | 3B |
|---|---|---|
| Generative judge, terse ($n$ = 1) | 211 + 5·1·7 ≈ **246 ms** | 1362 + 5·1·40 ≈ **1.56 s** |
| Generative judge, short verdict/JSON ($n$ = 30) | 211 + 5·30·7 ≈ **1.26 s** | 1362 + 5·30·40 ≈ **7.4 s** |
| System One (GroundOne) | 211 + 5·10 ≈ **0.26 s** | 1362 + 5·50 ≈ **1.6 s** |

Reading: with a one-letter judge the two are equivalent, as the theory predicts. With any verdict longer than a few tokens, the System One is about 4–5× faster at $K$ = 5, and the gap grows linearly in $n$ and $K$. Prefill sets a floor that **no** architecture removes. For 3B at 637 tokens that floor is about 1.4 s, a demo-UX argument for the 0.5B verifier.

## Splitwise: the two phases at datacenter scale
[[Patel 2024 - Splitwise (prefill vs decode phases)|Splitwise]] (Patel et al., ISCA 2024) characterises the phases on production Azure traces with Llama2-70B and BLOOM-176B on H100/A100 (§III):
- **Compute- vs memory-bound.** "Batching during the prompt phase is compute-bound, whereas the token phase is limited by memory capacity" (Insight V). TTFT grows almost linearly with prompt length because prefill keeps the GPU busy (Fig. 5a).
- **Decode dominates end-to-end time** even for long prompts and short outputs: for BLOOM-176B a 1,500-token prompt phase takes as long as 6 output tokens (Insight III).
- **Power.** Prefill power rises with batch size towards TDP; decode power stays flat because the phase is memory-bound (Insight VI, Fig. 8). Power-capping slows prefill a lot and decode hardly at all (Fig. 9).
- **Hardware.** Decode does not need the newest GPU (Insight VII), which motivates running the phases on different machines with KV-cache transfer.

## GroundOne measured latency and energy (2026-10-10)
Final measurements (MLX in-process, M4 16 GB, 200 T1 answers for latency, 100 for energy; [[GroundOne Results]]):

| System | s/answer at K ≥ 14 | J/answer | Net power |
| --- | --- | --- | --- |
| GroundOne 0.5B / 3B (design b, one prefill) | **0.41 / 2.57** | **5.5 / 33.1** | 16.2 W |
| Terse judge 0.5B / 3B (prefill + short decode) | 0.80 / 4.44 | 8.9 / 43.3 | 13.5 / 14.2 W |
| Verbose judge 0.5B / 3B (prefill + rationale decode) | 2.51 / 15.86 | 22.5 / 111.7 | 11.6 / 10.9 W |

- **Speed** follows the theory: the System One removes decoding, so it is ≈2× faster than the terse and ≈6× faster than the verbose judge at K ≥ 14, and the gap grows with K.
- **Energy** follows Splitwise's power characterisation: GroundOne's single long prefill is compute-bound and draws more power (16 W) than the judges' memory-bound decoding (11–14 W). Its energy advantage over the terse judge (1.3–1.6×) is therefore **smaller than its speed advantage**. See [[Energy of LLM Inference]].
- **Hardware bound.** On the M4 (120 GB/s), decode is bounded below by weight bytes / bandwidth (≈4 ms/token for 0.5B, ≈27 ms/token for 3B, 8-bit); prefill is not ([[Apple Silicon and MLX]]).

## Levers that act on each phase
- **Prefill**: shorter prompts, **prefix caching / reuse** across questions ([[KV Cache]], [[Kwon 2023 - PagedAttention vLLM|vLLM shared prefix]]), smaller model.
- **Decode**: fewer generated tokens (the System One idea), weight quantization (int8 lowered PaLM 540B decode from 36.9 to 28.5 ms/token, Pope §4.4), GQA/MQA for long contexts (Pope §3.3), batching (raises throughput, not single-request latency).

## Links
- [[KV Cache]], [[System One Models]], [[When System One Beats an LLM]], [[GroundOne]], [[Jev]], [[Jevs Architecture Unmasked]], [[Qwen2.5]], [[LoRA]], [[LLM-as-a-Judge]], [[Groundedness Verification]]
- Sources: [[Pope 2023 - Efficiently Scaling Transformer Inference]], [[Kwon 2023 - PagedAttention vLLM]], [[Patel 2024 - Splitwise (prefill vs decode phases)]], [[Alizadeh 2024 - LLM in a flash]], [[Apple 2024 - MacBook Pro 14-inch M4 tech specs]]
- Also: [[Energy of LLM Inference]], [[On-Device Inference]], [[Apple Silicon and MLX]], [[GroundOne Results]]

## Independent confirmations across hardware (ingest 2026-10-11)
- **Vendor-stated**: Apple attributes the M5's 3.3–4.1× faster time to first token to compute (GPU neural accelerators) and its 1.19–1.27× faster generation to a 1.28× bandwidth increase ([[Apple ML Research 2025 - Exploring LLMs with MLX and the neural accelerators in the M5 GPU]]).
- **Cross-machine**: DGX Spark (more compute, 273 GB/s) prefills 3.8× faster than an M3 Ultra (819 GB/s), which decodes 3.4× faster; decode reaches 65–73 % of theoretical bandwidth ([[EXO Labs 2025 - NVIDIA DGX Spark and Mac Studio, disaggregated inference]]).
- **Edge devices**: across 18 matched pairs, slowdowns accumulate in decode while prompt evaluation changes by at most +16 %; latency modelled as TTFT + (N−1)·TPOT ([[Das 2026 - Large Models for Small Devices, Edge AI Deployment (arXiv 2608.15693)|Das 2026]] §6.3, Eq. 13). Lu 2024 finds prefill compute-bound and architecture-sensitive, decode memory-bound and linear in size ([[Lu 2024 - Small Language Models, Survey, Measurements, and Insights (arXiv 2409.15790)|Lu 2024]]).
- **Consumer GPUs**: Llama 2 7B prefill at 14–15k tok/s on an RTX 5090 vs 3,220 on an M5 Max ([[Presenc 2026 - Local LLM tokens-per-second benchmarks]], attributed but mixed backends): Macs are weakest at prefill, the phase GroundOne uses, so claims about Macs should be about fitting the budget, not raw speed.
- Caution: Wang 2025 calls prefill "bandwidth-bound" (§4.3.2), contradicting all of the above; do not cite it on this point.
- For the thesis: the asymmetry is no longer only an argument from Pope et al. and the own Phase 0 measurement; it is visible in vendor documentation and independent benchmarks on every class of local hardware ([[Local Inference Hardware]]).
