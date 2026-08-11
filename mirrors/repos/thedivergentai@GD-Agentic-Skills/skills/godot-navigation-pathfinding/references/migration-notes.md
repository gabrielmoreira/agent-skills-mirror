# Migration notes: godot-navigation-pathfinding

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 3.x → 4.0

Official: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html)

- `Navigation2D`/`Navigation3D` hubs removed — use NavigationRegion*/Agent*/Server* stack.
- `NavigationMeshInstance` → `NavigationRegion3D`; `NavigationPolygonInstance` → `NavigationRegion2D`.
- `AStar` `get_points()` → `get_points_id()` (manual rename list).
- Re-bake navmeshes after convert; room/portal occlusion ≠ Navigation.

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `NavigationAgent2D/3D.set_velocity()` removed — assign `velocity` property each frame for RVO.
- `time_horizon` split into `time_horizon_agents` and `time_horizon_obstacles`.
- `NavigationAgent3D.agent_height_offset` → `path_height_offset`; `ignore_y` removed.
- `NavigationObstacle*.estimate_radius` removed; `get_rid()` → `get_agent_rid()`.
- `NavigationServer*.agent_set_callback()` → `agent_set_avoidance_callback()`.
- `PathFollow2D.lookahead` removed — update 2D path-following locomotion samples.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

*No skill-relevant breaking changes for this hop.*

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- `AStar2D/3D/Grid2D.get_*_path()` gain `allow_partial_path`.
- `NavigationRegion2D` experimental avoidance props removed — route avoidance through `NavigationAgent2D` instead.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `NavigationServer2D/3D.query_path()` gains optional async `callback`.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- Nav regions bake/update **asynchronously** by default — defer `query_path` until rebake completes after TileMap or CSG edits.
- Navmesh merge order changed — fix overlapping regions and tune `merge_rasterizer_cell_scale` when edge-merge errors appear.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- `AStar*.get_point_path()` / `get_id_path()` return empty when start point disabled/solid — guard custom A* wrappers accordingly.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

*No skill-relevant breaking changes for this hop.*
