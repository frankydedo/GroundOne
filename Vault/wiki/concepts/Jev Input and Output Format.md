---
type: concept
tags:
  - jev
  - architecture
  - typesafe
---
# Jev Input and Output Format

Unlike traditional Large Language Models (LLMs) which rely on conversational text prompts and output unstructured text, [[Jev]] (a [[System One Models|System One Model]]) uses a specialized Input/Output architecture designed for rapid, structured decision-making.

## Input: State and Instructions

Jev separates its input into two distinct components:

1. **State (Context)**: Unstructured text data representing the context, a document, or the environment's state. Crucially, this state is processed only once and stored in the [[KV Cache]].
2. **Instructions (Questions)**: Natural language criteria or questions that the model must evaluate against the state. Multiple questions can be passed in a single query and evaluated in parallel without recomputing the shared State.

*Example Input JSON:* 
```json
{
  "model": "jev-latest",
  "state": "Hi, I've been trying to connect my Stripe account for 3 days...",
  "questions": {
    "is_urgent": {
      "type": "noul",
      "instructions": "The message conveys urgency or time-sensitivity"
    }
  }
}
```

## Output: Structured Decisions

Jev **does not generate text**. It skips autoregressive token-by-token generation and instead uses a fixed output head to provide direct, TypeSafe primitive data types instantly.

*Example Output JSON:*
```json
{
  "nouls": {
    "is_urgent": {
      "type": "noul",
      "noul": 0.999
    }
  }
}
```

1. **Noul (Boolean / Binary)**: Outputs a True or False decision (e.g., Pass/Fail).
2. **Choice (Categorical)**: Selects a single option from a predefined list of valid categories.
3. **Score (Numerical)**: Grades the input against an ordered numerical rubric.

### Calibrated Probabilities
Alongside every output, Jev provides a probability score that TypeSafe describes as **calibrated** (via [[Reinforcement Learning with Calibrated Decisions]]). The *intended* meaning is that a `True` at 90% is correct about 90% of the time, which would allow confidence thresholds. **This is a vendor claim**: no public calibration measurement exists (see [[Calibration]], [[Expected Calibration Error]]).

### Zero Schema Hallucinations
Because Jev is forced to output one of the predefined types (Noul, Choice, or Score) rather than generating a sequence of text, it cannot produce invalid schemas or formatting. This is a property of the output interface, not of correctness: it can still pick the wrong valid option.
