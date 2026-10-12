---
name: bevy-3d-lighting
description: "Docs-first stub for Bevy 3D lights. Godot counterpart: godot-3d-lighting. Keywords: Bevy, lighting, directional, point, spot, bevy_light, PBR."
---

# Bevy 3D lighting (docs-first stub)

Not a full port. Docs-first stub. Godot counterpart: godot-3d-lighting.

## When to use

Load this when a 3D scene needs lights. Materials stay on bevy-3d-materials. Shadows and GI settings beyond the module blurbs are gaps.

## ECS shape

- **Module:** `bevy::light` says it provides directional, point, and spot lights, plus light probes, atmosphere, volumetrics, and shadow configuration.
- **Feature:** `bevy_light` is described the same way on the crate feature list.
- **PBR page names:** `DirectionalLightViewEntities`, `ExtractedDirectionalLight`, `ExtractedPointLight`, `ExtractedRectLight`, `GpuClusteredLight` (point, spot, or rectangle), `DistanceFog`, `LightProbePlugin`, `ContactShadows`.
- **Systems:** light clustering and extraction are engine-owned. Gameplay only spawns light entities.

## Godot idea to Bevy idiom

| Idea | Bevy idiom (idea only) |
| --- | --- |
| Sun | A directional light entity. Struct method list was not opened; the module states the kind exists. |
| Omni or point | A point light. Same limit. |
| Spot | A spot light. Same limit. |
| Fog | DistanceFog on the pbr page. |
| Baked GI | Irradiance volumes are a pbr module. Baking steps were not opened. |

## Gaps

- Individual light struct pages (`DirectionalLight`, `PointLight`, `SpotLight`) were not opened, so fields such as intensity or shadow cascades are not named here.
- `bevy_solari` is an experimental raytraced-lighting feature. Its API was not opened.
- Lightmap baking workflows were not opened.


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

- No Godot light node types. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.

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
- [bevy::light](https://docs.rs/bevy/latest/bevy/light/index.html) - Module blurb: directional, point, spot, probes, shadows.
- [bevy::pbr](https://docs.rs/bevy/latest/bevy/pbr/index.html) - Extracted lights, fog, probes, contact shadows.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-3d-materials](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-3d-materials/SKILL.md) - Lit surfaces.
- [bevy-camera-systems](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-camera-systems/SKILL.md) - Camera the lights affect.

#### Complements
- [bevy-3d-world-building](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-3d-world-building/SKILL.md) - Place light entities in a level.
- [godot-3d-lighting](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-3d-lighting/SKILL.md) - Godot counterpart. Source idea only.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
