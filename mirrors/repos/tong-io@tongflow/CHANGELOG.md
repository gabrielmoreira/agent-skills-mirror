# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-08-02

### Added

- **Workspace agent** (#130) — a collapsible chat panel on the right side of
  the canvas. Describe what you want in natural language (attach images,
  video, audio or documents straight into the chat) and the agent builds the
  workflow **live on the canvas**: nodes appear one by one with the camera
  following, prompts and parameters fill into the node forms, and one Cmd+Z
  undoes an entire agent turn. It edits incrementally ("make the video 10
  seconds") rather than rebuilding, validates every step against the ABI
  (structurally invalid graphs are rejected before they touch the canvas),
  can health-check a workflow and explain why a run failed, and answers
  questions about using TongFlow from the bundled docs. Bring your own
  brain: the agent runs on any installed OpenAI-compatible text plugin
  (OpenRouter, OpenAI, Gemini, DeepSeek, xAI, Doubao, APIMart, Agnes) with a
  two-level plugin → model picker.
- **App Mode** (#124) — present any workflow as a simple form app: inputs on
  top, results below, canvas hidden. Assets fed through add-nodes become
  replaceable inputs, so a finished workflow doubles as a reusable tool.
- **Canvas undo/redo** (#125) — Cmd+Z / Cmd+Shift+Z plus toolbar buttons,
  with field-level coalescing so a burst of typing is one undo step.
- **Settings overhaul & first-run onboarding** (#118) — settings are now
  human-readable cards with a guided first-run banner. Connecting services
  is a dedicated flow per provider: Modal (with one-shot paste that splits
  both tokens automatically, #119), Hugging Face (#120), and every provider
  API key (#121).
- **Clear, actionable task failures** (#122, #123, #126) — failures now carry
  stable error codes with localized messages and support links; upstream
  Modal/deployer error bodies are preserved in the failure details; a
  missing API key opens a guided dialog that deep-links to the right
  settings field.

### Changed

- **Python SDK 0.2.20** (#127) — direct-stream terminal callback so
  browser-direct streaming runs report their terminal state reliably, plus
  per-call model passthrough. All official Modal plugins repinned to 0.2.20.

### Fixed

- **Completed tasks replay instead of re-running** (#128) — reconnecting to
  a finished task's wait stream now replays the stored terminal state; a
  finished slot can no longer be accidentally re-executed.
- **Undo history stays intact across mount-time defaults** (#129) —
  programmatic default writes in six more node types no longer pollute the
  undo stack.

## [0.2.3] - 2026-07-28

### Fixed

- **One-click execution now handles dynamic split counts end-to-end** (#116) —
  a split's runtime item count drives downstream batch nodes: one plugin call
  per item (`batchField` fan-out in the engine), outputs collected in batch
  order. Previously only the first item was processed, silently.
- **Intermediate data nodes are pure channels in one-click runs** — consumers
  bind straight to the producer's output, so stale edit-time values of
  materialized nodes no longer leak into execution. Re-save workflows exported
  before this version to pick up the new bindings.
- **Loud failure instead of silent data loss** — a single-value input that
  receives multiple upstream values now fails the node with a clear message.

## [0.2.2] - 2026-07-25

### Added

- **DeepSeek plugin** (`tongflow-api-deepseek`) — DeepSeek V4 as a text
  provider for `gen-text` / `combine-text` / `split-text`, with a per-node
  **model dropdown** offering `deepseek-v4-flash` / `deepseek-v4-pro` each
  with thinking on/off (four choices).
- **Streaming "thinking" bubble** — when a plugin streams its reasoning
  (DeepSeek thinking mode), it now appears live in an auto-scrolling bubble
  anchored beside the node while it runs, separate from the status label and
  non-occluding. Backed by `progress(..., thinking=True)` in the SDK.
- **SenseNova-Vision plugin** (`tongflow-modal-sensenova-vision`) — SenseTime's
  unified vision model: image understanding / visual QA, detection & OCR
  structured text, full-scene surface normals, salient-object matting, and a
  human-pose overlay (an alternative implementation of those slots).
- **Open-vocabulary sound separation** (`separate-sound` node) — describe any
  sound in words ("dog barking") and split the audio into that sound and
  everything else.

### Changed

- **Cloud plugin execution path** (Python SDK **tongflow 0.2.7 → 0.2.17**) — a
  new single-container cloud execution surface so plugins can run in the
  user's own Modal without a per-call venv + subprocess:
  - `serve_slot` / `run_and_report` — single-slot execution and a background
    single-node runner that reports back over an HTTP callback;
  - `serve_stream` / `serve_stream_from_spec` — single-container streaming
    slot execution, including a browser-direct stream entry;
  - self-reported progress (and streamed reasoning) over an HTTP sink, so
    remote plugins drive the node status and thinking bubble;
  - an **injectable workflow invoker** that skips the venv + subprocess hop;
  - **default-slot claims** (`TONGFLOW_DEFAULT_SLOTS`, `@node_slot(default=True)`)
    so a plugin can declare the default implementation for a slot while still
    importing under older, already-deployed runtimes.

### Fixed

- SDK `HttpStore` now sends a User-Agent (works around a Cloudflare 403) and
  emits a stable event id in `serve_stream` (tongflow 0.2.13).

## [0.2.1] - 2026-07-12

### Added

- **Meta Sapiens2 human suite** (`tongflow-modal-sapiens2`) — five new ABI
  slots with canvas nodes and smart-island actions, backed by the Sapiens2-1B
  checkpoints on one Modal L40S (bf16, batched):
  - **Pose detection** (`image-pose`) — 308-keypoint whole-body skeleton
    (body, hands, face) on a clean black background;
  - **Body-part segmentation** (`image-body-seg`) — 29-class human parsing
    as a pure class-color map;
  - **Surface normals** (`image-normal`) — per-pixel normal map, background
    masked;
  - **Human matting** (`image-matting`) — straight-alpha transparent PNG;
  - additionally the existing **Image → 3D** slot gains a Sapiens2 pointmap
    implementation (colored human point cloud GLB).
- **Video motion capture** (`video-gen-model`) — monocular video → animated
  3D human GLB on Meta's MHR character (Momentum Human Rig, Apache-2.0),
  playable directly in the model node and importable into Blender as a
  skinned armature. Two competing implementations of the same node slot:
  - **tongflow-modal-sam-3d-body** — per-frame MHR regression (learned
    prior; body + hands, experimental face/jaw channels driving 72 sparse
    glTF morph targets);
  - **tongflow-modal-sapiens2** — geometric engine (308-keypoint pose +
    pointmap 3D lift, One-Euro smoothing, rest-pose hold for out-of-frame
    body parts).
- **Model node: animation playback** — models carrying animation clips now
  auto-play (30 fps cap, pauses off-viewport and in background tabs) with a
  play/pause control in the node preview and the fullscreen viewer.

### Changed

- **Model node initial framing** — the camera now homes straight onto the
  model's front (glTF +z convention) and maximizes the model in the frame
  (aspect-aware fit); fixed a centering bug that framed tall/offset models
  poorly and mixer leaks that kept animating after unmount.
- Python SDK **tongflow 0.2.6** — generated models and `NodeSlots` for the
  five new ABI slots.

## [0.2.0] - 2026-07-06

### Changed

- **The desktop app is now a lightweight cloud shell.** Installers are a
  ~10 MB [Pake](https://github.com/tw93/Pake) (Tauri) wrapper that loads
  the cloud studio at [app.tongflow.com](https://app.tongflow.com) — sign
  in with Google / GitHub / Apple / WeChat and create; plugins and
  execution are managed in the cloud. Release artifacts are now
  `TongFlow-mac-universal.dmg` (one build for Apple Silicon + Intel) and
  `TongFlow-win-x64.msi`. The previous Electron app (≤ v0.1.13), which
  bundled a local Next.js server, SQLite database, and Python plugin
  runtime (~200 MB), is no longer shipped — that fully local, account-free
  experience lives on via self-hosting (`pnpm start:prod` or Docker).
  Existing local installs keep working; no update is pushed to them.

### Added

- **Meta SAM suite** — four new official Modal GPU plugins (all require a
  Hugging Face token for the gated checkpoints):
  - **tongflow-modal-sam3** — text-guided matting: cut every instance of a
    described concept out of an image, or track it through a video;
  - **tongflow-modal-sam-audio** — text-prompted sound separation: noise
    reduction, vocal isolation, and free-text stem extraction (first
    official plugins for the noise-reduction and track-separation slots);
  - **tongflow-modal-sam-3d-objects** — single image → 3D Gaussian splat;
  - **tongflow-modal-sam-3d-body** — single image → full-body human mesh.
- **ACE-Step 1.5 music suite** — six new ABI slots with canvas nodes and
  smart-island actions, all served by the reworked `tongflow-modal-ace-step`
  plugin:
  - **Music repaint** (`music-repaint`) — regenerate a chosen time range;
  - **Music cover** (`music-cover`) — restyle a song via caption and/or
    reference track;
  - **Stem extraction** (`music-extract`) — isolate one of 12 stems
    (vocals, drums, bass, guitar, …);
  - **Add track** (`music-lego`) — generate a new stem over a mix;
  - **Complete arrangement** (`music-complete`) — fill in missing tracks;
  - **Music brief** (`music-brief`) — one-sentence idea → lyrics, style
    tags, BPM, key, and duration (runs on the 5 Hz LM).
  The plugin also implements **audio-describe** (music understanding via
  the LM) and exposes a per-node **model dropdown** for the DiT
  (`xl-sft` default / `xl-base` / `xl-turbo`).

### Changed

- **ACE-Step default model upgraded** from `xl-base` to **`xl-sft`** (the
  official best-quality variant); the upstream repo revision is now pinned.
- Python SDK **0.2.3** / **0.2.5** published: generated models for the six
  new music slots, a `current_model()` side channel so router-style model
  selection reaches Modal-backed plugins, and (0.2.5) the merged source of
  0.2.3 + 0.2.4's `HttpStore`.

## [0.1.13] - 2026-07-04

### Added

- **Audio understanding** — new `audio-describe` ABI slot and canvas node:
  select an audio node and hit **Describe** on the smart island to get a
  natural-language description of the clip (genre, mood, instruments,
  vocals, events), with an optional custom prompt. Implemented by four
  official plugins: **Gemini** (native audio in `generateContent`),
  **OpenAI** (`gpt-audio` via `input_audio` part), **Agnes**
  (`agnes-2.0-flash`, `input_audio` part), and **Gemma 4** (GPU, existing
  multimodal pipeline). Requires `tongflow==0.2.2`.
- **Reference audio for music generation** — the music node (`gen-music`)
  gains an optional `ref_audio` input handle: connect an audio node to
  condition the song on a reference track. ACE-Step uses it for
  style-transfer conditioning (`reference_audio`); LeVo uses it as the
  melody prompt (`melody_wavs`, first 10 s). Requires `tongflow==0.2.1`
  (published) and redeployed `tongflow-modal-ace-step` /
  `tongflow-modal-levo` plugins.

### Changed

- **Uploads: 50 MB file-size limit removed** — large media files can now be
  added to the canvas directly.
- Python SDK **0.2.1** / **0.2.2** published to PyPI (generated models and
  `NodeSlots` for the two new capabilities above). Official plugin repos
  created for **LeVo**, **Bernini**, **FastWan**, and **SenseNova-U1**.

### Fixed

- **Upload failures are no longer silent** — per-file upload errors are
  surfaced instead of quietly dropping the file.
- **Node prompt boxes no longer stretch endlessly** — long input now stops
  at a fixed height and scrolls (the auto-growing textarea previously
  expanded the whole node with no scrollbar).
- **Gemini plugin worked around Google's model retirement** — the default
  `gemini-2.0-flash` now 404s upstream; bumped to `gemini-2.5-flash` so the
  plugin works out of the box again.

## [0.1.12] - 2026-07-04

### Added

- **Agnes AI official plugin** (`tongflow-api-agnes`) — one API key covers
  **12 slots** via the OpenAI-compatible [Agnes AI](https://agnes-ai.com)
  gateway: text generation / splitting / combining and image understanding
  (`agnes-2.0-flash`, 512K context), image generation / editing
  (`agnes-image-2.1-flash` / `2.0-flash`, per-node model picker), multi-image
  fusion (`agnes-image-2.0-flash`), and async text / image / multi-image /
  first-last-frame → video (`agnes-video-v2.0`, up to ~18 s per clip).
- **Desktop auto-update** — the app checks for new releases and updates
  itself via an in-app update button; no more manual installer downloads.
- **Uninstall plugins** — installed plugins can now be removed from the
  plugin manager.
- **Cancel running nodes** — a running node can be cancelled from its
  loading overlay.

### Changed

- **Per-plugin env var cards** — Settings renders each plugin's declared
  environment variables (`tongflow.plugin.json`) as a pre-filled card;
  shared keys are hoisted into a single "Shared" card.
- **In-app dialogs** — native `confirm`/`alert` popups replaced with
  in-app dialogs.

## [0.1.11] - 2026-07-03

### Fixed

- **Plugin installs behind corporate proxies / private CAs** — installing a
  plugin no longer fails with `git failed: unable to verify the first
  certificate` when the network uses a TLS-inspection proxy or the plugin
  repo is served under a privately-trusted CA. The desktop app now launches
  its bundled Node server with `--use-system-ca`, so the OS trust store
  (macOS Keychain / Windows certificate store) is honored in addition to
  Node's built-in CA list.

## [0.1.10] - 2026-07-02

### Added

- **Per-node model picker for router-style plugins** — a plugin can now declare
  per-slot model lists (a `TONGFLOW_SLOT_MODELS` constant, discovered by the
  scanner without importing plugin code). The node shows a **Model** dropdown
  next to the plugin selector, and the selection travels top-level — like
  `pluginId` — through task creation, the `tasks` table, the plugin envelope,
  and workflow export. Fully opt-in: plugins that declare no models are
  unchanged, and new plugins degrade gracefully to their default model on
  older runtimes.
- **APIMart official plugin** (`tongflow-api-apimart`) — one API key routes
  **46 models across 7 slots** via the [APIMart](https://apimart.ai) gateway:
  image generation / editing (Z-Image-Turbo, Seedream 4.5 / 4.0 / 5.0-Lite,
  Nano Banana Pro / 2 / classic, GPT-Image 1 / 2, Imagen 4.0, Qwen Image 2.0,
  Wan2.7, Grok Imagine), text / image → video (Kling v3 / 3.0-Turbo / 2.6,
  VEO3.1 fast / quality / lite, Sora 2 / Pro, Seedance 2.0 / 1.5-Pro), text
  generation (GPT-5.x, Claude, Gemini, DeepSeek), Whisper transcription, and
  TTS — with the backing model selectable per node.
- **Link node** — link modality asset node plus a link → text transform,
  wired through connection validation and the workflow exporter.
- Registered the **LeVo** official plugin (`tongflow-modal-levo`).

### Changed

- Python SDK **0.2.0** published to PyPI: the plugin scanner emits per-slot
  model lists and the workflow engine forwards the node's model selection to
  plugins.

## [0.1.9] - 2026-06-30

### Added

- **Korean (`ko`) locale** — full UI translation, joining the existing
  English / Chinese / Japanese languages.
- Registered the **Boogu-Image** official plugin (`tongflow-modal-boogu`).

### Fixed

- Execution feedback is now cleared when a node's plugin is not installed,
  instead of leaving a stale error on the node.

## [0.1.8] - 2026-06-28

### Added

- **Doubao Seedance 2.0** official API plugin (`tongflow-api-bytedance`):
  Volcengine Ark video generation covering text → video, image → video,
  first/last-frame video, and image + audio → video.
- **Images → Video** node — free multi-image reference fusion: connect several
  reference images plus a prompt to generate a new video (Seedance multimodal
  reference). Backed by a new `images-gen-video` ABI slot, reachable from the
  smart-island compose menu when 2–9 image nodes (optionally plus one text
  node) are selected.
- **Video editing** node (`video-edit` ABI slot) and the **Bernini-R** unified
  renderer plugin (`tongflow-modal-bernini`).

### Fixed

- Image Fusion: a prompt fed from an upstream text node is now actually used at
  execution. Previously the node displayed the upstream text but refused to run
  with "required input text is empty"; the text handle is now wired into the
  ABI prompt (upstream edge wins, the manual textarea is the fallback).

## [0.1.7] - 2026-06-27

### Changed

- Canvas edges are no longer created by dragging from a handle. Handles set
  `isConnectableStart={false}`, so connections are created only via the
  operation panel (expands/compose). Users can still **reconnect** an existing
  edge's endpoint to another node.

### Added

- Reconnecting an edge endpoint is validated against the ABI contract: the
  upstream modality must match the target handle, single-value (non-array)
  input handles accept only one edge, `add` nodes fan out to a single edge,
  and modality nodes can't feed each other.
- Dropping a dragged edge endpoint on empty canvas prompts to delete the
  connection. The reconnect preview line matches the edge style so it stays
  visible and tracks the cursor.

### Fixed

- Aspect-ratio picker labels no longer overflow their button in English; long
  labels wrap onto multiple lines instead of clipping past the border.

## [0.1.6] - 2026-06-26

### Added

- Image generation nodes gain a **resolution tier** picker (1K / 2K / 4K)
  alongside the aspect-ratio picker. The chosen width/height is the aspect
  ratio's base (1K) dimensions scaled by the tier, persisted directly to the
  existing `width`/`height` ABI fields (no new contract field).

### Fixed

- Desktop release pipeline no longer fails to publish under GitHub's immutable
  releases. Per-arch installers are uploaded to a draft release and the draft
  is published once after all assets are attached, instead of publishing
  immediately and 422-ing on subsequent asset uploads. (Supersedes 0.1.5,
  which never shipped a usable release.)

## [0.1.4] - 2026-06-25

### Fixed

- Plugins no longer crash on a non-UTF-8 system locale (notably Windows
  Simplified-Chinese, whose ANSI code page is GBK / cp936). A spawned Python's
  stdout/stderr defaulted to the system locale, so a plugin printing a
  non-ASCII character — such as the `✓` emitted while downloading model
  weights — raised `UnicodeEncodeError: 'gbk' codec can't encode character`
  and surfaced as "downloading weights failed (exit 1)". Every Python spawn
  site now forces UTF-8 mode (`PYTHONUTF8=1`).

## [0.1.3] - 2026-06-22

### Added

- Official plugin **Unlimited-OCR** (`tongflow-modal-unlimited-ocr`) — Baidu's
  Unlimited-OCR for long-horizon document / PDF → text on the `parse-document`
  slot, a GPU alternative to Docling and PaddleOCR.

## [0.1.2] - 2026-06-20

### Added

- Official plugins **TripoSplat** (single image → 3D Gaussian Splatting) and
  **SCAIL-2** (controlled character animation) are now in the plugin registry.
- The 3D model node renders Gaussian-splat assets (`.splat`, `.ply`, `.spz`,
  `.ksplat`, `.sog`) in-app via SparkJS, with a free-tumble trackball camera and
  on-demand rendering for smooth performance on large splats.

### Fixed

- Plugin `model` (3D) outputs are now persisted to file references and rendered
  on the canvas; previously such outputs were dropped and the node showed
  nothing.

## [0.1.1] - 2026-06-16

### Fixed

- Installed plugins now appear in node pickers without reloading the app, and
  the plugin manager recovers from a directory left behind by an interrupted or
  failed clone instead of treating it as already installed.
- Packaged desktop app: rebuild `better-sqlite3`'s native binary for the bundled
  Node runtime during packaging, fixing `ERR_DLOPEN_FAILED` errors (e.g. "Failed
  to save workflow") when the build machine's Node differs from the bundled one.
- Exclude `.env` files from the packaged app bundle; the desktop app reads all
  configuration from the in-app settings store.

### Changed

- Bundled Node runtime and CI upgraded to Node 24.

## [0.1.0] - 2026-06-16

First public open-source release of TongFlow.

[0.2.0]: https://github.com/tong-io/tongflow/compare/v0.1.13...v0.2.0
[0.1.13]: https://github.com/tong-io/tongflow/compare/v0.1.12...v0.1.13
[0.1.12]: https://github.com/tong-io/tongflow/compare/v0.1.11...v0.1.12
[0.1.11]: https://github.com/tong-io/tongflow/compare/v0.1.10...v0.1.11
[0.1.10]: https://github.com/tong-io/tongflow/compare/v0.1.9...v0.1.10
[0.1.9]: https://github.com/tong-io/tongflow/compare/v0.1.8...v0.1.9
[0.1.8]: https://github.com/tong-io/tongflow/compare/v0.1.7...v0.1.8
[0.1.7]: https://github.com/tong-io/tongflow/compare/v0.1.6...v0.1.7
[0.1.6]: https://github.com/tong-io/tongflow/compare/v0.1.5...v0.1.6
[0.1.4]: https://github.com/tong-io/tongflow/compare/v0.1.3...v0.1.5
[0.1.3]: https://github.com/tong-io/tongflow/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/tong-io/tongflow/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/tong-io/tongflow/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/tong-io/tongflow/releases/tag/v0.1.0
