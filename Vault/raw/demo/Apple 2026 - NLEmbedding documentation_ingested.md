---
title: "Apple 2026 - NLEmbedding documentation"
url: https://developer.apple.com/documentation/naturallanguage/nlembedding
accessed: 2026-10-18
source: Apple developer documentation JSON
---

# NLEmbedding
A map of strings to vectors, which locates neighboring, similar strings.

## Overview
Use an NLEmbedding to find similar strings based on the proximity of their vectors.
The vocabulary is the entire set of strings in an embedding. Each string in the vocabulary has a vector, which is an array of doubles, and each double corresponds to a dimension in the embedding. An NLEmbedding uses these vectors to determine the distance between two strings, or to find the nearest neighbors of a string in the vocabulary. The higher the similarity of any two strings, the smaller the distance is between them.
NaturalLanguage provides built-in word embeddings that you can retrieve by using the wordEmbedding(for:) method. You can also compile your own custom embedding into an efficient, searchable, on-disk representation. Typically, you compile an embedding by using Create ML’s MLWordEmbedding and save it as a file for your Xcode project at development time. Alternatively, you can compile an embedding at runtime by using Natural Language’s writeEmbeddingForDictionary:language:revision:toURL:error: method.
Your custom embedding can use any kind of string that’s useful to your app, such as phrases, brand names, serial numbers, and so on. For example, you could make an embedding of movie titles. Each movie title could have a vector that places similar movies close together in the embedding.
A single NLEmbedding instance isn’t safe for concurrent use. Although its query methods, like vector(for:), look like read-only lookups, calling them on one instance from multiple threads or tasks at the same time can crash your app. Serialize access to a shared instance, or give each thread or task its own instance.
- topic: Creating a word embedding
- topic: Creating a sentence embedding
- topic: Finding strings and their distances in an embedding
- topic: Inspecting the vocabulary of an embedding
- topic: Saving an embedding
- topic: Checking for Natural Language support
- topic: Initializers
