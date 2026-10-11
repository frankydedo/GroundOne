---
title: "Google 2025 - Introducing Gemma 3n"
url: https://developers.googleblog.com/en/introducing-gemma-3n/
published: 2025-05-20
accessed: 2026-10-11
extracted_with: trafilatura 2.3.1
---

MAY 20, 2025

Following the exciting launches of [Gemma 3](https://blog.google/technology/developers/gemma-3/) and [Gemma 3 QAT](https://developers.googleblog.com/en/gemma-3-quantized-aware-trained-state-of-the-art-ai-to-consumer-gpus/), our family of state-of-the-art open models capable of running on a single cloud or desktop accelerator, we're pushing our vision for accessible AI even further. Gemma 3 delivered powerful capabilities for developers, and we're now extending that vision to highly capable, real-time AI operating directly on the devices you use every day – your phones, tablets, and laptops.

To power the next generation of on-device AI and support a diverse range of applications, including advancing the capabilities of Gemini Nano, we engineered a new, cutting-edge architecture. This next-generation foundation was created in close collaboration with mobile hardware leaders like Qualcomm Technologies, MediaTek, and Samsung's System LSI business, and is optimized for lightning-fast, multimodal AI, enabling truly personal and private experiences directly on your device.

[Gemma 3n](https://deepmind.google/models/gemma/gemma-3n/) is our first open model built on this groundbreaking, shared architecture, allowing developers to begin experimenting with this technology today in an early preview. The same advanced architecture also powers the next generation of [Gemini Nano](https://deepmind.google/technologies/gemini/nano/), which brings these capabilities to a broad range of features in Google apps and our on-device ecosystem, and will become available later this year. Gemma 3n enables you to start building on this foundation that will come to major platforms such as Android and Chrome.

This chart ranks AI models by Chatbot Arena Elo scores; higher scores (top numbers) indicate greater user preference. Gemma 3n ranks highly amongst both popular proprietary and open models.

Gemma 3n leverages a Google DeepMind innovation called Per-Layer Embeddings (PLE) that delivers a significant reduction in RAM usage. While the raw parameter count is 5B and 8B, this innovation allows you to run larger models on mobile devices or live-stream from the cloud, with a memory overhead comparable to a 2B and 4B model, meaning the models can operate with a dynamic memory footprint of just 2GB and 3GB. Learn more in our [documentation](https://ai.google.dev/gemma/docs/gemma-3n#parameters).

By exploring Gemma 3n, developers can get an early preview of the open model’s core capabilities and mobile-first architectural innovations that will be available on Android and Chrome with Gemini Nano.

In this post, we'll explore Gemma 3n's new capabilities, our approach to responsible development, and how you can access the preview today.

Key Capabilities of Gemma 3n

Engineered for fast, low-footprint AI experiences running locally, Gemma 3n delivers:

- **Optimized On-Device Performance & Efficiency:** Gemma 3n starts responding approximately 1.5x faster on mobile with significantly better quality (compared to Gemma 3 4B) and a reduced memory footprint achieved through innovations like Per Layer Embeddings, KVC sharing, and advanced activation quantization.

- **Many-in-1 Flexibility:** A model with a 4B active memory footprint that natively includes a nested state-of-the-art 2B active memory footprint submodel (thanks to [MatFormer](https://arxiv.org/abs/2310.07707) training). This provides flexibility to dynamically trade off performance and quality on the fly without hosting separate models. We further introduce mix’n’match capability in Gemma 3n to dynamically create submodels from the 4B model that can optimally fit your specific use case -- and associated quality/latency tradeoff. Stay tuned for more on this research in our upcoming technical report.

- **Privacy-First & Offline Ready:** Local execution enables features that respect user privacy and function reliably, even without an internet connection.

- **Expanded Multimodal Understanding with Audio:** Gemma 3n can understand and process audio, text, and images, and offers significantly enhanced video understanding. Its audio capabilities enable the model to perform high-quality Automatic Speech Recognition (transcription) and Translation (speech to translated text). Additionally, the model accepts interleaved inputs across modalities, enabling understanding of complex multimodal interactions. (Public implementation coming soon)

- **Improved Multilingual Capabilities:** Improved multilingual performance, particularly in Japanese, German, Korean, Spanish, and French. Strong performance reflected on multilingual benchmarks such as 50.1% on WMT24++ (ChrF).

This chart show’s MMLU performance vs model size of Gemma 3n’s mix-n-match (pretrained) capability.

Gemma 3n will empower a new wave of intelligent, on-the-go applications by enabling developers to:

1. **Build live, interactive experiences** that understand and respond to real-time visual and auditory cues from the user's environment.




Here’s an overview and the types of experiences you can build:

[Link to Youtube Video](https://www.youtube.com/watch?v=eJFJRyXEHZ0)
          (visible only when JS is disabled)

Our commitment to responsible AI development is paramount. Gemma 3n, like all Gemma models, underwent rigorous safety evaluations, data governance, and fine-tuning alignment with our safety policies. We approach open models with careful risk assessment, continually refining our practices as the AI landscape evolves.

Get Started: Preview Gemma 3n Today

We're excited to get Gemma 3n into your hands through a preview starting today:


Initial Access (Available Now):

- **Cloud-based Exploration with Google AI Studio:** Try Gemma 3n directly in your browser on [Google AI Studio](https://aistudio.google.com/app/prompts/new_chat?model=gemma-3n-e4b-it) – no setup needed. Explore its text input capabilities instantly.

- **On-Device Development with Google AI Edge:** For developers looking to integrate Gemma 3n locally, [Google AI Edge](https://developers.googleblog.com/en/google-ai-edge-small-language-models-multimodality-rag-function-calling) provides tools and libraries. You can get started with text and image understanding/generation capabilities today.


Gemma 3n marks the next step in democratizing access to cutting-edge, efficient AI. We’re incredibly excited to see what you’ll build as we make this technology progressively available, starting with today's preview.

Explore this announcement and all Google I/O 2025 updates on [io.google](https://io.google/2025/?utm_source=blogpost&utm_medium=pr&utm_campaign=event&utm_content=) starting May 22.
