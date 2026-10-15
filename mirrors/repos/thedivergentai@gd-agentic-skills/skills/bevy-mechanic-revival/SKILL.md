---
name: bevy-mechanic-revival
description: "Bevy ECS skill for a Bevy downed and revival loop. Keywords: Bevy, revival, downed, respawn, ECS."
---

# Bevy revival mechanic

## When to use

Load this when an actor is downed, can be revived, or respawns.

## ECS shape

- **Components:** a downed flag and a revive elapsed you define.
- **Resources:** run-wide tables live in a resource (bevy-data-resources), not an autoload.
- **Systems:** mutate those components on `Update` or the fixed timestep. Use `.chain()` when damage must land before death.
- **Messages:** one-shot facts (hit, pickup, quest advance) go through bevy-events-messaging. This file does not add a new event type name.

## Scope

Downed time, revive progress, and the last checkpoint are components. Overlap is a distance test here; a physics solver can replace that test later.

## Examples

```toml
[package]
name = "revival"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = "0.20"
```

Health hits zero, the actor is downed, and an ally within range fills the revive bar. A full bar clears the downed flag and restores health.

```rust
#[derive(Component)]
struct Health {
    current: f32,
    max: f32,
}

#[derive(Component)]
struct Downed {
    elapsed: f32,
}

#[derive(Component)]
struct Reviving {
    progress: f32,
    needed: f32,
}

#[derive(Component)]
struct Ally;

fn apply_down(
    mut commands: Commands,
    mut actors: Query<(Entity, &Health), Without<Downed>>,
) {
    for (entity, health) in &mut actors {
        if health.current <= 0.0 {
            commands.entity(entity).insert(Downed { elapsed: 0.0 });
        }
    }
}

fn tick_revive(
    time: Res<Time<Fixed>>,
    allies: Query<&Transform, With<Ally>>,
    mut downed: Query<(Entity, &Transform, &mut Health, &mut Downed, Option<&mut Reviving>)>,
    mut commands: Commands,
) {
    let dt = time.delta_secs();
    for (entity, transform, mut health, mut downed, reviving) in &mut downed {
        downed.elapsed += dt;
        let near = allies.iter().any(|ally| {
            ally.translation.distance(transform.translation) < 2.0
        });
        if !near {
            commands.entity(entity).remove::<Reviving>();
            continue;
        }
        let progress = reviving.map(|mut rev| {
            rev.progress += dt;
            rev.progress
        });
        if let Some(progress) = progress {
            if progress >= 2.0 {
                health.current = health.max;
                commands.entity(entity).remove::<Downed>().remove::<Reviving>();
            }
        } else {
            commands.entity(entity).insert(Reviving {
                progress: 0.0,
                needed: 2.0,
            });
        }
    }
}
```

The checkpoint resource stores the respawn pose. Death after the bleed-out moves the actor there and refills health.

```rust
#[derive(Resource)]
struct Checkpoint {
    translation: Vec3,
}

#[derive(Component)]
struct Health {
    current: f32,
    max: f32,
}

#[derive(Component)]
struct Downed {
    elapsed: f32,
}

fn move_to_checkpoint(
    mut query: Query<(Entity, &mut Transform, &mut Health, &Downed)>,
    checkpoint: Res<Checkpoint>,
    mut commands: Commands,
) {
    for (entity, mut transform, mut health, downed) in &mut query {
        if downed.elapsed < 8.0 {
            continue;
        }
        transform.translation = checkpoint.translation;
        health.current = health.max;
        commands.entity(entity).remove::<Downed>();
    }
}

pub struct RevivalPlugin;

impl Plugin for RevivalPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(Checkpoint {
            translation: Vec3::ZERO,
        })
        .add_systems(FixedUpdate, move_to_checkpoint);
    }
}
```

Touching a marker overwrites the checkpoint.

```rust
#[derive(Component)]
struct CheckpointMarker;

#[derive(Component)]
struct Player;

#[derive(Resource)]
struct Checkpoint {
    translation: Vec3,
}

fn capture_checkpoint(
    players: Query<&Transform, With<Player>>,
    markers: Query<&Transform, With<CheckpointMarker>>,
    mut checkpoint: ResMut<Checkpoint>,
) {
    let Ok(player) = players.single() else {
        return;
    };
    for marker in &markers {
        if player.translation.distance(marker.translation) < 1.2 {
            checkpoint.translation = marker.translation;
        }
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

- No Godot node, resource, or signal types for this mechanic. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

- No Godot types in Bevy code. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Official pages stay on the unversioned `latest` branch.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-combat-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-combat-system/SKILL.md) - What drops health to zero.
- [bevy-data-resources](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-data-resources/SKILL.md) - Tables and definitions.
- [bevy-events-messaging](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-events-messaging/SKILL.md) - One-shot facts.

#### Complements
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Mode flags.
- [godot-mechanic-revival](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-mechanic-revival/SKILL.md) - Revival on the Godot engine, same depth.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
