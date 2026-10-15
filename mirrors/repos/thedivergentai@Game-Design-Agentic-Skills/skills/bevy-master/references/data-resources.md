---
name: bevy-data-resources
description: "Place Bevy 0.20 gameplay data on a Component or a Resource. Use when choosing Query versus Res/ResMut, insert_resource, Time and Timer, or a RON/asset handle stored once for the app. Keywords: Bevy, Resource, Res, ResMut, Component, Timer, AssetServer."
---

# Bevy data resources

## When to use

Load this when you are deciding where a piece of data lives: on many entities, or once for the whole app. The Resources page and the ECS page are the source for the names below.

## ECS shape

- **Components** are for data you query across entities (`Component`, `Query`). Use them when many things carry the same kind of fields.
- **Resources** are globally unique data (`Resource`). The Resources page names elapsed time, asset collections, and renderers as examples. Access them with `Res<T>` (read) and `ResMut<T>` (write).
- **Insert.** `insert_resource` places a resource on the `App`. The page's sample derives `Resource` on `GreetTimer(Timer)` and inserts `Timer::from_seconds(2.0, TimerMode::Repeating)`.
- **Time.** `Time` is inserted by `add_plugins(DefaultPlugins)`. `time.delta()` is the elapsed time since the last update. `Timer::tick` and `just_finished` are the page's timer methods.
- **Schedule:** The sample reads `Res<Time>` and `ResMut<GreetTimer>` inside an `Update` system. Startup versus update is on the ECS page.

A resource can hold asset handles loaded through `AssetServer`. The handles are data; the loader stays on the asset server.

## Where data lives

| Need | Bevy idiom |
| --- | --- |
| Data on one gameplay thing | A `Component` |
| One copy for the whole app | A `Resource` inserted with `insert_resource` |
| Shared clock | `Time` from `DefaultPlugins`, or your own `Resource` |
| Authored data file | `serde` plus `ron::from_str` into a `Resource`, or `Handle<Mesh>` from `AssetServer` |

## Scope

- Handles, RON tables, and plugin `insert_resource` calls are in the examples below.
- Per-entity data files and save blobs are out of scope. See bevy-save-load.

```toml
[package]
name = "data-resources"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = "0.20"
serde = { version = "1", features = ["derive"] }
ron = "0.10"
```

One greet timer resource, ticked from `Time` on `Update`.

```rust
#[derive(Resource)]
struct GreetTimer(Timer);

fn greet(time: Res<Time>, mut timer: ResMut<GreetTimer>) {
    timer.0.tick(time.delta());
    if timer.0.just_finished() {
        let _ready = true;
    }
}

pub struct GreetPlugin;

impl Plugin for GreetPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(GreetTimer(Timer::from_seconds(2.0, TimerMode::Repeating)))
            .add_systems(Update, greet);
    }
}

fn main() {
    App::new().add_plugins(DefaultPlugins).add_plugins(GreetPlugin).run();
}
```

Per-entity speed stays a component. The shared multiplier stays a resource.

```rust
#[derive(Component)]
struct BaseSpeed(f32);

#[derive(Component)]
struct Speed(f32);

#[derive(Resource)]
struct SpeedScale(f32);

fn scale_speed(scale: Res<SpeedScale>, mut bodies: Query<(&BaseSpeed, &mut Speed)>) {
    for (base, mut speed) in &mut bodies {
        speed.0 = base.0 * scale.0;
    }
}

pub struct SpeedPlugin;

impl Plugin for SpeedPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(SpeedScale(1.0))
            .add_systems(Startup, |mut commands: Commands| {
                commands.spawn((BaseSpeed(4.0), Speed(4.0)));
            })
            .add_systems(Update, scale_speed);
    }
}
```

Load a scene handle into a resource, and parse a RON table into another.

```rust
use serde::Deserialize;

#[derive(Resource)]
struct LevelAssets {
    mesh: Handle<Mesh>,
}

#[derive(Deserialize, Resource)]
struct Tuning {
    speed: f32,
}

fn load_level(mut commands: Commands, assets: Res<AssetServer>) {
    commands.insert_resource(LevelAssets {
        mesh: assets.load("models/gate.glb#Mesh0/Primitive0"),
    });
}

fn tuning_from_ron(raw: &str) -> Result<Tuning, ron::error::SpannedError> {
    ron::from_str(raw)
}
```

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
| Per-entity data | `Component` + `Query` | One struct that stores every entity's fields |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Read the linked Bevy pages | A made-up crate or API |

Load [references/ecs-ownership.md](data-resources-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No packed scene or node-script stand-ins for `Resource`. WHY: app-wide data is a `Resource` inserted on the `App` or `Commands`.
- No invented asset or serialization APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No third-party crates. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Official links stay on the unversioned learn pages.

### Official Documentation
- [Resources](https://bevy.org/learn/quick-start/getting-started/resources/)  -  `Resource`, `Res`, `ResMut`, `insert_resource`, `Time`, `Timer`, `TimerMode`.
- [Quick Start: ECS](https://bevy.org/learn/quick-start/getting-started/ecs/)  -  `Component` and `Query` for per-entity data.
- [Apps](https://bevy.org/learn/quick-start/getting-started/apps/)  -  Resources as the single copy of global data in the `World`.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Component versus resource ownership.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md)  -  How components are spawned and queried.

#### Complements
- [bevy-app-resources](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-app-resources/SKILL.md)  -  Schedules and plugins around those resources.

#### Downstream / consumers
- Inventory, stats, and save skills cover items, attributes, and persistence.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Bevy router.
