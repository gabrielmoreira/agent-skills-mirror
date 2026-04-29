# Prop Pack Contract

Prop packs batch multiple small static map props into one generated sheet, then extract each cell into a transparent prop PNG.

Use prop packs to reduce repeated image-generation calls and prompt overhead. They trade per-prop control for speed, so use them only when the props can share one style, scale, perspective, and quality bar.

## When To Use

Good candidates:

- rocks, shrubs, flowers, mushrooms, logs
- crates, barrels, sacks, pots
- small signs, lamps, lanterns, fences, posts
- floor ornaments, small statues, ruins, debris
- repeated environmental dressing for one biome

Avoid prop packs for:

- buildings, gates, trees with wide canopies, bridges
- hero objects, key story artifacts, readable statues
- animated props or props with multiple states
- props requiring exact silhouette, scale, or identity
- props that are too wide/tall for equal cells

## Sheet Size Selection

- `2x2`: 4 props, safest batch size.
- `3x3`: 9 props, best default for small/medium environmental sets.
- `4x4`: 16 props, only for very simple small props with strong margins.

Use `3x3` by default when the user asks for a set of map props and does not specify count.
Use one-by-one generation instead of a pack for hero props, wide gates, buildings, wide trees, or anything that must line up exactly with collision.

## Prompt Pattern

```text
Create exactly one <ROWS>x<COLS> prop sheet for a top-down 2D RPG map.
Each cell contains one separate static environmental prop from this list, in row-major order:
1. <prop>
2. <prop>
...
All props share the same biome, palette, camera angle, selected map art style, and scale.
Use clean hand-painted HD 2D game asset style by default: crisp silhouettes, smooth surfaces, low texture noise, controlled accent lighting. Do not make pixel art unless the user asked for it.
Mostly front-facing top-down RPG object view: upright objects are vertical and centered, with only a small visible top face. Avoid strong isometric diagonal rotation; crates and barrels should not become diamond-shaped or tilted unless the user explicitly asks for isometric art.
Full object visible, centered in its own cell, crisp but not chunky outlines.
Each prop must fit fully inside the central 50% to 60% of its cell with generous flat magenta gutters on all four sides.
No prop, branch, roof, sign, glow, cable, smoke, sparkle, shadow, or fragment may touch or cross a cell edge.
Background must be 100% solid flat #FF00FF magenta in every cell, no gradients, no texture, no shadows, no floor plane.
No text, labels, UI, watermark, numbers, arrows, borders, grid lines, or readable letters.
```

If a cell should stay empty, explicitly say `empty magenta cell`.

## Extraction

Before extraction, run a chroma-key cleanup pass when the sheet has antialiased magenta fringe or when the props will be composited over a dark/detailed base. This is often better than direct hard-key extraction:

```bash
python $CODEX_HOME/skills/.system/imagegen/scripts/remove_chroma_key.py \
  --input assets/props/raw/forest-props-sheet.png \
  --out assets/props/raw/forest-props-sheet-alpha.png \
  --key-color '#ff00ff' \
  --soft-matte \
  --transparent-threshold 35 \
  --opaque-threshold 160 \
  --despill \
  --edge-contract 1 \
  --force
```

Use `scripts/extract_prop_pack.py`:

```bash
python skills/generate2dmap/scripts/extract_prop_pack.py \
  --input assets/props/raw/forest-props-sheet-alpha.png \
  --rows 3 \
  --cols 3 \
  --labels mossy-rock,shrub,fallen-log,small-lantern,wooden-sign,flower-patch,stump,crate,grass-tuft \
  --output-dir assets/props \
  --manifest assets/props/forest-prop-pack.json \
  --component-mode largest \
  --component-padding 8 \
  --min-component-area 200 \
  --reject-edge-touch
```

Output shape:

```text
assets/props/<label>/prop.png
assets/props/forest-prop-pack.json
```

The manifest contains source cell coordinates, crop boxes, alpha bounds, extracted image size, component counts, and `edge_touch` flags.

If the first pack fails because large props touch cell edges, regenerate with stricter occupancy wording such as `each prop must fit inside the central 50% of its cell`. Do not pass a failed pack by relaxing QC unless the clipped asset is intentionally discarded.

## Placement

After extraction, create placement JSON:

```json
{
  "props": [
    {
      "id": "mossy-rock-1",
      "image": "assets/props/mossy-rock/prop.png",
      "x": 420,
      "y": 512,
      "w": 96,
      "h": 72,
      "sortY": 512,
      "layer": "props"
    }
  ]
}
```

Then compose a QA preview with `scripts/compose_layered_preview.py`.

## QC Rules

Reject or regenerate the pack when:

- any accepted prop has `edge_touch: true`
- labels do not match the requested cells
- a prop has text, UI, shadows, or floor baked in
- prop identity drifts into character/NPC-like art
- a prop is too large for the intended placement scale

For noisy particles or edge debris, reprocess with `--component-mode largest`. For intentional multi-part props, use `--component-mode all` and increase the prompt margin.
