# `game-pack` reference

`sprite-gen game-pack` is a CPU-only command that compiles images, animation sequences, multi-state descriptors, and directional sprite sheets into deterministic multi-page texture atlases and a manifest. Source files remain unchanged on disk, and exported frames are resampled to target display dimensions.

## Command-line interface

```bash
sprite-gen game-pack --request game.json --out-dir game-assets
```

### Options

* `--request <path>`: Path to the request JSON file. Paths within the request resolve relative to the request file directory.
* `--out-dir <path>`: Target output directory. Must be a new directory path.
* `--page-size <int>`: Maximum page dimension in pixels. Defaults to `4096`. Lower bound is `1`; cannot exceed `4096`.
* `--max-bytes <int>`: Total encoded byte budget for all output files (PNG, WebP, JSON, JS modules, OGG, and M4A combined). Defaults to `50000000` (50 MB). Lower bound is `1`; configurable downward only.

Invalid arguments, missing files, frame dimension overflows, or budget violations exit with a non-zero status.

## Filesystem safety and determinism

* The output directory must not exist prior to packing.
* If the target directory already exists with the exact same pack generated from identical inputs, the existing pack is returned. Differing content causes execution to refuse.
* The command refuses to publish over input files: execution is rejected if the resolved output path equals any input file path or is an ancestor directory of any input file. Output may reside next to inputs or in a subdirectory.
* The full pack is encoded and size-verified in memory before staging. Output files are written to a temporary staging area, persisted with `fsync`, and published atomically via directory rename. Competing writers cannot interleave pages.
* Given identical inputs and encoder versions, output bytes are identical. Outputs contain no timestamps, absolute file system paths, or unstable sorting orders.

## Request format

```json
{
  "version": 1,
  "assets": [
    {
      "id": "hero-walk",
      "source": "walk.strip.json",
      "source_body_height": 400,
      "display": { "body_height": 96 }
    },
    {
      "id": "coin",
      "source": "coin.png",
      "display": { "height": 16 },
      "resample": "nearest"
    }
  ]
}
```

### Asset identification and naming

* Asset `id` and optional `state` names must use only letters, digits, underscores, dots, and hyphens (`[a-zA-Z0-9_.-]`).
* `state` selects a single named state from a multi-state source.
* Animation keys are named `<id>` for unlabelled sources, or `<id>/<state>` when selecting or expanding states and directions.
* Frame keys inside the manifest follow `<animation-key>/000000`.

### Supported sources

The `source` property resolves:
* A static PNG image.
* A video-loop strip JSON with a same-stem PNG.
* A row-major grid sidecar descriptor with a same-stem PNG.
* A video-set sheet JSON (expands directions).
* A compose-atlas manifest (expands all states).
* A `sprite-gen-asset` version 1 external descriptor with ordered frames `[{"file": "...", "duration": <seconds>}]`.

Playback order is preserved directly from the source description into output animation `frames`. Frames are never sorted by filename.

### Display sizing and resampling

The `display` object requires exactly one positive integer dimension:
* `width`: Canvas width in pixels; height preserves aspect ratio to the nearest whole pixel.
* `height`: Canvas height in pixels; width preserves aspect ratio to the nearest whole pixel.
* `body_height`: Character body height in pixels. Scales using source metadata `body_h`. When `body_h` is absent, provide `source_body_height` on the asset entry root.

Frame alpha is not auto-trimmed. Accepted request `resample` values remain `nearest` and `lanczos`, defaulting to `nearest` when source metadata contains `frame_variant=pixel`, and `lanczos` otherwise. `nearest` uses Pillow nearest-neighbour directly, preserving pixel-art samples. The `lanczos` request mode now delegates to the engine's shared `sprite_gen.util.resample.resize_cell`, the same cutout scaler used by video-loop, extract, slice-sheet, and scene. It scales coverage separately from colour (LANCZOS coverage and Hamming colour), avoiding the colour ringing of plain RGBA LANCZOS (refer to the Cells item in [video-pipeline.md](video-pipeline.md)). For plain pixel-art PNGs lacking metadata, set `"resample": "nearest"`.

### Playback overrides and defaults

Source policies and row anchors are preserved by the asset adapter. Optional entry overrides include:
* `anchor`: `[x, y]` in source pixel space. When undeclared in both source metadata and entry overrides, defaults to canvas bottom-center. Provide explicit coordinates for padded sources.
* `fps`: Playback frame rate.
* `loop`: Loop flag (defaults to `true`).
* `hold_last`: Hold final frame on completion (defaults to `false`).
* `end_frame`: Zero-based output playback termination index (defaults to final frame; validated within frame count).
* `blend`: `"normal"` (default) or `"add"`.
* `direction`: Direction override code or `null` (defaults to `null`). Allowed only if the entry resolves to one animation; the user can select one source `state` to override one animation. An entry expanding multiple states or directions must reject any `direction` field, including `null`, before publishing output.
* `events`: Array of `{"frame": <int>, "name": "<string>"}` triggers where `frame` is a zero-based playback position validated within frame count (defaults to `[]`).

## Packing and layout

* Every frame receives 1-pixel edge extrusion on each side (+2 pixels to width and height). Maximum frame dimension plus 2 pixels must fit within `--page-size`.
* Trimming and rotation are disabled (`trimmed: false`, `rotated: false`).
* Each page has PNG and lossless WebP copies (preserving exact RGB and alpha).
* Total byte size across all PNG, WebP, JSON, JS modules, OGG, and M4A outputs must not exceed `--max-bytes`.
* Layout packing bins assets and frames using stable keys.

## Output manifest

The output `game-pack.json` structure:

```json
{
  "kind": "sprite-gen-game-pack",
  "version": 1,
  "textures": [
    {
      "image": "atlas-000.png",
      "webp": "atlas-000.webp",
      "frames": {
        "hero-walk/000000": {
          "frame": { "x": 1, "y": 1, "w": 32, "h": 64 },
          "sourceSize": { "w": 32, "h": 64 },
          "spriteSourceSize": { "x": 0, "y": 0, "w": 32, "h": 64 },
          "trimmed": false,
          "rotated": false,
          "pivot": { "x": 0.5, "y": 1.0 }
        }
      },
      "meta": {
        "image": "atlas-000.png",
        "format": "RGBA8888",
        "size": { "w": 2048, "h": 2048 },
        "scale": "1"
      }
    }
  ],
  "animations": {
    "hero-walk": {
      "frames": ["hero-walk/000000"],
      "durations_ms": [100],
      "loop": true,
      "hold_last": false,
      "end_frame": 0,
      "blend": "normal",
      "events": [{ "frame": 0, "name": "impact" }],
      "direction": null,
      "anchor": [16, 64],
      "size": { "w": 32, "h": 64 }
    }
  }
}
```

Manifest fields:
* `textures[].frames`: TexturePacker JSON Hash format containing `frame`, `sourceSize`, `spriteSourceSize`, and normalized `pivot`.
* `animations[].anchor`: Output anchor coordinates `[x, y]` in resized canvas pixels.
* `animations[].durations_ms`: Frame durations in milliseconds for every frame position, including repeated positions.

## Phaser 4.2.1 integration

Phaser's [`JSONHash`](https://github.com/phaserjs/phaser/blob/v4.2.1/src/textures/parsers/JSONHash.js) parser reads `frame`, `sourceSize`, `spriteSourceSize`, and `pivot`.

Phaser's `load.multiatlas` expects frame arrays and cannot parse `game-pack.json` directly. With images already loaded as HTML image elements, bind the multi-page atlas to a single texture key using [`TextureManager.addAtlasJSONHash`](https://github.com/phaserjs/phaser/blob/v4.2.1/src/textures/TextureManager.js):

```javascript
function registerGamePack(scene, imagesInPageOrder, pack) {
  return scene.textures.addAtlasJSONHash('game', imagesInPageOrder, pack.textures);
}
```

`addAtlasJSONHash` assigns `sourceIndex` offsets to frames across pages. The game runtime is responsible for reading `durations_ms` and applying animation playback policies (`repeat = anim.loop ? -1 : 0`, `hold_last`, `blend`, and `events`).

## Audio Assets and Playback

Game packs support optional bundled audio declared in pack recipes via `request.audio`:

```json
{
  "audio": [
    { "id": "music", "source": "../music/sound.json" }
  ]
}
```

### Integration Rules
- **Packaging and Manifest**: Pack assembly copies format files flat into the output directory as `audio-<id>.ogg` (Opus, 160 kbps) and `audio-<id>.m4a` (AAC, 192 kbps). Output `manifest.audio[id]` contains:
  - `event`: Safe string event identifier matching animation event names.
  - `audio_kind`: `"sfx"` or `"bgm"`.
  - `loop`: Boolean looping flag.
  - `duration_seconds`: Final prepared playback duration `(end_frame - start_frame - overlap_frames) / sample_rate`.
  - `target_lufs`: Target integrated loudness.
  - `playback`: Integer coordinate object (`version`, `sample_rate`, `start_frame`, `end_frame`, `overlap_frames`) preserved exactly from source `sound.json`.
  - `files`: Format dictionary for `ogg` and `m4a` containing relative paths (`audio-<id>.ogg`, `audio-<id>.m4a`), `sha256`, decoded `duration_seconds`, `lufs`, and `true_peak_dbfs` (`encode_passes` and `pcm_peak_limit_dbtp` exist only in `sound.json` and are stripped on load).
  - `player`: Runtime helper descriptor:
    ```json
    {
      "path": "sprite-gen-audio-v2.mjs",
      "sha256": "<actual file hash>",
      "export": "createAudioSource"
    }
    ```
    The `player.sha256` value is the SHA-256 digest computed from the exact shipped bytes of the bundled module.
- **Runtime Helper**: Pack generation emits a single copy of `sprite-gen-audio-v2.mjs` into the pack root. The helper is self-contained with no external imports or dependencies. The canonical buffer preparation logic resides strictly in this helper; consumers must not duplicate blending logic.
- **Event Linkage**: String matching between audio `event` identifiers and animation `events[].name` provides runtime linkage for consumer engines. The pack does not require an animation for every audio asset (such as background music or UI sound effects) and emits no runtime game glue code.
- **Pack Limits**: All output files (PNG, WebP, JSON, JS modules, OGG, and M4A) count toward `--max-bytes` (default 50,000,000 bytes). Packs containing no audio remain byte-for-byte unchanged.
- **Web Audio Playback Contract**: Conforms to [W3C Web Audio decodeAudioData](https://www.w3.org/TR/webaudio-1.0/#dom-baseaudiocontext-decodeaudiodata) and [W3C Web Audio looping](https://www.w3.org/TR/webaudio-1.0/#looping).
  - Never play raw exported loop files with only `source.loop = true`; raw files are encoded audio containing complete pre-overlap sources and codec padding. HTML `<audio loop>` cannot guarantee gapless playback.
  - `prepareAudioBuffer(decoded, playback)` returns an immutable, cached source buffer with fixed rounded loop length or one-shot trimmed actual interval; see [rounding and decoder tolerance](sound.md#export-signatures).
  - Consumers must use `createAudioSource` to configure loop playback using an internally cached L+1 guard buffer, setting `loopEnd = L / sampleRate` which must not be overwritten with `source.buffer.duration`.

### Web Audio Playback Example

```javascript
// Playback must be initiated by a user gesture
button.addEventListener('click', async () => {
  const audioContext = new AudioContext();
  await audioContext.resume();

  // Load pack manifest
  const packURL = new URL('game-pack.json', import.meta.url);
  const packResponse = await fetch(packURL);
  const pack = await packResponse.json();

  // Inspect audio asset and import bundled runtime helper
  const audio = pack.audio.music;
  const helperURL = new URL(audio.player.path, packURL).href;
  const { createAudioSource } = await import(helperURL);

  // Caller selects supported format (e.g. m4a or ogg)
  const formatKey = 'm4a';
  const audioFile = audio.files[formatKey];
  const audioFileURL = new URL(audioFile.path, packURL);

  // Fetch and decode full source encoded audio file
  const fileResponse = await fetch(audioFileURL);
  const arrayBuffer = await fileResponse.arrayBuffer();
  const decoded = await audioContext.decodeAudioData(arrayBuffer);

  // Create configured, unstarted AudioBufferSourceNode
  const sourceNode = createAudioSource(audioContext, decoded, audio);
  sourceNode.connect(audioContext.destination);

  // Start playback
  sourceNode.start();
});
```
