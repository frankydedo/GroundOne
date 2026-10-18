---
type: concept
tags: [concept, retrieval, bm25, fts5, sqlite, embeddings, rag, demo, local]
---
# Local RAG Retrieval

Retrieval that runs entirely on the device, with no external vector database or embedding API. Retrieval component of the GroundOne demo ([[Demo Application]]).

## Building blocks available on a Mac
- **Lexical: SQLite FTS5.** Built into SQLite since 3.9.0; BM25 ranking (k1 = 1.2, b = 0.75; scores negated, lower is better; the `rank` column sorts faster); tokenizers unicode61, ascii, porter, trigram; `snippet()` and `highlight()` show the matching evidence ([[SQLite 2026 - FTS5 full-text search extension]]). No model, no download, deterministic.
- **Dense: sqlite-vec.** Pure-C SQLite extension with `vec0` tables (float, int8, binary) and KNN through `MATCH … ORDER BY distance`; pre-v1, breaking changes expected; no Swift binding and no stated licence in the README; loading extensions into the system SQLite is not covered, so bundling SQLite is the safe route ([[Garcia 2026 - sqlite-vec, vector search SQLite extension (GitHub README)]]).
- **Embeddings:** `NLEmbedding` (built-in word embeddings, a sentence-embedding API, custom compiled embeddings; not thread-safe; quality for retrieval unknown) ([[Apple 2026 - NLEmbedding documentation]]), or an MLX embedding model through `MLXEmbedders` ([[Apple ML Explore 2026 - MLX Swift LM, LLMs and VLMs with MLX Swift (GitHub README)]]). For a few hundred pages a brute-force cosine search in memory is enough.
- **Ingestion:** PDFKit for PDF text and display (the fetched page documents only topic titles; text extraction to verify in the class docs) ([[Apple 2026 - PDFKit documentation]]).

## Interaction with the verifier
- The retrieved passages are the *document* GroundOne reads; their total length drives the verifier's prefill cost ([[Prefill and Decode]]).
- A retrieval miss surfaces as a **"not mentioned"** verdict. This is a useful signal: the policy can re-query with the flagged sentence before asking the generator to rewrite (as CRAG corrects retrieval before generation, [[Yan 2024 - Corrective Retrieval Augmented Generation (arXiv 2401.15884)|Yan 2024]]).
- Lexical retrieval misses paraphrases; dense retrieval misses exact names and numbers. A hybrid (BM25 + embeddings) is the common compromise; for the demo BM25 alone is the simplest defensible default.

## Links
- [[Retrieval-Augmented Generation]], [[Demo Application]], [[Verify-and-Revise Loops]], [[On-Device Inference]], [[Lewis 2020 - Retrieval-Augmented Generation]]
