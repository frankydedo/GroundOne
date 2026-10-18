---
title: "Apple 2026 - NLTokenizer documentation"
url: https://developer.apple.com/documentation/naturallanguage/nltokenizer
accessed: 2026-10-18
source: Apple developer documentation JSON
---

# NLTokenizer
A tokenizer that segments natural language text into semantic units.

## Overview
NLTokenizer creates individual units from natural language text. Define the desired unit (word, sentence, paragraph, or document as declared in the NLTokenUnit) for tokenization, and then assign a string to tokenize. The enumerateTokensInRange:usingBlock: method provides the ranges of the tokens in the string based on the tokenization unit.
For more information, see tokenizing-natural-language-text.
 Use an NLTokenizer instance on one thread or one dispatch queue at a time. You do this by either serializing method calls to the tokenizer, or by creating a separate tokenizer instance for each thread and dispatch queue.
- topic: Creating a tokenizer
- topic: Configuring a tokenizer
- topic: Enumerating the tokens
