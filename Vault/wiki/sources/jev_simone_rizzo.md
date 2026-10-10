---
type: source
author: Simone Rizzo
date: 2026-09-22
tags: [jev, system-one-models, ai, architecture]
---
# Jev - System One Models (by Simone Rizzo)

**Raw file**: `raw/jev_video_transcript_ingested.txt`

This is a transcript of a YouTube video by Simone Rizzo explaining the new "System One Model" architecture, specifically focusing on a model called **Jev**. 

## Summary
Jev is not a Large Language Model (LLM) and does not generate text. Instead, it is an intelligent decision-making system (function calling) that takes unstructured text (state) and natural language instructions, outputting only three types of responses:
1. **Boolean** (Yes/No)
2. **Numeric Score** (e.g., 1 to 10)
3. **Choice from a List** (Classification)

## Key Insights
- **Speed and Cost**: It is 444x cheaper and 193x faster than current LLMs because it doesn't generate output tokens one by one.
- **Creator**: The team includes Diogo Almeida, a former OpenAI researcher and co-inventor of RLHF (Reinforcement Learning with Human Feedback) and InstructGPT.
- **Use Cases**: Fast, real-time scraping, playing video games (e.g., Doom) at 30 fps, parsing CVs to extract specific scores/metadata, routing between different AI models (e.g., choosing whether to use GPT-4 or Claude), guardrails for prompts, and fast batch processing.
- **Architecture**: It is a decoder-only model (based on models like Qwen 3.5 4B or MiniCPM) truncated before the final token generation layer. It has a fixed output head for up to 255 parallel tasks.
- **Training**: 
  1. Supervised Fine-Tuning (SFT) on 10k-50k examples.
  2. Reinforcement Learning with Calibrated Decisions/Rewards to ensure the output probabilities correctly reflect the model's confidence (certainty vs probability).
- **Allucinations**: The marketing claims 0% hallucinations, but as a statistical model, it can still assign incorrect probabilities to choices (e.g., guessing age wrong). The workaround is adding an "I don't know" category to choices.
- **Open Source Recreations**: "Samif" (formerly OpenJav) and "Jevlike".
