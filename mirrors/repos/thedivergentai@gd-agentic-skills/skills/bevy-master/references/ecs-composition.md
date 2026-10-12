---
name: bevy-ecs-composition
description: "Docs-first stub for Bevy entity composition. Godot counterpart: godot-composition. Not a full port. Keywords: Bevy, ECS, Component, Query, systems."
---

# Bevy ECS composition (docs-first stub)

Not a full port. Composition here is entities, components, and systems. It is not a node tree.

## When to use

Load this when gameplay data should be split across small components and systems, instead of one type that owns everything. The Quick Start ECS page is the source for the names below.

## ECS shape

- **Components** are Rust structs that derive `Component`. The ECS page splits `Person` and `Name` so more than one kind of entity can carry a name.
- **Entities** are spawned with `Commands` in a `Startup` system. The page spawns a tuple of components: `commands.spawn((Person, Name(...)))`.
- **Systems** are functions. `Query<&Name, With<Person>>` reads names on entities that also have `Person`. `Query<&mut Name, With<Person>>` writes. Register with `add_systems`.
- **Schedule:** `Startup` runs once. `Update` runs afterward. Systems run in parallel unless you call `.chain()`. The page chains `update_people` before `greet_people` and leaves an unrelated system outside the chain.

A `Bundle` trait page was not opened. Use the tuple spawn the ECS page shows. Do not invent a bundle macro.

## Godot idea to Bevy idiom

| Idea | Bevy idiom (idea only) |
| --- | --- |
| Has-a parts on one object | Several `Component` structs on one entity |
| Behavior script | A system function over a `Query` |
| Spawn at start | `Commands` in a `Startup` system |
| Ordered steps | `.chain()` on the systems that depend on each other |
| Parent/child scene tree | Not opened. Do not invent a hierarchy API |

## Gaps

- Parent-child hierarchy, required-component derives, and bundle helper traits were not opened.
- Change detection and system sets were not opened. Order that matters uses `.chain()` only.
- Editor composition and Control-tree apps stay on the Godot composition-apps skill (`n_a_godot_only`).


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

- No Godot node, scene, or component-script types. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No `Bundle` API that this file did not open. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No third-party crates. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No Creation Station content. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No umbrella skill over Godot and Bevy. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- Do not mark this row `ported`. It is `docs_mapped`. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/)  -  Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/)  -  Unversioned API index.
- [Quick Start: ECS](https://bevy.org/learn/quick-start/getting-started/ecs/)  -  `Component`, `Query`, `With`, `Commands`, `Startup`, `Update`, and `.chain()`.
- [Apps](https://bevy.org/learn/quick-start/getting-started/apps/)  -  `App` holds the `World` and the `Schedule`.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch.

### Related Skills

#### Prerequisites
- [bevy-master](../SKILL.md)  -  Who owns which piece of state.
- [bevy-project-foundations](project-foundations.md)  -  Crate and `App` shell.

#### Complements
- [bevy-data-resources](data-resources.md)  -  App-wide data that should not be a component.
- [bevy-events-messaging](events-messaging.md)  -  Cross-system notices that are not a shared component.
- [godot-composition](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-composition/SKILL.md)  -  Godot counterpart. Source idea only. Do not import Godot types.

#### Downstream / consumers
- [bevy-character-movement](character-movement.md)  -  Movement components and systems on the fixed timestep.

#### Master
- [bevy-master](../SKILL.md)  -  Bevy router.
