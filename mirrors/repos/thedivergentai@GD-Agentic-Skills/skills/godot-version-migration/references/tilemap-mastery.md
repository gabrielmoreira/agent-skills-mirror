# Migration notes: godot-tilemap-mastery

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 3.x → 4.0

Official: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html)

- TileMap `map_to_world`/`world_to_map` → `map_to_local`/`local_to_map`.
- Converter keeps TileMap; **TileMapLayer** split is a **4.3** hop — do not expect it at 4.0.
- GridMap `map_to_world`/`world_to_map` → local variants.
- Re-save tilesets after convert; verify collision polygons.

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `PathFollow2D.lookahead` removed — update tile-adjacent path-follow samples (moving platforms on Path2D).

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- `TileMap.cell_quadrant_size` → **`rendering_quadrant_size`** — grep performance tuning sections for the old property name.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- **TileMap layers → child `TileMapLayer` nodes** — migrate scenes/scripts: one node per layer, per-layer z-order, collision, and navigation polygons.
- Confirm `rendering_quadrant_size` lives on each `TileMapLayer` after migration.
- `TileData.get_navigation_polygon()` / `get_occluder()` gain flip/transpose optionals — pass transform when sampling nav/occluder from flipped tiles.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

*No skill-relevant breaking changes for this hop.*

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `TileMapLayer` physics chunking changed — `get_coords_for_body_rid()` is less precise; set `physics_quadrant_size = 1` when debugging which tile owns a collision RID.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

*No skill-relevant breaking changes for this hop.*

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

*No skill-relevant breaking changes for this hop.*
