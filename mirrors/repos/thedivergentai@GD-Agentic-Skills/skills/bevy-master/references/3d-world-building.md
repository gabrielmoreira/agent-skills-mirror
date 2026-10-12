---
name: bevy-3d-world-building
description: "Docs-first stub for Bevy 3D level assembly. Godot counterpart: godot-3d-world-building. Keywords: Bevy, level, scene, mesh, world, ECS."
---

# Bevy 3D world building (docs-first stub)

Not a full port. Docs-first stub. Godot counterpart: godot-3d-world-building.

## When to use

Load this when placing meshes, lights, and colliders into a level. Scene spawn mechanics stay on bevy-asset-scenes. Physics bodies stay on bevy-physics-3d.

## ECS shape

- **Spawn:** entities with transforms and render components. `bevy_mesh` provides a mesh format. Mesh primitive constructors were not opened.
- **Scenes:** `bevy_scene` and `bevy_gltf` are features. Spawn details are on bevy-asset-scenes (`AssetServer`, scene spawn).
- **Lights:** place them using bevy-3d-lighting.
- **Systems:** level streaming is your state plus asset handles. No streaming type was opened.

## Godot idea to Bevy idiom

| Idea | Bevy idiom (idea only) |
| --- | --- |
| Packed level | A scene asset spawned through bevy-asset-scenes |
| Kitbash props | Entities. No grid-map node. |
| Environment | Lights, DistanceFog, and camera. No world-environment node. |

## Gaps

- Mesh primitive helpers were not opened.
- CSG and terrain heightmap types were not in the opened module list.
- Collider authoring waits on the physics solver gap in bevy-physics-3d.


## Expert Knowledge Delta

Library target in prose: **Bevy 0.20.0**. Lattice URLs stay unversioned.

Opened canon only: `Component`, `Resource`, `Query`, `Commands`, `Startup`, `Update`, `Fixed` / `FixedMain` (`bevy::time`), `.chain()`, `Plugin`, `DefaultPlugins`, `MinimalPlugins`. Messages and observers are an ownership slot. This file does not invent their struct APIs. Systems run in parallel unless `.chain()` orders the ones that conflict.

### Who owns state

| Piece | Owner | Who may mutate | Schedule |
| --- | --- | --- | --- |
| Data on one entity | `Component` | One system via `Query` | `Update` or `FixedMain` |
| One value for the whole app | `Resource` | One system | `Startup` to insert, then the schedule that reads it |
| Spawn | `Commands` | The spawning system | `Startup` for the initial world; later schedules for runtime spawn |
| Order that must not race | `.chain()` | The chained systems only | Same schedule |
| Plugin boundary | `Plugin` | `build` registers systems and resources | Before the app runs |

Borrow rule: two systems that both mutably query the same component must be ordered (`.chain()`) or split so only one writes. Unrelated systems stay parallel. That is the ECS page rule, not a guess at a system-set API.

### Decision

| If you need | Do this | Do not |
| --- | --- | --- |
| Per-entity data | `Component` + `Query` | A Godot node script |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API this skill did not open | A Gaps row | A fabricated crate (solver, navmesh module, net, XR) |

Load `references/a-gate-notes.md` for the same table plus the gap rule.

## NEVER

- Do not put `/0.20.0/` in lattice URLs. WHY: permalinks stay on `latest`. The 0.20.0 pin belongs in prose once.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: those rows are gaps, blocked, or revisit.

- No Godot CSG, GridMap, or world-environment types. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.

- No Godot types in Bevy code. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No Creation Station content. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No umbrella skill over Godot and Bevy. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- Do not mark this row `ported`. It is `docs_mapped`. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/) - Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/) - Unversioned API index. Feature list opened for 0.20.0.
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.
- [bevy::gltf](https://docs.rs/bevy/latest/bevy/gltf/index.html) - glTF asset loader module exists.
- [bevy::mesh](https://docs.rs/bevy/latest/bevy/mesh/index.html) - Module exists. Body not opened.

### Related Skills

#### Prerequisites
- [bevy-master](../SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](ecs-composition.md) - Components and systems.
- [bevy-asset-scenes](asset-scenes.md) - Scene spawn.
- [bevy-3d-lighting](3d-lighting.md) - Lights.
- [bevy-3d-materials](3d-materials.md) - Surfaces.
- [bevy-camera-systems](camera-systems.md) - View.

#### Complements
- [bevy-procedural-generation](procedural-generation.md) - Generated layouts.
- [bevy-physics-3d](physics-3d.md) - Simulated props. Solver still unpicked.
- [godot-3d-world-building](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-3d-world-building/SKILL.md) - Godot counterpart. Source idea only.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](../SKILL.md) - Bevy router.
