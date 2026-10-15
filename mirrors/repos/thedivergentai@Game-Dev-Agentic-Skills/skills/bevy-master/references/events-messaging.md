---
name: bevy-events-messaging
description: "Bevy ECS skill for messages and observers. Keywords: Bevy, Message, Event, Observer."
---

# Bevy events and messaging

## When to use

Load this when one system should notice that something happened without storing that fact on every entity. Pick the mechanism from the pages below. Do not invent a third channel.

## ECS shape

- **Messages (pull).** `Message` is a buffered message for pull-based handling. `MessageWriter` writes. `MessageReader` reads and tracks what it already saw. `Messages` holds what occurred within the last two updates. Register the type with `App::add_message`. The engine updates the buffer; gameplay systems only write and read.
- **Events (push).** Derive `Event`, add an observer, trigger. `Commands::trigger` and `World::trigger` run observers immediately inside the call. `On<E>` is the system parameter. `Event::Trigger` defaults to `GlobalTrigger` for derived events.
- **Observers.** An `Observer` is a component that holds a system. `EntityEvent` targets one entity: the event carries the `entity` field, and `On::event_target` returns it.
- **State transitions.** `StateTransitionEvent<S>` fires when state `S` changes. That type lives with states. See bevy-state-machines.

## Examples

```toml
[dependencies]
bevy = "0.20"
```

A hit is a fact other systems poll. Register the message, write it from the strike system, and read it later in the same schedule. `add_message` keeps the double-buffered queue.

```rust
#[derive(Message)]
struct Hit {
    amount: i32,
}

fn install(app: &mut App) {
    app.add_message::<Hit>()
        .add_systems(Update, (deal, apply).chain());
}

fn deal(mut hits: MessageWriter<Hit>) {
    hits.write(Hit { amount: 12 });
}

fn apply(mut hits: MessageReader<Hit>) {
    for hit in hits.read() {
        info!("hit {}", hit.amount);
    }
}
```

A shout should run listeners now. Derive `Event`, observe with `On<Shout>`, and `trigger`. The observer runs inside `trigger` before the system returns.

```rust
#[derive(Event)]
struct Shout {
    text: String,
}

fn listen(shout: On<Shout>) {
    info!("{}", shout.event().text);
}

fn setup(mut commands: Commands) {
    commands.spawn(Observer::new(listen));
    commands.trigger(Shout {
        text: "round".into(),
    });
}
```

An entity-targeted event names its target. `event_target` is that entity; the observer still runs immediately.

```rust
#[derive(EntityEvent)]
struct Stagger {
    entity: Entity,
}

fn on_stagger(hit: On<Stagger>) {
    info!("stagger {:?}", hit.event_target());
}

fn strike(mut commands: Commands, fighters: Query<Entity>) {
    for entity in &fighters {
        commands.trigger(Stagger { entity });
    }
}
```

## Scope

- Register a message with `App::add_message` before any `MessageWriter` or `MessageReader`.
- Entity-targeted triggers use `EntityEvent` and `Commands::trigger` with the `entity` field set.
- Write and read a message in the same schedule with `.chain()` so the reader sees the write before the buffer updates.

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
| Per-entity data | `Component` + `Query` | One mutable blob shared by every entity |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Read the official Bevy pages | A made-up crate or API |

Load [references/ecs-ownership.md](events-messaging-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No invented message-registration or trigger methods. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No third-party crates. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Official pages stay on the unversioned site.

### Official Documentation
- [ECS messages](https://bevy.org/learn/quick-start/getting-started/ecs/)  -  Systems, `Query`, and where a buffered notice fits beside components.
- [Observer example](https://github.com/bevyengine/bevy/blob/latest/examples/ecs/observer_propagation.rs)  -  `Event`, `EntityEvent`, `Observer`, and `trigger`.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  ECS ownership before adding a notice channel.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md)  -  Systems that write or read the notice.

#### Complements
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md)  -  `StateTransitionEvent` for app-wide state changes.

#### Downstream / consumers
- Gameplay skills cover combat, abilities, and similar loops.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Bevy router.
