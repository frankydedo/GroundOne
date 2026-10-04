# LLM Wiki Schema

This directory operates as an **LLM-managed Wiki**, inspired by Andrej Karpathy's pattern. As an AI Agent, your primary role is to act as a disciplined, proactive wiki maintainer. Your goal is to build, structure, and maintain a persistent knowledge base in markdown, ensuring information is never lost in ephemeral chat history.

## Directory Structure
- `inbox/` (or `raw/`): Immutable directory containing original sources, raw text, or unstructured user notes. Read from here but do not modify the original files.
- `wiki/`: The persistent memory layer containing the Markdown files. You own and maintain this layer.
  - `wiki/sources/`: Dedicated pages summarizing specific ingested sources (articles, meetings, transcripts, documents).
  - `wiki/concepts/`: Dedicated pages for broader topics, entities, ideas, and methodologies.
- `scratch/` (or `output/`): Ephemeral directory for intermediate scripts, temporary analysis files, or generated outputs on demand. Must be kept clean and emptied after tasks.

## Key Files
- `index.md` (or `Home.md`): The entry point and content-oriented catalog of all pages in the wiki. Organized logically by categories. Must be updated when new significant nodes are added.
- `changelog.md` (or `log.md`): A chronological, append-only record of your operations (ingests, major structural changes). E.g., `## [YYYY-MM-DD] ingest | Project Alpha meeting notes`.
- `guidelines.md` (Optional): Specific rules or goals defined by the user for this specific vault.

## Conventions & Rules
1. **Obsidian Native:** Use `[[Wiki Links]]` to connect entities, concepts, and sources. E.g., `[[Machine Learning]]`. 
2. **Structured Metadata:** Include YAML frontmatter on all wiki pages for easy querying (e.g., Dataview in Obsidian). 
   - Example for sources: `type: source`, `author/creator`, `date`, `tags`.
   - Example for concepts: `type: concept`, `tags`.
3. **Compound Knowledge (CRITICAL):** When ingesting a new source or answering a complex query, do not just summarize it flatly. Extract its core concepts. 
   - If a concept doesn't have a page, create one. 
   - If it does, update the existing concept page with the new insights.
   - Weave a web of interconnected knowledge.

## Core Workflows
- **Ingest:** Command: `!ingest {target}`. 
  1. Read the raw source/note.
  2. Write a structured summary page in `wiki/sources/`.
  3. Update or create related `wiki/concepts/` pages with the newly extracted insights.
  4. Update `index.md` if a major new category/concept was created.
  5. Append the action to `changelog.md`.
  6. Move or rename the raw source to indicate it has been processed (e.g., `{name}_ingested`).

- **Query & Synthesize:** Command: `!query {question}`. 
  When asked to synthesize information (e.g., "What is our current strategy on X?"), search the wiki, aggregate the information, and save the robust answer as a new concept/overview page in the wiki. **Do NOT leave valuable synthesis only in the chat history.**

- **Lint / Maintenance:** Command: `!lint`. 
  Periodically health-check the wiki. Look for contradictions, stale claims, orphan pages (pages with no links), or missing cross-references, and fix them.
