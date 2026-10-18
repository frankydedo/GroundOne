---
title: "Apple 2026 - Core ML documentation"
url: https://developer.apple.com/documentation/coreml
accessed: 2026-10-18
source: Apple developer documentation JSON
---

# Core ML
Integrate machine learning models into your app.

## Overview
Use CoreML to integrate machine learning models into your app. CoreML provides a unified representation for all models. Your app uses CoreML APIs and user data to make predictions, and to train or fine-tune models, all on a person’s device.

A model is the result of applying a machine learning algorithm to a set of training data. You use a model to make predictions based on new input data. Models can accomplish a wide variety of tasks that would be difficult or impractical to write in code. For example, you can train a model to categorize photos, or detect specific objects within a photo directly from its pixels.
You build and train a model with the  bundled with Xcode. Models trained using CreateML are in the CoreML model format and are ready to use in your app. Alternatively, you can use a wide variety of other machine learning libraries and then use coremltools.readme.io to convert the model into the CoreML format. Once a model is on a person’s device, you can use CoreML to retrain or fine-tune it on-device, with that person’s data.
CoreML optimizes on-device performance by leveraging the CPU, GPU, and Neural Engine while minimizing its memory footprint and power consumption. Running a model strictly on a person’s device removes any need for a network connection, which helps keep a person’s data private and your app responsive.
The framework is the foundation for domain-specific frameworks and functionality. It supports Vision for analyzing images, NaturalLanguage for processing text, Speech for converting audio to text, and SoundAnalysis for identifying sounds in audio. CoreML itself builds on top of low-level primitives like Accelerate and bnns-library, as well as MetalPerformanceShaders.

If your app integrates AI models using the latest architectures and inference techniques, see CoreAI.
- topic: Core ML models
- topic: Model inputs and outputs
- topic: App integration
- topic: Model encryption
- topic: Compute devices
- topic: Compute plan
- topic: Model state
- topic: Model tensor
- topic: Model structure
- topic: Model errors
- topic: Model deployments
- topic: Optimization
- topic: Reference
