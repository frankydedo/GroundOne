# Accelerating Multi-Agent Systems via System One Architectures

This repository contains the full workspace for my thesis project exploring **System One Models** (specifically, a custom Jev-inspired parallel framework) to drastically reduce tool-calling latency in multi-agent architectures.

## Repository Structure

The workspace is divided into several top-level directories:

- **`Project/`**: The core implementation of the thesis project.
  - `src/router/`: The custom Python engine performing O(1) parallel logit extraction (System One Router).
  - `scripts/`: Utilities for downloading datasets and bootstrapping MLX environments.
  - `data/`: Training and validation datasets based on the Berkeley Function Calling Leaderboard.
  - `benchmarks/`: Evaluation scripts to benchmark traditional LLMs vs our custom router.
  - `docs/`: Thesis proposals, implementation phases, and Gantt charts.
- **`Tesi/`**: The LaTeX source code for the final thesis manuscript.
- **`Preprocessing/`**: Scripts and assets used for data preparation, such as audio transcription of technical talks.
- **`Vault/`**: An Obsidian-based knowledge base acting as an LLM Wiki. It contains deep-dives on architectures, models, and relevant research.
- **`llm-wiki.md`**: A compiled, unified version of the knowledge base.

## Project Goal
The primary objective (developed under `Project/`) is to demonstrate that by replacing autoregressive JSON generation with parallel option evaluation, routing latency on local Apple Silicon hardware can be reduced from seconds to milliseconds without significantly impacting tool-choice accuracy (Recall@1). By leveraging MLX and fine-tuned LoRA adapters, this architecture introduces epistemic honesty (Abstain logic) in a purely typed-decision format.
