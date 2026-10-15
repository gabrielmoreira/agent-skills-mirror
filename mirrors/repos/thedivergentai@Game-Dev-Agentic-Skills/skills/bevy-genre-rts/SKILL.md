---
name: bevy-genre-rts
description: "Route a Bevy 0.20 RTS. Use when selection and move orders are components, a control group is one resource, and marching runs after the order write in one chain. Keywords: Bevy, RTS, Selected, MoveOrder, ControlGroup, chain, genre."
---

# Bevy RTS (thin router)

Genre router. Domain work lives in the Bevy skills below.

## When to use

Load this for selection, orders, and groups.

## ECS shape

- **Components** hold the genre's per-entity flags as plain data. This file does not name new engine types.
- **Resources** hold run-wide counters (score, wave index, seed) via bevy-data-resources.
- **Systems** read those components on `Update` or the fixed timestep from bevy-master. Order them with `.chain()` when a later system must see the result.
- **Schedule:** gameplay mode changes go through bevy-state-machines. Do not invent a genre plugin.

## Routing

- [bevy-input-handling](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-input-handling/SKILL.md) - Selection clicks.
- [bevy-ai-navigation](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ai-navigation/SKILL.md) - Move orders and navigation.
- [bevy-combat-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-combat-system/SKILL.md) - Attacks.
- [bevy-economy-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-economy-system/SKILL.md) - Costs.

## Scope

Selection, move orders, and control groups are components and one resource. Pathfinding stays on bevy-ai-navigation.

## Examples

```toml
[package]
name = "rts"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = "0.20"
```

`Selected` marks the current group. A move order is a target point. March runs after the order is written.

```rust
#[derive(Component)]
struct Selected;

#[derive(Component)]
struct MoveOrder {
    target: Vec3,
}

fn issue_move(keys: Res<ButtonInput<KeyCode>>, mut units: Query<&mut MoveOrder, With<Selected>>) {
    if !keys.just_pressed(KeyCode::KeyM) {
        return;
    }
    for mut order in &mut units {
        order.target = Vec3::new(12.0, 0.0, 6.0);
    }
}

fn march(time: Res<Time<Fixed>>, mut units: Query<(&MoveOrder, &mut Transform)>) {
    let dt = time.delta_secs();
    for (order, mut transform) in &mut units {
        let delta = order.target - transform.translation;
        let step = 6.0 * dt;
        if delta.length() <= step {
            transform.translation = order.target;
        } else {
            transform.translation += delta.normalize_or_zero() * step;
        }
    }
}

pub struct OrderPlugin;

impl Plugin for OrderPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(FixedUpdate, (issue_move, march).chain());
    }
}
```

Number keys store the selected entities on a resource. Pressing the key again clears `Selected` and restores the group.

```rust
#[derive(Resource, Default)]
struct ControlGroup {
    members: Vec<Entity>,
}

#[derive(Component)]
struct Selected;

fn bind_group(
    keys: Res<ButtonInput<KeyCode>>,
    selected: Query<Entity, With<Selected>>,
    mut group: ResMut<ControlGroup>,
    mut commands: Commands,
) {
    if keys.just_pressed(KeyCode::Digit1) && keys.pressed(KeyCode::ControlLeft) {
        group.members.clear();
        for entity in &selected {
            group.members.push(entity);
        }
        return;
    }
    if keys.just_pressed(KeyCode::Digit1) {
        for entity in &selected {
            commands.entity(entity).remove::<Selected>();
        }
        for entity in group.members.clone() {
            commands.entity(entity).insert(Selected);
        }
    }
}
```

Click-select uses a pointer resource filled by another system. Units inside the radius gain `Selected`.

```rust
#[derive(Resource)]
struct PointerWorld(Vec3);

#[derive(Component)]
struct Selectable;

#[derive(Component)]
struct Selected;

fn click_select(
    buttons: Res<ButtonInput<MouseButton>>,
    pointer: Res<PointerWorld>,
    mut commands: Commands,
    units: Query<(Entity, &Transform), With<Selectable>>,
    selected: Query<Entity, With<Selected>>,
) {
    if !buttons.just_pressed(MouseButton::Left) {
        return;
    }
    for entity in &selected {
        commands.entity(entity).remove::<Selected>();
    }
    for (entity, transform) in &units {
        if transform.translation.distance(pointer.0) < 1.5 {
            commands.entity(entity).insert(Selected);
        }
    }
}

fn spawn_units(mut commands: Commands) {
    commands.insert_resource(PointerWorld(Vec3::ZERO));
    for index in 0..4 {
        commands.spawn((
            Selectable,
            MoveOrder {
                target: Vec3::new(index as f32 * 2.0, 0.0, 0.0),
            },
            Transform::from_xyz(index as f32 * 2.0, 0.0, 0.0),
        ));
    }
}

#[derive(Component)]
struct MoveOrder {
    target: Vec3,
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
| Group orders | `Selected` plus `MoveOrder` on each unit, marched in one system | A formation type invented as an engine singleton |

Load [references/ecs-ownership.md](references/ecs-ownership.md) for the ownership table.

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
- [bevy-input-handling](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-input-handling/SKILL.md) - Selection clicks.
- [bevy-ai-navigation](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ai-navigation/SKILL.md) - Move orders and navigation.
- [bevy-combat-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-combat-system/SKILL.md) - Attacks.
- [bevy-economy-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-economy-system/SKILL.md) - Costs.

#### Downstream / consumers
- None. This router does not own a second implementation.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
