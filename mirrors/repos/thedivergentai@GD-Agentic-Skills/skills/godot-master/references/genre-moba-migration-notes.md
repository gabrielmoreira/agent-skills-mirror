# Migration notes: godot-genre-moba

Incremental upgrade for topics this skill covers. Apply **one hop**, stabilize/test, then next. Never skip hops.

If the project is **< 4.0**, follow [godot-version-migration](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-version-migration/SKILL.md) era bridges (legacy → 3→4) until 4.0, then these hops. Official 3→4: [Upgrading from Godot 3 to Godot 4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.html).

## 4.0 → 4.1

Official: [Upgrading to Godot 4.1](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.1.html)

- `NavigationAgent2D/3D.set_velocity` → `velocity` property — retune minion/lane agent flow.
- `time_horizon` split into `time_horizon_agents` and `time_horizon_obstacles`.
- `NavigationAgent3D.agent_height_offset` → `path_height_offset`; `ignore_y` removed.
- `NavigationObstacle*.estimate_radius` removed; `get_rid` → `get_agent_rid`.
- `NavigationServer*.agent_set_callback` → `agent_set_avoidance_callback`.

## 4.1 → 4.2

Official: [Upgrading to Godot 4.2](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.2.html)

*No skill-relevant breaking changes for this hop.*

## 4.2 → 4.3

Official: [Upgrading to Godot 4.3](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.3.html)

- **TileMap layers → `TileMapLayer` nodes** — migrate Fog-of-War grid masks before relying on per-layer APIs.
- `SceneMultiplayer` caching protocol incompatible across versions — upgrade server and clients together; add version checks.
- `AStar2D/3D/Grid2D.get_*_path` gain `allow_partial_path`.
- `NavigationRegion2D` experimental avoidance props removed with no replacement.

## 4.3 → 4.4

Official: [Upgrading to Godot 4.4](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.4.html)

- `NavigationServer2D/3D.query_path` gains optional `callback` — async pathing under combat load.

## 4.4 → 4.5

Official: [Upgrading to Godot 4.5](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.5.html)

- `Node.get_rpc_config` → `get_node_rpc_config` — audit ability/cooldown RPC configs.
- Nav regions update asynchronously by default — expect brief lane nav desync after map edits.
- Navmesh merge order changed; edge merge errors may surface — fix overlapping brush navmeshes.

## 4.5 → 4.6

Official: [Upgrading to Godot 4.6](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.6.html)

- Retune Environment glow/fog if the genre leans on bloom-heavy looks (ability VFX, river glow).
- `AStar*.get_point_path` / `get_id_path` return empty path when `from_id` is disabled/solid.

## 4.6 → 4.7

Official: [Upgrading to Godot 4.7](https://docs.godotengine.org/en/stable/tutorials/migrating/upgrading_to_godot_4.7.html)

- Confirm project stretch mode and `AudioStreamPlayer.area_mask` after opening in 4.7.
- `AudioStreamPlayer.area_mask` default is **0** — set mask for bush/river zone audio and ability SFX buses.
- Mouse/keyboard device IDs are `InputEvent.DEVICE_ID_MOUSE` / `DEVICE_ID_KEYBOARD` (not `0`) — retune ability hotbar input checks.
