---
type: concept
tags:
  - benchmark
  - evaluation
---
# Berkeley Function Calling Leaderboard (BFCL)

The Berkeley Function Calling Leaderboard (BFCL) is a benchmark designed to evaluate Large Language Models' ability to accurately call functions and tools in real-world use cases. 

## Evolution
- **V1**: Introduced Abstract Syntax Tree (AST) evaluation and executable evaluation across Python and non-Python languages (REST, SQL, Java, Javascript).
- **V2**: Incorporated real-world, enterprise, and OSS-contributed data with a focus on Relevance/Irrelevance detection.
- **V3**: Expanded to multi-turn and multi-step interactions, testing edge cases like missing parameters, missing functions, and long-context resilience.
- **V4**: Evolved into a holistic agentic evaluation by introducing Web Search, Memory, and more complex Multi-turn metrics.

## Key Capabilities Tested
- **Relevance Detection**: Ensuring models do not hallucinate function calls when no tool is appropriate.
- **Parallel and Multiple Functions**: Invoking multiple tools at once or choosing from multiple options.
- **Multi-turn Logic**: Disambiguating or maintaining state across several conversation turns.
- **Agentic Features**: Web search, formatting sensitivity, and latency.

## Links
- [[Function Calling]]
- [[Berkeley Function Calling Leaderboard V4]]
- [[Hugging Face Datasets BFCL]]
