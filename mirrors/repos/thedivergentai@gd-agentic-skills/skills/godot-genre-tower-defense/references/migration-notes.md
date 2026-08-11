# Migration notes: godot-genre-tower-defense

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `NavigationAgent2D/3D.set_velocity` → `velocity` property.
- `time_horizon` split into `time_horizon_agents` and `time_horizon_obstacles`.
- `NavigationAgent3D.agent_height_offset` → `path_height_offset`; `ignore_y` removed.
- `NavigationObstacle*.estimate_radius` removed; `get_rid` → `get_agent_rid`.
- `NavigationServer*.agent_set_callback` → `agent_set_avoidance_callback`; target velocity / time_horizon server APIs split/removed.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

- `TileMap.cell_quadrant_size` → `rendering_quadrant_size`.

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- If the genre uses TileMap, migrate to TileMapLayer nodes before relying on layer APIs.
- If the genre ships multiplayer, upgrade all peers to 4.3 together (SceneMultiplayer protocol).
- `AStar2D/3D/Grid2D.get_*_path` gain `allow_partial_path`.
- `NavigationRegion2D` experimental avoidance props (`avoidance_layers`, `constrain_avoidance`, …) removed with no replacement.
- **TileMap layers moved to `TileMapLayer` nodes** — migrate scenes/scripts to per-layer nodes.
- `TileData.get_navigation_polygon` / `get_occluder` gain flip/transpose optionals.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `NavigationServer2D/3D.query_path` gains optional `callback`.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- Nav regions update asynchronously by default (`navigation/world/region_use_async_iterations`) — expect sync delay.
- Navmesh merge order changed; edge merge errors may surface — tune `merge_rasterizer_cell_scale` / fix overlapping navmeshes.
- `TileMapLayer.get_coords_for_body_rid` less precise with physics chunking — set `physics_quadrant_size = 1` for old precision.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- Retune Environment glow/fog if the genre leans on bloom-heavy looks.
- `AStar*.get_point_path` / `get_id_path` return empty path when `from_id` is disabled/solid.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- Confirm project stretch mode and AudioStreamPlayer area_mask after opening in 4.7.
