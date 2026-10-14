---
name: bevy-asset-scenes
description: "Bevy ECS skill for assets and scene spawning. Keywords: Bevy, AssetServer, Handle, Scene, bsn, spawn_scene."
---

# Bevy asset scenes

## When to use

Load this when content comes from disk or a scene description should spawn entities. `bevy::asset` and `bevy::scene` on docs.rs `latest` (0.20.0) are the sources.

## ECS shape

- **Assets:** `AssetServer` is the resource that loads from disk. `AssetServer::load` returns a `Handle` and does not reload while a strong handle still exists. Loaded data lives in `Assets<T>`. `AssetServer::is_loaded_with_dependencies` is true when the asset and its dependencies are ready. `LoadState` is the status type named on that page.
- **Handles:** strong handles are reference counted. Dropping the last strong handle removes the asset. Weak handles do not keep it alive. `Assets::add` inserts a procedural asset and does not deduplicate.
- **Hot reload:** the `file_watcher` Cargo feature, and `AssetPlugin`'s `watch_for_changes_override` field, are the toggles named on the asset index.
- **Scenes:** `bevy::scene` describes a `Scene` (entity, components, children, assets), built with the `bsn!` macro. `World::spawn_scene` and `Commands::spawn_scene` spawn immediately and error if asset dependencies are not loaded. `World::queue_spawn_scene` and `Commands::queue_spawn_scene` wait, then spawn in the `SpawnScene` schedule between `Update` and `PostUpdate`.
- **Hierarchy in a scene:** `Children [ ... ]` inside `bsn!`. Separate sibling entities with `--`. `#Name` assigns a `Name` inside that macro's scope.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Load a file | `AssetServer::load` → `Handle` |
| Wait until ready | `is_loaded_with_dependencies` before a state change |
| Instance a packed scene | `spawn_scene` or `queue_spawn_scene` around a `Scene` |
| Child nodes in that scene | `Children` inside `bsn!` |
| Change one entity's mesh | Swap the `Handle` on the component that stores it |

## Scope

- `.bsn` asset files are described as future on the scene page. Do not invent a file loader for them.
- A `DynamicScene` type was not on docs.rs `latest` (the struct URL 404'd on 2026-10-11). Do not cite it.
- Scene change as "free the old level, then spawn the next" is a design note. No level-switch API was opened.
- Custom `AssetLoader` registration is named as `App::register_asset_loader`. Check the asset docs for a worked example before writing one.

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

- No Godot packed-scene, node, or resource-loader types. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No scene format this file did not open. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No third-party scene crates. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/)  -  Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/)  -  Unversioned API index.
- [bevy::asset](https://docs.rs/bevy/latest/bevy/asset/index.html)  -  `AssetServer`, `Handle`, `Assets<T>`, load state, hot reload.
- [bevy::scene](https://docs.rs/bevy/latest/bevy/scene/index.html)  -  `Scene`, `bsn!`, `spawn_scene`, `queue_spawn_scene`, `SpawnScene`.
- [Assets](https://bevy.org/assets/)  -  Official asset catalog.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Who owns which piece of state.
- [bevy-project-foundations](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-project-foundations/SKILL.md)  -  Cargo features, including asset watcher flags.
- [bevy-state-machines](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md)  -  The asset page points at app states for load gates.

#### Complements
- [bevy-audio-systems](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-audio-systems/SKILL.md)  -  Clips loaded through `AssetServer`.
- [bevy-save-load](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-save-load/SKILL.md)  -  Player saves, separate from scene spawn.
- [godot-scene-management](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-scene-management/SKILL.md)  -  Equivalent Godot skill.

#### Downstream / consumers
- [bevy-camera-systems](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-camera-systems/SKILL.md)  -  Camera entities a scene may spawn.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Bevy router.
