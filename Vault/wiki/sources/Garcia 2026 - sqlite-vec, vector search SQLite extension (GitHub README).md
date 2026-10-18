---
type: source
author: "Alex Garcia (asg017) and contributors"
date: 2026
venue: "GitHub repository README, asg017/sqlite-vec (pre-v1; Mozilla Builders project; licence not stated in the extracted README; retrieved 2026-10-18)"
url: "https://github.com/asg017/sqlite-vec"
tags: [source, vector-search, sqlite, embeddings, retrieval, local-rag]
---
# Garcia 2026 – sqlite-vec, a vector search SQLite extension

**Raw file**: `raw/demo/Garcia 2026 - sqlite-vec, vector search SQLite extension (GitHub README)_ingested.md`

## Overview
"An extremely small, 'fast enough' vector search SQLite extension that runs anywhere", successor to `sqlite-vss`. It is a Mozilla Builders project (sponsored to "enable more powerful local AI applications"), with further sponsorship from Fly.io, Turso, SQLite Cloud and Shinkai. The README warns: **pre-v1, "expect breaking changes"**.

## Key Insights
- **Data model**: `vec0` virtual tables storing **float, int8 and binary** vectors; non-vector data in metadata, auxiliary or partition-key columns.
- **Implementation**: pure C, no dependencies, "runs anywhere SQLite runs" (Linux, macOS, Windows, browser via WASM, Raspberry Pi).
- **Query**: KNN via `WHERE embedding MATCH '<vector>' ORDER BY distance LIMIT k`; vectors given as JSON or a compact binary format. Loaded with `.load ./vec0`.
- **Packaged bindings**: Python, Node.js, Ruby, Go, Rust, Datasette, rqlite, sqlite-utils. **No Swift package is listed**; a Swift app would compile the C source into the app or load the extension.
- Siblings: `sqlite-lembed` (local embeddings from `.gguf` models), `sqlite-rembed` (remote embedding APIs).
- The README gives no index type (the example is brute-force-style KNN), no benchmarks and no licence text.

## Relevance to GroundOne
- **Optional dense half of the demo retriever** ([[Local RAG Retrieval]]): chunk embeddings live in the same SQLite file as the FTS5 index and the document store, so ingestion, keyword and vector search stay in one local database with no server. Hybrid ranking (BM25 + cosine) can then be done in SQL or in Swift.
- **Costs to state**: an embedding model is needed (NLEmbedding, a small MLX encoder, or a gguf model via sqlite-lembed), which competes for the 16 GB memory budget with the generator and GroundOne; pre-v1 API stability; integration work for Swift (C build; whether the macOS system SQLite permits loading extensions is not covered here and must be checked, bundling SQLite is the safe path).
- For a demo corpus of a few documents, brute-force KNN is adequate; scale claims should not be made from this source.

## Links
- Concepts: [[Local RAG Retrieval]], [[Retrieval-Augmented Generation]], [[Demo Application]], [[On-Device Inference]]
- Related: [[SQLite 2026 - FTS5 full-text search extension]], [[Apple 2026 - NLEmbedding documentation]], [[Lewis 2020 - Retrieval-Augmented Generation]]
