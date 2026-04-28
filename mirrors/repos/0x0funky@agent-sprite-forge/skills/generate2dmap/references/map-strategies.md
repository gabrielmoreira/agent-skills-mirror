# Map Pipeline Selection

Choose maps by combining pipeline axes. Avoid treating `hybrid` as a top-level strategy; most real 2D maps are hybrid combinations of visual art, objects, and collision metadata.

## Visual Model

### `baked_raster`

Use when:

- the scene is static, decorative, fixed-screen, or visual-first
- the game needs a battle background, title scene, menu backdrop, cutscene, or quick prototype
- collision is absent or can be represented by a few invisible shapes

Deliver one image plus optional collision/zones metadata.

### `layered_raster`

Use when:

- a hand-painted or generated base map is best, but tall objects need collision, occlusion, interaction, reuse, or later editing
- the scene is an RPG town, shrine, dungeon room, field, interior, or monster-taming exploration map
- y-sorted actors should walk in front of and behind props

Deliver a ground-only base image, separate props, placement metadata, collision/zones metadata, and a flattened preview.

### `tilemap`

Use when:

- the engine/editor already uses Tiled, LDtk, Phaser tilemaps, Godot TileMap, Unity Tilemap, or similar tooling
- the user asks for tiles, tilesets, tile collision, autotiling, or editable grid-perfect maps
- procedural generation, large maps, or editor workflows matter

Deliver engine-native map data, tileset images, tile layers, object layers, and tile/object collision.

### `layered_tilemap`

Use when:

- the game needs multiple tile layers such as ground, decor, walls, overhead, and foreground
- actors need to pass under selected tile layers
- collision and triggers are tile/object-layer driven

Deliver layered tile data and a render-order contract.

### `parallax_layers`

Use when:

- the map is a side-scroller, runner, shooter, or scrolling backdrop
- background depth matters more than top-down collision

Deliver background, midground, foreground, and scroll-speed metadata.

## Runtime Object Model

- `none`: the map is just a background or tile layers.
- `separate_props`: props are independent sprites but do not require y-sort.
- `y_sorted_props`: props and actors sort by base `y`; use for top-down RPG scenes.
- `interactive_entities`: objects need dialogue, pickups, doors, destructibles, or state.
- `foreground_occluders`: selected overlays always draw over actors.

Use the simplest model that can express collision and occlusion correctly.

## Collision Model

- `none`: visual-only maps and simple backgrounds.
- `coarse_shapes`: a few rectangles/ellipses for fixed arenas or decorative maps.
- `precise_shapes`: explicit blockers and walk bounds for layered RPG maps.
- `tile_collision`: collision stored per tile or tile layer.
- `polygon_walkmesh`: irregular walkable regions or constrained path maps.
- `trigger_zones`: encounter/rest/exit/dialogue areas; often combined with another collision model.

Do not infer collision from prop PNG bounds automatically. Use explicit blockers for prop bases and explicit walkable zones for navigation.

## Engine Target

- `raw_canvas`: use PNG assets, JSON metadata, and project-specific render code.
- `Phaser`: prefer atlas/tilemap JSON when the project already uses Phaser loaders.
- `Tiled_JSON`: produce Tiled-compatible tilesets, layers, objects, and custom properties.
- `LDtk`: produce or adapt to LDtk entity/layer concepts if the project uses LDtk.
- `Godot_TileMap`: produce tile layers and scene metadata matching Godot's structure.
- `Unity_Tilemap`: produce tileset/sprite assets and placement data for Unity workflows.
- project-native: preserve existing schema when a game already has one.

## Presets

### Fixed Battle Background

- `visual_model`: `baked_raster`
- `runtime_object_model`: `none`
- `collision_model`: `none` or `coarse_shapes`
- Typical deliverables: one PNG, optional zones.

### RPG Exploration Scene

- `visual_model`: `layered_raster`
- `runtime_object_model`: `y_sorted_props`
- `collision_model`: `precise_shapes + trigger_zones`
- Typical deliverables: base map, prop images, placement JSON, collision JSON, preview.

### Monster Grassland

- `visual_model`: `layered_raster`
- `runtime_object_model`: `y_sorted_props + interactive_entities`
- `collision_model`: `precise_shapes + trigger_zones`
- Good prop-pack candidates: rocks, shrubs, flowers, signs, small logs.

### Tile-Based Dungeon

- `visual_model`: `layered_tilemap`
- `runtime_object_model`: `interactive_entities`
- `collision_model`: `tile_collision + trigger_zones`
- Use only when the engine/editor supports tilemaps.

### Side-Scroller Stage

- `visual_model`: `parallax_layers`
- `runtime_object_model`: `separate_props`
- `collision_model`: `precise_shapes` or engine-native platform collision
- Typical deliverables: parallax layers, collision platforms, hazards, spawn/checkpoints.

## Escalation Heuristic

Start with the smallest bundle that works:

1. `baked_raster`
2. `baked_raster + coarse_shapes`
3. `layered_raster + a few props`
4. `layered_raster + y_sorted_props + precise_shapes`
5. `tilemap` or `layered_tilemap`, only when engine/editor requirements justify it
