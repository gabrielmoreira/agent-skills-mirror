---
name: bevy-app-resources
description: "Docs-first stub for Bevy app-wide resources and schedules. Godot counterpart: godot-autoload-architecture. Not a full port. Keywords: Bevy, Resource, App, Schedule, Plugin."
---

# Bevy app resources (docs-first stub)

Not a full port. App-wide data is a `Resource` on the `World`. There is no autoload and no singleton node.

## When to use

Load this when data or logic must exist for the whole app: one clock, one ruleset, startup spawn, or an ordered pair of systems. Pair with bevy-data-resources for the component-versus-resource split.

## ECS shape

- **App.** The Apps page: an `App` contains a `World` and the outer loop. It initializes resources (one copy), adds systems to a `Schedule`, and imports other `App` changes through plugins.
- **Resources.** `Resource`, `Res`, `ResMut`, and `insert_resource` (Resources page). `Time` arrives from `add_plugins(DefaultPlugins)`.
- **Plugins.** The Resources page implements `Plugin` and inserts the resource inside `build`. `DefaultPlugins` is the plugin set that adds `Time`. Do not add further plugin names in this stub.
- **Schedules.** `add_systems(Startup, ...)` runs once before other systems. `add_systems(Update, ...)` is the repeating schedule in the ECS page. `.chain()` orders systems that must see each other's writes. `bevy::ecs::message` names `FixedUpdate` only as the schedule after which `signal_message_update_system` runs. Fixed-timestep clock types stay in bevy-character-movement.
- **States.** App-wide modes are `bevy::state`, not a global node. See bevy-state-machines.

## Godot idea to Bevy idiom

| Idea | Bevy idiom (idea only) |
| --- | --- |
| Autoload singleton | A `Resource` inserted on the `App` |
| Global script that ticks | A system on `Update` (or a chained pair) |
| Boot setup | A `Startup` system or `insert_resource` in a `Plugin` |
| Cross-scene bus | A message or event. See bevy-events-messaging. Not a persistent node |

## Gaps

- Plugin dependency order and groups were not opened.
- Sub-apps were named on the state module (`SubApp`) and not opened here.
- Save-game resources and settings files were not opened (`bevy_settings` is a feature name on the crate page only).


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

- No autoload, singleton node, or signal bus. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No Godot types. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No invented plugin lists beyond `DefaultPlugins` and the `Plugin` trait the Resources page uses. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No third-party crates. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No Creation Station content. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No umbrella skill over Godot and Bevy. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- Do not mark this row `ported`. It is `docs_mapped`. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/)  -  Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/)  -  Unversioned API index. `default_app` includes `bevy_state` and `bevy_log`.
- [Apps](https://bevy.org/learn/quick-start/getting-started/apps/)  -  `App`, `World`, resources, `Schedule`, plugins.
- [Resources](https://bevy.org/learn/quick-start/getting-started/resources/)  -  `Resource`, `insert_resource`, `Plugin::build`, `DefaultPlugins`, `Time`.
- [Quick Start: ECS](https://bevy.org/learn/quick-start/getting-started/ecs/)  -  `Startup`, `Update`, `add_systems`, `.chain()`.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch.

### Related Skills

#### Prerequisites
- [bevy-master](../SKILL.md)  -  No autoload layer on top of the schedule.
- [bevy-project-foundations](project-foundations.md)  -  Crate and `App::new()`.

#### Complements
- [bevy-data-resources](data-resources.md)  -  When data is a component instead of a resource.
- [bevy-state-machines](state-machines.md)  -  App-wide `States` instead of a global mode flag on a node.
- [godot-autoload-architecture](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-autoload-architecture/SKILL.md)  -  Godot counterpart. Source idea only. Do not import Godot types.

#### Downstream / consumers
- None yet. Save, audio, and scene skills are not ported.

#### Master
- [bevy-master](../SKILL.md)  -  Bevy router.
