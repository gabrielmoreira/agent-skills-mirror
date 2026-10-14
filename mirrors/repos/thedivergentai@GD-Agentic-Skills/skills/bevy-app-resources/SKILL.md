---
name: bevy-app-resources
description: "Bevy ECS skill for app-wide resources and schedules. Keywords: Bevy, Resource, App, Schedule, Plugin."
---

# Bevy app resources

## When to use

Load this when data or logic must exist for the whole app: one clock, one ruleset, startup spawn, or an ordered pair of systems. Pair with bevy-data-resources for the component-versus-resource split.

## ECS shape

- **App.** The Apps page: an `App` contains a `World` and the outer loop. It initializes resources (one copy), adds systems to a `Schedule`, and imports other `App` changes through plugins.
- **Resources.** `Resource`, `Res`, `ResMut`, and `insert_resource` (Resources page). `Time` arrives from `add_plugins(DefaultPlugins)`.
- **Plugins.** The Resources page implements `Plugin` and inserts the resource inside `build`. `DefaultPlugins` is the plugin set that adds `Time`. Name only the plugins this page documents.
- **Schedules.** `add_systems(Startup, ...)` runs once before other systems. `add_systems(Update, ...)` is the repeating schedule in the ECS page. `.chain()` orders systems that must see each other's writes. `bevy::ecs::message` names `FixedUpdate` only as the schedule after which `signal_message_update_system` runs. Fixed-timestep clock types stay in bevy-character-movement.
- **States.** App-wide modes are `bevy::state`, not a global node. See bevy-state-machines.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Autoload singleton | A `Resource` inserted on the `App` |
| Global script that ticks | A system on `Update` (or a chained pair) |
| Boot setup | A `Startup` system or `insert_resource` in a `Plugin` |
| Cross-scene bus | A message or event. See bevy-events-messaging. Not a persistent node |

## Scope

- Check the plugins page for dependency order and groups before writing them.
- Sub-apps are named on the state module (`SubApp`). Check that module before writing sub-app setup.
- Save-game resources and settings files are yours to build. `bevy_settings` is a feature name on the crate page. Check that page before treating it as a settings API.

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

- No autoload, singleton node, or signal bus. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No Godot types. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented plugin lists beyond `DefaultPlugins` and the `Plugin` trait the Resources page uses. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No third-party crates. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

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
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  No autoload layer on top of the schedule.
- [bevy-project-foundations](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-project-foundations/SKILL.md)  -  Crate and `App::new()`.

#### Complements
- [bevy-data-resources](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md)  -  When data is a component instead of a resource.
- [bevy-state-machines](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md)  -  App-wide `States` instead of a global mode flag on a node.
- [godot-autoload-architecture](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-autoload-architecture/SKILL.md)  -  Equivalent Godot skill. Do not import Godot types.

#### Downstream / consumers
- Save, audio, and scene skills cover persistence, playback, and scene spawn.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Bevy router.
