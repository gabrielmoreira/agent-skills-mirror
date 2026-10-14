---
name: bevy-tilemap
description: "Bevy ECS skill for tile maps. Keywords: Bevy, tilemap, tiles, ECS, Sprite."
---

# Bevy tilemap

## When to use

Load this before storing a grid of tiles. The `bevy` crate has sprites and meshes. A tilemap is yours to build in ECS.

## ECS shape

- **Components:** a cell can be your own component (grid coord plus an id) spawned through normal ECS. `Sprite` can draw one cell. That is not a tilemap type.
- **Resources:** a map resource can hold width, height, and a seed. See bevy-data-resources.
- **Systems:** paint and collision generation are yours. No engine tile system was named.
- **Schedule:** generation on `Startup` or a state enter. Check the docs for a streaming API before writing one.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| TileSet atlas | No atlas type on the sprite page. Check that page before assuming one. |
| TileMap layer | A set of entities or a resource grid. No TileMap component. |
| Autotile | Your rule table. Unverified as an engine feature. |

## Scope

- No tilemap feature appears in the 0.20.0 feature list that was opened.
- No tilemap module appears in the module list.
- No third-party tile crate was chosen.

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

- No Godot TileMap or TileSet types. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No named tilemap crate as the chosen solution. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

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
- [bevy::sprite](https://docs.rs/bevy/latest/bevy/sprite/index.html) - `Sprite` only. Not a tile map.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-procedural-generation](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-procedural-generation/SKILL.md) - Seeded layouts.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md) - Map resource.

#### Complements
- [godot-tilemap-mastery](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-tilemap-mastery/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
