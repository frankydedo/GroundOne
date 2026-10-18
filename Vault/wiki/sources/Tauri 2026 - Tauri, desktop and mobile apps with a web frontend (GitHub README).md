---
type: source
author: "The Tauri Programme within The Commons Conservancy"
date: 2026
venue: "GitHub repository README, tauri-apps/tauri (status: stable; code MIT or MIT/Apache-2.0, logo CC-BY-NC-ND; retrieved 2026-10-18)"
url: "https://github.com/tauri-apps/tauri"
tags: [source, desktop-framework, rust, webview, cross-platform, demo-runtime]
---
# Tauri 2026 – Tauri: desktop and mobile apps with a web frontend (README)

**Raw file**: `raw/demo/Tauri 2026 - Tauri, desktop and mobile apps with a web frontend (GitHub README)_ingested.md`

## Overview
Tauri builds "tiny, blazingly fast binaries for all major operating systems". The UI is any front-end that compiles to HTML, JS and CSS; the backend is "a rust-sourced binary with an API that the front-end can interact with". Window handling is done by `tao`; rendering by **WRY**, a unified interface to the **system web view**: WKWebView on macOS and iOS, WebView2 on Windows, WebKitGTK on Linux, Android System WebView on Android. Sustained as a programme of the Commons Conservancy (Open Collective; partner CrabNebula).

## Key Insights
- **Platforms**: Windows 10+, **macOS 10.15+**, Linux (webkit2gtk 4.1 for Tauri v2, e.g. Ubuntu 22.04), iOS/iPadOS 9+, Android 7+ (currently 8+).
- **Features**: built-in bundler (`.app`, `.dmg`, `.deb`, `.rpm`, `.AppImage`, NSIS `.exe`, WiX `.msi`), self-updater (desktop only), system tray, native notifications, GitHub Action for CI, VS Code extension.
- **Native WebView protocol**: Tauri "doesn't create a localhost http(s) server" to serve the web view contents.
- **Licence**: MIT or MIT/Apache-2.0 where applicable.
- Getting started: `npm create tauri-app@latest`; architecture details in `ARCHITECTURE.md` (not ingested).

## Relevance to GroundOne
- **The main rejected alternative for the demo UI** ([[Demo Runtime Choice]]). Strengths: cross-platform reach, a web UI (rich text highlighting of supported / contradicted / not-mentioned sentences is easy in HTML), small bundles because no browser engine is shipped.
- **Why it loses for this demo**: (1) inference is the hard part and is Apple-GPU-specific anyway (MLX/Metal), so Tauri's cross-platform reach buys nothing for the verifier; (2) the Rust backend would need mlx-rs (unofficial bindings), llama.cpp or candle, i.e. either an unofficial MLX path or leaving the trained MLX 8-bit adapters; (3) the stack spans three languages (Rust, JS/TS, plus the model runtime) and an IPC boundary between UI and backend. On macOS the UI would render in WKWebView, the same engine as a SwiftUI `WKWebView` would use, so the visual advantage is small.
- Fair statement for the thesis: Tauri would be the better choice if the demo had to run on Windows/Linux too; it does not, because the thesis pillar is local inference on one Apple Silicon laptop ([[On-Device Inference]]).

## Links
- Concepts: [[Demo Runtime Choice]], [[Demo Application]], [[On-Device Inference]], [[Apple Silicon and MLX]], [[MLX Ecosystem]]
- Related: [[Tauri 2026 - What is Tauri]], [[Hugging Face 2026 - candle, minimalist ML framework for Rust (GitHub README)]], [[oxiglade 2026 - mlx-rs, unofficial Rust bindings to MLX (GitHub README)]], [[Swift.org 2026 - Platform support]], [[llama.cpp README (ggml-org)]]
