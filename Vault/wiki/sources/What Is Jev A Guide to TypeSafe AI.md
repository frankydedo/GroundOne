---
type: source
author: S. Runkle, H. Lovell
date: 2026-09-18
tags: [jev, langchain, typesafe-ai, agents]
---
# What Is Jev? A Guide to TypeSafe AI’s System One Model

**Raw file**: `raw/What Is Jev? A Guide to TypeSafe AI’s System One Model_ingested.md`

## Summary
A LangChain blog post detailing how Jev fits into the agent loop and how to use it via the `langchain-typesafe` integration.

## Key Insights
- **Agent Loop Bottleneck**: Traditional agent loops are slow and costly because every decision requires a full LLM call. Jev addresses this.
- **Question Types**: 
  1. *Choice*: Pick from options.
  2. *Score*: Rate an input.
  3. *Noul*: Boolean (yes/no) probability.
- **LangChain Integration**: `TypeSafeClassifier` from `langchain-typesafe` allows invoking Jev with state and questions.
- **Middleware Use Cases**:
  - `ModelRouterMiddleware`: Routes tasks to smaller or larger models based on criteria.
  - `AutoModeMiddleware`: Uses Jev as a guardrail to check and block risky tool calls before they execute.
