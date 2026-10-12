---
name: bevy-events-messaging
description: "Docs-first stub for Bevy messages and observers. Godot counterpart: godot-signal-architecture. Not a full port. Keywords: Bevy, Message, Event, Observer."
---

# Bevy events and messaging (docs-first stub)

Not a full port. Two opened mechanisms: buffered messages, and events that run observers immediately. Neither is a signal bus.

## When to use

Load this when one system should notice that something happened without storing that fact on every entity. Pick the mechanism from the pages below. Do not invent a third channel.

## ECS shape

- **Messages (pull).** `bevy::ecs::message` 0.20.0 defines the `Message` trait as a buffered message for pull-based handling. `MessageWriter` writes. `MessageReader` reads and tracks what it already saw. `Messages` holds what occurred within the last two `Messages::update` calls. `message_update_system` calls `Messages::update` on registered messages. `signal_message_update_system` signals that update after `FixedUpdate` systems. Registration helpers on `App` were not opened. Do not invent an `add_message` name.
- **Events (push).** The `Event` trait page: derive `Event`, add an observer, trigger. The sample uses `World::trigger` and `world.add_observer` with `On<Speak>`. `Commands::trigger` is also named. Observers run immediately inside the trigger call. `Event::Trigger` defaults to `GlobalTrigger` for derived events.
- **Observers.** `bevy::ecs::observer`: an `Observer` is a component that holds a system. `On` is the system parameter that processes the event. `EntityEvent` is the page's pointer for events that target one entity. The entity-event trait page was not opened.
- **State transitions.** `bevy::state` documents `StateTransitionEvent<S>` when state `S` changes. That type lives with states. See bevy-state-machines.

## Godot idea to Bevy idiom

| Idea | Bevy idiom (idea only) |
| --- | --- |
| Something happened; readers poll later | A `Message` plus `MessageWriter` / `MessageReader` |
| Something happened; listeners run now | An `Event` plus an `Observer` (`On<...>`) and `trigger` |
| Notice on one entity | `EntityEvent` (trait page not opened; do not invent methods) |
| Global signal singleton | Not this. Use a message type or a global event |

## Gaps

- `App` methods that register a message type were not opened.
- `EntityEvent` methods, entity-targeted trigger helpers, and observer run-condition helpers were not opened beyond the module index names.
- Ordering between `message_update_system` and gameplay systems was not opened beyond the `FixedUpdate` signal function name.


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

- No Godot signal types or a signal bus autoload. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No invented message-registration or trigger methods. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No third-party crates. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No Creation Station content. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No umbrella skill over Godot and Bevy. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- Do not mark this row `ported`. It is `docs_mapped`. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/)  -  Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/)  -  Unversioned API index.
- [bevy::ecs::message](https://docs.rs/bevy/latest/bevy/ecs/message/index.html)  -  `Message`, `MessageWriter`, `MessageReader`, `Messages`, `message_update_system`.
- [Event](https://docs.rs/bevy/latest/bevy/ecs/event/trait.Event.html)  -  `Event`, `On`, `World::trigger`, `Commands::trigger`, `add_observer`.
- [bevy::ecs::observer](https://docs.rs/bevy/latest/bevy/ecs/observer/index.html)  -  `Observer` and `On`.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch.

### Related Skills

#### Prerequisites
- [bevy-master](../SKILL.md)  -  ECS ownership before adding a notice channel.
- [bevy-ecs-composition](ecs-composition.md)  -  Systems that write or read the notice.

#### Complements
- [bevy-state-machines](state-machines.md)  -  `StateTransitionEvent` for app-wide state changes.
- [godot-signal-architecture](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-signal-architecture/SKILL.md)  -  Godot counterpart. Source idea only. Do not import Godot types.

#### Downstream / consumers
- None yet. Gameplay skills are not ported.

#### Master
- [bevy-master](../SKILL.md)  -  Bevy router.
