# GroundOne Studio: progress log

Development of the demo app specified in `Project/docs/demo_architecture.md`. One entry every ~30 minutes, newest last.
Results files are in `Project/outputs/demo/results/` (gitignored, like the other predictions).

## Report 1 — 2026-10-24 14:33 (start 14:03)

**Done and tested**
- Environment: Xcode 27.1 + Metal Toolchain, XcodeGen, UI-test automation (smoke UI test passes, screenshot extracted).
- Swift package `GroundOneKit` (`Project/demo/GroundOne Studio/Packages/GroundOneKit`): mlx-swift-lm 3.32.3, mlx-swift 0.32.3,
  swift-transformers 1.3.5 (tokenizer only; nothing is downloaded at run time).
- `GroundOneCore` (no ML imports): segmentation port, design-(b) prompt port, calibration and served rule (D27), policy,
  verify-and-revise loop, audit log (JSONL), B0a judge prompt and parser. 10 unit tests pass (`swift test`), including the
  loop with fake engines (repair, give-up → abstain/hide, audit round trip).
- Python fixture exporter `groundone/tools/export_fixtures.py` (200 T1 answers stratified by K, both models; T1 segmentation).
- **M1 conformance gate (§5.3)**, 200 answers, 1,747 markers, logits computed in Swift on the Python token ids:

| Check | 3B (default verifier) | 0.5B |
| --- | --- | --- |
| Token ids and marker positions identical | 200/200, 200/200 | 200/200, 200/200 |
| max \|Δlogit\| | 0.070 | 0.172 |
| max \|Δp\| (calibrated) | 0.0048 | 0.031 |
| share of sentences with \|Δp\| < 0.01 | 100 % | 99.83 % (3 of 1,747 above) |
| served labels identical | 100 % | 99.71 % (all disagreements within 0.01 of τ) |
| gate | **PASS** | fails only the strict \|Δp\| < 0.01 on 3 sentences |

- **Segmentation agreement** (NLTokenizer port vs pysbd, all 2,647 T1 answers): identical segmentation on 98.4 % of answers
  after adding pysbd-like rules (no break after initials/abbreviations or before a lowercase word); 95.2 % without them.
- Embedding candidates downloaded: Qwen3-Embedding-0.6B-4bit-DWQ (335 MB), bge-small-en-v1.5 (133 MB).

**In progress**: engines for generation (4-bit), retrieval (SQLite FTS5 + embeddings, RRF), PDF ingestion; then the app.

## Report 2 — 2026-10-24 15:18

**Done and tested**
- Engines: 4-bit generator (greedy streaming), local judge (same 3B base with the LoRA unloaded, B0a prompt), embedder
  (MLXEmbedders), SQLite FTS5 + dense hybrid retriever (RRF), PDF/text ingestion with page and character origin,
  source-link attributor (M3b: GroundOne per passage + word-overlap span).
- Library index of the research library (`Vault/raw`): 109 files (82 PDFs + notes), 5,886 passages, both embedders.
- **Retrieval check (decision 3)**, 12 questions with a known source paper:

| Retriever | hit@5 | MRR | s/query |
| --- | --- | --- | --- |
| BM25 | 1.00 | 0.92 | 0.003 |
| dense bge-small-en-v1.5 | 1.00 | 0.90 | 0.011 |
| dense Qwen3-Embedding-0.6B-4bit | 0.92 | 0.82 | 0.032 |
| hybrid bge-small | 1.00 | 1.00 | 0.013 |
| hybrid Qwen3-Embedding | 1.00 | 1.00 | 0.041 |

  Both hybrids are at the ceiling (the check is small and easy); **bge-small-en-v1.5 chosen** (equal here, 2.5× smaller,
  3× faster, MIT licence).
- Case-study set: `experiments/demo/scripts/inject_errors.py` → 100 T1 answers accepted by GroundOne 3B with all reference
  labels supported (pool 835), one injected error each: 25 number, 25 name, 25 date, 25 fabricated sentence
  (dates are mostly in summaries: 22 of 25). Case-study runner (`g1studio casestudy`) and report script written.
- SwiftUI app (XcodeGen project): Ask (coloured answer, sentence table, draft picker, status), inspector (timing chart,
  judge comparison, passages), Library, Policies editor, Measurements (session table, export, case-study summary),
  Audit log, PDF source viewer with highlight. Builds; renders correctly when launched (screenshot checked).

**Problems found and fixed**
- **Memory**: the first indexing run grew to 11.4 GB (swap 9.6 GB) because the Swift port did not set MLX's cache limit
  (Python sets 1 GB). Killed; limits added (`Runtime.configure`: cache 1 GB, memory 11 GB); re-run under `groundone guard`
  (peak 0.5 GB RSS, 24 s for the remaining 61 files). Procedural error on my side: that first run was not under the guard.
- **App launch blocked by macOS privacy (TCC)**: reading `~/Desktop` at launch waits for a permission dialog that cannot
  appear. The app now keeps its data in `~/Library/Application Support/GroundOne Studio` (filled by `g1studio install`:
  adapters + calibration, index with copies of the files, policies; 262 MB); models stay in the Hugging Face cache.

**In progress**: UI tests (the app now opens under XCTest, but the test stalls after typing the question; debugging),
then the case study (100 answers, under the guard).

## Report 3 — 2026-10-24 16:05

**Done and tested**
- **UI tests pass** (fake engines, deterministic; `scripts/uitest.sh`):
  - `testAskFlowWithFakeEngines`: question → first draft with a flagged sentence → rewrite → "Accepted by GroundOne after
    1 rewrite"; draft picker; judge comparison tab; passages tab; timing tab; source link → source viewer sheet.
  - `testSectionsWithFakeEngines`: Library, Policies (select and edit), Measurements (export button), Audit log.
  - Screenshots of every step are exported from the result bundle (`build/ui-shots/`) and were inspected.
- Three test-infrastructure problems found and fixed:
  1. a floating window of another app (Activity Monitor's GPU History) covered the Ask button and swallowed the click:
     the runner now hides Activity Monitor during the tests and shows it again after; the test submits with ⌘↩;
  2. `descendants(matching: .any)` queries stalled XCTest for minutes: typed queries only;
  3. XCTest hung while symbolicating any assertion failure (so a failing check froze the run): fixed by building the
     app and the test bundle without the debug dylib (`ENABLE_DEBUG_DYLIB = NO`); the runner also has a watchdog.
- App accessibility fixes found by the tests: explicit label on the status banner; sentence rows keep their links as
  separate elements (`.contain`, not `.combine`).

**Running**: the injected-error case study (100 answers, GroundOne 3B + 4-bit generator + local judge, Release build,
under `groundone guard`), started 16:03. First answer: GroundOne flags the injected number, the judge says B
(contradicted), the error is gone after one rewrite, answer accepted; GroundOne pass 1.4 s warm (2.7 s cold).

**Next**: end-to-end UI test with the real models (after the case study, to keep its timings clean), documentation.
