---
name: bevy-3d-lighting
description: "Bevy ECS skill for 3D lights. Keywords: Bevy, lighting, directional, point, spot, bevy_light, PBR."
---

# Bevy 3D lighting

## When to use

Load this when a 3D scene needs lights. Materials stay on bevy-3d-materials. Check the light module docs for shadow and GI settings beyond the module blurbs.

## ECS shape

- **Module:** `bevy::light` says it provides directional, point, and spot lights, plus light probes, atmosphere, volumetrics, and shadow configuration.
- **Feature:** `bevy_light` is described the same way on the crate feature list.
- **PBR page names:** `DirectionalLightViewEntities`, `ExtractedDirectionalLight`, `ExtractedPointLight`, `ExtractedRectLight`, `GpuClusteredLight` (point, spot, or rectangle), `DistanceFog`, `LightProbePlugin`, `ContactShadows`.
- **Systems:** light clustering and extraction are engine-owned. Gameplay only spawns light entities.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Sun | A directional light entity. The module states the kind exists. Check the struct page for method names before writing them. |
| Omni or point | A point light. Same limit. |
| Spot | A spot light. Same limit. |
| Fog | DistanceFog on the pbr page. |
| Baked GI | Irradiance volumes are a pbr module. Check that module for baking steps before writing them. |

## Scope

- Check the `DirectionalLight`, `PointLight`, and `SpotLight` docs.rs pages for field names such as intensity or shadow cascades before writing them.
- `bevy_solari` is an experimental raytraced-lighting feature. Check its docs.rs page before writing its API.
- Check the lightmap docs for baking steps before writing them.

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

- No Godot light node types. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

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
- [bevy::light](https://docs.rs/bevy/latest/bevy/light/index.html) - Module blurb: directional, point, spot, probes, shadows.
- [bevy::pbr](https://docs.rs/bevy/latest/bevy/pbr/index.html) - Extracted lights, fog, probes, contact shadows.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-3d-materials](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-3d-materials/SKILL.md) - Lit surfaces.
- [bevy-camera-systems](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-camera-systems/SKILL.md) - Camera the lights affect.

#### Complements
- [bevy-3d-world-building](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-3d-world-building/SKILL.md) - Place light entities in a level.
- [godot-3d-lighting](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-3d-lighting/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
