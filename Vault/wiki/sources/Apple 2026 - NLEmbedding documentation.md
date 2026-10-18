---
type: source
author: "Apple Inc."
date: 2026
venue: "Apple Developer Documentation, Natural Language framework, NLEmbedding class (documentation JSON; retrieved 2026-10-18)"
url: "https://developer.apple.com/documentation/naturallanguage/nlembedding"
tags: [source, apple, embeddings, natural-language, retrieval, on-device]
---
# Apple 2026 – NLEmbedding documentation

**Raw file**: `raw/demo/Apple 2026 - NLEmbedding documentation_ingested.md`

## Overview
`NLEmbedding` is "a map of strings to vectors, which locates neighboring, similar strings", part of Apple's Natural Language framework. **Short page**: class overview and topic titles; no dimensions, languages, model details or quality figures.

## Key Insights
- Each vocabulary string has a vector of doubles; the embedding computes distances between strings and nearest neighbours in the vocabulary ("the higher the similarity ... the smaller the distance").
- **Built-in word embeddings** via `wordEmbedding(for:)`; a topic titled **"Creating a sentence embedding"** exists but its contents were not extracted.
- **Custom embeddings** can be compiled into "an efficient, searchable, on-disk representation", at development time with Create ML's `MLWordEmbedding` or at runtime with `writeEmbeddingForDictionary:language:revision:toURL:error:`; any strings (phrases, product names, titles) can be keys.
- **Not thread-safe**: concurrent queries on one instance, even `vector(for:)`, "can crash your app"; serialise access or use one instance per thread or task.

## Relevance to GroundOne
- **Optional dense retriever with zero extra download** ([[Local RAG Retrieval]]): sentence embeddings from the OS could be stored in sqlite-vec next to an FTS5 BM25 index for hybrid retrieval. Their quality for passage retrieval is unknown from this source and would need a small retrieval check before use; the default retriever should stay BM25, which needs no model.
- **Vocabulary-bound neighbour search** (the class's own kNN) works over its vocabulary, not over arbitrary chunk vectors, so a vector index (sqlite-vec) is still needed for document chunks.
- The thread-safety rule matches the demo's design of one serialised inference/worker context (as in `engine.py`).

## Links
- Concepts: [[Local RAG Retrieval]], [[Retrieval-Augmented Generation]], [[Demo Application]], [[On-Device Inference]]
- Related: [[Garcia 2026 - sqlite-vec, vector search SQLite extension (GitHub README)]], [[SQLite 2026 - FTS5 full-text search extension]], [[Apple 2026 - NLTokenizer documentation]], [[Apple 2026 - Core ML documentation]]
