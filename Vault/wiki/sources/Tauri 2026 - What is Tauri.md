---
type: source
author: "Tauri Contributors"
date: 2026-07-22
venue: "Tauri v2 documentation, 'What is Tauri?' (page dated 2026-07-22; CC-BY / MIT; retrieved 2026-10-18)"
url: "https://v2.tauri.app/start/"
tags: [source, desktop-framework, rust, webview, cross-platform, security, demo-runtime]
---
# Tauri 2026 – What is Tauri?

**Raw file**: `raw/demo/Tauri 2026 - What is Tauri_ingested.md`

## Overview
The official introduction to Tauri v2: a framework for "tiny, fast binaries for all major desktop and mobile platforms", with any HTML/JS/CSS front-end and "languages such as Rust, Swift, and Kotlin for backend logic when needed". It names three advantages: a secure foundation, smaller bundles through the system web view, and flexibility of front-end and language bindings.

## Key Insights
- **Security**: built on Rust (memory, thread and type safety); a security audit for every major and minor release, covering upstream dependencies too (Tauri 2.0 audit by Radically Open Security). The page notes this "doesn't mitigate all risks".
- **Size**: apps reuse the system web view and do not bundle a browser engine; "a minimal Tauri app can be less than 600KB".
- **Bindings**: JavaScript calls Rust through the `invoke` function; **Swift and Kotlin bindings exist for Tauri Plugins** (the page does not say on which platforms; presumably the mobile targets, to be checked in the plugin docs).
- **Building blocks**: TAO (windows) and WRY (web view rendering) are Tauri-maintained libraries usable directly; an official and community plugin catalogue extends the core.
- Onboarding: `create-tauri-app`, a prerequisites guide, project-structure docs. Short page; no performance figures.

## Relevance to GroundOne
- Complements the README for [[Demo Runtime Choice]]: the 600 KB figure and the audit are Tauri's strongest arguments, but **bundle size is irrelevant for GroundOne**, whose app ships with ~0.5–3.5 GB of model weights (0.5B and 3B in 8-bit; order of magnitude from the parameter counts, not from this source).
- The Swift plugin bindings suggest a hybrid (Tauri shell + Swift plugin calling MLX Swift) is conceivable, but it would add a Rust layer and an IPC hop for no inference benefit; a native SwiftUI app keeps the MLX call on one in-process worker thread, as `engine.py` already does in Python (Metal contexts should not hop threads).
- The security argument (Rust memory safety) applies to the UI shell, not to the Metal kernels where the model runs.

## Links
- Concepts: [[Demo Runtime Choice]], [[Demo Application]], [[On-Device Inference]]
- Related: [[Tauri 2026 - Tauri, desktop and mobile apps with a web frontend (GitHub README)]], [[Hugging Face 2026 - candle, minimalist ML framework for Rust (GitHub README)]], [[Swift.org 2026 - Platform support]]
