---
name: bevy-3d-world-building
description: "Bevy ECS skill for 3D level assembly. Keywords: Bevy, level, scene, mesh, world, ECS."
---

# Bevy 3D world building

## When to use

Load this when placing meshes, lights, and colliders into a level. Scene spawn mechanics stay on bevy-asset-scenes. Physics bodies stay on bevy-physics-3d.

## ECS shape

- **Spawn:** entities with transforms and render components. `bevy_mesh` provides a mesh format. Check the mesh docs for primitive constructors before writing them.
- **Scenes:** `bevy_scene` and `bevy_gltf` are features. Spawn details are on bevy-asset-scenes (`AssetServer`, scene spawn).
- **Lights:** place them using bevy-3d-lighting.
- **Systems:** level streaming is your state plus asset handles. No streaming type was opened.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Packed level | A scene asset spawned through bevy-asset-scenes |
| Kitbash props | Entities. No grid-map node. |
| Environment | Lights, DistanceFog, and camera. No world-environment node. |

## Scope

- Check the mesh docs.rs page for primitive helper names before writing them.
- CSG and terrain heightmaps are yours to build in ECS. Check the mesh module list before assuming a built-in type.
- Collider authoring belongs with bevy-physics-3d once you choose a physics solver.

## Expert Knowledge Delta

Target: **Bevy 0.20+**.

Core ECS types: `Component`, `Resource`, `Query`, `Commands`, `Startup`, `Update`, `Fixed` / `FixedMain` (`bevy::time`), `.chain()`, `Plugin`, `DefaultPlugins`, `MinimalPlugins`. Messages and observers are an ownership slot. See `bevy-events-messaging` for their APIs. Systems run in parallel unless `.chain()` orders the ones that conflict.

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
| An API outside the documented set | Check the official docs first | A made-up crate or API |

Load [references/ecs-ownership.md](references/ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No Godot CSG, GridMap, or world-environment types. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

- No Godot types in Bevy code. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/) - Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/) - API reference and Cargo feature list.
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.
- [bevy::gltf](https://docs.rs/bevy/latest/bevy/gltf/index.html) - glTF asset loader module exists.
- [bevy::mesh](https://docs.rs/bevy/latest/bevy/mesh/index.html) - Mesh module reference.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-asset-scenes](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-asset-scenes/SKILL.md) - Scene spawn.
- [bevy-3d-lighting](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-3d-lighting/SKILL.md) - Lights.
- [bevy-3d-materials](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-3d-materials/SKILL.md) - Surfaces.
- [bevy-camera-systems](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-camera-systems/SKILL.md) - View.

#### Complements
- [bevy-procedural-generation](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-procedural-generation/SKILL.md) - Generated layouts.
- [bevy-physics-3d](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-physics-3d/SKILL.md) - Simulated props. Solver still unpicked.
- [godot-3d-world-building](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-3d-world-building/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
