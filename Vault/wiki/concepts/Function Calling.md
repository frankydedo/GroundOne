---
type: concept
tags:
  - capabilities
  - tools
---
# Function Calling

> **Status (lint 2026-10-05):** archived context. BFCL was the dataset of the earlier tool-routing experiment (LightningRoute, now in `Project_old/`), which was abandoned. The current thesis is [[GroundOne]].


Function Calling (or Tool Use) refers to the capability of a Large Language Model (LLM) to interact with external systems, APIs, or structured functions. Rather than just generating text, the model formulates a structured request (often in JSON) that matches a predefined function signature.

## Modalities
- **Native Function Calling (FC)**: Models explicitly fine-tuned to recognize tool descriptions and output structured calls.
- **Prompting**: Using the model's normal text generation capability to output structured JSON via few-shot or zero-shot prompting.

## Challenges and Evaluation
Frameworks like the [[Berkeley Function Calling Leaderboard]] evaluate models on:
- **Accuracy**: Did it pick the right tool and provide the correct parameters?
- **Relevance Detection**: Does the model know *when not* to call a tool?
- **Complex Topologies**: Parallel execution, multi-step orchestration, or missing parameter handling.
- **Multi-Turn**: Refining parameters over a multi-turn conversation.

## Links
- [[Berkeley Function Calling Leaderboard]]
