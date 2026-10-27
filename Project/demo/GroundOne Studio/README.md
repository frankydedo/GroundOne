# GroundOne Studio

<img src="Logo/IconComposer/renders/indigo.png" width="128" alt="GroundOne Studio app icon">

App icon: `Logo/IconComposer/GroundOne-indigo.icon` (Icon Composer document, set in `project.yml`; renders in
`Logo/IconComposer/renders/`, generator `Logo/IconComposer/build_icons.py`).

Native macOS demo of GroundOne (D28): a RAG assistant in which retrieval, generation and verification run in one
process on the laptop, and GroundOne decides what the user is shown. Specification and decisions:
`Project/docs/demo_architecture.md`; progress log: `Project/demo/docs/progress.md`.

- **GroundOne** (verifier): Qwen2.5-3B (or 0.5B) 8-bit + the thesis LoRA adapter, design-(b) prompt, A/B/C logits read
  at the `Verdict:` markers, calibration and threshold τ from `calibration.json`. Ported to Swift and checked against
  Python by the conformance test (§5.3).
- **Generator**: Qwen2.5-3B-Instruct 4-bit (separate weights).
- **Judge** (mandatory comparison): GroundOne's own base model with the adapter unloaded, B0a terse prompt.
- **Retriever**: SQLite FTS5 (BM25) + bge-small-en-v1.5 embeddings (MLX), reciprocal rank fusion.
- **Loop**: GroundOne flags sentences → the generator rewrites only those → GroundOne re-checks, as the policy says.

Everything is local: models come from the Hugging Face cache, nothing is downloaded or sent at run time.

## Layout

```
project.yml                     XcodeGen spec of the app (the .xcodeproj is generated, not versioned)
App/                            SwiftUI app: AppModel + Views (Ask, inspector, Library, Policies, Measurements, Audit)
UITests/                        XCUITest: fake-engine flows + one end-to-end test with the real models
Policies/                       example policy files (§7)
scripts/uitest.sh               runs the UI tests and exports the screenshots to build/ui-shots/
Packages/GroundOneKit/
  Sources/GroundOneCore/        no ML imports: segmentation, prompt, calibration, policy, loop, audit log, fakes
  Sources/GroundOneEngines/     MLX: GroundOne, generator, judge, embedder, library index, attributor, conformance
  Sources/g1studio/             command line: conformance, ingest, retrieval check, ask, case study, install
  Tests/GroundOneCoreTests/     unit tests (fake engines) + segmentation agreement with pysbd
```

## Build and run

Requirements: Xcode 27 with the Metal Toolchain (`xcodebuild -downloadComponent MetalToolchain`), XcodeGen
(`brew install xcodegen`), the models in the Hugging Face cache (`lmstudio-community/Qwen2.5-{3B,0.5B}-Instruct-MLX-8bit`,
`mlx-community/Qwen2.5-3B-Instruct-4bit`, `BAAI/bge-small-en-v1.5`) and the adapters in `Project/outputs/models/`.

```bash
cd "Project/demo/GroundOne Studio"
# command-line tools (MLX needs xcodebuild: SwiftPM on the command line cannot compile the Metal shaders)
(cd Packages/GroundOneKit && xcodebuild build -scheme g1studio -configuration Release -destination 'platform=macOS' \
   -derivedDataPath ../../build/dd -skipPackagePluginValidation -skipMacroValidation)
G1=build/dd/Build/Products/Release/g1studio
$G1 ingest library BAAI/bge-small-en-v1.5 ~/Desktop/THESIS/Vault/raw    # index the research library
$G1 install                                                             # copy adapters, index, files, policies for the app
# app
xcodegen generate
xcodebuild build -project GroundOneStudio.xcodeproj -scheme GroundOneStudio -configuration Release \
   -destination 'platform=macOS' -derivedDataPath build/app -skipPackagePluginValidation -skipMacroValidation
open "build/app/Build/Products/Release/GroundOne Studio.app"
```

The app reads its data from `~/Library/Application Support/GroundOne Studio/` (filled by `g1studio install`), so it never
needs access to the protected Desktop folder; the command-line tools read the thesis workspace directly.

## Tests

```bash
(cd Packages/GroundOneKit && swift test --filter GroundOneCoreTests)    # core + loop with fake engines, segmentation agreement
$G1 verify-fixture g1-3b-b1                                             # conformance gate (fixtures from export_fixtures.py)
scripts/uitest.sh testAskFlowWithFakeEngines testSectionsWithFakeEngines
scripts/uitest.sh testEndToEndRealModels                                # loads the real models (~6 GB)
```

Long runs that load models go under the memory guard, e.g. `groundone guard Project/jobs/queue_demo_casestudy.txt`.

## Command line

| Command | What it does |
| --- | --- |
| `verify-fixture <run> [n]` | conformance gate against the Python fixtures (`outputs/demo/results/conformance-<run>.json`) |
| `ingest <corpus> <embedder> <paths…>` | builds `outputs/demo/index/<corpus>-<embedder>.sqlite` |
| `retrieval-check [embedders…]` | the embedding choice (decision 3) |
| `ask "<question>" [--policy p] [--verifier run] [--no-judge]` | one end-to-end query, printed |
| `casestudy [--verifier run] [--n N]` | injected-error case study (D30) → `outputs/demo/casestudy/` |
| `prefetch-timing [run] [n]` | first verification cold vs after the sources were read ahead, on the fixture answers (`outputs/demo/results/prefetch-<run>.json`) |
| `install` | copies what the app needs into Application Support |
