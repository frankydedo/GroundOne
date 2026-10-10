---
type: source
author: "Shishir G. Patil et al."
date: 2026-09-28
tags:
  - function-calling
  - leaderboard
  - agents
---
# Berkeley Function Calling Leaderboard V4

**Raw file**: `raw/Berkeley Function Calling Leaderboard (BFCL) V4_ingested.md`

## Overview
The Berkeley Function Calling Leaderboard (BFCL) V4 evaluates the ability of LLMs to call functions (or tools) accurately in real-world scenarios. It evolved from simple tool use (AST metrics) to multi-turn interactions (V3) and holistic agentic evaluation (V4) including web search and memory.

## Key Insights
- **Agentic Evaluation**: V4 introduces web search, memory, and multi-turn capabilities.
- **Top Models**: Anthropic's Claude-Opus-4-5 and Claude-Sonnet-4-5 lead the leaderboard. Other strong models include Gemini-3-Pro-Preview, GLM-4.6, and Grok-4-1.
- **Evaluation Categories**:
  - Web Search, Memory, Multi-turn.
  - Non-live (AST) and Live (AST).
  - Hallucination Measurement (Relevance, Irrelevance).
  - Format Sensitivity.
  - Latency.
- **Function Calling approaches**: Native function calling (`FC`) vs Prompting (`Prompt`).
