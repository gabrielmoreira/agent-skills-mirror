---
name: bevy-spatial-queries
description: "Answer Bevy 0.20 line-of-sight, radius, and cursor picks with Transform distance and facing. Use when a design needs a probe and collider casts belong on the physics skills. Keywords: Bevy, spatial query, viewport_to_world_2d, GlobalTransform, facing, radius."
---

# Bevy spatial queries

## When to use

Load this when a design needs line of sight, a volume overlap, a ground probe, or a mouse pick. Screen-to-2D-world mapping that does not hit a collider is a camera helper, not a physics query.

## ECS shape

- **Components** own a probe radius or a facing marker. Positions come from `GlobalTransform`.
- **Camera pick:** `Camera::viewport_to_world_2d` with `GlobalTransform` maps a cursor to a 2D world point. That is a camera map, then a distance test against sprites. See bevy-camera-systems.
- **Systems** read transforms after movement. Chain the probe after the system that writes `Transform` when both run in the same schedule.

## Probe choice

| Need | Bevy path |
| --- | --- |
| Collider cast or sweep | bevy-physics-2d or bevy-physics-3d. This skill measures distance and facing with `Transform`. |
| Pointer in the 2D world | `viewport_to_world_2d`, then the nearest entity inside a radius. |
| Exclude the caster | Skip the probe `Entity` when comparing distances. |
| View cone | Dot the view forward with the direction to the target and compare against a cosine threshold. |

## Scope

- Stock Bevy measures points, radii, and facing. Collider casts, sweeps, and normals stay on bevy-physics-2d and bevy-physics-3d.
- A probe never reports itself. Compare `Entity` before accepting a hit.
- Chain the probe after movement so it reads the transforms written this frame.

## Examples

```toml
[dependencies]
bevy = "0.20"
```

Map the cursor into the world, then keep the closest marker inside the pick radius.

```rust
#[derive(Component)]
struct Pickable;

use bevy::window::PrimaryWindow;

fn pick_nearest(
    windows: Query<&Window, With<PrimaryWindow>>,
    cameras: Query<(&Camera, &GlobalTransform), With<Camera2d>>,
    targets: Query<(Entity, &GlobalTransform), With<Pickable>>,
) {
    let Ok(window) = windows.single() else {
        return;
    };
    let Ok((camera, camera_tf)) = cameras.single() else {
        return;
    };
    let Some(cursor) = window.cursor_position() else {
        return;
    };
    let Ok(world) = camera.viewport_to_world_2d(camera_tf, cursor) else {
        return;
    };
    let mut best: Option<(Entity, f32)> = None;
    for (entity, transform) in &targets {
        let point = transform.translation().truncate();
        let distance = point.distance(world);
        if distance > 24.0 {
            continue;
        }
        if best.is_none_or(|(_, so_far)| distance < so_far) {
            best = Some((entity, distance));
        }
    }
    let _hit = best.map(|(entity, _)| entity);
}
```

A radius probe lists other entities inside its range and skips its own entity.

```rust
#[derive(Component)]
struct Probe {
    radius: f32,
}

#[derive(Component)]
struct Body;

fn overlaps(
    probes: Query<(Entity, &GlobalTransform, &Probe)>,
    bodies: Query<(Entity, &GlobalTransform), With<Body>>,
) {
    for (probe_entity, probe_tf, probe) in &probes {
        for (body, body_tf) in &bodies {
            if body == probe_entity {
                continue;
            }
            let distance = probe_tf.translation().distance(body_tf.translation());
            if distance <= probe.radius {
                let _hit = body;
            }
        }
    }
}
```

Facing uses the view forward and a cosine limit. Movement writes `Transform` first. The sight test reads `Transform` in the next chained system, because `GlobalTransform` updates only after propagation.

```rust
#[derive(Component)]
struct Watcher {
    cos_limit: f32,
}

#[derive(Component)]
struct Mark;

fn advance(mut watchers: Query<&mut Transform, With<Watcher>>) {
    for mut transform in &mut watchers {
        transform.translation.x += 1.0;
    }
}

fn can_see(
    watchers: Query<(&Transform, &Watcher)>,
    marks: Query<&Transform, (With<Mark>, Without<Watcher>)>,
) {
    for (watcher_tf, watcher) in &watchers {
        let origin = watcher_tf.translation;
        let forward = watcher_tf.forward().as_vec3();
        for mark_tf in &marks {
            let to = mark_tf.translation - origin;
            let length = to.length();
            if length <= f32::EPSILON {
                continue;
            }
            let facing = forward.dot(to / length);
            if facing >= watcher.cos_limit {
                let _seen = true;
            }
        }
    }
}

pub struct SpatialPlugin;

impl Plugin for SpatialPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Update, (advance, can_see).chain());
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
| Per-entity data | `Component` + `Query` | A field stored outside the world |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Same-frame facing | `advance` then `can_see` with `.chain()` on `Transform` | Reading `GlobalTransform` in the system that just wrote `Transform` |
| Collider cast | bevy-physics-2d or bevy-physics-3d | An invented ray or mask API |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Check the official documentation | A made-up crate or API |

Load [references/ecs-ownership.md](spatial-queries-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- Do not read `GlobalTransform` in the same system that just wrote `Transform`. WHY: propagation has not run, so the global pose is still last frame.
- No Avian, Rapier, or any other named physics crate as the chosen solver. WHY: collider casts stay on the physics skills; this skill uses transforms.
- No invented `intersect_ray` or mask APIs. WHY: stock Bevy here is distance, radius, and a dot product.

## Reference

Official links stay on unversioned `latest` pages. The library pin on bevy-master stays **0.20.0**. No stock spatial-query module is used here.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No query plugin was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - Systems, `Query`, and `.chain()`.
- [Quick Start: plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `add_plugins` without a chosen physics crate. `viewport_to_world_2d` is a camera map; details live on bevy-camera-systems.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - ECS ownership.
- [bevy-camera-systems](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-camera-systems/SKILL.md) - Viewport to 2D world, without a hit test.

#### Complements
- [bevy-physics-2d](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-physics-2d/SKILL.md) - 2D physics and solver choice.
- [bevy-physics-3d](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-physics-3d/SKILL.md) - 3D physics and solver choice.
- [godot-raycasting-queries](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-raycasting-queries/SKILL.md) - Godot package for cast queries.

#### Downstream / consumers
- [bevy-ai-navigation](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ai-navigation/SKILL.md) - Sensors that need a cast.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
