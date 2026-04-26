# Map Strategy Selection

Choose the lightest structure that gives the game enough control.

## Single Baked Image

Use when:

- the scene is small, static, decorative, or fixed-screen
- collision is absent, coarse, or handled by simple invisible shapes
- no actor needs to pass behind tall objects
- the user values speed over future editability
- the map is a menu background, battle backdrop, title scene, cutscene, or quick prototype

Deliver:

- one map image
- optional prompt file
- optional simple collision shapes
- direct code integration

Do not split props just because the skill can do it.

## Layered Base Plus Props

Use when:

- objects block movement precisely
- actors must walk in front of and behind objects
- objects are interactive, animated, reusable, destructible, or likely to be edited
- the user complains about collision accuracy or visual overlap
- the scene is an RPG exploration map, town, dungeon, field, shrine, house interior, or tactical arena

Deliver:

- ground-only base image
- prop sprites generated through `$generate2dsprite` or provided separately
- prop placement metadata
- collision/zones metadata
- flattened preview for QA
- code integration with render ordering

Use `$generate2dsprite` for generated prop sprites. Do not split props just because this strategy exists; choose layered props only when the game benefits from independent collision, occlusion, interaction, reuse, animation, or later editing.

## Tilemap / Tileset

Use when:

- the existing engine uses Tiled, Phaser tilemaps, Godot TileMap, Unity Tilemap, or another tilemap format
- the user asks for tiles, tilesets, tile collision, autotiling, or map editor compatibility
- grid-perfect editing, procedural generation, or very large maps matter

Deliver according to the engine:

- tileset image
- tilemap JSON/TMX/engine-native data
- tile collision layers
- object/trigger layers

Do not force image-generation-only maps into a tilemap workflow unless the user asks.

## Hybrid

Use when:

- most of the scene can be baked but a few objects need control
- only foreground occlusion or interactables need separate sprites
- the project already has a baked map and only one or two pain points

Deliver:

- baked background or base
- only the necessary prop/foreground overlays
- targeted collision metadata

## Escalation Heuristic

Start simple, then escalate:

1. Single image
2. Single image plus collision metadata
3. Hybrid image plus a few props/overlays
4. Fully layered base plus props
5. Tilemap, when engine/editor requirements justify it
