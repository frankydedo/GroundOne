---
type: concept
tags: [concept, edge-cloud, hybrid-inference, routing, cascades, speculative-decoding, on-device]
---
# Edge-Cloud Collaborative Inference

Designs that split the work between a small model on the device and a large model in the cloud. They are the main alternative to fully local inference in the edge-AI literature, and the design the thesis deliberately does not adopt ([[On-Device Inference]], [[Privacy and Data Sovereignty]]).

## Taxonomy ([[Li 2025 - Collaborative Inference between Edge SLMs and Cloud LLMs, A Survey (arXiv 2507.16731)|Li 2025]] §2, Table 2)
- **Task assignment**: route each query to the edge or the cloud model (routers, cascades).
- **Task division**: split one query (offloading layers or sub-tasks, early exit).
- **Mixture**: combine both at task level or at token level; **speculative decoding** lets the small model draft tokens that the large one verifies.
- **Confidence-based offloading**: the device sends its output to the server only when its calibrated confidence is low ([[Qu 2024 - Mobile Edge Intelligence for LLMs, A Contemporary Survey (arXiv 2407.18921)|Qu 2024]] §VIII-C, §IX-A), a form of [[Selective Prediction]].
- Qu 2024 argues that pure on-device deployment is too limited and favours edge servers; a counter-position the thesis should acknowledge.
- Apple's on-device model plus Private Cloud Compute is the main industrial example ([[Gunter 2024 - Apple Intelligence Foundation Language Models]]). EXO's disaggregation of prefill (DGX Spark) and decode (Mac Studio) is a local-only variant ([[EXO Labs 2025 - NVIDIA DGX Spark and Mac Studio, disaggregated inference]]).

## Terminology warning
In these surveys "verification" almost always means the **draft-and-verify step of speculative decoding**, not groundedness verification. None of the four edge surveys ingested on 2026-10-11 discusses hallucination checking or a classification readout from logits on device.

## Relevance to GroundOne
- GroundOne's calibrated P(supported) and dev threshold would make it a natural **local gate** in a cascade (escalate only uncertain sentences), but sending them to a cloud model would break the locality pillar; the thesis treats deferral as a signal to the user instead ([[Selective Prediction]]).
- Li 2025 lists uncertainty from unnormalised logits as an open challenge (§6), which is what GroundOne's readout and calibration provide ([[Verbalised vs Logit Confidence]]).

## Links
- Concepts: [[On-Device Inference]], [[Small Language Models]], [[Selective Prediction]], [[Calibration]], [[Privacy and Data Sovereignty]], [[Prefill and Decode]]
