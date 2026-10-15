---
name: bevy-game-loop-time-trial
description: "Run a Bevy 0.20 time trial as ECS data. Use when a race clock, split gates, and a finish line share one resource and must be chained, while movement steps on FixedUpdate. Keywords: Bevy, time trial, RaceClock, SplitGate, FixedUpdate, chain."
---

# Bevy time-trial loop

## When to use

Load this when a run records elapsed time, splits, or a finish line.

## ECS shape

- **Components:** a racer marker and a finish volume.
- **Resources:** the race clock, split list, and best time live on one resource.
- **Systems:** tick the clock, record a split, then test the finish line, in that order with `.chain()`.
- **Messages:** one-shot facts (hit, pickup, quest advance) go through bevy-events-messaging. This file does not add a new event type name.

```toml
[package]
name = "time-trial"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = "0.20"
```

The race clock is one resource. Three systems write it, so they share one chain.

```rust
#[derive(Resource)]
struct RaceClock {
    elapsed: f32,
    splits: Vec<f32>,
    finished: bool,
    best: f32,
}

#[derive(Component)]
struct Racer;

#[derive(Component)]
struct FinishLine;

fn spawn_course(mut commands: Commands) {
    commands.insert_resource(RaceClock {
        elapsed: 0.0,
        splits: Vec::new(),
        finished: false,
        best: f32::MAX,
    });
    commands.spawn((Racer, Transform::from_xyz(0.0, 0.0, 0.0)));
    commands.spawn((FinishLine, Transform::from_xyz(10.0, 0.0, 0.0)));
    commands.spawn(SplitGate {
        at_x: 5.0,
        taken: false,
    });
}

fn tick_race(time: Res<Time>, mut clock: ResMut<RaceClock>) {
    if !clock.finished {
        clock.elapsed += time.delta_secs();
    }
}

#[derive(Component)]
struct SplitGate {
    at_x: f32,
    taken: bool,
}

fn record_split(
    mut clock: ResMut<RaceClock>,
    racers: Query<&Transform, With<Racer>>,
    mut gates: Query<&mut SplitGate>,
) {
    if clock.finished {
        return;
    }
    let Some(racer) = racers.iter().next() else {
        return;
    };
    for mut gate in &mut gates {
        if !gate.taken && racer.translation.x >= gate.at_x {
            gate.taken = true;
            let elapsed = clock.elapsed;
            clock.splits.push(elapsed);
        }
    }
}

fn cross_finish(
    mut clock: ResMut<RaceClock>,
    racers: Query<&Transform, With<Racer>>,
    lines: Query<&Transform, With<FinishLine>>,
) {
    if clock.finished {
        return;
    }
    let Some(racer) = racers.iter().next() else {
        return;
    };
    let Some(line) = lines.iter().next() else {
        return;
    };
    if racer.translation.x >= line.translation.x {
        clock.finished = true;
        if clock.elapsed < clock.best {
            clock.best = clock.elapsed;
        }
    }
}

pub struct TimeTrialPlugin;

impl Plugin for TimeTrialPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Startup, spawn_course).add_systems(
            Update,
            (tick_race, record_split, cross_finish).chain(),
        );
    }
}
```

A fixed step moves the racer. It does not own the race clock.

```rust
#[derive(Component)]
struct Racer;

fn drive(time: Res<Time<Fixed>>, mut racers: Query<&mut Transform, With<Racer>>) {
    let step = time.delta_secs() * 8.0;
    for mut transform in &mut racers {
        transform.translation.x += step;
    }
}

pub struct DrivePlugin;

impl Plugin for DrivePlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(FixedUpdate, drive);
    }
}
```

## Race data

| Need | Bevy idiom |
| --- | --- |
| Race clock | Elapsed on a resource. The fixed clock is a stepper, not a race format. |
| Split | Your own list on that resource, written when the racer passes a `SplitGate`. |
| Finish | A `finished` flag on that resource. |

## Scope

- Race timer, split, and ghost data are yours to build as components.
- Ghost replay belongs on bevy-save-load.

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

Load [references/ecs-ownership.md](game-loop-time-trial-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No signal bus for splits or the finish. WHY: the clock resource is shared state; one-shot notices belong in bevy-events-messaging.
- No node types in Bevy code. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Official links stay on the unversioned learn pages.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Countdown and finish.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md) - Tables and definitions.
- [bevy-events-messaging](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-events-messaging/SKILL.md) - One-shot facts.

#### Complements
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Mode flags.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
