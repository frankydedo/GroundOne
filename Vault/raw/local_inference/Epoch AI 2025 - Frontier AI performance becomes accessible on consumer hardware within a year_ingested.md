---
title: "Epoch AI 2025 - Frontier AI performance becomes accessible on consumer hardware within a year"
url: https://epoch.ai/data-insights/consumer-gpu-model-gap
published: 2025-08-15
accessed: 2026-10-11
extracted_with: trafilatura 2.3.1
---

Using a single top-of-the-line gaming GPU like NVIDIA’s RTX 5090 (under $2500), anyone can locally run models matching the absolute frontier of LLM performance from just 6 to 12 months ago. This lag is consistent with our previous estimate of a [5 to 22 month gap for open-weight models of any size](https://epoch.ai/blog/open-models-report#open-models-have-lagged-on-benchmarks-by-5-to-22-months). However, it should be noted that small open models are more likely to be optimized for specific benchmarks, so the “real-world” lag may be somewhat longer.

| Consumer-hardware model performance |  |  |  |  |  |  |  |  |  | 
|---|---|---|---|---|---|---|---|---|---|
| Model | Organization | Formatted Model Name | Date | GPQA-Diamond | MMLU-Pro | AA Intelligence | LMArena ELO | Parameters | Notes | 
|---|---|---|---|---|---|---|---|---|---|
| mistralai/Mistral-7B-Instruct-v0.1 | Mistral | Mistral 7B | 2023-10-10 | 18.0 | 25.00 | 1 | 1,113 | 7.2e+9 |  | 
| microsoft/Phi-3-medium-128k-instruct | Microsoft | Phi 3 Medium | 2024-04-23 | 33.0 | 54.00 | 13 |  | 1.4e+10 |  | 
| microsoft/Phi-3-medium-4k-instruct | Microsoft | Phi 3 Medium | 2024-04-23 |  |  |  | 1,201 | 1.4e+10 |  | 
| google/gemma-2-27b-it |  | Gemma 2 27B | 2024-06-24 | 36.0 | 57.00 | 20 | 1,286 | 2.7e+10 |  | 
| meta-llama/Llama-3.1-8B | Meta | Llama 3.1-8B | 2024-07-23 | 26.0 | 48.00 | 19 |  | 8.0e+9 |  | 
| meta-llama/Llama-3.1-8B-Instruct | Meta | Llama 3.1-8B | 2024-07-23 |  |  |  | 1,215 | 8.0e+9 |  | 
| Qwen/Qwen2.5-32B-Instruct | Qwen | Qwen2.5 32B | 2024-09-17 | 47.0 | 70.00 | 26 |  | 3.3e+10 |  | 
| mistralai/Mistral-Small-2409 | Mistral | Mistral Small 2 | 2024-09-17 | 38.0 | 53.00 | 16 |  | 2.2e+10 |  | 
| Qwen/Qwen2.5-14B-Instruct | Qwen | Qwen2.5 14B | 2024-09-19 |  | 63.70 |  |  | 1.5e+10 |  | 
| Qwen/Qwen2.5-Coder-14B-Instruct | Qwen | Qwen2.5 Coder 14B | 2024-11-12 |  | 55.60 |  |  | 1.5e+10 |  | 
| Qwen/Qwen2.5-Coder-32B-Instruct | Qwen | Qwen2.5 Coder 32B | 2024-11-12 | 42.0 | 64.00 | 25 | 1,271 | 3.3e+10 |  | 
| microsoft/phi-4 | Microsoft | Phi 4 | 2024-12-12 | 57.5 | 71.00 | 28 | 1,258 | 1.5e+10 |  | 
| tiiuae/Falcon3-10B-Instruct | Technology Innovation Institute | Falcon3 10B | 2024-12-17 |  | 44.00 |  |  | 1.0e+10 |  | 
| deepseek-ai/DeepSeek-R1-Distill-Qwen-32B | DeepSeek | DeepSeek R1 (Qwen 32B) | 2025-01-22 | 62.0 | 74.00 | 41 |  | 3.3e+10 |  | 
| deepseek-ai/DeepSeek-R1-Distill-Qwen-14B | DeepSeek | DeepSeek R1 (Qwen 14B) | 2025-01-22 | 48.0 | 74.00 | 38 |  | 1.5e+10 |  | 
| mistralai/Mistral-Small-24B-Instruct-2501 | Mistral | Mistral Small 3 | 2025-01-30 | 46.2 | 65.50 | 24 | 1,275 | 2.4e+10 | MMLU Pro digitized from announcement charts | 
| s1-32B | Stanford University, University of Washington, Allen Institute for AI, Contextual AI | s1-32B | 2025-01-31 | 59.6 |  |  |  | 3.3e+10 |  | 
| simplescaling/s1.1-32B | Stanford University, University of Washington, Allen Institute for AI, Contextual AI | s1.1-32B | 2025-02-11 | 63.6 |  |  |  | 3.3e+10 |  | 
| QwQ-32B-Preview | Qwen | QwQ-32B-Preview | 2024-11-28 | 56.0 | 65.00 | 32 | 1,169 | 3.3e+10 |  | 
| QwQ-32B | Qwen | QwQ-32B | 2025-03-06 | 59.0 | 76.00 | 48 | 1,336 | 3.3e+10 |  | 
| Gemma 3 27B IT |  | Gemma 3 27B IT | 2025-03-12 | 43.0 | 67.00 | 25 | 1,363 | 2.7e+10 |  | 
| mistralai/Mistral-Small-3.1-24B-Instruct-2503 | Mistral | Mistral Small 3.1 | 2025-03-17 | 45.0 | 66.00 | 26 | 1,295 | 2.4e+10 |  | 
| EXAONE-Deep-32B | LG AI Research | EXAONE-Deep-32B | 2025-03-19 | 66.1 |  |  |  | 3.2e+10 |  | 
| EXAONE-Deep-7.8B | LG AI Research | EXAONE-Deep-7.8B | 2025-03-19 | 62.6 |  |  |  | 7.8e+9 |  | 
| NousResearch/DeepHermes-3-Mistral-24B-Preview | Nous Research | DeepHermes 3 (Mistral 24B) | 2025-03-29 | 38.0 | 58.00 | 18 |  | 2.4e+10 |  | 
| Qwen3-30B-A3B (Reasoning) | Qwen | Qwen3 30B-A3B (Reasoning) | 2025-04-29 | 62.0 | 78.00 | 42 | 1,328 | 3.1e+10 |  | 
| Qwen3-32B (Reasoning) | Qwen | Qwen3 32B (Reasoning) | 2025-04-29 | 66.8 | 79.80 | 44 | 1,346 | 3.3e+10 |  | 
| Qwen3 14B (Reasoning) | Qwen | Qwen3 14B (Reasoning) | 2025-04-29 | 60.0 | 77.00 | 45 |  | 1.5e+10 |  | 
| Phi 4 Reasoning Plus | Microsoft | Phi 4 Reasoning Plus | 2025-04-30 | 68.9 | 76.00 |  |  | 1.5e+10 |  | 
| deepseek-ai/DeepSeek-R1-0528-Qwen3-8B | DeepSeek | DeepSeek R1 0528 (Qwen3 8B) | 2025-05-28 | 61.0 | 74.00 | 42 |  | 8.2e+9 |  | 
| MiMo RL 0530 | Xiaomi | MiMo RL 0530 | 2025-06-05 | 60.6 | 58.60 |  |  | 7.8e+9 |  | 
| Magistral Small | Mistral | Magistral Small | 2025-06-10 | 64.0 | 75.00 | 36 |  | 2.4e+10 |  | 
| mistralai/Mistral-Small-3.2-24B-Instruct-2506 | Mistral | Mistral Small 3.2 | 2025-06-20 | 51.0 | 68.00 | 32 | 1,351 | 2.4e+10 |  | 
| EXAONE 4.0 32B (Reasoning) | LG AI Research | EXAONE 4.0 32B (Reasoning) | 2025-07-15 | 74.0 | 82.00 | 51 |  | 3.2e+10 |  | 
| Qwen3 30B-A3B-2507 (Reasoning) | Qwen | Qwen3 30B-A3B-2507 (Reasoning) | 2025-07-29 | 71.0 | 81.00 | 53 | 1,382 | 3.1e+10 |  | 
| Hunyuan-4B-Instruct | Tencent | Hunyuan 4B | 2025-08-04 | 61.1 | 51.91 |  |  | 4.2e+9 |  | 
| Hunyuan-7B-Instruct | Tencent | Hunyuan 7B | 2025-08-04 | 60.1 | 57.79 |  |  | 7.5e+9 |  | 
| gpt-oss-20B | OpenAI | gpt-oss-20B | 2025-08-05 | 62.0 | 74.00 | 49 | 1,330 | 2.2e+10 |  | 
| meta-llama/Meta-Llama-3-8B-Instruct | Meta | Llama 3 8B | 2024-04-18 | 30.0 | 41.00 | 9 | 1,225 | 8.0e+9 |  | 
| granite-3.1-8b-instruct | IBM | Granite 3.1 8B | 2024-12-18 |  |  |  | 1,213 | 8.2e+9 |  | 
| Qwen/Qwen1.5-14B-Chat | Alibaba | Qwen1.5-14B | 2024-02-04 |  |  |  | 1,196 | 1.4e+10 |  | 
| gemma-1.1-7b-it |  | Gemma-1.1-7B | 2024-04-09 |  |  |  | 1,180 | 7.0e+9 |  | 
| Qwen-14B-chat | Alibaba | Qwen-14B | 2023-09-28 |  |  | 2 | 1,141 | 1.4e+10 |  | 
| Vicuna-13B v1.5 | LMSYS | Vicuna-13B | 2023-08-01 |  |  |  | 1,145 | 1.3e+10 |  | 

| Frontier model performance |  |  |  |  |  |  |  |  |  | 
|---|---|---|---|---|---|---|---|---|---|
| Model | Organization | Formatted Model Name | Date | GPQA-Diamond | MMLU-Pro | AA Intelligence | LMArena ELO | Parameters | Notes | 
|---|---|---|---|---|---|---|---|---|---|
| GPT-4 (Jun 2023) | OpenAI | GPT-4 (Jun 2023) | 2023-06-14 | 31.0 |  |  | 1,275 | 1.8e+12 |  | 
| Claude 2 | Anthropic | Claude 2 | 2023-07-11 | 35.0 | 49 | 11 |  |  |  | 
| Claude 2.1 | Anthropic | Claude 2.1 | 2023-11-20 | 32.0 | 50 | 12 |  |  |  | 
| GPT-4 Preview (Nov 2023) | OpenAI | GPT-4 Preview (Nov 2023) | 2023-11-06 | 42.0 |  |  | 1,314 |  |  | 
| Claude 3 Opus | Anthropic | Claude 3 Opus | 2024-02-29 | 47.0 | 70 | 24 | 1,322 |  |  | 
| GPT-4o (May 2024) | OpenAI | GPT-4o (May 2024) | 2024-05-13 | 49.0 | 74 | 30 | 1,343 |  |  | 
| Claude 3.5 Sonnet (Jun 2024) | Anthropic | Claude 3.5 Sonnet (Jun 2024) | 2024-06-20 | 54.0 | 75 | 29 | 1,340 |  |  | 
| Claude 3.5 Sonnet (Oct 2024) | Anthropic | Claude 3.5 Sonnet (Oct 2024) | 2024-10-22 | 60.0 | 77 | 33 | 1,367 |  |  | 
| o1-mini (high) | OpenAI | o1-mini (high) | 2024-09-12 | 62.0 |  |  |  |  |  | 
| o1-mini | OpenAI | o1-mini | 2024-09-12 | 60.0 | 74 | 43 | 1,335 |  |  | 
| o1 | OpenAI | o1 | 2024-12-05 | 75.0 | 84 | 52 | 1,398 |  |  | 
| o3-mini (high) | OpenAI | o3-mini (high) | 2025-01-30 | 77.0 | 80 | 55 | 1,363 |  |  | 
| o3 | OpenAI | o3 | 2025-04-16 | 83.0 | 85 | 67 | 1,447 |  |  | 
| o4-mini (high) | OpenAI | o4-mini (high) | 2025-04-16 | 83.0 | 83 | 65 | 1,397 |  |  | 
| GPT-4.1 | OpenAI | GPT-4.1 | 2025-04-14 | 67.0 | 81 | 47 | 1,406 |  |  | 
| Claude 3.7 Sonnet (64k thinking) | Anthropic | Claude 3.7 Sonnet (64k thinking) | 2025-02-24 | 79.0 | 84 | 47 |  |  |  | 
| Claude 3.7 Sonnet (32k thinking) | Anthropic | Claude 3.7 Sonnet (32k thinking) | 2025-02-24 |  |  |  | 1,385 |  |  | 
| Claude 4 Sonnet Thinking | Anthropic | Claude 4 Sonnet Thinking | 2025-05-22 | 78.0 | 84 | 59 | 1,400 |  |  | 
| Claude 4 Opus Thinking | Anthropic | Claude 4 Opus Thinking | 2025-05-22 | 80.0 | 87 | 55 | 1,420 |  |  | 
| Claude 4.1 Opus Thinking | Anthropic | Claude 4.1 Opus Thinking | 2025-08-05 | 76.8 |  | 61 | 1,450 |  |  | 
| Gemini 2.5 Pro Exp (Mar 2025) | Google DeepMind | Gemini 2.5 Pro Exp (Mar 2025) | 2025-03-25 | 84.0 | 86 | 59 |  |  |  | 
| Gemini 2.5 Pro Preview (Jun 2025) | Google DeepMind | Gemini 2.5 Pro Preview (Jun 2025) | 2025-06-05 | 85.0 |  |  |  |  |  | 
| Gemini 2.5 Pro | Google DeepMind | Gemini 2.5 Pro | 2025-03-25 | 84.0 | 86 | 65 | 1,458 |  |  | 
| Grok 4 | xAI | Grok 4 | 2025-07-09 | 87.0 | 87 | 68 | 1,428 |  |  | 
| GPT-5 | OpenAI | GPT-5 | 2025-08-06 | 85.0 | 87 | 69 | 1,461 |  |  | 

| Consumer-hardware model performance |  |  |  |  |  |  |  |  |  | 
|---|---|---|---|---|---|---|---|---|---|
| Model | Organization | Formatted Model Name | Date | GPQA-Diamond | MMLU-Pro | AA Intelligence | LMArena ELO | Parameters | Notes | 
|---|---|---|---|---|---|---|---|---|---|
| mistralai/Mistral-7B-Instruct-v0.1 | Mistral | Mistral 7B | 2023-10-10 | 18.0 | 25.00 | 1 | 1,113 | 7.2e+9 |  | 
| microsoft/Phi-3-medium-128k-instruct | Microsoft | Phi 3 Medium | 2024-04-23 | 33.0 | 54.00 | 13 |  | 1.4e+10 |  | 
| microsoft/Phi-3-medium-4k-instruct | Microsoft | Phi 3 Medium | 2024-04-23 |  |  |  | 1,201 | 1.4e+10 |  | 
| google/gemma-2-27b-it |  | Gemma 2 27B | 2024-06-24 | 36.0 | 57.00 | 20 | 1,286 | 2.7e+10 |  | 
| meta-llama/Llama-3.1-8B | Meta | Llama 3.1-8B | 2024-07-23 | 26.0 | 48.00 | 19 |  | 8.0e+9 |  | 
| meta-llama/Llama-3.1-8B-Instruct | Meta | Llama 3.1-8B | 2024-07-23 |  |  |  | 1,215 | 8.0e+9 |  | 
| Qwen/Qwen2.5-32B-Instruct | Qwen | Qwen2.5 32B | 2024-09-17 | 47.0 | 70.00 | 26 |  | 3.3e+10 |  | 
| mistralai/Mistral-Small-2409 | Mistral | Mistral Small 2 | 2024-09-17 | 38.0 | 53.00 | 16 |  | 2.2e+10 |  | 
| Qwen/Qwen2.5-14B-Instruct | Qwen | Qwen2.5 14B | 2024-09-19 |  | 63.70 |  |  | 1.5e+10 |  | 
| Qwen/Qwen2.5-Coder-14B-Instruct | Qwen | Qwen2.5 Coder 14B | 2024-11-12 |  | 55.60 |  |  | 1.5e+10 |  | 
| Qwen/Qwen2.5-Coder-32B-Instruct | Qwen | Qwen2.5 Coder 32B | 2024-11-12 | 42.0 | 64.00 | 25 | 1,271 | 3.3e+10 |  | 
| microsoft/phi-4 | Microsoft | Phi 4 | 2024-12-12 | 57.5 | 71.00 | 28 | 1,258 | 1.5e+10 |  | 
| tiiuae/Falcon3-10B-Instruct | Technology Innovation Institute | Falcon3 10B | 2024-12-17 |  | 44.00 |  |  | 1.0e+10 |  | 
| deepseek-ai/DeepSeek-R1-Distill-Qwen-32B | DeepSeek | DeepSeek R1 (Qwen 32B) | 2025-01-22 | 62.0 | 74.00 | 41 |  | 3.3e+10 |  | 
| deepseek-ai/DeepSeek-R1-Distill-Qwen-14B | DeepSeek | DeepSeek R1 (Qwen 14B) | 2025-01-22 | 48.0 | 74.00 | 38 |  | 1.5e+10 |  | 
| mistralai/Mistral-Small-24B-Instruct-2501 | Mistral | Mistral Small 3 | 2025-01-30 | 46.2 | 65.50 | 24 | 1,275 | 2.4e+10 | MMLU Pro digitized from announcement charts | 
| s1-32B | Stanford University, University of Washington, Allen Institute for AI, Contextual AI | s1-32B | 2025-01-31 | 59.6 |  |  |  | 3.3e+10 |  | 
| simplescaling/s1.1-32B | Stanford University, University of Washington, Allen Institute for AI, Contextual AI | s1.1-32B | 2025-02-11 | 63.6 |  |  |  | 3.3e+10 |  | 
| QwQ-32B-Preview | Qwen | QwQ-32B-Preview | 2024-11-28 | 56.0 | 65.00 | 32 | 1,169 | 3.3e+10 |  | 
| QwQ-32B | Qwen | QwQ-32B | 2025-03-06 | 59.0 | 76.00 | 48 | 1,336 | 3.3e+10 |  | 
| Gemma 3 27B IT |  | Gemma 3 27B IT | 2025-03-12 | 43.0 | 67.00 | 25 | 1,363 | 2.7e+10 |  | 
| mistralai/Mistral-Small-3.1-24B-Instruct-2503 | Mistral | Mistral Small 3.1 | 2025-03-17 | 45.0 | 66.00 | 26 | 1,295 | 2.4e+10 |  | 
| EXAONE-Deep-32B | LG AI Research | EXAONE-Deep-32B | 2025-03-19 | 66.1 |  |  |  | 3.2e+10 |  | 
| EXAONE-Deep-7.8B | LG AI Research | EXAONE-Deep-7.8B | 2025-03-19 | 62.6 |  |  |  | 7.8e+9 |  | 
| NousResearch/DeepHermes-3-Mistral-24B-Preview | Nous Research | DeepHermes 3 (Mistral 24B) | 2025-03-29 | 38.0 | 58.00 | 18 |  | 2.4e+10 |  | 
| Qwen3-30B-A3B (Reasoning) | Qwen | Qwen3 30B-A3B (Reasoning) | 2025-04-29 | 62.0 | 78.00 | 42 | 1,328 | 3.1e+10 |  | 
| Qwen3-32B (Reasoning) | Qwen | Qwen3 32B (Reasoning) | 2025-04-29 | 66.8 | 79.80 | 44 | 1,346 | 3.3e+10 |  | 
| Qwen3 14B (Reasoning) | Qwen | Qwen3 14B (Reasoning) | 2025-04-29 | 60.0 | 77.00 | 45 |  | 1.5e+10 |  | 
| Phi 4 Reasoning Plus | Microsoft | Phi 4 Reasoning Plus | 2025-04-30 | 68.9 | 76.00 |  |  | 1.5e+10 |  | 
| deepseek-ai/DeepSeek-R1-0528-Qwen3-8B | DeepSeek | DeepSeek R1 0528 (Qwen3 8B) | 2025-05-28 | 61.0 | 74.00 | 42 |  | 8.2e+9 |  | 
| MiMo RL 0530 | Xiaomi | MiMo RL 0530 | 2025-06-05 | 60.6 | 58.60 |  |  | 7.8e+9 |  | 
| Magistral Small | Mistral | Magistral Small | 2025-06-10 | 64.0 | 75.00 | 36 |  | 2.4e+10 |  | 
| mistralai/Mistral-Small-3.2-24B-Instruct-2506 | Mistral | Mistral Small 3.2 | 2025-06-20 | 51.0 | 68.00 | 32 | 1,351 | 2.4e+10 |  | 
| EXAONE 4.0 32B (Reasoning) | LG AI Research | EXAONE 4.0 32B (Reasoning) | 2025-07-15 | 74.0 | 82.00 | 51 |  | 3.2e+10 |  | 
| Qwen3 30B-A3B-2507 (Reasoning) | Qwen | Qwen3 30B-A3B-2507 (Reasoning) | 2025-07-29 | 71.0 | 81.00 | 53 | 1,382 | 3.1e+10 |  | 
| Hunyuan-4B-Instruct | Tencent | Hunyuan 4B | 2025-08-04 | 61.1 | 51.91 |  |  | 4.2e+9 |  | 
| Hunyuan-7B-Instruct | Tencent | Hunyuan 7B | 2025-08-04 | 60.1 | 57.79 |  |  | 7.5e+9 |  | 
| gpt-oss-20B | OpenAI | gpt-oss-20B | 2025-08-05 | 62.0 | 74.00 | 49 | 1,330 | 2.2e+10 |  | 
| meta-llama/Meta-Llama-3-8B-Instruct | Meta | Llama 3 8B | 2024-04-18 | 30.0 | 41.00 | 9 | 1,225 | 8.0e+9 |  | 
| granite-3.1-8b-instruct | IBM | Granite 3.1 8B | 2024-12-18 |  |  |  | 1,213 | 8.2e+9 |  | 
| Qwen/Qwen1.5-14B-Chat | Alibaba | Qwen1.5-14B | 2024-02-04 |  |  |  | 1,196 | 1.4e+10 |  | 
| gemma-1.1-7b-it |  | Gemma-1.1-7B | 2024-04-09 |  |  |  | 1,180 | 7.0e+9 |  | 
| Qwen-14B-chat | Alibaba | Qwen-14B | 2023-09-28 |  |  | 2 | 1,141 | 1.4e+10 |  | 
| Vicuna-13B v1.5 | LMSYS | Vicuna-13B | 2023-08-01 |  |  |  | 1,145 | 1.3e+10 |  | 

| Frontier model performance |  |  |  |  |  |  |  |  |  | 
|---|---|---|---|---|---|---|---|---|---|
| Model | Organization | Formatted Model Name | Date | GPQA-Diamond | MMLU-Pro | AA Intelligence | LMArena ELO | Parameters | Notes | 
|---|---|---|---|---|---|---|---|---|---|
| GPT-4 (Jun 2023) | OpenAI | GPT-4 (Jun 2023) | 2023-06-14 | 31.0 |  |  | 1,275 | 1.8e+12 |  | 
| Claude 2 | Anthropic | Claude 2 | 2023-07-11 | 35.0 | 49 | 11 |  |  |  | 
| Claude 2.1 | Anthropic | Claude 2.1 | 2023-11-20 | 32.0 | 50 | 12 |  |  |  | 
| GPT-4 Preview (Nov 2023) | OpenAI | GPT-4 Preview (Nov 2023) | 2023-11-06 | 42.0 |  |  | 1,314 |  |  | 
| Claude 3 Opus | Anthropic | Claude 3 Opus | 2024-02-29 | 47.0 | 70 | 24 | 1,322 |  |  | 
| GPT-4o (May 2024) | OpenAI | GPT-4o (May 2024) | 2024-05-13 | 49.0 | 74 | 30 | 1,343 |  |  | 
| Claude 3.5 Sonnet (Jun 2024) | Anthropic | Claude 3.5 Sonnet (Jun 2024) | 2024-06-20 | 54.0 | 75 | 29 | 1,340 |  |  | 
| Claude 3.5 Sonnet (Oct 2024) | Anthropic | Claude 3.5 Sonnet (Oct 2024) | 2024-10-22 | 60.0 | 77 | 33 | 1,367 |  |  | 
| o1-mini (high) | OpenAI | o1-mini (high) | 2024-09-12 | 62.0 |  |  |  |  |  | 
| o1-mini | OpenAI | o1-mini | 2024-09-12 | 60.0 | 74 | 43 | 1,335 |  |  | 
| o1 | OpenAI | o1 | 2024-12-05 | 75.0 | 84 | 52 | 1,398 |  |  | 
| o3-mini (high) | OpenAI | o3-mini (high) | 2025-01-30 | 77.0 | 80 | 55 | 1,363 |  |  | 
| o3 | OpenAI | o3 | 2025-04-16 | 83.0 | 85 | 67 | 1,447 |  |  | 
| o4-mini (high) | OpenAI | o4-mini (high) | 2025-04-16 | 83.0 | 83 | 65 | 1,397 |  |  | 
| GPT-4.1 | OpenAI | GPT-4.1 | 2025-04-14 | 67.0 | 81 | 47 | 1,406 |  |  | 
| Claude 3.7 Sonnet (64k thinking) | Anthropic | Claude 3.7 Sonnet (64k thinking) | 2025-02-24 | 79.0 | 84 | 47 |  |  |  | 
| Claude 3.7 Sonnet (32k thinking) | Anthropic | Claude 3.7 Sonnet (32k thinking) | 2025-02-24 |  |  |  | 1,385 |  |  | 
| Claude 4 Sonnet Thinking | Anthropic | Claude 4 Sonnet Thinking | 2025-05-22 | 78.0 | 84 | 59 | 1,400 |  |  | 
| Claude 4 Opus Thinking | Anthropic | Claude 4 Opus Thinking | 2025-05-22 | 80.0 | 87 | 55 | 1,420 |  |  | 
| Claude 4.1 Opus Thinking | Anthropic | Claude 4.1 Opus Thinking | 2025-08-05 | 76.8 |  | 61 | 1,450 |  |  | 
| Gemini 2.5 Pro Exp (Mar 2025) | Google DeepMind | Gemini 2.5 Pro Exp (Mar 2025) | 2025-03-25 | 84.0 | 86 | 59 |  |  |  | 
| Gemini 2.5 Pro Preview (Jun 2025) | Google DeepMind | Gemini 2.5 Pro Preview (Jun 2025) | 2025-06-05 | 85.0 |  |  |  |  |  | 
| Gemini 2.5 Pro | Google DeepMind | Gemini 2.5 Pro | 2025-03-25 | 84.0 | 86 | 65 | 1,458 |  |  | 
| Grok 4 | xAI | Grok 4 | 2025-07-09 | 87.0 | 87 | 68 | 1,428 |  |  | 
| GPT-5 | OpenAI | GPT-5 | 2025-08-06 | 85.0 | 87 | 69 | 1,461 |  |  | 

| Consumer-hardware model performance |  |  |  |  |  |  |  |  |  | 
|---|---|---|---|---|---|---|---|---|---|
| Model | Organization | Formatted Model Name | Date | GPQA-Diamond | MMLU-Pro | AA Intelligence | LMArena ELO | Parameters | Notes | 
|---|---|---|---|---|---|---|---|---|---|
| mistralai/Mistral-7B-Instruct-v0.1 | Mistral | Mistral 7B | 2023-10-10 | 18.0 | 25.00 | 1 | 1,113 | 7.2e+9 |  | 
| microsoft/Phi-3-medium-128k-instruct | Microsoft | Phi 3 Medium | 2024-04-23 | 33.0 | 54.00 | 13 |  | 1.4e+10 |  | 
| microsoft/Phi-3-medium-4k-instruct | Microsoft | Phi 3 Medium | 2024-04-23 |  |  |  | 1,201 | 1.4e+10 |  | 
| google/gemma-2-27b-it |  | Gemma 2 27B | 2024-06-24 | 36.0 | 57.00 | 20 | 1,286 | 2.7e+10 |  | 
| meta-llama/Llama-3.1-8B | Meta | Llama 3.1-8B | 2024-07-23 | 26.0 | 48.00 | 19 |  | 8.0e+9 |  | 
| meta-llama/Llama-3.1-8B-Instruct | Meta | Llama 3.1-8B | 2024-07-23 |  |  |  | 1,215 | 8.0e+9 |  | 
| Qwen/Qwen2.5-32B-Instruct | Qwen | Qwen2.5 32B | 2024-09-17 | 47.0 | 70.00 | 26 |  | 3.3e+10 |  | 
| mistralai/Mistral-Small-2409 | Mistral | Mistral Small 2 | 2024-09-17 | 38.0 | 53.00 | 16 |  | 2.2e+10 |  | 
| Qwen/Qwen2.5-14B-Instruct | Qwen | Qwen2.5 14B | 2024-09-19 |  | 63.70 |  |  | 1.5e+10 |  | 
| Qwen/Qwen2.5-Coder-14B-Instruct | Qwen | Qwen2.5 Coder 14B | 2024-11-12 |  | 55.60 |  |  | 1.5e+10 |  | 
| Qwen/Qwen2.5-Coder-32B-Instruct | Qwen | Qwen2.5 Coder 32B | 2024-11-12 | 42.0 | 64.00 | 25 | 1,271 | 3.3e+10 |  | 
| microsoft/phi-4 | Microsoft | Phi 4 | 2024-12-12 | 57.5 | 71.00 | 28 | 1,258 | 1.5e+10 |  | 
| tiiuae/Falcon3-10B-Instruct | Technology Innovation Institute | Falcon3 10B | 2024-12-17 |  | 44.00 |  |  | 1.0e+10 |  | 
| deepseek-ai/DeepSeek-R1-Distill-Qwen-32B | DeepSeek | DeepSeek R1 (Qwen 32B) | 2025-01-22 | 62.0 | 74.00 | 41 |  | 3.3e+10 |  | 
| deepseek-ai/DeepSeek-R1-Distill-Qwen-14B | DeepSeek | DeepSeek R1 (Qwen 14B) | 2025-01-22 | 48.0 | 74.00 | 38 |  | 1.5e+10 |  | 
| mistralai/Mistral-Small-24B-Instruct-2501 | Mistral | Mistral Small 3 | 2025-01-30 | 46.2 | 65.50 | 24 | 1,275 | 2.4e+10 | MMLU Pro digitized from announcement charts | 
| s1-32B | Stanford University, University of Washington, Allen Institute for AI, Contextual AI | s1-32B | 2025-01-31 | 59.6 |  |  |  | 3.3e+10 |  | 
| simplescaling/s1.1-32B | Stanford University, University of Washington, Allen Institute for AI, Contextual AI | s1.1-32B | 2025-02-11 | 63.6 |  |  |  | 3.3e+10 |  | 
| QwQ-32B-Preview | Qwen | QwQ-32B-Preview | 2024-11-28 | 56.0 | 65.00 | 32 | 1,169 | 3.3e+10 |  | 
| QwQ-32B | Qwen | QwQ-32B | 2025-03-06 | 59.0 | 76.00 | 48 | 1,336 | 3.3e+10 |  | 
| Gemma 3 27B IT |  | Gemma 3 27B IT | 2025-03-12 | 43.0 | 67.00 | 25 | 1,363 | 2.7e+10 |  | 
| mistralai/Mistral-Small-3.1-24B-Instruct-2503 | Mistral | Mistral Small 3.1 | 2025-03-17 | 45.0 | 66.00 | 26 | 1,295 | 2.4e+10 |  | 
| EXAONE-Deep-32B | LG AI Research | EXAONE-Deep-32B | 2025-03-19 | 66.1 |  |  |  | 3.2e+10 |  | 
| EXAONE-Deep-7.8B | LG AI Research | EXAONE-Deep-7.8B | 2025-03-19 | 62.6 |  |  |  | 7.8e+9 |  | 
| NousResearch/DeepHermes-3-Mistral-24B-Preview | Nous Research | DeepHermes 3 (Mistral 24B) | 2025-03-29 | 38.0 | 58.00 | 18 |  | 2.4e+10 |  | 
| Qwen3-30B-A3B (Reasoning) | Qwen | Qwen3 30B-A3B (Reasoning) | 2025-04-29 | 62.0 | 78.00 | 42 | 1,328 | 3.1e+10 |  | 
| Qwen3-32B (Reasoning) | Qwen | Qwen3 32B (Reasoning) | 2025-04-29 | 66.8 | 79.80 | 44 | 1,346 | 3.3e+10 |  | 
| Qwen3 14B (Reasoning) | Qwen | Qwen3 14B (Reasoning) | 2025-04-29 | 60.0 | 77.00 | 45 |  | 1.5e+10 |  | 
| Phi 4 Reasoning Plus | Microsoft | Phi 4 Reasoning Plus | 2025-04-30 | 68.9 | 76.00 |  |  | 1.5e+10 |  | 
| deepseek-ai/DeepSeek-R1-0528-Qwen3-8B | DeepSeek | DeepSeek R1 0528 (Qwen3 8B) | 2025-05-28 | 61.0 | 74.00 | 42 |  | 8.2e+9 |  | 
| MiMo RL 0530 | Xiaomi | MiMo RL 0530 | 2025-06-05 | 60.6 | 58.60 |  |  | 7.8e+9 |  | 
| Magistral Small | Mistral | Magistral Small | 2025-06-10 | 64.0 | 75.00 | 36 |  | 2.4e+10 |  | 
| mistralai/Mistral-Small-3.2-24B-Instruct-2506 | Mistral | Mistral Small 3.2 | 2025-06-20 | 51.0 | 68.00 | 32 | 1,351 | 2.4e+10 |  | 
| EXAONE 4.0 32B (Reasoning) | LG AI Research | EXAONE 4.0 32B (Reasoning) | 2025-07-15 | 74.0 | 82.00 | 51 |  | 3.2e+10 |  | 
| Qwen3 30B-A3B-2507 (Reasoning) | Qwen | Qwen3 30B-A3B-2507 (Reasoning) | 2025-07-29 | 71.0 | 81.00 | 53 | 1,382 | 3.1e+10 |  | 
| Hunyuan-4B-Instruct | Tencent | Hunyuan 4B | 2025-08-04 | 61.1 | 51.91 |  |  | 4.2e+9 |  | 
| Hunyuan-7B-Instruct | Tencent | Hunyuan 7B | 2025-08-04 | 60.1 | 57.79 |  |  | 7.5e+9 |  | 
| gpt-oss-20B | OpenAI | gpt-oss-20B | 2025-08-05 | 62.0 | 74.00 | 49 | 1,330 | 2.2e+10 |  | 
| meta-llama/Meta-Llama-3-8B-Instruct | Meta | Llama 3 8B | 2024-04-18 | 30.0 | 41.00 | 9 | 1,225 | 8.0e+9 |  | 
| granite-3.1-8b-instruct | IBM | Granite 3.1 8B | 2024-12-18 |  |  |  | 1,213 | 8.2e+9 |  | 
| Qwen/Qwen1.5-14B-Chat | Alibaba | Qwen1.5-14B | 2024-02-04 |  |  |  | 1,196 | 1.4e+10 |  | 
| gemma-1.1-7b-it |  | Gemma-1.1-7B | 2024-04-09 |  |  |  | 1,180 | 7.0e+9 |  | 
| Qwen-14B-chat | Alibaba | Qwen-14B | 2023-09-28 |  |  | 2 | 1,141 | 1.4e+10 |  | 
| Vicuna-13B v1.5 | LMSYS | Vicuna-13B | 2023-08-01 |  |  |  | 1,145 | 1.3e+10 |  | 

| Frontier model performance |  |  |  |  |  |  |  |  |  | 
|---|---|---|---|---|---|---|---|---|---|
| Model | Organization | Formatted Model Name | Date | GPQA-Diamond | MMLU-Pro | AA Intelligence | LMArena ELO | Parameters | Notes | 
|---|---|---|---|---|---|---|---|---|---|
| GPT-4 (Jun 2023) | OpenAI | GPT-4 (Jun 2023) | 2023-06-14 | 31.0 |  |  | 1,275 | 1.8e+12 |  | 
| Claude 2 | Anthropic | Claude 2 | 2023-07-11 | 35.0 | 49 | 11 |  |  |  | 
| Claude 2.1 | Anthropic | Claude 2.1 | 2023-11-20 | 32.0 | 50 | 12 |  |  |  | 
| GPT-4 Preview (Nov 2023) | OpenAI | GPT-4 Preview (Nov 2023) | 2023-11-06 | 42.0 |  |  | 1,314 |  |  | 
| Claude 3 Opus | Anthropic | Claude 3 Opus | 2024-02-29 | 47.0 | 70 | 24 | 1,322 |  |  | 
| GPT-4o (May 2024) | OpenAI | GPT-4o (May 2024) | 2024-05-13 | 49.0 | 74 | 30 | 1,343 |  |  | 
| Claude 3.5 Sonnet (Jun 2024) | Anthropic | Claude 3.5 Sonnet (Jun 2024) | 2024-06-20 | 54.0 | 75 | 29 | 1,340 |  |  | 
| Claude 3.5 Sonnet (Oct 2024) | Anthropic | Claude 3.5 Sonnet (Oct 2024) | 2024-10-22 | 60.0 | 77 | 33 | 1,367 |  |  | 
| o1-mini (high) | OpenAI | o1-mini (high) | 2024-09-12 | 62.0 |  |  |  |  |  | 
| o1-mini | OpenAI | o1-mini | 2024-09-12 | 60.0 | 74 | 43 | 1,335 |  |  | 
| o1 | OpenAI | o1 | 2024-12-05 | 75.0 | 84 | 52 | 1,398 |  |  | 
| o3-mini (high) | OpenAI | o3-mini (high) | 2025-01-30 | 77.0 | 80 | 55 | 1,363 |  |  | 
| o3 | OpenAI | o3 | 2025-04-16 | 83.0 | 85 | 67 | 1,447 |  |  | 
| o4-mini (high) | OpenAI | o4-mini (high) | 2025-04-16 | 83.0 | 83 | 65 | 1,397 |  |  | 
| GPT-4.1 | OpenAI | GPT-4.1 | 2025-04-14 | 67.0 | 81 | 47 | 1,406 |  |  | 
| Claude 3.7 Sonnet (64k thinking) | Anthropic | Claude 3.7 Sonnet (64k thinking) | 2025-02-24 | 79.0 | 84 | 47 |  |  |  | 
| Claude 3.7 Sonnet (32k thinking) | Anthropic | Claude 3.7 Sonnet (32k thinking) | 2025-02-24 |  |  |  | 1,385 |  |  | 
| Claude 4 Sonnet Thinking | Anthropic | Claude 4 Sonnet Thinking | 2025-05-22 | 78.0 | 84 | 59 | 1,400 |  |  | 
| Claude 4 Opus Thinking | Anthropic | Claude 4 Opus Thinking | 2025-05-22 | 80.0 | 87 | 55 | 1,420 |  |  | 
| Claude 4.1 Opus Thinking | Anthropic | Claude 4.1 Opus Thinking | 2025-08-05 | 76.8 |  | 61 | 1,450 |  |  | 
| Gemini 2.5 Pro Exp (Mar 2025) | Google DeepMind | Gemini 2.5 Pro Exp (Mar 2025) | 2025-03-25 | 84.0 | 86 | 59 |  |  |  | 
| Gemini 2.5 Pro Preview (Jun 2025) | Google DeepMind | Gemini 2.5 Pro Preview (Jun 2025) | 2025-06-05 | 85.0 |  |  |  |  |  | 
| Gemini 2.5 Pro | Google DeepMind | Gemini 2.5 Pro | 2025-03-25 | 84.0 | 86 | 65 | 1,458 |  |  | 
| Grok 4 | xAI | Grok 4 | 2025-07-09 | 87.0 | 87 | 68 | 1,428 |  |  | 
| GPT-5 | OpenAI | GPT-5 | 2025-08-06 | 85.0 | 87 | 69 | 1,461 |  |  | 

| Consumer-hardware model performance |  |  |  |  |  |  |  |  |  | 
|---|---|---|---|---|---|---|---|---|---|
| Model | Organization | Formatted Model Name | Date | GPQA-Diamond | MMLU-Pro | AA Intelligence | LMArena ELO | Parameters | Notes | 
|---|---|---|---|---|---|---|---|---|---|
| mistralai/Mistral-7B-Instruct-v0.1 | Mistral | Mistral 7B | 2023-10-10 | 18.0 | 25.00 | 1 | 1,113 | 7.2e+9 |  | 
| microsoft/Phi-3-medium-128k-instruct | Microsoft | Phi 3 Medium | 2024-04-23 | 33.0 | 54.00 | 13 |  | 1.4e+10 |  | 
| microsoft/Phi-3-medium-4k-instruct | Microsoft | Phi 3 Medium | 2024-04-23 |  |  |  | 1,201 | 1.4e+10 |  | 
| google/gemma-2-27b-it |  | Gemma 2 27B | 2024-06-24 | 36.0 | 57.00 | 20 | 1,286 | 2.7e+10 |  | 
| meta-llama/Llama-3.1-8B | Meta | Llama 3.1-8B | 2024-07-23 | 26.0 | 48.00 | 19 |  | 8.0e+9 |  | 
| meta-llama/Llama-3.1-8B-Instruct | Meta | Llama 3.1-8B | 2024-07-23 |  |  |  | 1,215 | 8.0e+9 |  | 
| Qwen/Qwen2.5-32B-Instruct | Qwen | Qwen2.5 32B | 2024-09-17 | 47.0 | 70.00 | 26 |  | 3.3e+10 |  | 
| mistralai/Mistral-Small-2409 | Mistral | Mistral Small 2 | 2024-09-17 | 38.0 | 53.00 | 16 |  | 2.2e+10 |  | 
| Qwen/Qwen2.5-14B-Instruct | Qwen | Qwen2.5 14B | 2024-09-19 |  | 63.70 |  |  | 1.5e+10 |  | 
| Qwen/Qwen2.5-Coder-14B-Instruct | Qwen | Qwen2.5 Coder 14B | 2024-11-12 |  | 55.60 |  |  | 1.5e+10 |  | 
| Qwen/Qwen2.5-Coder-32B-Instruct | Qwen | Qwen2.5 Coder 32B | 2024-11-12 | 42.0 | 64.00 | 25 | 1,271 | 3.3e+10 |  | 
| microsoft/phi-4 | Microsoft | Phi 4 | 2024-12-12 | 57.5 | 71.00 | 28 | 1,258 | 1.5e+10 |  | 
| tiiuae/Falcon3-10B-Instruct | Technology Innovation Institute | Falcon3 10B | 2024-12-17 |  | 44.00 |  |  | 1.0e+10 |  | 
| deepseek-ai/DeepSeek-R1-Distill-Qwen-32B | DeepSeek | DeepSeek R1 (Qwen 32B) | 2025-01-22 | 62.0 | 74.00 | 41 |  | 3.3e+10 |  | 
| deepseek-ai/DeepSeek-R1-Distill-Qwen-14B | DeepSeek | DeepSeek R1 (Qwen 14B) | 2025-01-22 | 48.0 | 74.00 | 38 |  | 1.5e+10 |  | 
| mistralai/Mistral-Small-24B-Instruct-2501 | Mistral | Mistral Small 3 | 2025-01-30 | 46.2 | 65.50 | 24 | 1,275 | 2.4e+10 | MMLU Pro digitized from announcement charts | 
| s1-32B | Stanford University, University of Washington, Allen Institute for AI, Contextual AI | s1-32B | 2025-01-31 | 59.6 |  |  |  | 3.3e+10 |  | 
| simplescaling/s1.1-32B | Stanford University, University of Washington, Allen Institute for AI, Contextual AI | s1.1-32B | 2025-02-11 | 63.6 |  |  |  | 3.3e+10 |  | 
| QwQ-32B-Preview | Qwen | QwQ-32B-Preview | 2024-11-28 | 56.0 | 65.00 | 32 | 1,169 | 3.3e+10 |  | 
| QwQ-32B | Qwen | QwQ-32B | 2025-03-06 | 59.0 | 76.00 | 48 | 1,336 | 3.3e+10 |  | 
| Gemma 3 27B IT |  | Gemma 3 27B IT | 2025-03-12 | 43.0 | 67.00 | 25 | 1,363 | 2.7e+10 |  | 
| mistralai/Mistral-Small-3.1-24B-Instruct-2503 | Mistral | Mistral Small 3.1 | 2025-03-17 | 45.0 | 66.00 | 26 | 1,295 | 2.4e+10 |  | 
| EXAONE-Deep-32B | LG AI Research | EXAONE-Deep-32B | 2025-03-19 | 66.1 |  |  |  | 3.2e+10 |  | 
| EXAONE-Deep-7.8B | LG AI Research | EXAONE-Deep-7.8B | 2025-03-19 | 62.6 |  |  |  | 7.8e+9 |  | 
| NousResearch/DeepHermes-3-Mistral-24B-Preview | Nous Research | DeepHermes 3 (Mistral 24B) | 2025-03-29 | 38.0 | 58.00 | 18 |  | 2.4e+10 |  | 
| Qwen3-30B-A3B (Reasoning) | Qwen | Qwen3 30B-A3B (Reasoning) | 2025-04-29 | 62.0 | 78.00 | 42 | 1,328 | 3.1e+10 |  | 
| Qwen3-32B (Reasoning) | Qwen | Qwen3 32B (Reasoning) | 2025-04-29 | 66.8 | 79.80 | 44 | 1,346 | 3.3e+10 |  | 
| Qwen3 14B (Reasoning) | Qwen | Qwen3 14B (Reasoning) | 2025-04-29 | 60.0 | 77.00 | 45 |  | 1.5e+10 |  | 
| Phi 4 Reasoning Plus | Microsoft | Phi 4 Reasoning Plus | 2025-04-30 | 68.9 | 76.00 |  |  | 1.5e+10 |  | 
| deepseek-ai/DeepSeek-R1-0528-Qwen3-8B | DeepSeek | DeepSeek R1 0528 (Qwen3 8B) | 2025-05-28 | 61.0 | 74.00 | 42 |  | 8.2e+9 |  | 
| MiMo RL 0530 | Xiaomi | MiMo RL 0530 | 2025-06-05 | 60.6 | 58.60 |  |  | 7.8e+9 |  | 
| Magistral Small | Mistral | Magistral Small | 2025-06-10 | 64.0 | 75.00 | 36 |  | 2.4e+10 |  | 
| mistralai/Mistral-Small-3.2-24B-Instruct-2506 | Mistral | Mistral Small 3.2 | 2025-06-20 | 51.0 | 68.00 | 32 | 1,351 | 2.4e+10 |  | 
| EXAONE 4.0 32B (Reasoning) | LG AI Research | EXAONE 4.0 32B (Reasoning) | 2025-07-15 | 74.0 | 82.00 | 51 |  | 3.2e+10 |  | 
| Qwen3 30B-A3B-2507 (Reasoning) | Qwen | Qwen3 30B-A3B-2507 (Reasoning) | 2025-07-29 | 71.0 | 81.00 | 53 | 1,382 | 3.1e+10 |  | 
| Hunyuan-4B-Instruct | Tencent | Hunyuan 4B | 2025-08-04 | 61.1 | 51.91 |  |  | 4.2e+9 |  | 
| Hunyuan-7B-Instruct | Tencent | Hunyuan 7B | 2025-08-04 | 60.1 | 57.79 |  |  | 7.5e+9 |  | 
| gpt-oss-20B | OpenAI | gpt-oss-20B | 2025-08-05 | 62.0 | 74.00 | 49 | 1,330 | 2.2e+10 |  | 
| meta-llama/Meta-Llama-3-8B-Instruct | Meta | Llama 3 8B | 2024-04-18 | 30.0 | 41.00 | 9 | 1,225 | 8.0e+9 |  | 
| granite-3.1-8b-instruct | IBM | Granite 3.1 8B | 2024-12-18 |  |  |  | 1,213 | 8.2e+9 |  | 
| Qwen/Qwen1.5-14B-Chat | Alibaba | Qwen1.5-14B | 2024-02-04 |  |  |  | 1,196 | 1.4e+10 |  | 
| gemma-1.1-7b-it |  | Gemma-1.1-7B | 2024-04-09 |  |  |  | 1,180 | 7.0e+9 |  | 
| Qwen-14B-chat | Alibaba | Qwen-14B | 2023-09-28 |  |  | 2 | 1,141 | 1.4e+10 |  | 
| Vicuna-13B v1.5 | LMSYS | Vicuna-13B | 2023-08-01 |  |  |  | 1,145 | 1.3e+10 |  | 

| Frontier model performance |  |  |  |  |  |  |  |  |  | 
|---|---|---|---|---|---|---|---|---|---|
| Model | Organization | Formatted Model Name | Date | GPQA-Diamond | MMLU-Pro | AA Intelligence | LMArena ELO | Parameters | Notes | 
|---|---|---|---|---|---|---|---|---|---|
| GPT-4 (Jun 2023) | OpenAI | GPT-4 (Jun 2023) | 2023-06-14 | 31.0 |  |  | 1,275 | 1.8e+12 |  | 
| Claude 2 | Anthropic | Claude 2 | 2023-07-11 | 35.0 | 49 | 11 |  |  |  | 
| Claude 2.1 | Anthropic | Claude 2.1 | 2023-11-20 | 32.0 | 50 | 12 |  |  |  | 
| GPT-4 Preview (Nov 2023) | OpenAI | GPT-4 Preview (Nov 2023) | 2023-11-06 | 42.0 |  |  | 1,314 |  |  | 
| Claude 3 Opus | Anthropic | Claude 3 Opus | 2024-02-29 | 47.0 | 70 | 24 | 1,322 |  |  | 
| GPT-4o (May 2024) | OpenAI | GPT-4o (May 2024) | 2024-05-13 | 49.0 | 74 | 30 | 1,343 |  |  | 
| Claude 3.5 Sonnet (Jun 2024) | Anthropic | Claude 3.5 Sonnet (Jun 2024) | 2024-06-20 | 54.0 | 75 | 29 | 1,340 |  |  | 
| Claude 3.5 Sonnet (Oct 2024) | Anthropic | Claude 3.5 Sonnet (Oct 2024) | 2024-10-22 | 60.0 | 77 | 33 | 1,367 |  |  | 
| o1-mini (high) | OpenAI | o1-mini (high) | 2024-09-12 | 62.0 |  |  |  |  |  | 
| o1-mini | OpenAI | o1-mini | 2024-09-12 | 60.0 | 74 | 43 | 1,335 |  |  | 
| o1 | OpenAI | o1 | 2024-12-05 | 75.0 | 84 | 52 | 1,398 |  |  | 
| o3-mini (high) | OpenAI | o3-mini (high) | 2025-01-30 | 77.0 | 80 | 55 | 1,363 |  |  | 
| o3 | OpenAI | o3 | 2025-04-16 | 83.0 | 85 | 67 | 1,447 |  |  | 
| o4-mini (high) | OpenAI | o4-mini (high) | 2025-04-16 | 83.0 | 83 | 65 | 1,397 |  |  | 
| GPT-4.1 | OpenAI | GPT-4.1 | 2025-04-14 | 67.0 | 81 | 47 | 1,406 |  |  | 
| Claude 3.7 Sonnet (64k thinking) | Anthropic | Claude 3.7 Sonnet (64k thinking) | 2025-02-24 | 79.0 | 84 | 47 |  |  |  | 
| Claude 3.7 Sonnet (32k thinking) | Anthropic | Claude 3.7 Sonnet (32k thinking) | 2025-02-24 |  |  |  | 1,385 |  |  | 
| Claude 4 Sonnet Thinking | Anthropic | Claude 4 Sonnet Thinking | 2025-05-22 | 78.0 | 84 | 59 | 1,400 |  |  | 
| Claude 4 Opus Thinking | Anthropic | Claude 4 Opus Thinking | 2025-05-22 | 80.0 | 87 | 55 | 1,420 |  |  | 
| Claude 4.1 Opus Thinking | Anthropic | Claude 4.1 Opus Thinking | 2025-08-05 | 76.8 |  | 61 | 1,450 |  |  | 
| Gemini 2.5 Pro Exp (Mar 2025) | Google DeepMind | Gemini 2.5 Pro Exp (Mar 2025) | 2025-03-25 | 84.0 | 86 | 59 |  |  |  | 
| Gemini 2.5 Pro Preview (Jun 2025) | Google DeepMind | Gemini 2.5 Pro Preview (Jun 2025) | 2025-06-05 | 85.0 |  |  |  |  |  | 
| Gemini 2.5 Pro | Google DeepMind | Gemini 2.5 Pro | 2025-03-25 | 84.0 | 86 | 65 | 1,458 |  |  | 
| Grok 4 | xAI | Grok 4 | 2025-07-09 | 87.0 | 87 | 68 | 1,428 |  |  | 
| GPT-5 | OpenAI | GPT-5 | 2025-08-06 | 85.0 | 87 | 69 | 1,461 |  |  | 

Several factors drive this democratizing trend, including a [comparable rate of scaling among open-weight models to the closed-source frontier](https://epoch.ai/blog/open-models-report#the-scaling-of-open-models-lags-by-about-15-months), the success of techniques like [model distillation](https://arxiv.org/abs/2501.19393), and continual progress in GPUs enabling larger models to be run at home.

Epoch's work is free to use, distribute, and reproduce provided the source and authors are credited under the Creative Commons BY license.

## Learn more about this graph

We find that leading open models runnable on a single consumer GPU typically match the capabilities of frontier models after an average lag between 6-12 months. This relatively short and consistent lag means that the most advanced AI capabilities are becoming widely accessible for local development and experimentation in under a year.

### Data

Model information, such as release date and parameter count, is drawn from original model reports, the [Epoch AI Models database](https://epoch.ai/data/ai-models), and HuggingFace model cards. Benchmark scores are aggregated from the [Epoch AI Benchmarking Hub](https://epoch.ai/benchmarks), Artificial Analysis, LM Arena, and developer-reported results.

We analyze model performance across four benchmarks/metrics: GPQA-Diamond, MMLU-Pro, the Artificial Analysis Intelligence Index, and LM Arena Elo scores. We selected GPQA-Diamond and MMLU-Pro because they test a broad conception of knowledge and reasoning, have remained unsaturated over a reasonably long period, and have good data availability. We include the Artificial Analysis Intelligence Index as it provides a composite score of model performance. However, this index incorporates GPQA-Diamond and MMLU-Pro, so there is correlation between these metrics. Finally, we include LM Arena Elo scores to capture user preferences, though LM Arena Elo scores have [their own limitations](https://arxiv.org/abs/2504.20879).

Epoch’s Benchmarking Hub prioritizes models at or near the frontier of capabilities, and thus tends to underrepresent small, open models. To identify models that push the frontier of the capabilities available on a consumer GPU, we use the following steps:

1. **Defining Hardware Constraints**: We first establish the largest parameter size model that can be run on the NVIDIA consumer GPU at the time. Based on memory capacity and common quantization schemes, we defined this limit as ≤ 28B parameters for the NVIDIA RTX 4090 era and ≤ 40B parameters for the subsequent RTX 5090 era.
2. **Identifying SOTA Open Models**: To create a candidate list of high-performing open models within these size constraints, we analyzed evaluation data from sources like the [OpenLLM Leaderboard](https://huggingface.co/spaces/open-llm-leaderboard/open_llm_leaderboard#/) and [Artificial Analysis](https://artificialanalysis.ai/models/open-source/small). OpenLLM leaderboard has comprehensive coverage of open models and provides a strong signal for identifying which models were pushing the frontier of capabilities over time. However, the initiative ended in February 2025 so we supplemented and cross-checked this with data from Artificial Analysis to create a set of open models that were at or near the performance frontier for their respective time periods.
3. **Collecting and Prioritizing Scores**: For each model, we sought a reliable benchmarks score. We consider multiple sources and employ a hierarchy for collecting scores. Our prioritization was as follows: 1) Artificial Analysis benchmarking, as they have the most extensive GPQA-Diamond and MMLU-Pro coverage for small models, 2) Epoch AI Benchmarking Hub, and 3) developer-reported results (which tend to be slightly higher than third-party evaluations). For many older models, we relied exclusively on third-party evaluations. Some potentially significant open models are excluded from the analysis due to a lack of available scores from any of the sources. For model Elo values, we pull the style-controlled scores from the LM Arena Text leaderboard.

We use data from Epoch AI’s Benchmarking Hub to plot the absolute frontier on GPQA-Diamond. For plotting absolute frontier on MMLU-Pro and AA Intelligence Index, we use data from Artificial Analysis.

### Analysis

A key component of our analysis is determining the largest model size that a single node of the RTX 4090 and 5090 can run. We focus on models that could fit entirely on a card’s VRAM with weights quantized to 4-bits. The total VRAM usage is modeled as:

$$
\text{VRAM Usage} = \text{Weights} + \text{KV Cache} + \text{Runtime Overhead}
$$
We make the following calculations and assumptions:

1. **VRAM Conversion:** We convert a card’s marketed VRAM from decimal gigabytes (GB) to binary gibibytes (GiB), which is standard for memory reporting. The RTX 4090’s 24GB is \~22.37 GiB, and the RTX 5090’s 32 GB is \~29.80 GiB.
2. **Component Sizing:** We assume typical values for each component:
  - Weights: We use an average of 0.54 bytes per parameter, which is typical of 4-bit quantized models.
  - KV Cache: We assume an 8k context length with INT8 precision in a Llama-class model depth and width, resulting in a cache size of \~6.6 GiB.
  - Overhead: We add \~2 GiB for the CUDA context, allocator fragmentation, and other runtime needs.

Under these assumptions, the theoretical ceiling for an RTX 4090 is \~27B parameters (weights: 13.6 GiB + KV cache: 6.6 GiB + overhead: 2.0 GiB ≈22.2 GiB). For the RTX 5090, the theoretical ceiling is \~40B parameters.

To obtain an estimate for the performance trend, we fit a simple model regressing benchmark accuracy/score for the top-1 models on release date. To generate confidence intervals, we used bootstrap sampling with replacement (n=500). We then calculated the 5th and 95th percentiles of the bootstrap slope distribution to construct 90% confidence intervals.

Notably, our analysis of LM Arena Elo scores suggests that open models runnable on a consumer GPU have a steeper slope (+125 ELO/year) compared to frontier models (+80 ELO/year), suggesting faster rate of progress for consumer-accessible models.

| Metric | Average Lag | 
|---|---|
| GPQA-Diamond | 7.4 months | 
| MMLU-Pro | 7.3 months | 
| LM Arena Elo | 12.4 months | 
| Artificial Analysis Intelligence Index | 6.3 months | 

Code for our analysis and the plot is available [here](https://colab.research.google.com/drive/1ZMoyYGZC6bd593pLeipCq2Z17J6Il6sj?usp=sharing).

### Assumptions

We rely on benchmark data from multiple sources which introduces variance in evaluation methodologies. To mitigate this, we standardize our sourcing where possible: most of the GPQA-Diamond scores for the open models come from Artificial Analysis and all of the data for the absolute frontier is drawn from Epoch AI’s Benchmarking Hub. We also face data gaps as some open models lack any developer reported or third party evals against GPQA-Diamond.

We model the gap between our two sets of models (small open models, and top-1 frontier) by calculating the average distance between the trends. We use a simple linear regression for our main analysis, to simplify interpretation. For benchmarks scored between 0 and 100%, it is more appropriate to model the relationship over time with a logistic regression, but results are highly similar in either case.

We only consider models whose full set of weights can fit in GPU memory. This creates a bias away from sparsely activated models, since these models outperform dense models with the same number of active parameters but underperform those with the same number of total parameters.

It may be possible to run larger models than our calculated limits on a single GPU, through techniques like VRAM offloading or more extreme quantizations. However, these techniques tend to require significant tradeoffs in inference speed or output quality, respectively. Accepting these tradeoffs would likely reduce the calculated gap modestly.

Our estimates for the largest model runnable on a single node assume a fixed context length of 8K. Our [previous work](https://epoch.ai/data-insights/output-length) has found that the average output length is growing 2.2x per year and 5x per year for non-reasoning and reasoning models respectively. Today’s reasoning models can even average 20K token outputs in which case the KV cache memory footprint would grow to 15 GiB rather than the 6 GiB of 8K context length. Our estimates are therefore on the higher end of what is runnable for long-context applications, however there are techniques to reduce the footprint of the KV cache.
