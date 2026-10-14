---
name: bevy-performance
description: "Bevy ECS skill for runtime cost. Keywords: Bevy, parallel systems, chain, FrameTimeDiagnosticsPlugin, Handles."
---

# Bevy performance

## When to use

Load this when a system is slow or assets stay in memory. Pair it with `bevy-debugging-profiling` for the counters. Sources: the Quick Start ECS page, `bevy::diagnostic`, and the `bevy::asset` index (docs.rs `latest`, 0.20.0).

## ECS shape

- **Systems:** the ECS page says systems run in parallel when they can. `.chain()` forces order and removes that parallelism for the chained set. Put `.chain()` only on the systems that must see each other's writes.
- **Fixed step:** movement and other gameplay that should not follow the render frame belong on `Fixed` / `FixedMain` (`bevy::time`), not on every `Update`.
- **Measures:** `FrameTimeDiagnosticsPlugin` records frame time, fps, and frame count. `EntityCountDiagnosticsPlugin` records entity count. `SystemInformationDiagnosticsPlugin` records process `cpu_usage` and `mem_usage`. `LogDiagnosticsPlugin` prints them. No target milliseconds are stated on those pages.
- **Memory:** `Handle` is reference counted. A strong handle kept in a long-lived `Resource` keeps the asset. The last strong drop removes it from `Assets<T>`. `Assets::add` does not deduplicate procedural assets. `AssetServer::load` reuses a handle while one remains.
- **Schedule:** diagnostics plugins are added on the `App` after `DefaultPlugins`. Do not invent a budget resource.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Stop scripts from fighting | Let independent systems run in parallel; `.chain()` only for real order |
| Physics-ish tick vs render | `Fixed` versus `Update` |
| Watch frame time | `FrameTimeDiagnosticsPlugin` |
| Unload unused art | Drop the last strong `Handle` |

## Scope

- Check the render docs before naming frustum culling, LOD, or draw-call batching knobs.
- No entity count cap or frame-time budget number is on these pages.
- Check the ECS docs, and bevy-ecs-composition, for change detection as a performance tool before writing it.

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

- No Godot servers, visibility notifiers, or profiler monitors. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No culling or batching API this file did not open. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No third-party profiler crates. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/)  -  Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/)  -  Unversioned API index.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/)  -  Parallel systems and `.chain()`.
- [bevy::time](https://docs.rs/bevy/latest/bevy/time/index.html)  -  `Fixed` and `FixedMain`.
- [bevy::diagnostic](https://docs.rs/bevy/latest/bevy/diagnostic/index.html)  -  Frame time, entity count, system info.
- [bevy::asset](https://docs.rs/bevy/latest/bevy/asset/index.html)  -  Handle lifetimes and `Assets::add`.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Who owns which piece of state.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md)  -  Systems and `.chain()`.
- [bevy-debugging-profiling](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-debugging-profiling/SKILL.md)  -  How those diagnostics are plugged in.

#### Complements
- [bevy-asset-scenes](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-asset-scenes/SKILL.md)  -  When handles are loaded and dropped.
- [bevy-character-movement](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-character-movement/SKILL.md)  -  Work that belongs on the fixed timestep.
- [godot-performance-optimization](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-performance-optimization/SKILL.md)  -  Equivalent Godot skill.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Bevy router.
