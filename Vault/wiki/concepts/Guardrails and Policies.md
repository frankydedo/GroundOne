---
type: concept
tags: [concept, guardrails, policy, rails, audit, demo, enterprise]
---
# Guardrails and Policies

The layer that decides what a user is shown after a model has answered: block, rewrite, flag, hide or abstain, according to rules an organisation sets. In the GroundOne demo the policy decides what happens to each sentence given its verdict ([[Demo Application]]).

## NeMo Guardrails as the reference
- A runtime proxy around an LLM with programmable rails written in Colang; five rail types (input, dialog, retrieval, execution, output); output rails can reject or alter an answer ([[Rebedea 2023 - NeMo Guardrails, Controllable and Safe LLM Applications (arXiv 2310.10501)|Rebedea 2023]], [[NVIDIA 2026 - NeMo Guardrails (GitHub README)]]).
- The fact-checking rail is a yes/no LLM prompt on the whole response, about 80 % accurate on MS MARCO; the hallucination rail is evaluated on 20 questions; integrations name AlignScore and Lynx ([[Zha 2023 - AlignScore]], [[Ravi 2024 - Lynx]]).
- Rails block, deflect or abstain, but do not send the verdict back for a targeted rewrite. Latency about 3× the bare LLM.
- Python only; **anonymous telemetry to NVIDIA is on by default** and must be disabled before start-up, a point against it under the locality pillar ([[Privacy and Data Sovereignty]]).

## Thresholded actions
- CRAG maps a retrieval-evaluator score to three actions with two hand-set, per-dataset thresholds; an "ambiguous" band reduces sensitivity to evaluator errors ([[Yan 2024 - Corrective Retrieval Augmented Generation (arXiv 2401.15884)|Yan 2024]]).
- GroundOne's served rule is the same pattern with a learned, calibrated score: supported iff calibrated P(supported) ≥ τ fitted on dev (D27), else the argmax of contradicted / not mentioned ([[Calibration]], [[Selective Prediction]]).

## Policy design for the demo
- **Strict vs lenient**: block contradicted and not mentioned, or only contradicted (the two policies derived from the three probabilities in the thesis).
- **Threshold**: calibrated τ by default; a stricter value trades coverage for precision ([[Selective Prediction]]).
- **Attempts and failure action**: up to N targeted rewrites ([[Verify-and-Revise Loops]]), then highlight, hide the sentence, or abstain.
- **Audit log**: every draft, verdict and policy decision recorded, which a single yes/no rail does not give per sentence.
- Policies are data (a JSON file), not code: they can be reviewed and versioned like any other configuration.

## Links
- [[Demo Application]], [[Verify-and-Revise Loops]], [[Groundedness Verification]], [[Calibration]], [[Selective Prediction]], [[System One Models]]
