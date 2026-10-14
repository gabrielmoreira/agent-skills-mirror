---
name: bevy-shaders
description: "Bevy ECS skill for shaders. Keywords: Bevy, shader, material, bevy_shader, bevy_material, StandardMaterial."
---

# Bevy shaders and materials

## When to use

Load this when a surface needs a material or a custom shader asset. 3D PBR defaults stay on bevy-3d-materials. Do not treat this as a Godot shader-language port.

## ECS shape

- **Features on the crate page:** `bevy_shader` (shaders through asset handles) and `bevy_material` (material abstraction).
- **PBR hook:** `StandardMaterial` is named in feature blurbs (`pbr_anisotropy_texture` and neighbors) and in the `DistanceFog` summary on the pbr page.
- **Extension:** `ExtendedMaterial` is on the pbr page as a material that extends a base material with extra shaders and data. Check that page for type parameters before writing them.
- **Systems:** material extraction is engine-owned. Do not schedule a custom shader compiler.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Shader material | A material asset handle. Check the shader docs for the source language before writing it. |
| Spatial shader | Unverified. Do not copy Godot shader hints. |
| Full-screen pass | bevy_post_process is a feature. Check that feature's docs for effect types before writing them. |

## Scope

- Check the `bevy::shader` and `bevy::material` module pages before naming a `Shader` struct or a `Material` trait method.
- Check the shader docs for WGSL entry points, bind group layout, and pipeline specialization keys before writing them.

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

- No Godot shader language or hint syntax. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

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
- [bevy::pbr](https://docs.rs/bevy/latest/bevy/pbr/index.html) - `ExtendedMaterial`, `DistanceFog` mentions `StandardMaterial`.
- [bevy::material](https://docs.rs/bevy/latest/bevy/material/index.html) - Material module reference.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-3d-materials](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-3d-materials/SKILL.md) - StandardMaterial surface fields.
- [bevy-asset-scenes](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-asset-scenes/SKILL.md) - Asset handles.

#### Complements
- [bevy-3d-lighting](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-3d-lighting/SKILL.md) - Lights are not shaders.
- [godot-shaders-basics](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-shaders-basics/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
