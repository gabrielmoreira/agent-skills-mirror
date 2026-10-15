---
name: bevy-genre-open-world
description: "Route a Bevy 0.20 open world. Use when region membership is a component, the player cell is one resource, and activation runs after the cell write in one chain. Keywords: Bevy, Open world, Resident, PlayerCell, Active, chain, genre."
---

# Bevy Open world (thin router)

Genre router. Domain work lives in the Bevy skills below.

## When to use

Load this for streaming regions and distant actors. Do not invent a world-partition type.

## ECS shape

- **Components** hold the genre's per-entity flags as plain data. This file does not name new engine types.
- **Resources** hold run-wide counters (score, wave index, seed) via bevy-data-resources.
- **Systems** read those components on `Update` or the fixed timestep from bevy-master. Order them with `.chain()` when a later system must see the result.
- **Schedule:** gameplay mode changes go through bevy-state-machines. Do not invent a genre plugin.

## Routing

- [bevy-asset-scenes](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-asset-scenes/SKILL.md) - Region scenes.
- [bevy-3d-world-building](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-3d-world-building/SKILL.md) - Assembly.
- [bevy-ai-navigation](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ai-navigation/SKILL.md) - Ambient actors.
- [bevy-quest-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-quest-system/SKILL.md) - Objectives.

## Scope

Region membership and activation distance are components you own. Mesh LOD stays on bevy-3d-world-building.

## Examples

```toml
[package]
name = "open-world"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = "0.20"
```

A cell index on the player resource decides which residents are active. One system writes `PlayerCell`; the next inserts or removes `Active`.

```rust
#[derive(Component)]
struct Player;

#[derive(Component)]
struct Resident {
    cell: i32,
}

#[derive(Component)]
struct Active;

#[derive(Resource)]
struct PlayerCell(i32);

fn track_cell(players: Query<&Transform, With<Player>>, mut cell: ResMut<PlayerCell>) {
    for transform in &players {
        cell.0 = (transform.translation.x / 64.0).floor() as i32;
        break;
    }
}

fn activate(
    cell: Res<PlayerCell>,
    mut commands: Commands,
    idle: Query<(Entity, &Resident), Without<Active>>,
) {
    for (entity, resident) in &idle {
        if (resident.cell - cell.0).abs() <= 1 {
            commands.entity(entity).insert(Active);
        }
    }
}

fn deactivate(
    cell: Res<PlayerCell>,
    mut commands: Commands,
    active: Query<(Entity, &Resident), With<Active>>,
) {
    for (entity, resident) in &active {
        if (resident.cell - cell.0).abs() > 1 {
            commands.entity(entity).remove::<Active>();
        }
    }
}

pub struct RegionPlugin;

impl Plugin for RegionPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(PlayerCell(0)).add_systems(
            Update,
            (track_cell, activate, deactivate).chain(),
        );
    }
}
```

Distant actors keep a home point and only move while `Active` is present.

```rust
#[derive(Component)]
struct Wander {
    home: Vec3,
    angle: f32,
}

fn wander(time: Res<Time>, mut actors: Query<(&mut Transform, &mut Wander), With<Active>>) {
    let dt = time.delta_secs();
    for (mut transform, mut wander) in &mut actors {
        wander.angle += dt;
        let offset = Vec3::new(wander.angle.sin() * 2.0, 0.0, wander.angle.cos() * 2.0);
        transform.translation = wander.home + offset;
    }
}

#[derive(Component)]
struct Active;
```

Spawn the player and a ring of residents from `Startup`.

```rust
#[derive(Component)]
struct Player;

#[derive(Component)]
struct Resident {
    cell: i32,
}

#[derive(Component)]
struct Wander {
    home: Vec3,
    angle: f32,
}

fn spawn_world(mut commands: Commands) {
    commands.spawn((Player, Transform::from_xyz(0.0, 0.0, 0.0)));
    for index in 0..5 {
        let home = Vec3::new(index as f32 * 64.0, 0.0, 0.0);
        commands.spawn((
            Resident { cell: index },
            Wander { home, angle: index as f32 },
            Transform::from_translation(home),
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
| Region streaming | `Resident` cell plus `Active` inserted by one chained system | A world-partition type invented in this file |

Load [references/ecs-ownership.md](genre-open-world-ecs-ownership.md) for the ownership table.

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
- [bevy-asset-scenes](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-asset-scenes/SKILL.md) - Region scenes.
- [bevy-3d-world-building](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-3d-world-building/SKILL.md) - Assembly.
- [bevy-ai-navigation](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ai-navigation/SKILL.md) - Ambient actors.
- [bevy-quest-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-quest-system/SKILL.md) - Objectives.

#### Downstream / consumers
- None. This router does not own a second implementation.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
