---
name: bevy-save-load
description: "Docs-first stub for Bevy persistence boundaries. Godot counterpart: godot-save-load-systems. Not a full port. Keywords: Bevy, save, Resource, Scene, AssetServer, gaps."
---

# Bevy save and load (docs-first stub)

Not a full port. This file records what was opened and what was not. There is no Bevy save-slot API in the pages below.

## When to use

Load this when a design asks to persist player progress. Route asset and scene spawning to `bevy-asset-scenes`. Keep save bytes as an explicit gap until a current page names the format.

## ECS shape

- **What exists:** app-wide progress can be a `Resource` (see `bevy-data-resources`). Level content loads through `AssetServer` and may spawn with `spawn_scene` / `queue_spawn_scene` (`bevy::scene`, docs.rs `latest`, 0.20.0).
- **What was checked and rejected:** `https://docs.rs/bevy/latest/bevy/scene/struct.DynamicScene.html` returned 404 on 2026-10-11. The live scene index documents `Scene` and `bsn!`, not a save-file serializer. Do not call `DynamicScene::serialize` from this skill.
- **Schedule:** no save system is specified here. Do not invent a filesystem write inside `Update`.

## Godot idea to Bevy idiom

| Idea | Bevy idiom (idea only) |
| --- | --- |
| Resource file for designer data | An asset `Handle`, or a `Resource` you own in code |
| Packed scene instance | `Scene` spawn on `bevy-asset-scenes` |
| Player save slot | Not opened. Leave it as data you have not serialized yet |

## Gaps

- No save path, slot index, version field, or RON/JSON writer was opened on docs.rs `latest`.
- Scene spawn is not a save game. Do not treat `bsn!` as a user save.
- Wasm has no general filesystem story on the pages opened for this batch. Do not invent one.


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

- No Godot `Resource`, `FileAccess`, or config-file types. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No `DynamicScene` or scene-file writer this file's opened pages do not list. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No third-party save crates. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No Creation Station content. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No umbrella skill over Godot and Bevy. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- Do not mark this row `ported`. It is `docs_mapped` because the gap was checked against live docs. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/)  -  Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/)  -  Unversioned API index.
- [bevy::scene](https://docs.rs/bevy/latest/bevy/scene/index.html)  -  Spawn API that is not a save format. `DynamicScene` struct URL 404.
- [bevy::asset](https://docs.rs/bevy/latest/bevy/asset/index.html)  -  Disk assets, not player slots.
- [Resources](https://bevy.org/learn/quick-start/getting-started/resources/)  -  App-wide data that a future save would have to name.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch.

### Related Skills

#### Prerequisites
- [bevy-master](../SKILL.md)  -  Who owns which piece of state.
- [bevy-data-resources](data-resources.md)  -  `Resource` versus `Component`.
- [bevy-asset-scenes](asset-scenes.md)  -  Loading content. Not a save slot.

#### Complements
- [godot-save-load-systems](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-save-load-systems/SKILL.md)  -  Godot counterpart. Source idea only.

#### Downstream / consumers
- None until a save format is opened.

#### Master
- [bevy-master](../SKILL.md)  -  Bevy router.
