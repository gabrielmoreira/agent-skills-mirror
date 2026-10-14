---
name: bevy-state-machines
description: "Bevy ECS skill for app states and per-entity state data. Keywords: Bevy, States, NextState, OnEnter."
---

# Bevy state machines

## When to use

Load this when the app needs a large-scale mode (paused, in a menu, loading) or when one entity needs a small mode flag. Use `bevy::state` for the first. Use a component for the second. Do not merge them into one Godot-style state graph.

## ECS shape

- **App states.** `bevy::state`: states are app-wide finite state machines. Three types implement `States`.
  - Standard states change only by setting the `NextState<S>` resource.
  - `SubStates` also use `NextState<S>`, and are removed from the `World` when source states are not in the required state.
  - `ComputedStates` derive from other states through a `compute` method.
- **Transition schedules.** `OnEnter<S>`, `OnExit<S>`, and `OnTransition<S>` run systems on matching transitions. `StateTransitionEvent<S>` fires when state `S` changes. Run conditions: `in_state<S>` and `state_changed<S>`.
- **Entity lifetime.** `DespawnOnEnter<S>` and `DespawnOnExit<S>` despawn entities on those transitions (`state_scoped`).
- **Feature.** The `bevy` 0.20.0 crate page includes `bevy_state` in the `default_app` collection. The state module was opened; `App` installation method names were not. Do not invent `init_state` or similar.
- **Per-entity mode.** Store an enum in a `Component` and branch in a system (`Query` from the ECS page). No per-entity state-machine type was opened.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| App mode (menu, pause, play) | A `States` type and `NextState<S>` |
| Run logic only in one mode | `in_state` or an `OnEnter` / `OnExit` / `OnTransition` schedule |
| Child mode that exists only inside a parent mode | `SubStates` |
| Mode derived from other modes | `ComputedStates` |
| One actor's animation or combat mode | An enum `Component` plus a system. Not `States` unless it is truly app-wide |

## Scope

- Check `bevy::state::app` for state installation methods on `App` before writing them.
- The module names states, sub-states, and computed-state examples. Check those examples before writing them.
- Hierarchical per-entity graphs, transition tables, and animation state machines are yours to build. Check the state docs before assuming a built-in type.

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

- No Godot animation-tree or node state-machine types. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented `App` state-setup methods. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No third-party crates. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/)  -  Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/)  -  `bevy_state` ships inside the `default_app` collection.
- [bevy::state](https://docs.rs/bevy/latest/bevy/state/index.html)  -  `States`, `NextState`, `SubStates`, `ComputedStates`, transition schedules, `StateTransitionEvent`, `in_state`, `state_changed`, `DespawnOnEnter`, `DespawnOnExit`.
- [Quick Start: ECS](https://bevy.org/learn/quick-start/getting-started/ecs/)  -  `Component` and `Query` for a per-entity mode flag.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch. State examples live in that tree.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Schedules versus a scene tree.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md)  -  `NextState<S>` is a resource. Per-entity modes are components.

#### Complements
- [bevy-events-messaging](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-events-messaging/SKILL.md)  -  Messages and observers that are not state transitions.
- [godot-state-machine-advanced](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-state-machine-advanced/SKILL.md)  -  Equivalent Godot skill. Do not import Godot types.

#### Downstream / consumers
- [bevy-character-movement](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-character-movement/SKILL.md)  -  Actor motion. A jump or ground mode stays a component unless a mode needs `States`.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Bevy router.
