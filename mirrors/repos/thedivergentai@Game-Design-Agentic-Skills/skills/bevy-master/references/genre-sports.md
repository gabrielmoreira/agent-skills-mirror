---
name: bevy-genre-sports
description: "Thin Bevy genre router for Sports. Keywords: Bevy, Sports, genre, ECS, router."
---

# Bevy Sports (thin router)

Genre router. Domain work lives in the Bevy skills below.

## When to use

Load this for match clock, teams, and ball entities you define.

## ECS shape

- **Components** hold the genre's per-entity flags as plain data. This file does not name new engine types.
- **Resources** hold run-wide counters (score, wave index, seed) via bevy-data-resources.
- **Systems** read those components on `Update` or the fixed timestep from bevy-master. Order them with `.chain()` when a later system must see the result.
- **Schedule:** gameplay mode changes go through bevy-state-machines. Do not invent a genre plugin.

## Routing

- [bevy-game-loop-time-trial](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-game-loop-time-trial/SKILL.md) - Match clock.
- [bevy-combat-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-combat-system/SKILL.md) - Contact if the sport uses hits.
- [bevy-character-movement](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-character-movement/SKILL.md) - Athletes.
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Period state.

## Scope

Match clock, score, possession, and formation targets are components and one resource. A rigid-body ball solver stays on the physics skill once one is chosen.

## Examples

```toml
[package]
name = "sports"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = "0.20"
```

The clock and score are one resource. Period changes after the clock step in the same chain.

```rust
#[derive(Clone, Copy, PartialEq, Eq)]
enum Period {
    Kickoff,
    Playing,
    Goal,
    FullTime,
}

#[derive(Resource)]
struct Match {
    period: Period,
    seconds_left: f32,
    score_a: u32,
    score_b: u32,
}

fn tick_match(time: Res<Time<Fixed>>, mut game: ResMut<Match>) {
    if game.period != Period::Playing {
        return;
    }
    game.seconds_left = (game.seconds_left - time.delta_secs()).max(0.0);
    if game.seconds_left == 0.0 {
        game.period = Period::FullTime;
    }
}

fn score_goal(team_a: bool, game: &mut Match) {
    if team_a {
        game.score_a += 1;
    } else {
        game.score_b += 1;
    }
    game.period = Period::Goal;
}

pub struct MatchPlugin;

impl Plugin for MatchPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(Match {
            period: Period::Kickoff,
            seconds_left: 300.0,
            score_a: 0,
            score_b: 0,
        })
        .add_systems(FixedUpdate, tick_match);
    }
}
```

Athletes seek a slot. Only the presser chases the ball; the rest hold formation so the side does not bunch.

```rust
#[derive(Component)]
struct Athlete {
    speed: f32,
    presses: bool,
}

#[derive(Component)]
struct Slot {
    offset: Vec3,
}

#[derive(Component)]
struct Ball;

fn hold_formation(
    time: Res<Time<Fixed>>,
    ball: Query<&Transform, With<Ball>>,
    slots: Query<&Slot>,
    mut athletes: Query<(&Athlete, &mut Transform), Without<Ball>>,
) {
    let Ok(ball_tf) = ball.single() else {
        return;
    };
    let dt = time.delta_secs();
    for (athlete, mut transform) in &mut athletes {
        let mut target = ball_tf.translation;
        if !athlete.presses {
            if let Some(slot) = slots.iter().next() {
                target += slot.offset;
            }
        }
        let delta = target - transform.translation;
        let step = athlete.speed * dt;
        if delta.length() > step {
            transform.translation += delta.normalize() * step;
        } else {
            transform.translation = target;
        }
    }
}
```

The action key passes when the controlled athlete has the ball, and takes the ball when that athlete is close.

```rust
#[derive(Component)]
struct Controlled;

#[derive(Component)]
struct HasBall;

#[derive(Component)]
struct Athlete {
    speed: f32,
    presses: bool,
}

#[derive(Component)]
struct Ball;

fn contextual_action(
    keys: Res<ButtonInput<KeyCode>>,
    ball: Query<&Transform, With<Ball>>,
    mut athletes: Query<(Entity, &Transform, Has<HasBall>, Has<Controlled>), With<Athlete>>,
    mut commands: Commands,
) {
    if !keys.just_pressed(KeyCode::KeyJ) {
        return;
    }
    let Ok(ball_tf) = ball.single() else {
        return;
    };
    for (entity, transform, has_ball, controlled) in &mut athletes {
        if !controlled {
            continue;
        }
        if has_ball {
            commands.entity(entity).remove::<HasBall>();
        } else if transform.translation.distance(ball_tf.translation) < 1.5 {
            commands.entity(entity).insert(HasBall);
        }
    }
}
```

Kickoff places two athletes, one slot, and the ball.

```rust
#[derive(Component)]
struct Athlete {
    speed: f32,
    presses: bool,
}

#[derive(Component)]
struct Controlled;

#[derive(Component)]
struct Slot {
    offset: Vec3,
}

#[derive(Component)]
struct Ball;

fn spawn_kickoff(mut commands: Commands) {
    commands.spawn((
        Athlete {
            speed: 6.0,
            presses: true,
        },
        Controlled,
        Transform::from_xyz(-2.0, 0.0, 0.0),
    ));
    commands.spawn((
        Athlete {
            speed: 5.0,
            presses: false,
        },
        Transform::from_xyz(-8.0, 0.0, 2.0),
    ));
    commands.spawn((
        Slot {
            offset: Vec3::new(-6.0, 0.0, 4.0),
        },
        Transform::default(),
    ));
    commands.spawn((Ball, Transform::from_xyz(0.0, 0.4, 0.0)));
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
| Per-entity data | `Component` + `Query` | A Godot node script |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Check the official docs first | A made-up crate or API |

Load [references/ecs-ownership.md](genre-sports-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No Godot types in Bevy code. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented genre APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- Do not pick a physics or net crate here. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Official pages stay on the unversioned `latest` branch.

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
- [godot-genre-sports](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-genre-sports/SKILL.md) - Sports on the Godot engine, same depth.
- [bevy-game-loop-time-trial](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-game-loop-time-trial/SKILL.md) - Match clock.
- [bevy-combat-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-combat-system/SKILL.md) - Contact if the sport uses hits.
- [bevy-character-movement](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-character-movement/SKILL.md) - Athletes.
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Period state.

#### Downstream / consumers
- None. This router does not own a second implementation.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
