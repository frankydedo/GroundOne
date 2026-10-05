---
type: source
author: "Yelp"
date: 2026-10-05
url: https://business.yelp.com/data/resources/open-dataset/
tags: [source, web-page, dataset, yelp, structured-data, ragtruth-upstream]
---
# Yelp Open Dataset

**Raw file**: `raw/Yelp Open Dataset - official page_ingested.md` (official page, accessed 2026-10-05; legacy URL `yelp.com/dataset`, which RAGTruth cites as "Yelp. 2021. Yelp open dataset. Accessed: 2023-11-03"). No associated paper.

## Overview
A subset of Yelp data "intended for educational use": businesses with reviews, photos, check-ins and attributes (hours, parking, ambience). It is the upstream source of the **Data2txt** task in [[RAGTruth]], where a business record plus reviews is given to the generator as JSON.

## Key Insights (as stated on the page)
- **Size**: 6,990,280 reviews; 150,346 businesses; 11 metropolitan areas; 200,100 pictures.
- **Downloads**: JSON (4.35 GB compressed, 8.65 GB uncompressed: 1 PDF + 5 JSON files); Photos (7.45 GB).
- **Terms**: in the documentation/agreement bundled with the download and Yelp's Terms of Service; not reproduced on the page.

## Relevance to GroundOne
- RAGTruth Data2txt contexts are nested JSON records (name, address, hours, attributes with many `null` values, 3 reviews). JSON `null` read as false produces the `due_to_null` spans ([[RAGTruth]]).
- Data2txt is where RAGTruth's contradictions live (77 % of contradiction spans; ~64–69 % of responses hallucinated), and where the strict/lenient rules differ most ([[GroundOne 2026 - EDA report]]). It is also the least demo-like input format (X7 in [[Datasets for GroundOne]]).
- Terms of use for redistribution of derived data were not checked here (they are only in the download bundle).

## Links
[[RAGTruth]], [[Dataset card - RAGTruth README]], [[Datasets for GroundOne]]
