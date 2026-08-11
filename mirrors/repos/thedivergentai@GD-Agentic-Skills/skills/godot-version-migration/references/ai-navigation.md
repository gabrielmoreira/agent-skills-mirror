# Migration notes: godot-ai-navigation

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `NavigationAgent2D/3D.set_velocity()` removed — assign `velocity` property each physics frame for RVO avoidance.
- `time_horizon` split into `time_horizon_agents` and `time_horizon_obstacles` — retune avoidance crowding separately for agents vs static obstacles.
- `NavigationAgent3D.agent_height_offset` → `path_height_offset`; `ignore_y` removed — grep skill scripts for the old property name.
- `NavigationObstacle*.estimate_radius` removed; `get_rid()` → `get_agent_rid()`.
- `NavigationServer*.agent_set_callback()` → `agent_set_avoidance_callback()`; legacy target-velocity / time-horizon server APIs split or removed.
- `PathFollow2D.lookahead` removed — update 2D escort / patrol samples that follow baked paths.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

*No skill-relevant breaking changes for this hop.*

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- `AStar2D/3D/Grid2D.get_*_path()` gain `allow_partial_path` — enable when agents should move toward a unreachable target instead of failing.
- `NavigationRegion2D` experimental avoidance props (`avoidance_layers`, `constrain_avoidance`, …) **removed** — use `NavigationAgent2D` RVO on agents instead of region-side avoidance.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `NavigationServer2D/3D.query_path()` gains optional `callback` — use for async path requests without blocking the main thread.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- Navigation regions update **asynchronously** by default (`navigation/world/region_use_async_iterations`) — wait a frame or poll before assuming rebaked navmesh is query-ready after geometry edits.
- Navmesh merge order changed — edge merge errors may surface; tune `merge_rasterizer_cell_scale` and fix overlapping navmesh sources.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- `AStar*.get_point_path()` / `get_id_path()` return **empty path** when `from_id` is disabled/solid — treat empty as "no route" instead of error/null.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

*No skill-relevant breaking changes for this hop.*
