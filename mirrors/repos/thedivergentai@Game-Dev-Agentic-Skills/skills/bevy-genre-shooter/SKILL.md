---
name: bevy-genre-shooter
description: "Route a Bevy 0.20 shooter: projectile entities, hitscan by translation, collide-and-despawn, wave budget resource. Keywords: Bevy, shooter, Projectile, hitscan, Wave, despawn, ECS."
---

# Bevy Shooter (thin router)

Genre router. Domain work lives in the Bevy skills below.

## When to use

Load this for a 2D or top-down shooter loop: aim, projectiles as entities, and waves.

## ECS shape

- **Components** hold the genre's per-entity flags as plain data. This file does not name new engine types.
- **Resources** hold run-wide counters (score, wave index, seed) via bevy-data-resources.
- **Systems** read those components on `Update` or the fixed timestep from bevy-master. Order them with `.chain()` when a later system must see the result.
- **Schedule:** gameplay mode changes go through bevy-state-machines. Do not invent a genre plugin.

## Routing

- [bevy-input-handling](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-input-handling/SKILL.md) - Aim and fire.
- [bevy-combat-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-combat-system/SKILL.md) - Damage.
- [bevy-game-loop-waves](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-game-loop-waves/SKILL.md) - Spawns.
- [bevy-spatial-queries](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-spatial-queries/SKILL.md) - Shots and spatial queries.

## Examples

```toml
[dependencies]
bevy = "0.20"
```

A projectile is an entity with velocity. The ship is a separate component. Fire spawns; motion integrates. They touch different data, so they can run in parallel.

```rust
#[derive(Component)]
struct Ship;

#[derive(Component)]
struct Projectile {
    velocity: Vec2,
    damage: i32,
}

fn fire(
    mouse: Res<ButtonInput<MouseButton>>,
    ships: Query<&Transform, With<Ship>>,
    mut commands: Commands,
) {
    if !mouse.just_pressed(MouseButton::Left) {
        return;
    }
    for tf in &ships {
        commands.spawn((
            Projectile {
                velocity: Vec2::new(480.0, 0.0),
                damage: 1,
            },
            Transform::from_translation(tf.translation),
        ));
    }
}

fn fly(mut shots: Query<(&Projectile, &mut Transform)>, time: Res<Time>) {
    let dt = time.delta_secs();
    for (shot, mut tf) in &mut shots {
        tf.translation.x += shot.velocity.x * dt;
        tf.translation.y += shot.velocity.y * dt;
    }
}

fn install_shots(app: &mut App) {
    app.add_systems(Update, (fire, fly));
}
```

Hitscan picks the nearest target inside a range by comparing translations, then applies damage after the read loop ends.

```rust
#[derive(Component)]
struct Health(i32);

#[derive(Component)]
struct Ship;

fn hitscan(
    ships: Query<&Transform, With<Ship>>,
    mut targets: Query<(Entity, &Transform, &mut Health), Without<Ship>>,
) {
    let mut chosen: Vec<Entity> = Vec::new();
    for origin in &ships {
        let mut best: Option<Entity> = None;
        let mut best_dist = 240.0_f32;
        for (entity, tf, _) in &targets {
            let dist = origin
                .translation
                .truncate()
                .distance(tf.translation.truncate());
            if dist < best_dist {
                best_dist = dist;
                best = Some(entity);
            }
        }
        if let Some(entity) = best {
            chosen.push(entity);
        }
    }
    for entity in chosen {
        if let Ok((_, _, mut hp)) = targets.get_mut(entity) {
            hp.0 -= 1;
        }
    }
}
```

A shot that reaches a hurtbox despawns. Chain `collide` after `fly` when both write projectile entities in the same schedule.

```rust
#[derive(Component)]
struct Projectile {
    damage: i32,
}

#[derive(Component)]
struct Health(i32);

fn collide(
    mut commands: Commands,
    shots: Query<(Entity, &Transform, &Projectile)>,
    mut targets: Query<(&Transform, &mut Health), Without<Projectile>>,
) {
    for (shot_entity, shot_tf, shot) in &shots {
        for (tf, mut hp) in &mut targets {
            let dist = shot_tf
                .translation
                .truncate()
                .distance(tf.translation.truncate());
            if dist < 16.0 {
                hp.0 -= shot.damage;
                commands.entity(shot_entity).despawn();
                break;
            }
        }
    }
}
```

The wave index is a resource. Spawning enemies spends the budget, matching bevy-game-loop-waves.

```rust
#[derive(Resource)]
struct Wave {
    index: u32,
    budget: u32,
}

#[derive(Component)]
struct Enemy;

#[derive(Component)]
struct Health(i32);

fn spawn_wave(mut commands: Commands, mut wave: ResMut<Wave>) {
    if wave.budget == 0 {
        return;
    }
    for _ in 0..wave.budget {
        commands.spawn((Enemy, Health(3)));
    }
    wave.budget = 0;
    wave.index += 1;
}
```

## Scope

- Aim routing and named actions belong on bevy-input-handling.
- A spatial index for many bodies belongs on bevy-spatial-queries. The range check above is enough for a handful of targets.

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
| Per-entity data | `Component` + `Query` | A field stored off the entity |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Use the examples in this skill | A made-up crate or API |

Load [references/ecs-ownership.md](references/ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- Do not despawn a projectile from inside a mutable query over that same projectile. WHY: despawn goes through `Commands`; `collide` reads shots immutably and writes `Health` on the other query.
- Do not chain `fire` and `fly` when they touch different data. WHY: spawn and integration stay parallel; chain only `collide` after `fly` when both run in one schedule and the shot must move before the range test.
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
- [godot-genre-shooter](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-genre-shooter/SKILL.md) - Shooter on the Godot engine, same depth.
- [bevy-input-handling](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-input-handling/SKILL.md) - Aim and fire.
- [bevy-combat-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-combat-system/SKILL.md) - Damage.
- [bevy-game-loop-waves](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-game-loop-waves/SKILL.md) - Spawns.
- [bevy-spatial-queries](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-spatial-queries/SKILL.md) - Shots and spatial queries.

#### Downstream / consumers
- None. This router does not own a second implementation.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
