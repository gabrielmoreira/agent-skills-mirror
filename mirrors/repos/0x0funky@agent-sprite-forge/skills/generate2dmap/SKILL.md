---
name: generate2dmap
description: "Generate 2D game maps for RPGs, monster-taming games, tactical maps, arcade games, and canvas/HTML games by choosing the right map strategy: single baked background, layered base map plus prop sprites, tilemap/tileset, or hybrid. Use when Codex needs to make or revise a 2D map, collision map, map props, tile-like layout, top-down scene, parallax/overlay layer, simple background map, or a base-map-plus-sprites game scene."
---

# Generate2dmap

## Overview

Choose and build the simplest 2D map structure that supports the game's needs. This skill is a map orchestrator: it decides whether the right output is a single baked map, a baked map plus collision metadata, a hybrid map, a layered base map plus props, or a tilemap.

Use a single baked image for simple or mostly decorative maps. Use layered assets when collision, occlusion, interaction, reuse, or animation matter. Use tilemaps when the existing engine or user request expects tile-based editing.

Invoke `$generate2dsprite` only when the chosen map strategy needs reusable transparent props, usually in layered or hybrid maps. Do not create props just because this skill can use them.

## Workflow

1. Inspect the target game.
   - Find map dimensions, camera scale, render loop, asset loading, collision shape support, spawn/rest/NPC/encounter zone data, and debug collision tools.
   - Preserve the game engine's existing style and coordinate system.

2. Choose the map strategy.
   - Single baked image: best for simple maps, menu/background scenes, fixed arenas, prototypes, and games with minimal or coarse collision.
   - Layered map: best for RPG exploration, precise collision, tall objects, occlusion, props reused across areas, animated props, or interactables.
   - Tilemap: best when the engine already uses tiles, the user asks for tile editing/export, or grid-perfect level design matters.
   - Hybrid: use a baked base/background with a small number of separate overlays, props, or collision shapes.
   - Read [references/map-strategies.md](references/map-strategies.md) when the strategy is not obvious.

3. Produce the chosen asset set.
   - For a single baked map, generate or edit one complete map image and integrate it directly.
   - For a single baked map with gameplay constraints, generate or edit one complete map image plus collision or zone metadata.
   - For a hybrid map, keep most of the scene baked and split out only the objects that need collision, occlusion, interaction, reuse, or animation.
   - For a layered map, create a ground-only base map plus generated props. Use `$generate2dsprite` for the prop assets, then place them in map coordinates. Read [references/layered-map-contract.md](references/layered-map-contract.md) before implementing a new layered map or a major map revision.
   - For a tilemap, follow the project's tilemap format or create a tileset/map JSON only when the consuming engine supports it.

4. Build collision and zones.
   - Use simple structured shapes first: rectangles, ellipses, and polygons.
   - Keep collision data independent from art files.
   - Add only the gameplay metadata the map needs: walk bounds, blockers, encounter zones, rest zones, NPC collision radius, spawn point, battle return points, exits, or triggers.
   - For single baked maps, collision may be coarse or minimal if the gameplay does not require precision.
   - For layered maps, verify critical points programmatically: spawn is walkable, path centers are walkable, prop bases block, entrances remain open.

5. QA and iterate.
   - Produce a flattened preview when using layered assets.
   - Check map scale, camera framing, text/UI overlap, collision, path readability, and keyboard/controller navigation.
   - If a layered prop is poor or touches edges, regenerate or reprocess the prop instead of cutting it from a baked map.

## Decision Rules

- Prefer the simplest map that works for the requested game.
- Use a single baked image when the map is decorative, tiny, fixed-screen, or only needs broad collision.
- Use layered props when an object should block, cover, interact, animate, be reused, or be edited independently.
- Paint purely ground-level details into the base map.
- If a baked map's collision or occlusion feels imprecise, convert only the troublesome objects into props instead of rebuilding everything.
- Use tilesets only when the existing game already uses tilemap tooling or the user asks for a tile-based editor/export.
- Keep generated text out of map art. Put labels and UI in code.

## Expected Deliverables

For a simple baked scene, produce:

- `assets/map/<name>.png`
- optional `<name>.prompt.txt`
- optional collision metadata if gameplay needs it
- code changes that load/use the image

For a layered playable scene, produce:

- `assets/map/<name>-base.png`
- `assets/map/<name>-base.prompt.txt`
- generated prop folders created through `$generate2dsprite`
- `assets/props/<prop-name>/prop.png` plus `pipeline-meta.json`
- prop placement metadata in the target game's format
- `assets/map/<name>-layered-preview.png` as a flattened final preview for QA and showcase
- collision metadata such as `data/collision-map.json`
- code changes that load the base map, load prop images, render y-sorted props/actors, and use the collision metadata

## Validation

Always validate what the chosen strategy requires:

- map files exist and have expected dimensions
- transparent prop PNGs have alpha when props are used
- prop `pipeline-meta.json` has no `edge_touch_frames` when generated props are used
- game JavaScript/TypeScript parses
- collision JSON parses when collision metadata exists
- critical point tests pass when precise collision is required
- visual preview or in-game render looks coherent at the game's camera size
