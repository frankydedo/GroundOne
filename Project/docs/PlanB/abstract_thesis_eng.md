# Abstract

## TITLE
SemIf-Router: Accelerating Multi-Agent Systems via System One Architectures

## State of the Art (SOTA)
The current paradigm for autonomous multi-agent systems and tool-calling frameworks (e.g., LangChain, AutoGPT, Model Context Protocol) relies heavily on standard Large Language Models (LLMs) acting as decision-making orchestrators. In these systems, the agent operates in a continuous loop: reading the state, determining the next action or tool to invoke, generating the tool parameters in text format (JSON), and observing the result.

While highly capable, this approach suffers from a severe latency bottleneck due to the **autoregressive nature of LLMs**. Generating the JSON payload for a tool call requires a token-by-token decoding process, leading to execution times that often exceed several seconds for a single routing decision. When scaling to complex workflows requiring dozens of micro-decisions, this latency compounds, rendering real-time (or near-real-time) agentic execution impractical on consumer hardware without incurring prohibitive cloud API costs.

## Our Proposal
This thesis project introduces **SemIf-Router**, an ultra-fast local agentic orchestrator based on the emerging *"System One"* model paradigm (inspired by the Jev architecture and implemented via the open-source `SemIf` framework).

Instead of textually generating the JSON of the tool to be called, SemIf-Router completely bypasses autoregressive decoding. The system dynamically translates tool descriptions (API schemas) into *Textual Options*. The user prompt (the *State*) is processed a single time and stored in the **KV Cache**. Subsequently, the model evaluates all options (available tools) in parallel, instantly returning a calibrated probability distribution.

By leveraging the native Apple backend (MLX) on a MacBook Pro with 16GB of Unified Memory, the project demonstrates how small-scale models (from 0.5 to 4 billion parameters) can slash routing latency from an order of magnitude of seconds (typical of autoregressive servers like LM Studio or Llama.cpp) to tens of **milliseconds**.

The work entails implementing the router as a drop-in replacement local API, followed by rigorous benchmarking against standard generative models on the *Berkeley Function Calling Leaderboard (BFCL)*. The primary goal is to demonstrate that the System One architecture solves the O(N) latency problem associated with token generation while maintaining a competitive *Recall@1*.

Finally, the research will investigate the **Accuracy vs. Latency trade-off**, comparing the performance of the base model (e.g., Qwen3.5-4B) with an even smaller counterpart (e.g., Qwen2.5-0.5B or MiniCPM-2B), to determine the dimensional lower bound capable of guaranteeing reliable local agentic routing.
