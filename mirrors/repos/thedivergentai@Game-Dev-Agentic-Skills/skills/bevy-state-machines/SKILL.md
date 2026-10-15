---
name: bevy-state-machines
description: "Bevy ECS skill for app states and per-entity state data. Keywords: Bevy, States, NextState, OnEnter."
---

# Bevy state machines

## When to use

Load this when the app needs a large-scale mode (paused, in a menu, loading) or when one entity needs a small mode flag. Use `bevy::state` for the first. Use a component for the second. Keep those two owners separate.

## ECS shape

- **App states.** `bevy::state`: states are app-wide finite state machines. Three types implement `States`.
  - Standard states change only by setting the `NextState<S>` resource.
  - `SubStates` also use `NextState<S>`, and are removed from the `World` when source states are not in the required state.
  - `ComputedStates` derive from other states through a `compute` method.
- **Transition schedules.** `OnEnter<S>`, `OnExit<S>`, and `OnTransition<S>` run systems on matching transitions. `StateTransitionEvent<S>` fires when state `S` changes. Run conditions: `in_state<S>` and `state_changed<S>`.
- **Entity lifetime.** `DespawnOnEnter<S>` and `DespawnOnExit<S>` despawn entities on those transitions (`state_scoped`).
- **Feature.** `bevy_state` ships in the default `bevy` app plugins. Install a state with `init_state`.
- **Per-entity mode.** Store an enum in a `Component` and branch in a system. That enum is not a `States` type.

```toml
[dependencies]
bevy = "0.20"
```

App modes are `States`. Gameplay systems use `in_state`. Pause writes `NextState`.

```rust
#[derive(States, Debug, Clone, Copy, Eq, PartialEq, Hash, Default)]
enum AppMode {
    #[default]
    Menu,
    Play,
}

fn show_menu(mut commands: Commands) {
    commands.spawn((Name::new("menu"), DespawnOnExit(AppMode::Menu)));
}

fn spawn_player(mut commands: Commands) {
    commands.spawn((Name::new("player"), Transform::default()));
}

fn request_play(keys: Res<ButtonInput<KeyCode>>, mut next: ResMut<NextState<AppMode>>) {
    if keys.just_pressed(KeyCode::Enter) {
        next.set(AppMode::Play);
    }
}

pub struct ModePlugin;

impl Plugin for ModePlugin {
    fn build(&self, app: &mut App) {
        app.init_state::<AppMode>()
            .add_systems(OnEnter(AppMode::Menu), show_menu)
            .add_systems(OnEnter(AppMode::Play), spawn_player)
            .add_systems(Update, request_play.run_if(in_state(AppMode::Menu)));
    }
}
```

A pause flag exists only while `AppMode::Play` is active. `SubStates` removes it otherwise.

```rust
#[derive(States, Debug, Clone, Copy, Eq, PartialEq, Hash, Default)]
enum AppMode {
    #[default]
    Menu,
    Play,
}

#[derive(SubStates, Debug, Clone, Copy, Eq, PartialEq, Hash, Default)]
#[source(AppMode = AppMode::Play)]
enum Session {
    #[default]
    Running,
    Paused,
}

fn toggle_pause(
    keys: Res<ButtonInput<KeyCode>>,
    session: Res<State<Session>>,
    mut next: ResMut<NextState<Session>>,
) {
    if keys.just_pressed(KeyCode::Escape) {
        let flipped = match session.get() {
            Session::Running => Session::Paused,
            Session::Paused => Session::Running,
        };
        next.set(flipped);
    }
}

fn install_pause(app: &mut App) {
    app.add_sub_state::<Session>()
        .add_systems(Update, toggle_pause.run_if(in_state(Session::Running)));
}
```

One actor's stance is a component. It does not change the app state.

```rust
#[derive(Component, Clone, Copy, PartialEq, Eq)]
enum Stance {
    Idle,
    Attack,
}

fn begin_attack(keys: Res<ButtonInput<KeyCode>>, mut actors: Query<&mut Stance>) {
    if keys.just_pressed(KeyCode::KeyF) {
        for mut stance in &mut actors {
            *stance = Stance::Attack;
        }
    }
}
```

## Choose the owner

| Need | Owner |
| --- | --- |
| App mode (menu, pause, play) | A `States` type and `NextState<S>` |
| Run logic only in one mode | `in_state` or an `OnEnter` / `OnExit` / `OnTransition` schedule |
| Child mode that exists only inside a parent mode | `SubStates` |
| Mode derived from other modes | `ComputedStates` |
| One actor's stance | An enum `Component` plus a system. Not `States` unless it is truly app-wide |

## Scope

- Install app modes with `init_state`. Install a child mode with `add_sub_state`.
- `OnEnter`, `OnExit`, and `in_state` cover the schedules shown above.
- A per-entity stance is the `Stance` component. Animation graphs belong on bevy-animation-graph.

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
| Per-entity data | `Component` + `Query` | A value that is not a component |
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

The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Quick Start: ECS](https://bevy.org/learn/quick-start/getting-started/ecs/)  -  `Component` and `Query` for a per-entity mode flag.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch. State examples live in that tree.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Schedules versus a scene tree.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md)  -  `NextState<S>` is a resource. Per-entity modes are components.

#### Complements
- [bevy-events-messaging](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-events-messaging/SKILL.md)  -  Messages and observers that are not state transitions.
- [godot-state-machine-advanced](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-state-machine-advanced/SKILL.md)  -  Equivalent Godot skill. Do not import Godot types.

#### Downstream / consumers
- [bevy-character-movement](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-character-movement/SKILL.md)  -  Actor motion. A jump or ground mode stays a component unless a mode needs `States`.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Bevy router.
