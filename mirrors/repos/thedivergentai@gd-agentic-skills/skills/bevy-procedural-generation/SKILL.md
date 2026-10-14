---
name: bevy-procedural-generation
description: "Bevy ECS skill for procedural generation. Keywords: Bevy, procedural, seed, dungeon, terrain, ECS."
---

# Bevy procedural generation

## When to use

Load this when a level, loot table, or map should be reproducible from a seed, and you need the ECS shape. Spawning the finished layout uses `Commands` on `Startup` or a later schedule you already use. Saving the seed belongs on bevy-save-load.

## ECS shape

- **Components:** cell, room, or prop facts you define. The ECS page shows plain `Component` structs and `commands.spawn`.
- **Resources:** one seed and a generator state you own as a `Resource` (see bevy-data-resources). Do not invent a Bevy RNG type.
- **Systems:** fill the resource on `Startup`, then spawn entities from that data. Use `.chain()` so spawn sees the finished grid.
- **Schedule:** `Startup` for a one-shot map. A streaming map is a later system on `Update`. Check the docs for a background-thread API before leaving the main schedules.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Seeded run | A `Resource` holding a seed you define |
| Chunk or dungeon grid | Your components, spawned with `Commands` |
| Noise, BSP, walk, collapse | Algorithm names from the Godot skill are ideas only. Check the docs.rs crate index before treating them as Bevy functions. |
| Tile write | No tile API here. Wait for a later tile skill |
| Nav bake after generation | Nav bake after generation belongs on bevy-navigation. |

## Scope

- Check docs.rs `bevy` `latest` for a noise, RNG, or constraint-solver module before writing one.
- Check the docs for worker threads and off-main-thread spawn before writing a pool type.
- The assets catalog was not used to pick a generation plugin.
- Large-grid batching and navigation rebake are unverified.

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

- No Godot noise, tile, or thread-pool types. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented noise, wave-function, or chunk APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No named third-party generation crate as the chosen tool. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/) - Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/) - Unversioned API index. No procedural module was opened.
- [Assets](https://bevy.org/assets/) - Official asset catalog. No generation plugin was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, `Commands`, `Startup`, and `.chain()`.
- [Resources](https://bevy.org/learn/quick-start/getting-started/resources/) - App-wide seed state. API limits are on bevy-data-resources.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - ECS ownership.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md) - `Resource` versus `Component`.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Spawn tuples and `.chain()`.

#### Complements
- [bevy-asset-scenes](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-asset-scenes/SKILL.md) - Spawn a scene asset. Not a generator.
- [bevy-save-load](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-save-load/SKILL.md) - Seed persistence.
- [bevy-navigation](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-navigation/SKILL.md) - No bake after a generated map.
- [godot-procedural-generation](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-procedural-generation/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
