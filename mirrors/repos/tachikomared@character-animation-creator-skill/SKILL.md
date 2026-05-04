---
name: game-character-64
description: Create game-ready 64x64 pixel-art character spritesheets from text concepts, reference images, or existing character art. Use when Codex needs to design, generate, clean up, validate, and package 2D game characters with 8-direction movement, idle, walk/run, and attack animations for RPGs, top-down games, action games, tactics games, roguelikes, or sprite-based game prototypes.
---

# Game Character 64

## Overview

Use this skill to produce game-character spritesheets with `64x64` cells, 8-direction orientation, and attack animation rows. It builds on image generation for character art, then uses deterministic scripts for pixel cleanup and validation.

Default output is an atlas plus QA files:

```text
run/
  prompts/
  generated/
  final/character-sheet.png
  final/character-sheet-clean.png
  qa/validation.json
  qa/contact-sheet.png
```

## Direction Set

Use this direction order unless the user or target engine specifies otherwise:

```text
south, south-east, east, north-east, north, north-west, west, south-west
```

Default rows:

```text
idle-<direction>    4 frames each
walk-<direction>    6 frames each
attack-<direction>  6 frames each
```

This is `24 rows x 6 columns` if idle rows are padded to 6 cells. At `64x64`, the default atlas is `384x1536`.

For smaller scopes, ask once or choose the smallest useful set:

- `walk-only`: 8 rows x 6 frames
- `idle-walk`: 16 rows x 6 frames
- `combat`: idle, walk, attack for all 8 directions

## Workflow

1. Establish character identity: species, class, silhouette, palette, weapon, outfit, and must-keep reference details.
2. Create a canonical base sprite first. It should be a readable `64x64` pixel-art character, not a high-detail illustration.
3. Generate row strips for each animation row using the base sprite and any user reference images as grounding inputs.
4. Keep the character identity locked across all rows: head shape, colors, outfit, weapon, proportions, and silhouette.
5. Save generated strips under `generated/` and assemble or copy them into a grid atlas.
6. Run `scripts/pixel_snap.py` on the atlas or individual frames.
7. Run `scripts/validate_64_sheet.py` and create a contact sheet.
8. If validation fails, regenerate only the failing row or frame group.

## Image Generation Rules

Use `$imagegen` for visual generation. Do not hand-draw missing animation frames with local code. Deterministic scripts may clean, quantize, crop, validate, or compose already-generated art.

Prompt row strips with:

```text
64x64 pixel-art game sprite animation strip.
One row, <N> separated frames, <direction> direction, <action> action.
Flat chroma-key background, no shadows, no floor, no UI, no text, no frame numbers.
Preserve the canonical character identity exactly.
Hard pixel-art edges, limited palette, readable silhouette.
```

Use chroma key colors that do not appear in the character. Prefer `#00ff00`; use magenta if the character is green.

## Pixel Cleanup

Run pixel cleanup after generation:

```bash
python "<skill>/scripts/pixel_snap.py" \
  --input path/to/source.png \
  --output path/to/clean.png \
  --cell 64 \
  --palette 32 \
  --scale-mode nearest \
  --alpha-threshold 24
```

Use `--pixelate-scale 2` when the generated image is too smooth: it downscales and upscales with nearest-neighbor to harden edges.

Do not over-clean faces, eyes, hands, or weapon tips. If strict cleanup damages identity, rerun with a larger palette or no pixelate scale.

## Chroma Key Handling

For generated animation strips, remove chroma key in two passes:

1. Edge-connected flood removal: remove only chroma-key pixels connected to the image border.
2. Final residue cleanup: after each frame is fitted into `64x64`, remove only near-exact key pixels.

Do not globally delete all green-ish pixels. Many fantasy, magic, poison, robot, and cyber characters use green as part of the sprite. For green characters or green VFX, prefer magenta `#ff00ff` as the generated background.

Recommended thresholds:

```text
edge flood threshold: 100-110 distance from key
final residue threshold: 60-75 distance from key
alpha threshold: 12 for detailed attack/VFX sheets, 24 for simpler characters
palette: 96-128 for attack/VFX, 32-64 for simple idle/walk
```

Block acceptance when near-exact chroma residue remains in fitted frames unless it is intentionally part of the sprite. A useful check is counting opaque pixels within distance `<= 72` of the key color.

## Preview Export

Prefer animated WebP for transparent previews. GIF is only a compatibility preview and must be exported carefully:

- upscale frames with nearest-neighbor before previewing, usually `x4`
- use a stable global palette for all frames
- reserve palette index `0` for transparency
- write `disposal=2`, so each frame clears the previous frame
- disable dithering
- do not use GIF optimizer modes that change disposal to `1`

Use:

```bash
python "<skill>/scripts/export_animation_previews.py" \
  --atlas path/to/character-sheet-clean.png \
  --rows 8 \
  --columns 6 \
  --row-names south,south-east,east,north-east,north,north-west,west,south-west \
  --prefix attack \
  --out-dir path/to/qa/previews \
  --scale 4
```

This writes transparent animated WebP, transparent GIF with `disposal=2`, checkerboard GIF, and PNG strip previews for each row.

## Validation

Validate atlas geometry and frame content:

```bash
python "<skill>/scripts/validate_64_sheet.py" \
  --input path/to/character-sheet-clean.png \
  --rows 24 \
  --columns 6 \
  --json-out path/to/qa/validation.json \
  --contact-sheet path/to/qa/contact-sheet.png
```

Block acceptance when:

- atlas dimensions do not equal `columns*64` by `rows*64`
- required frames are empty
- sprites touch cell edges unexpectedly
- chroma-key color remains as opaque pixels
- rows drift into different characters, outfits, weapons, or palettes
- attack effects are detached, oversized, or cross into neighboring cells

Validation scripts catch geometry and pixel risks. Visual review is still required for animation quality and identity consistency.

## Attack Animation Guidance

For melee attacks, show anticipation, swing/contact, and recovery. Keep weapon arcs attached to the weapon and inside the cell.

For ranged attacks, animate the character firing/casting, not the projectile traveling across the sheet. Detached projectiles should be separate VFX assets unless the user requests embedded attack effects.

For magic attacks, keep glow and effects hard-edged, opaque, and close to the body or weapon. Avoid soft particles and transparent bloom.

## Engine Notes

Ask for the target engine if export naming matters. Common presets:

- Godot/Unity: one atlas PNG plus JSON metadata.
- Phaser/Pixi: one PNG atlas and frame map.
- Aseprite workflow: separate PNG rows or frames named `<action>_<direction>_<index>.png`.

If unspecified, produce a simple PNG atlas and `metadata.json` with cell size, row names, frame counts, and direction order.
