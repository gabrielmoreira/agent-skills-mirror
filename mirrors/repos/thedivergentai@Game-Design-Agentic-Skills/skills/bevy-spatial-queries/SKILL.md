---
name: bevy-spatial-queries
description: "Bevy ECS skill for spatial queries. Keywords: Bevy, raycast, shapecast, picking, physics query."
---

# Bevy spatial queries

## When to use

Load this when a design needs line of sight, a volume overlap, a ground probe, or a mouse pick. Screen-to-2D-world mapping that does not hit a collider is a camera helper, not a physics query.

## ECS shape

- **Components** would own query origin, direction, and a mask once a solver defines them. Check the solver docs before naming those types.
- **Resources** would own a physics world. None was opened.
- **Systems** would run the query after the solver step. Order that with `.chain()` on the ECS page. The clock is `Fixed` / `FixedMain` from `bevy::time`, which is not a query API.
- **Camera-only pick:** `Camera::viewport_to_world_2d` with `GlobalTransform` maps a viewport position to a 2D world position. That is not an intersection test. See bevy-camera-systems.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Ray or shape cast | Check bevy-physics-2d or bevy-physics-3d before naming a cast API. |
| Mouse position in 2D world | `viewport_to_world_2d` on a `Camera` (bevy-camera-systems). A collider hit belongs with the physics skills once you choose a solver. |
| Exclude the caster | Unverified. Do not copy Godot RID exclude lists |
| Field-of-view fan | Design data on components. Check the docs for a sensor API before writing one. |

## Scope

- The `bevy` 0.20.0 feature list has no physics-engine feature, so there is no ray, shape, point, or sweep query to cite.
- Third-party plugins may be added with `add_plugins`. Check a physics crate's own docs before naming a query API.
- Piercing casts, reflection from normals, and ground volumes are unverified.

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

- No Godot ray, shape-cast, or direct-space-state types. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No Avian, Rapier, or any other named physics crate as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented `intersect_ray` or mask APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/) - Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/) - Unversioned API index. No spatial-query module was opened.
- [Assets](https://bevy.org/assets/) - Official asset catalog. No query plugin was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - Systems, `Query`, and `.chain()`.
- [bevy::camera](https://docs.rs/bevy/latest/bevy/camera/index.html) - `viewport_to_world_2d` is a camera map, not a collider query. Details live on bevy-camera-systems.
- [Quick Start: plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - Third-party `add_plugins` without a chosen crate.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - ECS ownership.
- [bevy-camera-systems](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-camera-systems/SKILL.md) - Viewport to 2D world, without a hit test.

#### Complements
- [bevy-physics-2d](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-physics-2d/SKILL.md) - 2D physics and solver choice.
- [bevy-physics-3d](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-physics-3d/SKILL.md) - 3D physics and solver choice.
- [godot-raycasting-queries](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-raycasting-queries/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- [bevy-ai-navigation](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ai-navigation/SKILL.md) - Sensors that need a cast.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
