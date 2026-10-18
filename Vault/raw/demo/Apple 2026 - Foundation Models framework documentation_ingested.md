---
title: "Apple 2026 - Foundation Models framework documentation"
url: https://developer.apple.com/documentation/foundationmodels
accessed: 2026-10-18
source: Apple developer documentation JSON
---

# Foundation Models
Perform tasks with models that specialize in language understanding, structured output, and tool calling.

## Overview
The Foundation Models framework provides access to any large language model, like the on-device and Private Cloud Compute models designed for Apple Intelligence. These models help you perform intelligent tasks specific to your use case.

On-device models excel at a diverse range of text generation tasks, like summarization, entity extraction, text and image understanding, refinement, dialog for games, generating creative content, and more. When you need more reasoning capabilities and context size, use Private Cloud Compute or any server model provider.
The dynamic profile API provides the flexibility to select the best model configuration for your task, and lets you build many useful abstractions, such as agents or skills.
Generate entire Swift data structures with guided generation. With the `@Generable` macro, you can define custom data structures and the framework provides strong guarantees that the model generates instances of your type.
Use Tool to create custom tools that the model can call to assist with handling your request. For example, the model can call a tool that searches a local or online database for information, or calls a service in your app.
To use Apple Foundation Models, people need a device that supports Apple Intelligence. For a list of supported devices, see .

## What’s new
- topic: Essentials
- topic: Sessions and prompts
- topic: Session transcripts
- topic: Prompt attachments
- topic: Dynamic profiles
- topic: Structured output
- topic: Tools
- topic: System language model
- topic: Private Cloud Compute
- topic: Custom language model provider
- topic: Custom session properties
- topic: Safety
- topic: Performance and evaluation
- topic: Protocols
