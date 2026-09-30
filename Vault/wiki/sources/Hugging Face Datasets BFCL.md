---
type: source
author: "Gorilla LLM"
date: 2026-09-28
tags:
  - dataset
  - function-calling
---
# Hugging Face Datasets BFCL

## Overview
This source details the dataset composition and evaluation methodology for the Berkeley Function Calling Leaderboard (BFCL) hosted on Hugging Face.

## Key Insights
- **Dataset Versions**:
  - **BFCL V1**: Covers Python (Simple, Multiple, Parallel) and Non-Python (Chatting, REST API, SQL, Java, JS). Evaluates via AST and Executable paths.
  - **BFCL V2 Live**: Uses real-world data with a focus on multiple function scenarios and relevance/irrelevance detection (e.g., when no functions are relevant).
  - **BFCL V3**: Introduces multi-step and multi-turn function calling, including missing parameters/functions, long-context, and composite scenarios.
- **Relevance Detection**: Tests whether models hallucinate function calls when none are applicable.
- **Evaluation Format**: The dataset is organized in JSON files (not compatible with HF's `load_dataset`), evaluating both Abstract Syntax Tree (AST) matching and executable correctness.
