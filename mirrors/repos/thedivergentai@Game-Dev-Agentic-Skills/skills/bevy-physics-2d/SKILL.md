---
name: bevy-physics-2d
description: "Bevy ECS skill for 2D physics. Keywords: Bevy, physics, 2D, ECS, collision."
---

# Bevy 2D physics

## When to use

Load this when a Bevy app needs simulated 2D bodies, triggers, or layer filtering before choosing a solver. Pair with bevy-character-movement for player motion that should not be a rigid body. Pair with bevy-spatial-queries for casts that also wait on a solver.

## ECS shape

- **Components** own velocity, mass, a circle radius, and a layer mask for props you simulate yourself.
- **Resources** own gravity.
- **Systems** integrate on `FixedUpdate`, then separate overlapping circles. `.chain()` runs separation after the step.
- **Schedule:** the fixed step is the clock. A solver plugin can replace the integrator when you need joints and a spatial index. This file does not name that plugin's types. Player locomotion stays on bevy-character-movement.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Simulated 2D prop | `Body2d` plus `Transform`, integrated on `FixedUpdate` |
| Player locomotion | bevy-character-movement, not this integrator |
| Trigger volumes | An `Aabb` overlap that records occupants |
| Layers and masks | A `LayerMask` you define, filtered in the overlap system |

## Scope

Gravity, velocity, circle overlap, and AABB triggers are ordinary components stepped on `FixedUpdate`. Joints, continuous collision, and a spatial index belong to a physics solver you add as a plugin. Casts that need that solver's world belong on bevy-spatial-queries.

## Examples

```toml
[dependencies]
bevy = "0.20"
```

Integrate velocity under gravity, then push overlapping circles apart when their layer masks intersect. Both systems write `Body2d` and `Transform`, so they run as one chain.

```rust
#[derive(Component)]
struct Body2d {
    velocity: Vec2,
    mass: f32,
    radius: f32,
}

#[derive(Component)]
struct LayerMask {
    layer: u32,
    mask: u32,
}

#[derive(Resource)]
struct Gravity2d(Vec2);

fn integrate_2d(
    time: Res<Time<Fixed>>,
    gravity: Res<Gravity2d>,
    mut bodies: Query<(&mut Transform, &mut Body2d)>,
) {
    let dt = time.delta_secs();
    for (mut tf, mut body) in &mut bodies {
        body.velocity += gravity.0 * dt;
        tf.translation.x += body.velocity.x * dt;
        tf.translation.y += body.velocity.y * dt;
        if tf.translation.y < body.radius {
            tf.translation.y = body.radius;
            body.velocity.y = body.velocity.y.max(0.0);
        }
    }
}

fn masks_overlap(a: &LayerMask, b: &LayerMask) -> bool {
    (a.mask & b.layer) != 0 && (b.mask & a.layer) != 0
}

fn separate_circles(mut bodies: Query<(Entity, &mut Transform, &mut Body2d, &LayerMask)>) {
    let mut pairs: Vec<(Entity, Entity)> = Vec::new();
    for (a, tf_a, body_a, layer_a) in &bodies {
        for (b, tf_b, body_b, layer_b) in &bodies {
            if a.index() >= b.index() || !masks_overlap(layer_a, layer_b) {
                continue;
            }
            let delta = tf_b.translation.truncate() - tf_a.translation.truncate();
            let min = body_a.radius + body_b.radius;
            if delta.length() < min {
                pairs.push((a, b));
            }
        }
    }
    for (a, b) in pairs {
        let Ok([(_, mut tf_a, mut body_a, _), (_, mut tf_b, mut body_b, _)]) =
            bodies.get_many_mut([a, b])
        else {
            continue;
        };
        let delta = tf_b.translation.truncate() - tf_a.translation.truncate();
        let dist = delta.length();
        let min = body_a.radius + body_b.radius;
        if dist >= min || dist == 0.0 {
            continue;
        }
        let normal = delta / dist;
        let push = (min - dist) * 0.5;
        tf_a.translation.x -= normal.x * push;
        tf_a.translation.y -= normal.y * push;
        tf_b.translation.x += normal.x * push;
        tf_b.translation.y += normal.y * push;
        let rel = (body_b.velocity - body_a.velocity).dot(normal);
        if rel < 0.0 {
            let inv_a = 1.0 / body_a.mass.max(0.001);
            let inv_b = 1.0 / body_b.mass.max(0.001);
            let impulse = -rel / (inv_a + inv_b);
            body_a.velocity -= normal * impulse * inv_a;
            body_b.velocity += normal * impulse * inv_b;
        }
    }
}

pub struct Physics2dPlugin;

impl Plugin for Physics2dPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(Gravity2d(Vec2::new(0.0, -9.8)))
            .add_systems(FixedUpdate, (integrate_2d, separate_circles).chain());
    }
}
```

An AABB trigger remembers who is inside. A ray against a circle reports the nearest hit along the segment.

```rust
#[derive(Component)]
struct AabbTrigger {
    half: Vec2,
}

#[derive(Component)]
struct Inside(Vec<Entity>);

#[derive(Component)]
struct Body2d {
    velocity: Vec2,
    mass: f32,
    radius: f32,
}

#[derive(Component)]
struct LayerMask {
    layer: u32,
    mask: u32,
}

fn fill_trigger(
    triggers: Query<(Entity, &Transform, &AabbTrigger)>,
    bodies: Query<(Entity, &Transform, &Body2d)>,
    mut occupants: Query<&mut Inside>,
) {
    for (trigger_e, tf, aabb) in &triggers {
        let Ok(mut inside) = occupants.get_mut(trigger_e) else {
            continue;
        };
        inside.0.clear();
        for (body_e, body_tf, body) in &bodies {
            let delta = (body_tf.translation - tf.translation).truncate().abs();
            if delta.x <= aabb.half.x + body.radius && delta.y <= aabb.half.y + body.radius {
                inside.0.push(body_e);
            }
        }
    }
}

fn ray_circle(origin: Vec2, dir: Vec2, center: Vec2, radius: f32) -> Option<f32> {
    let oc = origin - center;
    let a = dir.dot(dir);
    if a == 0.0 {
        return None;
    }
    let b = 2.0 * oc.dot(dir);
    let c = oc.dot(oc) - radius * radius;
    let disc = b * b - 4.0 * a * c;
    if disc < 0.0 {
        return None;
    }
    let t = (-b - disc.sqrt()) / (2.0 * a);
    if t >= 0.0 { Some(t) } else { None }
}

fn spawn_ball(mut commands: Commands) {
    commands.spawn((
        Transform::from_xyz(0.0, 3.0, 0.0),
        Body2d {
            velocity: Vec2::ZERO,
            mass: 1.0,
            radius: 0.4,
        },
        LayerMask { layer: 1, mask: 2 },
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

- No Godot 2D physics node or server types. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No Avian, Rapier, or any other named physics crate as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented collider, layer, or joint APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- `bevy crate` - API index. The 0.20.0 feature list has no physics-engine feature.
- [Assets](https://bevy.org/assets/) - Official asset catalog. No physics plugin is named from it here.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [Quick Start: plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and third-party `add_plugins`.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- `bevy::time` - `Fixed` and `run_fixed_main_schedule` (`FixedMain`) as a clock, not a solver.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - ECS ownership and the fixed-timestep schedule names.

#### Complements
- [bevy-physics-3d](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-physics-3d/SKILL.md) - Simulated 3D bodies and solver choice.
- [bevy-character-movement](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-character-movement/SKILL.md) - Player locomotion that should not be a rigid body.
- [bevy-spatial-queries](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-spatial-queries/SKILL.md) - Casts and overlaps. Choose a physics solver before adding them.
- [godot-2d-physics](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-2d-physics/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- Combat and shooter skills cover hit detection and shots.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
