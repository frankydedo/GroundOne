# Abstract

## TITLE
Engineering and Fine-Tuning a Local System One Router for Multi-Agent Systems

## State of the Art (SOTA)
The current paradigm for autonomous multi-agent systems relies heavily on standard Large Language Models (LLMs) acting as decision-making orchestrators. Generating the JSON payload for a tool call requires an autoregressive token-by-token decoding process. This mechanism introduces a severe latency bottleneck, making real-time agentic execution impractical on local consumer hardware.
Furthermore, generative models tend to be overconfident and struggle in scenarios where no available tool is suitable, leading to schema hallucinations and erroneous routing.

## Our Proposal
This thesis project introduces a customized framework and decision model inspired by the emerging *"System One"* paradigm. Rather than relying on pre-existing zero-shot solutions, the work focuses on the entire Machine Learning Engineering pipeline to build an ultra-fast agentic orchestrator from scratch, executed 100% locally on Apple Silicon architecture.

Instead of generating text, the router dynamically translates tool schemas into *Textual Options*. Leveraging the MLX framework's KV Cache, the "State" (user prompt) is processed only once, computing the probabilities of the available options in parallel.
The central contribution of this work is the **LoRA Fine-Tuning** of a compact LLM (e.g., Qwen3.5-4B). The model is trained specifically on data derived from the *Berkeley Function Calling Leaderboard (BFCL)* to optimize tool selection and calibrate uncertainty, teaching the system to abstain when lacking evidence in order to ensure epistemic honesty.

The project will demonstrate how combining inference parallelization with fine-tuning dedicated to "Typed Decisions" slashes routing latency from seconds to tens of milliseconds. This approach overcomes the operational limits of traditional generative systems while operating entirely within the memory constraints of a personal computer.
