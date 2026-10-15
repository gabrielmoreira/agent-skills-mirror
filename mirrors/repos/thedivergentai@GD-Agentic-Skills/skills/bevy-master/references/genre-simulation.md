---
name: bevy-genre-simulation
description: "Route a Bevy 0.20 simulation. Use when hunger and jobs are components, the sim hour is one resource, and needs run after the clock step in one chain. Keywords: Bevy, Simulation, SimClock, Hunger, Job, FixedUpdate, chain, genre."
---

# Bevy Simulation (thin router)

Genre router. Domain work lives in the Bevy skills below.

## When to use

Load this for agents, resources, and a clock you step.

## ECS shape

- **Components** hold the genre's per-entity flags as plain data. This file does not name new engine types.
- **Resources** hold run-wide counters (score, wave index, seed) via bevy-data-resources.
- **Systems** read those components on `Update` or the fixed timestep from bevy-master. Order them with `.chain()` when a later system must see the result.
- **Schedule:** gameplay mode changes go through bevy-state-machines. Do not invent a genre plugin.

## Routing

- [bevy-economy-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-economy-system/SKILL.md) - Stocks.
- [bevy-ai-navigation](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ai-navigation/SKILL.md) - Agent policy.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md) - Sim tables.
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Pause.

## Scope

Needs, jobs, and the sim hour are components and one clock resource. Pause is a bool on that clock.

## Examples

```toml
[package]
name = "simulation"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = "0.20"
```

The clock is the only writer of sim hours. Hunger and food change in the next system so they see the same pause flag.

```rust
#[derive(Resource)]
struct SimClock {
    hour: f32,
    paused: bool,
}

#[derive(Component)]
struct Hunger {
    value: f32,
}

#[derive(Component)]
struct Pantry {
    food: f32,
}

fn advance_clock(time: Res<Time<Fixed>>, mut clock: ResMut<SimClock>) {
    if clock.paused {
        return;
    }
    clock.hour = (clock.hour + time.delta_secs()).rem_euclid(24.0);
}

fn eat(time: Res<Time<Fixed>>, clock: Res<SimClock>, mut agents: Query<(&mut Hunger, &mut Pantry)>) {
    if clock.paused {
        return;
    }
    let dt = time.delta_secs();
    for (mut hunger, mut pantry) in &mut agents {
        hunger.value = (hunger.value + dt * 0.15).min(1.0);
        if hunger.value > 0.5 && pantry.food > 0.0 {
            let bite = (dt * 0.4).min(pantry.food);
            pantry.food -= bite;
            hunger.value = (hunger.value - bite).max(0.0);
        }
    }
}

fn toggle_pause(keys: Res<ButtonInput<KeyCode>>, mut clock: ResMut<SimClock>) {
    if keys.just_pressed(KeyCode::Space) {
        clock.paused = !clock.paused;
    }
}

pub struct SimPlugin;

impl Plugin for SimPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(SimClock {
            hour: 8.0,
            paused: false,
        })
        .add_systems(FixedUpdate, (toggle_pause, advance_clock, eat).chain());
    }
}
```

A job is a target stock on the agent. Work transfers from a shared depot resource into that stock.

```rust
#[derive(Component)]
struct Job {
    rate: f32,
    held: f32,
    capacity: f32,
}

#[derive(Resource)]
struct Depot {
    timber: f32,
}

fn work(time: Res<Time<Fixed>>, clock: Res<SimClock>, mut depot: ResMut<Depot>, mut workers: Query<&mut Job>) {
    if clock.paused {
        return;
    }
    let dt = time.delta_secs();
    for mut job in &mut workers {
        if job.held >= job.capacity || depot.timber <= 0.0 {
            continue;
        }
        let moved = (job.rate * dt).min(depot.timber).min(job.capacity - job.held);
        depot.timber -= moved;
        job.held += moved;
    }
}

#[derive(Resource)]
struct SimClock {
    hour: f32,
    paused: bool,
}
```

Startup inserts the clock, the depot, and two agents.

```rust
#[derive(Component)]
struct Hunger {
    value: f32,
}

#[derive(Component)]
struct Pantry {
    food: f32,
}

#[derive(Component)]
struct Job {
    rate: f32,
    held: f32,
    capacity: f32,
}

#[derive(Resource)]
struct Depot {
    timber: f32,
}

#[derive(Resource)]
struct SimClock {
    hour: f32,
    paused: bool,
}

fn spawn_town(mut commands: Commands) {
    commands.insert_resource(SimClock {
        hour: 8.0,
        paused: false,
    });
    commands.insert_resource(Depot { timber: 40.0 });
    for index in 0..2 {
        commands.spawn((
            Hunger { value: 0.2 },
            Pantry { food: 3.0 + index as f32 },
            Job {
                rate: 1.5,
                held: 0.0,
                capacity: 8.0,
            },
        ));
    }
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
| Per-entity data | `Component` + `Query` | A scene-tree script |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| A stepped sim hour | `SimClock` on `FixedUpdate`, with needs on the agent | Copy the hour onto every entity each frame |

Load [references/ecs-ownership.md](genre-simulation-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No scene-tree types in Bevy code. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented genre APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- Do not pick a physics or net crate here. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Official links stay on the unversioned learn pages.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - ECS ownership and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Spawn and query shape.

#### Complements
- [bevy-economy-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-economy-system/SKILL.md) - Stocks.
- [bevy-ai-navigation](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ai-navigation/SKILL.md) - Agent policy.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md) - Sim tables.
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Pause.

#### Downstream / consumers
- None. This router does not own a second implementation.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
