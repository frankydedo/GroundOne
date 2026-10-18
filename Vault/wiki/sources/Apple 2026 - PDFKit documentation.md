---
type: source
author: "Apple Inc."
date: 2026
venue: "Apple Developer Documentation, PDFKit framework landing page (documentation JSON; retrieved 2026-10-18)"
url: "https://developer.apple.com/documentation/pdfkit"
tags: [source, apple, pdf, document-ingestion, demo-app]
---
# Apple 2026 – PDFKit documentation

**Raw file**: `raw/demo/Apple 2026 - PDFKit documentation_ingested.md`

## Overview
PDFKit lets apps "display and manipulate PDF documents". **Extremely thin extraction** (327 bytes): the one-line abstract and five topic titles only.

## Key Insights
- Topic titles: **Views**, **Content Model**, **Annotations**, Protocols, Reference.
- Nothing in the raw documents text extraction, page selection, search or annotation APIs; those details must come from the class pages (not ingested) before being cited.

## Relevance to GroundOne
- **Candidate PDF ingestion and display layer** of the demo ([[Demo Application]]): a system framework, so no third-party PDF parser is needed in a Swift app, and its views and annotations could show retrieved passages and highlight the evidence span next to each verdict. The specific capability needed (plain-text extraction per page, so that chunks can be indexed in FTS5) is plausible for a "Content Model" but is **not stated in this source**.
- PDF text extraction quality (reading order, hyphenation, headers/footers) changes what the retriever indexes and what GroundOne verifies against; the demo should show the extracted text the verifier saw, so that a "not mentioned" verdict caused by extraction loss is visible.

## Links
- Concepts: [[Demo Application]], [[Local RAG Retrieval]], [[Retrieval-Augmented Generation]]
- Related: [[SQLite 2026 - FTS5 full-text search extension]], [[Apple 2026 - NLTokenizer documentation]]
