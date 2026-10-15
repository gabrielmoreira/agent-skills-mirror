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

## Version 2: images, tiles and UI

Version 2 adds three sections for painted scene art: single images such as props (`images`), repeating ground tiles (`tiles`) and a UI kit with nine-slice frames and icons (`ui`). A request opts in with `"version": 2`; the manifest it produces says `"version": 2`. A version 1 request is packed exactly as before: the same files with the same bytes, and a version 1 manifest that has none of the new keys. A version 1 request that names `images`, `tiles` or `ui` is refused instead of being packed without them.

### Version 2 request

```json
{
  "version": 2,
  "assets": [
    { "id": "hero", "source": "hero.strip.json", "display": { "height": 96 } }
  ],
  "images": [
    { "id": "fountain", "source": "props/fountain.png", "display": { "height": 120 },
      "anchor": [256, 725], "footprint": "base" },
    { "id": "lantern", "source": "props/lantern.png", "display": { "height": 96 },
      "footprint": { "x": 180, "y": 640, "w": 150, "h": 80 } }
  ],
  "tiles": [
    { "id": "ground", "source": "ground-tile.png", "display": { "width": 480 } }
  ],
  "ui": {
    "kit": "ui/ui-kit.json",
    "scale": 0.5,
    "icons": [
      { "id": "sword", "source": "icons/sword.png", "display": { "height": 48 } }
    ]
  }
}
```

* `assets` and `audio` keep their version 1 meaning. In version 2, `assets` may be empty or absent; the request must still declare at least one asset, image, tile, UI kit or icon.
* Every `id` uses the asset name characters (`[A-Za-z0-9_.-]`) and is unique within its section.
* `images[]`: one PNG each (a static image or a one-frame descriptor; more frames are refused). `display` takes exactly one of `width` or `height` (no `body_height`), and `resample` works as for assets. `anchor` is `[x, y]` in source pixels and defaults to the bottom centre of the image. `footprint` is optional: an explicit `{x, y, w, h}` rectangle in source pixels, or `"base"` for the measured base described below.
* Props cut from one sheet by [`slice-sheet`](sheet-slicing.md#props-and-icons-sheet-scale-and-contain-fit) share one canvas size, so giving every cell of the sheet the same `display` height keeps the sizes the sheet gave them (`--scale sheet`). The [slice-sheet report](sheet-slicing.md#report) states each cell's `anchor`, the centre of its main subject's base, in the PNG's own pixels: pass it as the entry's `anchor` as it is.
* `tiles[]`: one PNG each, ideally a seamless tile from [`background-tile --axis xy`](asset-tools.md#repeating-tiles). `display` takes exactly one of `width` or `height`: the size of one tile on screen. The tile's pixels are never resampled: the pack stores the source pixels and states both sizes.
* `ui.kit`: the JSON report a [`ui-kit`](ui-kit.md) run wrote. Every element it lists becomes a nine-slice entry, with the element PNGs it names (paths relative to the report). `ui.scale` (default `1`, positive) resizes every kit element by the same factor, so the kit stays one consistent set; a [fill](ui-kit.md#fills) instead takes its size from its frame's content area, below.
* `ui.icons[]`: fixed images such as upgrade or weapon icons, with `id`, `source` and `display` as for `images` (no anchor or footprint).
* The `"base"` footprint is measured on the source image: take the bounding box of pixels with alpha at least 128, keep its lowest fifth (rounded up, at least one row), and the footprint is the bounding box of the pixels with alpha at least 128 inside that band. It is where a prop meets the ground in a top-down or three-quarter view. It is a measurement, not a collision shape the art guarantees.

### Version 2 manifest

```json
{
  "kind": "sprite-gen-game-pack",
  "version": 2,
  "textures": [ "...as in version 1; image, ui and icon frames are atlas frames here..." ],
  "animations": { "...as in version 1..." },
  "images": {
    "fountain": {
      "frame": "image/fountain",
      "size": { "w": 104, "h": 120 },
      "anchor": [52, 120],
      "footprint": { "x": 10, "y": 96, "w": 84, "h": 24 }
    }
  },
  "tiles": {
    "ground": {
      "image": "tile-ground.png",
      "webp": "tile-ground.webp",
      "size": { "w": 960, "h": 960 },
      "display_size": { "w": 480, "h": 480 }
    }
  },
  "ui": {
    "nine_slice": {
      "panel": {
        "frame": "ui/panel",
        "size": { "w": 288, "h": 200 },
        "stretch": "xy",
        "insets": { "left": 56, "right": 56, "top": 46, "bottom": 46 },
        "padding": { "left": 24, "right": 24, "top": 22, "bottom": 22 }
      },
      "hp_bar_frame": {
        "frame": "ui/hp_bar_frame",
        "size": { "w": 304, "h": 56 },
        "stretch": "x",
        "insets": { "left": 66, "right": 30, "top": 0, "bottom": 0 },
        "padding": { "left": 70, "right": 34, "top": 18, "bottom": 18 }
      },
      "hp_bar_fill": {
        "frame": "ui/hp_bar_fill",
        "size": { "w": 200, "h": 20 },
        "stretch": "x",
        "insets": { "left": 6, "right": 6, "top": 0, "bottom": 0 },
        "padding": { "left": 0, "right": 0, "top": 0, "bottom": 0 },
        "inside": { "element": "hp_bar_frame", "rect": { "x": 70, "y": 18, "w": 200, "h": 20 } }
      }
    },
    "icons": {
      "sword": { "frame": "icon/sword", "size": { "w": 48, "h": 48 } }
    }
  }
}
```

A version 2 manifest always has `images`, `tiles` and `ui`, and `ui` always has `nine_slice` and `icons`; each may be empty (`{}`). Keys are the request ids and are sorted.

What each field means, with no reading left to the consumer:

* **Where the pixels are.** `images[*].frame`, `ui.nine_slice[*].frame` and `ui.icons[*].frame` are atlas frame names in `textures[].frames`, so they load with the atlas like animation frames. Their names are `image/<id>`, `ui/<id>` and `icon/<id>`. A tile is not in the atlas: `tiles[*].image` is its own PNG file in the pack (with a lossless WebP copy in `webp`), because a repeating texture needs its own image to wrap.
* **Units.** Every size, anchor, footprint, inset and padding is in pixels of the image as stored in the pack, after the display resize: the frame's own pixels for atlas frames, the PNG's pixels for tiles. Nothing is in source pixels.
* `images[*].size` is the stored frame size. `anchor` is `[x, y]` from the frame's top-left corner (a fraction where the scaled point falls between pixels, as for animation anchors), and the atlas frame's `pivot` is the same point normalised. `footprint` is `{x, y, w, h}` from the frame's top-left corner, or `null` when the request declared none. A source footprint is scaled outward to whole pixels (left and top rounded down, right and bottom rounded up) and kept inside the frame.
* `tiles[*].size` is the stored PNG size. `display_size` is the on-screen size of one tile: draw the repeating texture with a tile scale of `display_size.w / size.w` horizontally and `display_size.h / size.h` vertically.
* `ui.nine_slice[*].size` is the stored frame size. `stretch` says how the element may be resized: `"xy"` both ways (a nine-slice), `"x"` in width only (a three-slice whose height stays `size.h`; `top` and `bottom` are `0`), `"none"` not at all (draw it at `size`; every inset is `0`). `insets` are the widths of the fixed border slices: in Phaser, `scene.add.nineslice(x, y, texture, frame, width, height, insets.left, insets.right, insets.top, insets.bottom)`. The stretched middle lies between the insets, and every corner ornament the [`ui-kit`](ui-kit.md) run found lies inside them. When the pack resizes the kit by `ui.scale`, each inset is the report's inset scaled and rounded up, or, where it is larger, the inset the same [measurement](ui-kit.md#insets) finds on the resized pixels: resampling spreads an ornament's edge a little, and that fringe stays in the fixed slice too. A scale so small that the insets leave no stretchable middle, or the padding no content area, is refused.
* `padding` places the element's content: the inner area where a panel's text, a card's contents, a badge's digits or a bar's fill goes. For an element drawn at width `W` and height `H` (its stored size or any size its `stretch` allows), the content rectangle is `x = padding.left`, `y = padding.top`, `w = W - padding.left - padding.right`, `h = H - padding.top - padding.bottom`, from the element's top-left corner. For `hp_bar_frame` and `xp_bar_frame` this is the track: fill it from its left edge to show a fraction, with the kit's `hp_bar_fill` and `xp_bar_fill` when it has them (`inside`, below). Paddings are scaled with `ui.scale` and rounded up, so the content area only shrinks.
* `inside` is on a fill alone (`hp_bar_fill`, `xp_bar_fill`): `element` is the frame it goes in, and `rect` that frame's content rectangle, from the frame's top-left corner in the frame's stored pixels (its `padding` applied to its `size`). The fill is stored at exactly that rectangle's size: resized by the one factor that makes it as tall as the rectangle (its ends keep their shape; each inset is the report's inset times that factor, rounded up, or the [measured](ui-kit.md#insets) inset of the resized pixels where that is larger), then drawn as wide as the rectangle with its end slices kept and its middle columns repeated or dropped. So a full bar is the fill drawn at its `size` at `rect.x`, `rect.y` in the frame, and it covers the content rectangle to the pixel; a fraction `f` is the fill drawn as a three-slice `f × size.w` wide from there (narrower than its two ends, `insets.left + insets.right`, a three-slice cannot shrink: show the fill's left part instead). When the frame is drawn wider than its stored size, the content rectangle grows with it: draw the fill as wide as the new rectangle allows. `ui.scale` reaches a fill only through its frame. A fill whose frame is not in the report (or is itself a fill), a fill that does not stretch `"x"`, and a fill whose two ends, so resized, are as wide as the rectangle are refused. The pack reads only `inside.element` from the report and works the rectangle out again from the frame it packed.
* `ui.icons[*].size` is the stored frame size; icons are drawn as they are.
* The atlas frames of images, UI elements and icons have `trimmed: false`, `rotated: false` and the same one-pixel extrusion as animation frames. UI element and icon frames have the pivot `{x: 0.5, y: 0.5}`.

The UI kit element names are fixed by the [`ui-kit` layout](ui-kit.md#layout): `panel`, `button`, `button_pressed`, `card`, `hp_bar_frame`, `xp_bar_frame` and `timer_badge` from a square sheet, and from a 2:3 sheet those seven and `hp_bar_fill`, `xp_bar_fill`, `slot`, `badge`, `pip_on`, `pip_off`, `joystick_base` and `joystick_knob`. Their `stretch` is part of the layout: the frames, buttons, slot and badge are `"xy"`; the two bar frames and the two fills `"x"`; the timer badge, the pips and the joystick base and knob `"none"`. The fills, the pips and the joystick parts hold no content, so their padding is `0`. These names are additive: the manifest stays version 2, and a kit from a square sheet packs to the same manifest and the same atlas pixels as before. A 2:3 sheet may leave an optional element out ([missing elements](ui-kit.md#missing-elements)): the report then names it under `missing` and has no entry for it, and the pack has no `ui.nine_slice` entry and no atlas frame for it. A game falls back for exactly the parts `nine_slice` lacks.

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
  - `files`: Format dictionary for `ogg` and `m4a` containing relative paths (`audio-<id>.ogg`, `audio-<id>.m4a`), `sha256`, decoded `duration_seconds`, `lufs`, and `true_peak_dbfs` (`encode_passes` and `pcm_peak_limit_dbtp` exist only in `sound.json` and are stripped on load). Source `sound.json` manifests must specify `recipe.processing_version` 3 or 4 (version 4 manifests require the `normalization` record, while version 3 manifests are decoded and re-measured under the version 3 [loudness rule](sound.md#loudness-rule)). For a peak-limited sound in version 4, `lufs` sits below `target_lufs` (version 3 has no peak-limited goal).
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
