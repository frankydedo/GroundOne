---
type: source
author: "Swift.org (Swift project, swiftlang/swift-org-website)"
date: 2026
venue: "Swift.org website, Platform support page (source in swiftlang/swift-org-website; retrieved 2026-10-18)"
url: "https://www.swift.org/platform-support/"
tags: [source, swift, programming-language, cross-platform, toolchain, demo-runtime]
---
# Swift.org 2026 – Platform support

**Raw file**: `raw/demo/Swift.org 2026 - Platform support_ingested.md`

## Overview
The official statement of where Swift's toolchain runs and where Swift programs can be deployed. Platforms are split into **Deployment and Development** (compiler and tools run there) and **Deployment-only** (programs run there, tools may not). Each platform has a "platform owner"; Apple is the toolchain provider for Apple platforms, Linux and Windows, with pull-request testing required on all three.

## Key Insights
- **Development hosts**: macOS (targets Apple platforms), Ubuntu, Debian, Fedora, Amazon Linux, Red Hat UBI, Windows; Swift Package Manager and SourceKit-LSP are available on all of them.
- **Minimum deployment versions**: **macOS 13.0**, iOS 16.0, watchOS 9.0, tvOS 16.0, visionOS 1.0, **Android 9 (API 28)**, Ubuntu 22.04, Debian 12, Fedora 41, Amazon Linux 2023, RHEL UBI 9, Windows 10.0.
- **Debugger/REPL**: debugger everywhere listed; REPL on macOS and Linux distributions, not on iOS/watchOS/tvOS/Windows.
- **Governance**: platform owners meet bi-weekly; toolchains built by non-Apple owners are re-signed by Apple under the swift.org certificate; new platforms are proposed on forums.swift.org and reviewed by the Core team.
- The page covers the **language and core libraries only**; it says nothing about SwiftUI, Metal or MLX Swift.

## Relevance to GroundOne
- Counters the objection that choosing Swift locks the demo to Apple: the **language** is portable (Linux, Windows, Android), so the non-UI core of the demo (segmentation port, retrieval over SQLite, policy logic) could in principle be reused elsewhere. The **UI and inference layers are Apple-only by construction** (SwiftUI and MLX/Metal; facts outside this source), which matches the thesis scope of a single Apple Silicon laptop ([[Demo Runtime Choice]]).
- The macOS 13.0 floor for Swift itself is not the binding constraint; the effective deployment floor of the demo is set by MLX Swift and, if used, by Apple frameworks such as Foundation Models (Apple Intelligence devices only).

## Links
- Concepts: [[Demo Runtime Choice]], [[Demo Application]], [[On-Device Inference]], [[Apple Silicon and MLX]], [[MLX Ecosystem]]
- Related: [[Tauri 2026 - Tauri, desktop and mobile apps with a web frontend (GitHub README)]], [[Apple ML Explore 2026 - MLX Swift (GitHub README)]], [[Apple 2026 - Foundation Models framework documentation]]
