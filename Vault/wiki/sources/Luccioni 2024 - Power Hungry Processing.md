---
type: source
author: "Alexandra Sasha Luccioni, Yacine Jernite, Emma Strubell"
date: 2024
venue: "ACM FAccT 2024 (arXiv 2311.16863)"
url: "https://arxiv.org/abs/2311.16863"
tags: [source, paper, energy, carbon, inference, task-specific, multi-purpose, green-ai]
---
# Luccioni 2024 – Power Hungry Processing: Watts Driving the Cost of AI Deployment?

**Raw file**: `raw/Luccioni 2024 - Power Hungry Processing_ingested.pdf`

## Overview
The first systematic comparison of the **inference** energy and carbon cost of ML systems (Hugging Face, CMU/AI2). It measures 88 models on 10 tasks and 30 datasets, 1,000 inferences per dataset, each set repeated 10 times, **without batching** to mimic in-situ deployment (§3.2). Hardware is one A100-80GB on an 8-GPU AWS node; energy and carbon come from **Code Carbon** (GPU, CPU and RAM breakdown, §3.2). The headline: **multi-purpose generative models are orders of magnitude more expensive than task-specific models** for the same task, even at similar parameter counts (abstract, §4.2).

## Key Insights
1. **Task structure matters more than size (§4.1, Table 2, Fig. 2).** Mean energy per 1,000 inferences ranges from **0.002 kWh for text classification** to 0.047 kWh for text generation and **2.9 kWh for image generation**, a factor of over 1,450. Classification (text or image) is cheapest; generative tasks are over 10× more expensive than classification.
2. **Output length drives cost (§4.1, §4.2.2, Table 4, Fig. 6).** Text generation uses 15× more energy than masked language modelling, which outputs a single token, because each new token needs another forward pass. Emissions correlate with output length, with a steeper slope for decoder-only models (BLOOMz) than for seq2seq models (Flan-T5).
3. **Task-specific vs multi-purpose (§4.2.1, Fig. 3).** On extractive QA (SciQ) the most efficient task-specific models emit 0.3 g CO₂eq per 1,000 inferences against about 10 g for multi-purpose models. The authors' explanation: a task-specific classifier takes a softmax over a two-class vector, while a multi-purpose model generates "positive"/"negative" over the whole vocabulary. On summarization the gap narrows (4–10 g vs 20–30 g).
4. **Zero-shot model costs (Table 3).** Per 1,000 inferences: BLOOMz-560M 0.054 kWh, BLOOMz-3B 0.073 kWh, BLOOMz-7B 0.104 kWh; Flan-T5-base 0.026 kWh to Flan-T5-XXL 0.083 kWh. Accuracy of multi-purpose models is higher on average for text classification, but at several orders of magnitude more emissions (Fig. 4).
5. **Inference reaches training cost (§4.3, Table 5).** BLOOMz-7B reaches parity between training (plus fine-tuning) energy and inference energy after about 592 million inferences.
6. **Caveats stated by the authors.** Idle power of the other GPUs on the node is included (footnote 3); the comparison of task-specific and zero-shot accuracy is imperfect because decision spaces differ (§4.2.1).

## Relevance to GroundOne
- **The closest argument to GroundOne's design.** Luccioni's mechanism (a classifier's restricted softmax vs generating a label over the vocabulary, plus energy that grows with output length) is exactly the difference between GroundOne's restricted A/B/C readout and a generative judge. GroundOne makes the same move *inside* a decoder LLM: it keeps the decoder's capacity and context, but answers like a classifier. See [[System One Models]] and [[Energy of LLM Inference]].
- **Measured on-device confirmation, with a nuance.** GroundOne uses 1.6× (0.5B) and 1.3× (3B) less energy than a terse one-token judge, and 4.1× and 3.4× less than a verbose judge with a rationale. The large gap appears against long outputs, as Luccioni predicts. Against a one-token judge the gap is modest because both pay the same prefill; GroundOne's single long prefill also draws more power (16 W vs 11–14 W).
- **Specialisation over generality.** The paper's conclusion (weigh the utility of general-purpose generative systems against their energy cost) supports the thesis framing of a small specialist verifier instead of a general LLM judge.
- **Units.** BLOOMz-560M at 0.054 kWh per 1,000 inferences is about 194 J per inference on an A100 node including idle GPUs; GroundOne 0.5B uses 5.5 J per whole verified answer on the M4 (SoC only). Hardware, measurement scope and tasks differ, so this is context, not a controlled comparison.

## Links
- Concepts: [[Energy of LLM Inference]], [[System One Models]], [[When System One Beats an LLM]], [[On-Device Inference]], [[LLM-as-a-Judge]]
- Related sources: [[Samsi 2023 - From Words to Watts]], [[Patel 2024 - Splitwise (prefill vs decode phases)]]
