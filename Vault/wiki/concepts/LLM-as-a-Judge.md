---
type: concept
tags:
  - evaluation
  - metrics
---
# LLM-as-a-Judge

LLM-as-a-Judge is an evaluation paradigm where a Large Language Model (or a [[System One Models|System One Model]] like [[Jev]]) is used to score, grade, or evaluate the outputs of another AI system.

## Applications
- **Quality Assurance**: Checking if an answer is factually correct based on provided documentation.
- **Routing**: Evaluating prompts to decide which model or tool should handle them.
- **Monitoring**: Running at scale in production (e.g., using MLflow) to catch regressions or hallucinations.

## Key Considerations
- **Rationale vs. Speed**: Traditional LLMs can provide a text-based rationale (explaining *why* an answer is bad), which is great for debugging. However, they are slow and expensive.
- **System One Evaluators**: Models like [[Jev]] provide instant, cheap classifications with calibrated probabilities but lack the ability to generate explanatory text. They are ideal for large-scale evaluation pipelines where cost and latency are critical bottlenecks.
