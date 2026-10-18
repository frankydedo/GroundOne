---
type: source
author: "SQLite developers (sqlite.org)"
date: 2026-10-09
venue: "SQLite documentation, 'SQLite FTS5 Extension' (page dated 2026-10-09; retrieved 2026-10-18)"
url: "https://www.sqlite.org/fts5.html"
tags: [source, full-text-search, bm25, sqlite, retrieval, local-rag, tokenizer]
---
# SQLite 2026 – FTS5 full-text search extension

**Raw file**: `raw/demo/SQLite 2026 - FTS5 full-text search extension_ingested.md`

## Overview
FTS5 is an SQLite virtual-table module providing full-text search. The page (about 2,300 lines) also documents the query syntax, table options, custom tokenizer and auxiliary-function C APIs and maintenance commands. **This page extracts only what the demo needs**: virtual tables, `bm25()`, tokenizers, `highlight()`/`snippet()`, external-content tables. The BM25 formulas were images and **did not survive extraction**; the constants and the sign convention are in the text.

## Key Insights
- **Availability**: part of the SQLite amalgamation since 3.9.0 (2015-10-14); otherwise enabled with `--enable-fts5` / `SQLITE_ENABLE_FTS5`, or built as a loadable extension (`fts5.c`).
- **Tables and queries**: `CREATE VIRTUAL TABLE t USING fts5(col1, col2, ...)` (no types or constraints; implicit `rowid`); query with `MATCH`, `=` or table-valued syntax; case-independent by default. Query language: prefix terms (`term*`), phrases, `NEAR(... , N)`, `AND`/`OR`/`NOT`, column filters, initial-token `^`.
- **Ranking with `bm25()`**: Okapi BM25 with **k1 = 1.2 and b = 0.75 hard-coded**; per-phrase IDF over the table's rows; document length vs average length. The result is **multiplied by −1**, so better matches are numerically lower and `ORDER BY bm25(t)` returns best first. Optional per-column weights (`bm25(email, 10.0, 5.0)`). The hidden `rank` column equals `bm25()` by default and is faster for `ORDER BY rank ... LIMIT`; the rank function can be changed per query or persistently.
- **Tokenizers**: `unicode61` (default; Unicode 6.1 letters/numbers/private-use as token characters, case folding, Latin diacritics removed by default; options `remove_diacritics`, `tokenchars`, `separators`, `categories`), `ascii`, **`porter`** (English stemming wrapper around another tokenizer) and **`trigram`** (substring matching, also indexes `LIKE`/`GLOB`; substrings under 3 characters match nothing). Custom tokenizers via a C API; tokens are silently truncated at 32,768 bytes.
- **Snippets for evidence display**: `highlight(t, col, open, close)` marks every match in a column; `snippet(t, col, open, close, ellipsis, max_tokens)` picks a fragment (≤ 64 tokens) maximising distinct query terms, favouring column starts and text after "." or ":".
- **Storage options**: external-content tables (`content='t1', content_rowid='id'`) index a normal table, kept consistent by triggers that the user must write; contentless and contentless-delete tables; `detail=full|column|none` trades features for index size (example: 1,636 MiB of e-mail gave a 743 / 340 / 134 MiB index); `prefix=` builds extra prefix indexes.

## Relevance to GroundOne
- **Zero-model default retriever for the demo** ([[Local RAG Retrieval]]): chunk table + external-content FTS5 index + `ORDER BY rank LIMIT k`. It needs no embedding model, so the 16 GB memory budget stays with the generator and the verifier, and it is deterministic and inspectable, which matters when the demo has to explain why a sentence was judged "not mentioned".
- **Known weakness to state**: BM25 is lexical; paraphrased questions can miss the relevant passage. The `porter` tokenizer helps with English inflections; dense embeddings via sqlite-vec are the optional complement. Retrieval misses surface downstream as "not mentioned" verdicts, so a verify-and-revise policy can treat a high not-mentioned rate as a signal to re-retrieve (CRAG-style) rather than only to rewrite.
- **UI**: `snippet()`/`highlight()` give evidence fragments with markup for the passages shown next to each verdict, for free.
- The `rank`/`bm25` sign convention (lower is better) must be handled if scores are fused with cosine similarities.

## Links
- Concepts: [[Local RAG Retrieval]], [[Retrieval-Augmented Generation]], [[Demo Application]], [[On-Device Inference]]
- Related: [[Garcia 2026 - sqlite-vec, vector search SQLite extension (GitHub README)]], [[Apple 2026 - NLEmbedding documentation]], [[Apple 2026 - PDFKit documentation]], [[Lewis 2020 - Retrieval-Augmented Generation]], [[Yan 2024 - Corrective Retrieval Augmented Generation (arXiv 2401.15884)]]
