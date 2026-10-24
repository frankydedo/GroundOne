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

## Report 4 — 2026-10-24 16:22

**Case study done (3B)**: 100 injected errors, Swift engines in one process, Release build, under the guard, 17.4 min.
Summary in `outputs/demo/casestudy/summary_full.json`; figures `outputs/figures/demo/casestudy_{survival,outcomes,judge_time}_g1-3b-b1.png`.

| Measure | Value |
| --- | --- |
| GroundOne flags the injected sentence (first draft) | 100 / 100 (all four error types) |
| Generative judge (same base, no adapter, B0a) flags it | 88.5 % (output fully parsed 99 %) |
| GroundOne false alarms on the other (correct) sentences | 2.1 % |
| Answers still containing the error: no loop / after 1 rewrite / after 2 | 100 % / 14 % / 14 % |
| Final status accepted by GroundOne | 87 % (13 % highlighted under the policy) |
| Of the 14 surviving errors | 13 still flagged, **1 accepted by GroundOne** (a miss) |
| How the 86 removed errors were removed | **75 sentence deleted**, 10 original value restored, 1 rewritten |
| Other (correct) sentences kept verbatim | 97.8 % |
| GroundOne pass, median | 1.77 s (input median 758 tokens) |
| Judge, median | 2.33 s (23 generated tokens) → 1.4× GroundOne |
| Verification share of loop time | 58 % (the first draft is given, so the loop only generates rewrites) |
| MLX memory: after loading generator + GroundOne 3B / peak in the loop | 5.1 GB / 6.2 GB |

Reading, to be stated in the thesis as such:
- Detection is 100 % *by construction of the set*: the 100 answers were chosen because GroundOne accepted the originals,
  and the injected errors are blunt (values absent from the document). It shows the loop mechanics, not GroundOne's recall.
- The loop removes 86 % of the errors, but mostly by **deleting** the flagged sentence: for swapped values the correct
  information goes with it (CoVe-like precision by deletion, §4). The 3B generator, told "write DELETE if the document
  gives no basis", deletes far more often than it corrects. A second round adds nothing (14 % → 14 %).
- Prompt not changed after seeing these results (that would tune on the same 100 answers). **Decision for the author**:
  keep v1 as the reported result, or also report a pre-declared "repair-first" rewrite prompt as a labelled second run.
- Speed: Swift reproduces the Python latency picture (Python, same 3B, 200 T1 answers: GroundOne median 1.99 s, terse
  judge 3.16 s). On short terse outputs the judge is only ~1.4–1.6× slower; the thesis gains are accuracy, calibration and
  one-pass multi-sentence scoring, not latency against the terse judge (consistent with CLAUDE.md).

**Running now (chained queue under the guard)**: Release conformance timings on the latency subset (3B, 0.5B), 0.5B case
study, equal-compute best-of-3 baseline (60 T1 documents), three library questions end to end, `install`, end-to-end UI
test with the real models.

## Report 5 — 2026-10-24 17:13

**Done and tested**
- **Speed parity Swift vs Python** (Release; same 200 T1 answers as the thesis latency subset, forward pass on the same
  token ids): 3B mean 2.13 s vs 2.04 s in Python; 0.5B 0.343 s vs 0.333 s.
- **0.5B case study** (selector in the app): detection 100 %, but false alarms on correct sentences 16.8 % (3B: 2.1 %),
  correct sentences kept verbatim 81 % (3B: 97.8 %); its own judge (0.5B base) flags only 34.6 % and parses 81 %;
  error survival 9 %; GroundOne pass 0.29 s; MLX peak 3.3 GB. Caveat: the set was selected with the 3B.
- **Equal-compute baseline** (60 fresh T1 answers, 3B): loop accepted by GroundOne 98.3 % (first draft alone 51.7 %),
  median 7.1 s and 112 generated tokens; best-of-3 sampling (T = 0.7) 61.7 %, 10.0 s, 218 tokens. Acceptance is
  GroundOne's, and the loop reaches it partly by deleting sentences (report 4).
- **Library questions end to end** (`outputs/demo/audit/cli.jsonl`): e.g. the calibration question: the generator adds
  "temperature typically between 0 and 1" (wrong) and two unsupported claims; GroundOne flags all three as not
  mentioned, the generative judge marks every sentence supported; the loop removes them and the answer shrinks to the
  one correct sentence. Total 16 s, MLX peak 6.1 GB.
- **End-to-end UI test with the real models PASSES** (332 s): models load, question answered from the library, accepted by
  GroundOne, judge tab, timing tab (6.19 GB MLX peak), "Find evidence" produces the link "Supported by Guo 2017 … p.1".
  The test's own link check waited too little (evidence needs k GroundOne passes); fixed and re-running to capture the
  PDF viewer.
- Figures: `outputs/figures/demo/casestudy_{survival,outcomes,judge_time}_g1-{3b,05b}-b1.png` with captions.

## Report 6 — 2026-10-24 18:28 (end of the session's work)

**Done and tested since report 5**
- End-to-end UI test with the real models passes, now including the source viewer: the link opens Guo et al. (2017)
  at page 1 with the whole supporting sentence highlighted. Two fixes: span chosen by IDF-weighted stem overlap within the
  passage (distinctive words outweigh repeated ones); highlight found by matching the start and end of the sentence in
  the page text (line-end hyphenation broke whole-sentence matching).
- Fake-engine UI tests and the 10 core unit tests re-run after the changes: all pass.
- Release build of the app launches, loads the three models (MLX 5.3 GB) and shows the 109-document library; works in
  dark mode.
- App screenshots with captions for the thesis: `outputs/figures/demo/app_*.png`.
- Commits `fb9fcca`, `04d1631` (not pushed).

**Milestones (§9)**: M0 ✓, M1 ✓ (3B PASS; 0.5B labels agree, 3 sentences above the strict |Δp|), M2 ✓, M3 ✓, M3b ✓,
M4 ✓ (measurement mode, mandatory judge comparison, export, figures, plus the best-of-3 baseline), M5 ✓ (README,
screenshots). Not done (optional in the spec): re-querying the retriever for "not mentioned" sentences (stretch, §4),
GDPR/AI Act corpus (§4b), app icon and signing for distribution.

**Decisions left to the author**
1. Rewrite prompt: report v1 only, or add a pre-declared "repair-first" run labelled post hoc (deletion dominates repairs).
2. Whether the 0.5B case study goes into the chapter (set selected with the 3B: caveat).
3. Whether to disable the "automation mode without authentication" now (`sudo automationmodetool disable-automationmode-without-authentication`);
   the UI tests need it on.

## Report 7 — 2026-10-24 20:10 — rewriting redesigned (author's specification)

One request per flagged sentence with the relevant excerpt and an instruction by error type (contradicted: correct,
never delete; not stated: rewrite from the source or delete). Fresh set of 100 injected answers (3B), first design as
control on the same set: errors left 9 % vs 13 %; removed errors restored / rewritten / deleted 41 / 1 / 49 vs 7 / 0 / 80;
numbers restored 18/25 vs 2/25, dates 16/25 vs 0/25; fabricated removed 25/25 vs 22/25; accepted by GroundOne 90 % both;
misses 3 both; rewrite 0.9 s vs 2.1 s per round. Unit tests (13) and fake UI tests pass; the app uses the new design.
