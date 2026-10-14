---
name: bevy-project-foundations
description: "Bevy ECS skill for a Bevy Rust project layout. Keywords: Bevy, Cargo, features, project layout."
---

# Bevy project foundations

## When to use

Load this when a new Bevy app needs a crate, a pin, and a place for feature code before gameplay systems exist. Folder names below are layout habits. They are not engine types.

## ECS shape

- **Crate:** Getting Started says start with `cargo init` or `cargo new my_project`, then `cargo add bevy`. The same page's `Cargo.toml` sample still shows `bevy = "0.19"`. The library pin on bevy-master is **0.20.0**.
- **Features:** The `bevy` 0.20.0 crate page documents profiles (`default`, `2d`, `3d`, `ui`) and `default-features = false` when you want a smaller set. One sample on that page still shows `version = "0.18"`. That sample is not the pin.
- **App shell:** `App::new().run()` (Apps page). `use bevy::prelude::*` brings in the guide's essentials. Plugins, systems, and resources are added on that `App`.
- **Code layout:** Split by feature in ordinary Rust modules if the crate grows. These pages do not define a required directory tree.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| New project | `cargo new` plus the `bevy` dependency |
| Engine module toggles | Cargo features and profiles on the `bevy` crate |
| Feature folders | Rust modules you choose. Not a scene tree |
| Editor project file | Check the docs before adding a project manifest beside `Cargo.toml`. |

## Scope

- Getting Started still shows `bevy = "0.19"` and a `v0.19.0` checkout example. Pin **0.20.0** from crates.io and docs.rs, not from that snippet.
- OS window, audio, and input dependencies are mentioned as a Setup page. Check that page for package names before writing them.
- Workspace members, feature-folder enforcement, and naming linters are not on these pages.

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

- No Godot project types, scenes, or autoloads in this crate. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented Cargo features beyond the profiles and collections on docs.rs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No third-party crates. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/)  -  Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/)  -  Profiles, collections, and Cargo features (0.20.0).
- [Getting started](https://bevy.org/learn/quick-start/getting-started/)  -  `cargo new` / `cargo add bevy`. The version snippet is stale.
- [Apps](https://bevy.org/learn/quick-start/getting-started/apps/)  -  `App::new()`, `World`, and `Schedule`.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Library pin and which Bevy skill to load next.

#### Complements
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md)  -  Entities, components, and systems after the crate exists.
- [godot-project-foundations](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-project-foundations/SKILL.md)  -  Equivalent Godot skill. Do not import Godot types.

#### Downstream / consumers
- [bevy-app-resources](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-app-resources/SKILL.md)  -  App-wide resources once the `App` exists.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Bevy router.
