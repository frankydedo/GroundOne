---
type: concept
tags: [architecture, ai]
---
# System One Models

**System One Models** are a new paradigm of AI architectures defined by [[TypeSafe AI]]. They are designed for fast, intuitive, and immediate decision-making, taking structured decisions that software can use directly, in contrast to the slower, reasoning-heavy text generation of traditional LLMs.

The name likely draws inspiration from Daniel Kahneman's "Thinking, Fast and Slow", where "System 1" is fast, automatic, and intuitive.

## Characteristics
- **No Text Generation**: They do not generate tokens sequentially. Instead, they output structured, primitive data types (Booleans, Scores, Choices) instantly.
- **High Speed & Low Latency**: By skipping the autoregressive generation phase, they process information in milliseconds.
- **Fixed Task Outputs**: They use a modified architecture with fixed output heads to perform classification, scoring, or binary decisions based on an input state and instructions.

## Example Models
- [[Jev]]: A prominent example of a System One Model created by a team of ex-OpenAI researchers.
