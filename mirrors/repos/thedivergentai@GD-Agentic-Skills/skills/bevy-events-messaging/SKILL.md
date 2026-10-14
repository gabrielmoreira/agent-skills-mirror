---
name: bevy-events-messaging
description: "Bevy ECS skill for messages and observers. Keywords: Bevy, Message, Event, Observer."
---

# Bevy events and messaging

## When to use

Load this when one system should notice that something happened without storing that fact on every entity. Pick the mechanism from the pages below. Do not invent a third channel.

## ECS shape

- **Messages (pull).** `bevy::ecs::message` 0.20.0 defines the `Message` trait as a buffered message for pull-based handling. `MessageWriter` writes. `MessageReader` reads and tracks what it already saw. `Messages` holds what occurred within the last two `Messages::update` calls. `message_update_system` calls `Messages::update` on registered messages. `signal_message_update_system` signals that update after `FixedUpdate` systems. Check the `App` docs for message registration helpers before writing a method name.
- **Events (push).** The `Event` trait page: derive `Event`, add an observer, trigger. The sample uses `World::trigger` and `world.add_observer` with `On<Speak>`. `Commands::trigger` is also named. Observers run immediately inside the trigger call. `Event::Trigger` defaults to `GlobalTrigger` for derived events.
- **Observers.** `bevy::ecs::observer`: an `Observer` is a component that holds a system. `On` is the system parameter that processes the event. `EntityEvent` is the page's pointer for events that target one entity. Check that trait page for method names before writing them.
- **State transitions.** `bevy::state` documents `StateTransitionEvent<S>` when state `S` changes. That type lives with states. See bevy-state-machines.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Something happened; readers poll later | A `Message` plus `MessageWriter` / `MessageReader` |
| Something happened; listeners run now | An `Event` plus an `Observer` (`On<...>`) and `trigger` |
| Notice on one entity | `EntityEvent`. Check the trait page for methods before writing them. |
| Global signal singleton | Not this. Use a message type or a global event |

## Scope

- Check the `App` docs for methods that register a message type before writing them.
- Check the observer module for `EntityEvent` methods, entity-targeted trigger helpers, and observer run-condition helpers beyond the module index names.
- Check the message docs for ordering between `message_update_system` and gameplay systems beyond the `FixedUpdate` signal function name.

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

- No Godot signal types or a signal bus autoload. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented message-registration or trigger methods. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No third-party crates. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

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
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  ECS ownership before adding a notice channel.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md)  -  Systems that write or read the notice.

#### Complements
- [bevy-state-machines](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md)  -  `StateTransitionEvent` for app-wide state changes.
- [godot-signal-architecture](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-signal-architecture/SKILL.md)  -  Equivalent Godot skill. Do not import Godot types.

#### Downstream / consumers
- Gameplay skills cover combat, abilities, and similar loops.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Bevy router.
