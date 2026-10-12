---
name: bevy-procedural-generation
description: "Docs-first stub for Bevy procedural generation. Godot counterpart: godot-procedural-generation. Not a full port. Keywords: Bevy, procedural, seed, dungeon, terrain, ECS, gaps."
---

# Bevy procedural generation (docs-first stub)

Not a full port. Seeded layout is your data and systems. No noise crate, tile API, or worker-pool API was opened.

## When to use

Load this when a level, loot table, or map should be reproducible from a seed, and you need the ECS shape plus the gap list. Spawning the finished layout uses `Commands` on `Startup` or a later schedule you already use. Saving the seed is a bevy-save-load concern, and that skill still has no save format.

## ECS shape

- **Components:** cell, room, or prop facts you define. The ECS page shows plain `Component` structs and `commands.spawn`.
- **Resources:** one seed and a generator state you own as a `Resource` (see bevy-data-resources). Do not invent a Bevy RNG type.
- **Systems:** fill the resource on `Startup`, then spawn entities from that data. Use `.chain()` so spawn sees the finished grid.
- **Schedule:** `Startup` for a one-shot map. A streaming map is a later system on `Update`. No background-thread API was opened, so generation in this stub stays on the main schedules.

## Godot idea to Bevy idiom

| Idea | Bevy idiom (idea only) |
| --- | --- |
| Seeded run | A `Resource` holding a seed you define |
| Chunk or dungeon grid | Your components, spawned with `Commands` |
| Noise, BSP, walk, collapse | Algorithm names from the Godot skill are ideas only. No Bevy function was opened |
| Tile write | No tile API here. Wait for a later tile skill |
| Nav bake after generation | Gap on bevy-navigation |

## Gaps

- No noise, RNG, or constraint-solver module was opened on docs.rs `bevy` `latest`.
- Worker threads and off-main-thread spawn were not opened. Do not invent a pool type.
- The assets catalog was not used to pick a generation plugin.
- Large-grid batching and navigation rebake are unverified.


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

- No Godot noise, tile, or thread-pool types. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No invented noise, wave-function, or chunk APIs. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No named third-party generation crate as the chosen tool. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No Creation Station content. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No umbrella skill over Godot and Bevy. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- Do not mark this row `ported`. It is `docs_mapped`. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.

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
- [bevy-master](../SKILL.md) - ECS ownership.
- [bevy-data-resources](data-resources.md) - `Resource` versus `Component`.
- [bevy-ecs-composition](ecs-composition.md) - Spawn tuples and `.chain()`.

#### Complements
- [bevy-asset-scenes](asset-scenes.md) - Spawn a scene asset. Not a generator.
- [bevy-save-load](save-load.md) - Seed persistence is still a format gap.
- [bevy-navigation](ai-navigation.md) - No bake after a generated map.
- [godot-procedural-generation](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-procedural-generation/SKILL.md) - Godot counterpart. Source idea only.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](../SKILL.md) - Bevy router.
