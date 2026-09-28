# Accelerare i Sistemi Multi-Agente tramite Architetture System One

This repository contains the full workspace for my thesis project exploring **System One Models** (specifically, the Jev-inspired SemIf framework) to drastically reduce tool-calling latency in multi-agent architectures.

## Repository Structure

The workspace is divided into several top-level directories:

- **`Project/`**: The core of the thesis project.
  - `doc/`: Thesis proposals, planning documents, and abstracts.
  - `experiments/`: Scripts for benchmarking traditional Generative LLMs (via LM Studio) against the SemIf parallel-evaluation router.
  - `data/`: Datasets for evaluation (e.g., subsets of the Berkeley Function Calling Leaderboard).
- **`SemIf/`**: The core System One framework used for the router experiments.
- **`Preprocessing/`**: Scripts and assets used for data preparation, such as audio transcription of technical talks.
- **`Vault/`**: An Obsidian-based knowledge base acting as an LLM Wiki. It contains deep-dives on architectures, models, and relevant research.
- **`llm-wiki.md`**: A compiled, unified version of the knowledge base.

## Project Goal
The primary objective (developed under `Project/`) is to demonstrate that by replacing autoregressive JSON generation with parallel option evaluation (SemIf-Router), routing latency on local Apple Silicon hardware can be reduced from seconds to milliseconds without significantly impacting tool-choice accuracy (Recall@1).
