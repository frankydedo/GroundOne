---
source: https://llm-aggrefact.github.io/
accessed: 2026-10-05
citation: "Tang, L., Laban, P., Durrett, G. LLM-AggreFact Leaderboard (benchmark from MiniCheck, EMNLP 2024)."
note: "Page text converted to markdown. The site shows 11 of 39 models by default; the full table below was extracted from the data embedded in the page. *Average = unweighted mean of the 11 dataset BAcc scores (matches the site's Average column)."
---

- [Home](/)
- [Blog](/blog)

# LLM-AggreFact Leaderboard
LLM-AggreFact is a fact-checking benchmark that aggregates 11 of the most up-to-date publicly available datasets on grounded factuality (i.e., hallucination) evaluation.
Please see our [blog post](/blog) for a more detailed description.

### Benchmark Details [expand]

### Model Comparison
Compare model performance across different datasets.


## Full leaderboard (all 39 models)

| Rank | Model | Size | Average* | CNN | XSum | MediaS | MeetB | WiCE | REVEAL | ClaimVerify | FactCheck | ExpertQA | LFQA | RAGTruth | Link |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Bespoke-Minicheck-7B | 7B | 77.4 | 65.5 | 77.8 | 76 | 78.3 | 83 | 88 | 75.3 | 77.7 | 59.2 | 86.7 | 84 | https://huggingface.co/bespokelabs/Bespoke-Minicheck-7B |
| 2 | Claude-3.5 Sonnet | - | 77.2 | 67.6 | 75.1 | 73.4 | 84.6 | 77.7 | 89.1 | 71.4 | 77.8 | 60.9 | 85.6 | 86.1 | https://www.anthropic.com/news/claude-3-5-sonnet |
| 3 | Mistral-Large 2 | 123B | 76.5 | 64.8 | 74.7 | 69.6 | 84.2 | 80.3 | 87.7 | 71.8 | 74.5 | 60.8 | 87 | 85.9 | https://huggingface.co/mistralai/Mistral-Large-Instruct-2407 |
| 4 | Granite Guardian 3.3 | 8B | 76.5 | 67 | 74.9 | 74 | 78.6 | 76.6 | 89.6 | 75.9 | 76.1 | 59.6 | 86.9 | 82.2 | https://huggingface.co/ibm-granite/granite-guardian-3.3-8b |
| 5 | gpt-4-turbo-preview | - | 76.2 | 66.7 | 76.5 | 71.4 | 79.9 | 80.4 | 87.8 | 67.6 | 79.9 | 59.2 | 83.1 | 85.3 | https://platform.openai.com/docs/models/gpt-4-turbo-and-gpt-4 |
| 6 | gpt-4o-2024-05-13 | - | 75.9 | 68.1 | 76.8 | 71.4 | 79.8 | 78.5 | 86.5 | 69 | 77.5 | 59.6 | 83.6 | 84.3 | https://platform.openai.com/docs/models/gpt-4o |
| 7 | Qwen2.5-72B-Instruct | 72B | 75.6 | 63.6 | 73 | 71.9 | 80.4 | 80.2 | 88.9 | 70 | 77 | 60.1 | 84.3 | 81.9 | https://huggingface.co/Qwen/Qwen2.5-72B-Instruct |
| 8 | FactCG-DeBERTa-L | 0.4B | 75.6 | 70.1 | 73.9 | 72.3 | 74.3 | 74.2 | 88.4 | 78.5 | 72.1 | 59.1 | 86.7 | 82.3 | https://github.com/derenlei/FactCG |
| 9 | Llama-3.1-70B-Instruct | 70B | 75.1 | 65.7 | 72.5 | 72.9 | 81 | 73.9 | 86.4 | 70.3 | 78.6 | 58.5 | 83.8 | 83 | https://huggingface.co/meta-llama/Meta-Llama-3.1-70B-Instruct |
| 10 | MiniCheck-Flan-T5-L | 0.8B | 75.0 | 69.9 | 74.3 | 73.6 | 77.3 | 72.2 | 86.2 | 74.6 | 74.7 | 59 | 85.2 | 78 | https://huggingface.co/lytang/MiniCheck-Flan-T5-Large |
| 11 | Claude-3 Opus | - | 74.8 | 65.2 | 72.4 | 74.1 | 82.4 | 75 | 83.8 | 69.3 | 78.8 | 58.8 | 81.6 | 81.8 | https://www.anthropic.com/news/claude-3-family |
| 12 | Llama-3.3-70B-Instruct | 70B | 74.5 | 68.7 | 74.7 | 69.5 | 78.4 | 76.6 | 85.5 | 67.4 | 78.5 | 58.3 | 79.8 | 82.6 | https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct |
| 13 | Llama-3.1-405B-Instruct | 405B | 74.4 | 64.8 | 75.1 | 68.6 | 81.2 | 71.8 | 86.4 | 67.5 | 79.4 | 58.5 | 81.9 | 82.9 | https://huggingface.co/meta-llama/Meta-Llama-3.1-405B-Instruct |
| 14 | Mistral-Large | - | 74.2 | 58.4 | 76.3 | 67.3 | 78.9 | 76.6 | 88.4 | 67.6 | 79 | 60 | 81.7 | 81.7 | https://mistral.ai/news/mistral-large/ |
| 15 | gpt-4o-mini-2024-07-18 | - | 74.0 | 61.8 | 73.6 | 71.3 | 79.7 | 76.3 | 85.8 | 69.8 | 76 | 58.3 | 80.3 | 81.6 | https://openai.com/index/gpt-4o-mini-advancing-cost-efficient-intelligence/ |
| 16 | Llama-3-70B-Instruct | 70B | 73.7 | 63.7 | 70.2 | 71.5 | 80.6 | 74.4 | 85.9 | 67.8 | 76.2 | 57.8 | 82.4 | 80.6 | https://huggingface.co/meta-llama/Meta-Llama-3-70B-Instruct |
| 17 | MiniCheck-RoBERTa-L | 0.4B | 73.5 | 63.7 | 70.8 | 71.9 | 75.9 | 67.6 | 88.8 | 77.4 | 73.3 | 57.4 | 84.4 | 77.2 | https://huggingface.co/lytang/MiniCheck-RoBERTa-Large |
| 18 | MiniCheck-DeBERTa-L | 0.4B | 73.1 | 64.2 | 71 | 69.3 | 72.7 | 69.4 | 87.3 | 75.6 | 73 | 58.9 | 83.9 | 78.8 | https://huggingface.co/lytang/MiniCheck-DeBERTa-v3-Large |
| 19 | Qwen2.5-7B-Instruct | 7B | 72.8 | 54.6 | 69.9 | 71.5 | 75.2 | 76.3 | 86.9 | 70.1 | 74.9 | 61 | 84.2 | 76.5 | https://huggingface.co/Qwen/Qwen2.5-7B-Instruct |
| 20 | QwQ-32B-Preview | 32B | 71.8 | 57 | 71.6 | 69.3 | 78.5 | 72.3 | 86.2 | 67.7 | 75.6 | 60 | 78.9 | 72.4 | https://huggingface.co/Qwen/QwQ-32B-Preview |
| 21 | HHEM-2.1-open | 0.1B | 71.8 | 62.8 | 67.8 | 67.2 | 71 | 75.9 | 86.6 | 73.9 | 71.8 | 58.4 | 84.1 | 69.9 | https://huggingface.co/vectara/hallucination_evaluation_model |
| 22 | Mixtral-8x22B | 176B | 71.5 | 57.3 | 70.3 | 69 | 78.5 | 69.5 | 85.8 | 63.8 | 79.5 | 57.4 | 76.5 | 78.8 | https://huggingface.co/mistralai/Mixtral-8x22B-Instruct-v0.1 |
| 23 | Claude-2.1 | - | 71.1 | 59.9 | 66.4 | 69.2 | 72.3 | 64.3 | 88.2 | 69.7 | 79.3 | 59.8 | 78.2 | 75 | https://www.anthropic.com/news/claude-2-1 |
| 24 | AlignScore | 0.4B | 70.5 | 52.4 | 71.4 | 69.2 | 72.6 | 66 | 85.3 | 69.6 | 74.3 | 58.3 | 84.5 | 71.7 | https://github.com/yuh-zha/AlignScore |
| 25 | Llama-3.1-8B-Instruct | 8B | 70.3 | 54.7 | 68.5 | 71.1 | 75.5 | 72 | 83.5 | 66.5 | 72.3 | 57.8 | 77.5 | 73.6 | https://huggingface.co/meta-llama/Meta-Llama-3.1-8B-Instruct |
| 26 | GPT-3.5-Turbo | - | 70.1 | 63.2 | 72.4 | 66.8 | 73.4 | 68.5 | 84.7 | 65.2 | 70.8 | 57.2 | 73.8 | 75.6 | https://platform.openai.com/docs/models/gpt-3-5-turbo |
| 27 | SummaC-ZS | 0.1B | 67.7 | 51.1 | 61.5 | 69.5 | 71 | 62.8 | 85.3 | 69.7 | 75.2 | 55.2 | 77.6 | 65.6 | https://github.com/tingofurro/summac/ |
| 28 | Tülu-3-70B | 70B | 67.6 | 58.3 | 66.4 | 62.7 | 70.6 | 64.6 | 82.5 | 62.2 | 76.5 | 55.7 | 70.8 | 73.8 | https://huggingface.co/allenai/Llama-3.1-Tulu-3-70B |
| 29 | Mistral-8x7B | 56B | 67.4 | 55 | 65.5 | 68.5 | 73.3 | 63.8 | 80.8 | 64.3 | 75.1 | 56.3 | 70.8 | 68.1 | https://mistral.ai/technology/#models |
| 30 | PaLM2-Bison | - | 66.1 | 52.4 | 59 | 68.3 | 73.6 | 63.4 | 84.2 | 60.5 | 76.4 | 56.6 | 71.4 | 61.6 | https://blog.google/technology/ai/google-palm-2-ai-large-language-model/ |
| 31 | Gemini-Pro | - | 65.4 | 49.4 | 60.6 | 63.8 | 65.8 | 65.8 | 85.5 | 61.8 | 76.8 | 56.8 | 75.9 | 57.6 | https://deepmind.google/technologies/gemini/pro/ |
| 32 | DAE | 0.1B | 65.0 | 50.8 | 59.1 | 65.1 | 69.5 | 58.5 | 81.3 | 64 | 72.5 | 56.2 | 72.2 | 65.3 | https://github.com/tagoyal/factuality-datasets |
| 33 | Qwen2.5-0.5B-Instruct | 0.5B | 64.2 | 55.5 | 62.9 | 60 | 64.7 | 65.9 | 85.8 | 61.4 | 68.9 | 56.8 | 72.4 | 51.6 | https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct |
| 34 | InternLM2.5-7B-chat | 7B | 63.6 | 58.4 | 57.9 | 62.5 | 68 | 63.7 | 77.3 | 59.8 | 67.5 | 55.2 | 64.9 | 64 | https://huggingface.co/internlm/internlm2_5-7b-chat |
| 35 | Tülu-3-8B | 8B | 63.2 | 51 | 58.5 | 63.4 | 67.7 | 58.7 | 81.8 | 63.2 | 68.6 | 56.2 | 68.5 | 57.8 | https://huggingface.co/allenai/Llama-3.1-Tulu-3-8B |
| 36 | T5-NLI-Mixed | 11B | 61.1 | 54.6 | 52.3 | 59.1 | 55.3 | 55.3 | 87.2 | 59.5 | 69 | 55.6 | 61.8 | 62.5 | https://huggingface.co/google/t5_xxl_true_nli_mixture |
| 37 | SummaC-CV | 0.1B | 61.0 | 65.2 | 54.5 | 63.7 | 62.8 | 54.3 | 67.7 | 70.9 | 53.4 | 54.9 | 62.1 | 61.7 | https://github.com/tingofurro/summac/ |
| 38 | Llama-3.2-3B-Instruct | 3B | 60.0 | 51.5 | 60.5 | 53.1 | 52.5 | 58.5 | 81.9 | 62.3 | 62.6 | 55.8 | 58.5 | 63 | https://huggingface.co/meta-llama/Llama-3.2-3B-Instruct |
| 39 | Llama-3.2-1B-Instruct | 1B | 50.3 | 50.1 | 50.9 | 50 | 50.2 | 49.7 | 50.4 | 50.5 | 50.2 | 49.9 | 50.1 | 50.9 | https://huggingface.co/meta-llama/Llama-3.2-1B-Instruct |
### Team [expand]

### Citation [expand]