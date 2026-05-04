---
name: generate2dsprite
description: "Generate and postprocess general 2D game assets and animation sheets: pixel-art sprites, clean HD map props, creatures, characters, NPCs, spells, projectiles, impacts, props, summons, and transparent GIF exports. Use when Codex should infer the asset plan from a natural-language request, match a reference or map art style, call built-in `image_gen` for solid-magenta raw sheets, and use the local processor only for chroma-key cleanup, frame extraction, alignment, QC, and transparent exports."
---

# Generate2dsprite

Use this skill for self-contained 2D sprite or animation assets.

If the user wants a whole playable content pack, map, story, slideshow, or pack assembly, use `generate2dgamepack`.

## Parameters

Infer these from the user request:

- `asset_type`: `player` | `npc` | `creature` | `character` | `spell` | `projectile` | `impact` | `prop` | `summon` | `fx`
- `action`: `single` | `idle` | `cast` | `attack` | `shoot` | `jump` | `hurt` | `combat` | `walk` | `run` | `hover` | `charge` | `projectile` | `impact` | `explode` | `death`
- `view`: `topdown` | `side` | `3/4`
- `sheet`: `auto` | `1x4` | `2x2` | `2x3` | `3x3` | `4x4` | `5x5` | `custom_grid`
- `frames`: `auto` or explicit count
- `bundle`: `single_asset` | `unit_bundle` | `spell_bundle` | `combat_bundle` | `line_bundle` | `hero_action_bundle` | `engine_atlas`
- `effect_policy`: `all` | `largest`
- `anchor`: `center` | `bottom` | `feet`
- `margin`: `tight` | `normal` | `safe`
- `art_style`: pixel_art | clean_hd | pixel_inspired | retro_pixel | map_style | project-native
- `reference`: `none` | `attached_image` | `generated_image` | `local_file`
- `layout_guide`: `none` | `optional` | `recommended`
- `prompt`: the user's theme or visual direction
- `role`: only when the asset is clearly an NPC role
- `name`: optional output slug

Read [references/modes.md](references/modes.md) when the request is ambiguous.

## Agent Rules

- Decide the asset plan yourself. Do not force the user to spell out sheet size, frame count, or bundle structure when the request already implies them.
- Do not pack unrelated actions into one raw generated sheet just to satisfy a `4x4`, `5x5`, or custom engine atlas. A raw generated sheet should represent one action family, one continuous sequence, one canonical directional locomotion sheet, or one prop/asset pack.
- For controllable heroes, main characters, and high-value player assets with multiple actions, generate separate per-action sheets first, QC each action, then deterministically assemble the engine-required atlas only after the rows/strips pass visual review.
- Write the art prompt yourself. Do not default to the prompt-builder script.
- Use built-in `image_gen` for every raw image.
- When the user provides or implies a visual reference, use built-in image edit/reference semantics only after the reference image is visible in the conversation context. If the reference is a local file, call `view_image` first; do not rely on a filesystem path in the prompt as the visual reference.
- Do not force pixel art when the asset is a map prop for `$generate2dmap` or when the user/project requests a different style. Match the map or reference style first.
- Use the script only as a deterministic processor: magenta cleanup, frame splitting, component filtering, scaling, alignment, QC metadata, transparent sheet export, and GIF export.
- Do not use scripts to generate the creative image prompt. If a legacy prompt-builder command exists, treat it as historical compatibility only, not the normal skill workflow.
- Layout guides are allowed only as deterministic geometry references for image generation. They may show slot count, spacing, centering, and safe padding, but must never define the creative art direction.
- Treat script flags as execution primitives chosen by the agent, not user-facing hardcoded workflow.
- If a generated sheet touches cell edges, drifts in scale, or breaks a projectile / impact loop, either reprocess with better primitive settings or regenerate the raw sheet.
- Keep the solid `#FF00FF` background rule unless the user explicitly wants a different processing workflow.

## Workflow

### 1. Infer the asset plan

Pick the smallest useful output.

Examples:

- controllable hero with four directions -> `player` + `player_sheet`
- side-view controllable hero with idle/run/shoot/jump -> `player` + `hero_action_bundle`
  - idle sheet
  - run sheet
  - shoot sheet with body/weapon only
  - jump sheet
  - projectile / muzzle flash as separate assets when needed
  - optional assembled engine atlas after per-action QC
- healer overworld NPC -> `npc` + `single_asset` or `unit_bundle`
- large boss idle loop -> `creature` + `idle` + `3x3`
- wizard throwing a magic orb -> `spell_bundle`
  - caster cast sheet
  - projectile loop
  - impact burst
- monster line request -> `line_bundle`
  - plan 1-3 forms
  - per form, make the sheets the request actually needs

### 2. Write the prompt manually

Use [references/prompt-rules.md](references/prompt-rules.md).

Choose `art_style` before writing the prompt:

- Use `pixel_art` or `retro_pixel` for classic sprites, 16-bit RPG actors, and requests that explicitly ask for pixel art.
- Use `clean_hd` for map props or assets intended to match clean hand-painted HD maps.
- Use `pixel_inspired` only when the user wants a pixel-adjacent look without retro chunkiness.
- Use `map_style` or `project-native` when an existing map, game, or reference should define the style.

If a reference is involved:

- Make the reference visible first. For local paths, use `view_image`; for freshly generated references, rely on the image already shown in context.
- State the reference role explicitly: preserve identity/style, create an animation sheet for the same subject, create an evolution/variant, or derive a matching prop/FX.
- Preserve the stable identity markers from the reference: silhouette, palette, face/eye features, costume marks, major accessories, and material language.
- Let only the requested action or evolution change. Do not redesign the subject unless the user asks.
- Still require exact sheet shape, solid magenta background, frame containment, and same scale across frames.

Keep the strict parts:

- solid `#FF00FF` background
- exact sheet shape
- same character or asset identity across frames
- same bounding box and pixel scale across frames
- explicit containment: nothing may cross cell edges

Mixed-action atlas guardrail:

- Do not ask `image_gen` to generate unrelated action rows in one raw sheet, such as `row 1 idle, row 2 run, row 3 shoot, row 4 jump`, for a controllable hero or main character.
- If an engine needs a combined `4x4`, `5x5`, or custom atlas, generate the action rows/strips separately, process and QC them separately, then assemble the delivery atlas deterministically.
- Exceptions are canonical directional locomotion sheets, one continuous long action sequence, prop packs, tileset-like atlases, and low-stakes compact enemy combat sheets. These still need one coherent prompt and visual QC.
- Keep projectile, muzzle flash, impact, dust trails, and detached FX in separate sheets unless they are intentionally part of the same action silhouette and remain tightly attached.

If a layout guide is useful, generate one before calling built-in `image_gen`:

```bash
python scripts/make_layout_guide.py \
  --rows <rows> \
  --cols <cols> \
  --cell-width 384 \
  --cell-height 384 \
  --output <run-dir>/references/<rows>x<cols>-layout-guide.png
```

Then make the guide visible in the conversation context and tell `image_gen` to use it only for invisible slot count, spacing, centering, and safe padding. The output must not reproduce guide boxes, safe-area rectangles, center marks, labels, borders, or guide background.

Use layout guides deliberately:

- recommended for `prop_pack_3x3`, `prop_pack_4x4`, tileset-like atlases, fixed atlas rows, and non-directional 16-frame action sequences such as casting, summoning, charging, death, or transformation
- optional for `3x3` large idle and high-value showcase loops when previous generations drift in scale or spacing
- not the default for `4x4` four-direction walk sheets, because the guide can make directional poses too conservative; use it only after an unguided run fails layout or edge safety

### 3. Generate the raw image

Use built-in `image_gen`.

After generation:

- find the raw PNG under `$CODEX_HOME/generated_images/...`
- copy or reference it from the working output folder
- keep the original generated image in place

### 4. Postprocess locally

Run `scripts/generate2dsprite.py process` on the raw image.

The processor is intentionally low-level. The agent chooses:

- `rows` / `cols`
- `fit_scale`
- `align`
- `shared_scale`
- `component_mode`
- `component_padding`
- `edge_touch` rejection strategy

Use the processor to gather QC metadata, not to make aesthetic decisions for you.

For hero action bundles, process each action row as its own sheet before any final atlas assembly. Prefer `component_mode=largest` for body-only hero rows when projectiles, dust, muzzle flashes, or trails would distort the body bounding box. Use `component_mode=all` for projectile, impact, aura, or intentionally attached FX sheets.

### 5. QC the result

Check:

- did any frame touch the cell edge
- did any frame resize differently than intended
- did detached effects become noise
- does the sheet still read as one coherent animation

If not, rerun with different processor settings or regenerate the raw sheet.

### 6. Return the right bundle

For a single sheet, expect:

- `raw-sheet.png`
- `raw-sheet-clean.png`
- `sheet-transparent.png`
- frame PNGs
- `animation.gif`
- `prompt-used.txt`
- `pipeline-meta.json`

For `player_sheet`, expect:

- transparent 4x4 sheet
- 16 frame PNGs
- direction strips
- 4 direction GIFs

For `spell_bundle` or `unit_bundle`, create one folder per asset in the bundle.

For `hero_action_bundle`, expect:

- one raw and processed sheet per action
- per-action frame PNGs and GIFs for visual QC
- separate projectile / muzzle / impact assets when the hero shoots or casts
- optional assembled `engine-atlas-transparent.png` only after per-action QC passes

## Defaults

- `idle`
  - small or medium actor -> `2x2`
  - large creature or boss -> `3x3`
- `cast` -> prefer `2x3`
- `projectile` -> prefer `1x4`
- `impact` / `explode` -> prefer `2x2`
- `walk`
  - topdown actor -> `4x4` for four-direction walk
  - side-view asset -> `2x2`
- controllable hero or main player with multiple actions -> `hero_action_bundle`
  - generate one action per raw sheet, commonly `1x4` per action
  - do not generate a mixed-action raw `4x4`, `5x5`, or custom atlas
  - assemble the final atlas only as a deterministic delivery step if the game requires it
- `4x4`, `5x5`, and custom grids
  - use as raw generation only for one coherent long action sequence, canonical directional locomotion, prop packs, or tileset-like atlases
  - use as delivery atlases for mixed actions only after separate action sheets pass QC
- use `shared_scale` by default for any multi-frame asset where frame-to-frame consistency matters
- use `largest` component mode when detached sparkles or edge debris make the main body unstable

## Resources

- `references/modes.md`: asset, action, bundle, and sheet selection
- `references/prompt-rules.md`: manual prompt patterns and containment rules
- `scripts/generate2dsprite.py`: postprocess primitive for cleanup, extraction, alignment, QC, and GIF export
