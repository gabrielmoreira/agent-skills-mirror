---
name: bevy-genre-shooter-fps
description: "Bevy genre router for FPS shooter. Keywords: Bevy, FPS shooter, genre, ECS, router."
---

# Bevy FPS shooter

Genre router. Domain work lives in the Bevy skills below.

## When to use

Load this for a first-person shooter route: 3D camera, view model, and combat.

## ECS shape

- **Components** hold the genre's per-entity flags as plain data. This file does not name new engine types.
- **Resources** hold run-wide counters (score, wave index, seed) via bevy-data-resources.
- **Systems** read those components on `Update` or the fixed timestep from bevy-master. Order them with `.chain()` when a later system must see the result.
- **Schedule:** gameplay mode changes go through bevy-state-machines. Look, the view model, and the shot clock below are components plus one resource.

## Examples

```toml
[dependencies]
bevy = "0.20"
```

Pitch stays on the camera. Yaw stays on the body so the view model inherits the turn. The shot clock is a resource. `tick_shot` then `fire` share `ShotClock`, so they chain. Look writes a different component and stays outside that chain.

```rust
use bevy::input::mouse::AccumulatedMouseMotion;
use bevy::window::{CursorGrabMode, CursorOptions, PrimaryWindow};

#[derive(Component)]
struct LookPitch {
    radians: f32,
}

#[derive(Component)]
struct FpsBody;

#[derive(Component)]
struct ViewModel;

#[derive(Resource)]
struct ShotClock {
    seconds_left: f32,
}

fn boot(mut commands: Commands) {
    commands.insert_resource(ShotClock { seconds_left: 0.0 });
    let body = commands
        .spawn((FpsBody, Transform::from_xyz(0.0, 1.6, 0.0)))
        .id();
    commands.spawn((
        Camera3d::default(),
        LookPitch { radians: 0.0 },
        Transform::default(),
        ChildOf(body),
    ));
    commands.spawn((
        ViewModel,
        Transform::from_xyz(0.25, -0.2, -0.45),
        ChildOf(body),
    ));
}

fn lock_pointer(mut windows: Query<&mut CursorOptions, With<PrimaryWindow>>) {
    for mut window in &mut windows {
        window.visible = false;
        window.grab_mode = CursorGrabMode::Locked;
    }
}

fn apply_look(
    motion: Res<AccumulatedMouseMotion>,
    mut bodies: Query<&mut Transform, With<FpsBody>>,
    mut cameras: Query<(&mut Transform, &mut LookPitch), Without<FpsBody>>,
) {
    let dx = motion.delta.x;
    let dy = motion.delta.y;
    for mut transform in &mut bodies {
        transform.rotate_y(-dx * 0.002);
    }
    for (mut transform, mut pitch) in &mut cameras {
        pitch.radians = (pitch.radians - dy * 0.002).clamp(-1.2, 1.2);
        transform.rotation = Quat::from_rotation_x(pitch.radians);
    }
}

fn tick_shot(time: Res<Time>, mut clock: ResMut<ShotClock>) {
    clock.seconds_left = (clock.seconds_left - time.delta_secs()).max(0.0);
}

fn fire(
    keys: Res<ButtonInput<MouseButton>>,
    mut clock: ResMut<ShotClock>,
) {
    if clock.seconds_left > 0.0 || !keys.just_pressed(MouseButton::Left) {
        return;
    }
    clock.seconds_left = 0.12;
}

fn install(app: &mut App) {
    app.add_systems(Startup, (boot, lock_pointer))
        .add_systems(Update, apply_look)
        .add_systems(Update, (tick_shot, fire).chain());
}
```

A shot hits when a target lies inside a cone along the body's forward axis. This is data on transforms. Physics crates stay in the combat skill.

```rust
#[derive(Component)]
struct FpsBody;

#[derive(Component)]
struct Target;

#[derive(Component)]
struct Health {
    points: i32,
}

fn hitscan(
    bodies: Query<&GlobalTransform, With<FpsBody>>,
    mut targets: Query<(&GlobalTransform, &mut Health), With<Target>>,
) {
    let Some(body) = bodies.iter().next() else {
        return;
    };
    let origin = body.translation();
    let forward = body.forward().as_vec3();
    for (transform, mut health) in &mut targets {
        let to_target = transform.translation() - origin;
        let distance = to_target.length();
        if distance > 40.0 || distance < 0.05 {
            continue;
        }
        let along = to_target.normalize().dot(forward);
        if along > 0.98 {
            health.points -= 20;
        }
    }
}
```

## Scene shape

| Piece | Bevy idiom |
| --- | --- |
| Genre content | Entities plus the domain skills linked below |
| Run-wide director | A `Resource` |
| Loop notices | bevy-events-messaging |

## Routing

- [bevy-camera-systems](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-camera-systems/SKILL.md) - Camera3d.
- [bevy-input-handling](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-input-handling/SKILL.md) - Look. Pointer lock is `CursorOptions` on the primary window.
- [bevy-combat-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-combat-system/SKILL.md) - Damage.
- [bevy-3d-world-building](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-3d-world-building/SKILL.md) - Arenas.

## Scope

- Look is `LookPitch` on the camera plus yaw on `FpsBody`. The camera and view model use `ChildOf` so they inherit that yaw. Pointer lock uses `CursorOptions`. `ShotClock` gates fire. The hitscan example compares transforms. `bevy_camera_controller` is an optional Bevy feature; this skill uses `Camera3d` and `Transform` directly.
- Broader spatial queries belong on bevy-spatial-queries.

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
| Per-entity data | `Component` + `Query` | One script that owns the whole tree |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Check the official docs first | A made-up crate or API |

Load [references/ecs-ownership.md](genre-shooter-fps-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No foreign-engine types in Bevy code. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented genre APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- Do not pick a physics or net crate here. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

Official pages stay on unversioned permalinks. The library pin on bevy-master stays **0.20**.

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
- [godot-genre-shooter-fps](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-genre-shooter-fps/SKILL.md) - Peer skill for the same genre.
- [bevy-camera-systems](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-camera-systems/SKILL.md) - Camera3d.
- [bevy-input-handling](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-input-handling/SKILL.md) - Look. Pointer lock is `CursorOptions` on the primary window.
- [bevy-combat-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-combat-system/SKILL.md) - Damage.
- [bevy-3d-world-building](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-3d-world-building/SKILL.md) - Arenas.

#### Downstream / consumers
- None. This router does not own a second implementation.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
