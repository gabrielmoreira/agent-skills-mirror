---
name: bevy-adapt-2d-to-3d
description: "Rewrite Bevy 2D actors and cameras into 3D meshes and Camera3d while keeping gameplay components. Use when a Bevy 2D game should gain a perspective camera, mesh draw, and a planar velocity lifted onto XZ. Keywords: Camera2d, Camera3d, Sprite, Mesh3d, StandardMaterial, WishVelocity."
---

# Bevy adapt 2D to 3D

## When to use

Load this when a 2D design should gain a 3D camera and meshes. Keep gameplay components. Swap the camera and the drawable.

## ECS shape

- **Cameras:** `Camera2d` and `Camera3d` are already documented on bevy-camera-systems. An entity should not keep both as if they were one camera mode unless that skill says so.
- **Draw:** `Sprite` is 2D. Meshes and `StandardMaterial` are 3D (bevy-3d-materials).
- **Features:** the crate page separates `2d` and `3d` profiles. Enabling 3D does not delete 2D types.
- **Motion:** bevy-character-movement stays the locomotion skill. A 3D velocity is still your component until a solver exists.

## What changes

| Keep | Replace |
| --- | --- |
| Gameplay components on the actor | `Sprite` with `Mesh3d` and `MeshMaterial3d` |
| The camera entity | `Camera2d` with `Camera3d` and a perspective `Projection` |
| Planar motion as data | `Vec2` velocity with a `Vec3` wish on XZ |

There is no conversion helper. A startup system rewrites the entities you already spawned. Physics solvers stay on the physics skills.

```toml
[dependencies]
bevy = "0.20"
```

```rust
use bevy::mesh::Meshable;

#[derive(Component)]
struct Actor;

#[derive(Component)]
struct PlanarVelocity(Vec2);

#[derive(Component)]
struct WishVelocity(Vec3);

fn promote_actors(
    mut commands: Commands,
    mut meshes: ResMut<Assets<Mesh>>,
    mut materials: ResMut<Assets<StandardMaterial>>,
    actors: Query<(Entity, &Transform), (With<Actor>, With<Sprite>)>,
) {
    let mesh = meshes.add(Cuboid::new(0.8, 1.6, 0.8).mesh());
    let material = materials.add(StandardMaterial {
        base_color: Color::srgb(0.75, 0.45, 0.25),
        ..default()
    });
    for (entity, transform) in &actors {
        let ground = Vec3::new(transform.translation.x, 0.8, transform.translation.y);
        commands.entity(entity).remove::<Sprite>().insert((
            Mesh3d(mesh.clone()),
            MeshMaterial3d(material.clone()),
            Transform::from_translation(ground),
        ));
    }
}

fn promote_camera(mut commands: Commands, cameras: Query<Entity, With<Camera2d>>) {
    for entity in &cameras {
        commands.entity(entity).remove::<Camera2d>().insert((
            Camera3d::default(),
            Projection::Perspective(PerspectiveProjection::default()),
            Transform::from_xyz(0.0, 6.0, 12.0).looking_at(Vec3::ZERO, Vec3::Y),
        ));
    }
}
fn lift_velocity(mut actors: Query<(&PlanarVelocity, &mut WishVelocity), With<Actor>>) {
    for (planar, mut wish) in &mut actors {
        wish.0 = Vec3::new(planar.0.x, 0.0, planar.0.y);
    }
}

pub struct AdaptTo3dPlugin;

impl Plugin for AdaptTo3dPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Startup, (promote_actors, promote_camera).chain())
            .add_systems(FixedUpdate, lift_velocity);
    }
}
```

```rust
fn spawn_follow_camera(mut commands: Commands) {
    commands.spawn((
        Camera3d::default(),
        Projection::Perspective(PerspectiveProjection {
            fov: 50.0_f32.to_radians(),
            ..default()
        }),
        Transform::from_xyz(0.0, 4.0, 8.0).looking_at(Vec3::new(0.0, 1.0, 0.0), Vec3::Y),
    ));
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
| Per-entity data | `Component` + `Query` | One script that owns the whole actor |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Check the official docs first | A made-up crate or API |

Load [references/ecs-ownership.md](adapt-2d-to-3d-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No node convert-to-3D operation from another engine. WHY: Bevy has no scene-tree convert; a startup system removes `Sprite` and inserts mesh components on the same entity.
- No foreign engine types in Bevy code. WHY: `Camera3d` and `Mesh3d` are the draw path this schedule already runs.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Load [references/ecs-ownership.md](adapt-2d-to-3d-ecs-ownership.md) when a system both removes 2D components and writes a velocity. Do not load it to author materials.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-camera-systems](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-camera-systems/SKILL.md) - Camera2d and Camera3d.
- [bevy-3d-world-building](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-3d-world-building/SKILL.md) - Level assembly.

#### Complements
- [bevy-adapt-3d-to-2d](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-adapt-3d-to-2d/SKILL.md) - The reverse adapt.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
