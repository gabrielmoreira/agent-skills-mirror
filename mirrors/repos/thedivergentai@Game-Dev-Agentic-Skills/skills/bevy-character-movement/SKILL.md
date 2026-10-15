---
name: bevy-character-movement
description: "Bevy 0.20 kinematic character movement: intent components, FixedUpdate integration, coyote time, and jump buffer. Use when a player or actor walks or jumps and the step must stay stable. Keywords: Bevy, movement, FixedUpdate, coyote, jump buffer, ECS."
---

# Bevy character movement

## When to use

Load this when a Bevy app needs a player or actor that moves in discrete steps (walk, jump feel, ground check) and you need the ECS shape before any solver code exists. Coyote time and a jump buffer are design notes. They are not a node port.

## ECS shape

- **Components** own pose and intent: position, velocity, and a jump-buffer or coyote timer as data. The Quick Start ECS page shows components as Rust structs that derive `Component`.
- **Resources** own clocks and tuning shared by every mover. `bevy::time` 0.20.0 documents `Time`, `Fixed` (fixed timestep clock), and `Virtual`.
- **Systems** read intent and write velocity or position. Register them on the fixed schedule, not on a per-node physics callback.
- **Schedule:** `run_fixed_main_schedule` runs `FixedMain` from virtual time (`bevy::time` 0.20.0). Order dependent systems with `.chain()` (ECS page). Do not paste a Godot physics-process function.

## Engine counterparts

| Godot idea | Bevy idiom |
| --- | --- |
| Body that you move yourself | Entity with movement components and a system |
| Step that should stay stable when frame time changes | System on the fixed timestep (`Fixed` / `FixedMain`) |
| Coyote time, jump buffer | Timer data on the entity or a small resource, consumed by the movement system |
| Collision response | Collision response belongs on bevy-physics-3d. |

## Scope

Locomotion here is kinematic data on `FixedUpdate`: intent, velocity, coyote time, and a jump buffer. Collision response belongs on bevy-physics-3d. Do not call `move_and_slide`, `_physics_process`, or `CharacterBody2D`.

```toml
[dependencies]
bevy = "0.20"
```

```rust
#[derive(Component, Default)]
struct PlanarIntent {
    axis: Vec2,
    jump_pressed: bool,
}

#[derive(Component)]
struct KinematicBody {
    velocity: Vec3,
    grounded: bool,
    coyote: f32,
    jump_buffer: f32,
}

#[derive(Resource)]
struct MoveTuning {
    speed: f32,
    jump_speed: f32,
    gravity: f32,
    coyote_time: f32,
    jump_buffer_time: f32,
}

impl Default for MoveTuning {
    fn default() -> Self {
        Self {
            speed: 6.0,
            jump_speed: 8.0,
            gravity: 20.0,
            coyote_time: 0.12,
            jump_buffer_time: 0.12,
        }
    }
}

fn read_move_intent(keys: Res<ButtonInput<KeyCode>>, mut bodies: Query<&mut PlanarIntent>) {
    let mut axis = Vec2::ZERO;
    if keys.pressed(KeyCode::KeyA) {
        axis.x -= 1.0;
    }
    if keys.pressed(KeyCode::KeyD) {
        axis.x += 1.0;
    }
    let jump_pressed = keys.just_pressed(KeyCode::Space);
    for mut intent in &mut bodies {
        intent.axis = axis;
        intent.jump_pressed = jump_pressed;
    }
}

fn step_kinematic(
    time: Res<Time<Fixed>>,
    tuning: Res<MoveTuning>,
    mut bodies: Query<(&mut PlanarIntent, &mut KinematicBody, &mut Transform)>,
) {
    let dt = time.delta_secs();
    for (mut intent, mut body, mut transform) in &mut bodies {
        body.velocity.x = intent.axis.x * tuning.speed;
        if body.grounded {
            body.coyote = tuning.coyote_time;
        } else {
            body.coyote = (body.coyote - dt).max(0.0);
            body.velocity.y -= tuning.gravity * dt;
        }
        if intent.jump_pressed {
            body.jump_buffer = tuning.jump_buffer_time;
            intent.jump_pressed = false;
        } else {
            body.jump_buffer = (body.jump_buffer - dt).max(0.0);
        }
        if body.jump_buffer > 0.0 && body.coyote > 0.0 {
            body.velocity.y = tuning.jump_speed;
            body.jump_buffer = 0.0;
            body.coyote = 0.0;
            body.grounded = false;
        }
        transform.translation += body.velocity * dt;
        if transform.translation.y <= 0.0 {
            transform.translation.y = 0.0;
            body.velocity.y = 0.0;
            body.grounded = true;
        }
    }
}

fn spawn_mover(mut commands: Commands) {
    commands.spawn((
        Transform::default(),
        PlanarIntent::default(),
        KinematicBody {
            velocity: Vec3::ZERO,
            grounded: true,
            coyote: 0.0,
            jump_buffer: 0.0,
        },
    ));
}

pub struct CharacterMovementPlugin;

impl Plugin for CharacterMovementPlugin {
    fn build(&self, app: &mut App) {
        app.init_resource::<MoveTuning>()
            .add_systems(Startup, spawn_mover)
            .add_systems(Update, read_move_intent)
            .add_systems(FixedUpdate, step_kinematic);
    }
}
```

Sample `ButtonInput::just_pressed` in `Update`. `FixedUpdate` can run zero times or several times in one frame, so a press read there is dropped or repeated. The intent component keeps the edge until `FixedUpdate` consumes it.

When a physics skill writes `Grounded`, chain the coyote refill after that write so the timer sees the contact from the same tick.

```rust
#[derive(Component)]
struct Grounded;

#[derive(Component)]
struct CoyoteTimer(f32);

#[derive(Resource)]
struct CoyoteWindow(f32);

fn refill_coyote(window: Res<CoyoteWindow>, mut movers: Query<&mut CoyoteTimer, With<Grounded>>) {
    for mut timer in &mut movers {
        timer.0 = window.0;
    }
}

fn tick_coyote(time: Res<Time<Fixed>>, mut movers: Query<&mut CoyoteTimer, Without<Grounded>>) {
    let dt = time.delta_secs();
    for mut timer in &mut movers {
        timer.0 = (timer.0 - dt).max(0.0);
    }
}

pub struct CoyotePlugin;

impl Plugin for CoyotePlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(CoyoteWindow(0.12)).add_systems(
            FixedUpdate,
            (refill_coyote, tick_coyote).chain(),
        );
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
| An API outside this skill | Load the skill that owns it | A made-up crate or API |

Load [references/ecs-ownership.md](references/ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not step locomotion on raw `Update` when the step must stay stable. WHY: `bevy::time` documents `Fixed` and `run_fixed_main_schedule` (`FixedMain`) for a fixed clock.
- Do not read `ButtonInput::just_pressed` inside `FixedUpdate`. WHY: that schedule can skip a frame or run more than once, so the press is lost or applied twice.
- Do not call `move_and_slide`, `_physics_process`, or `CharacterBody2D`. WHY: those are Godot types. This skill only owns ECS movement data.
- Do not invent a character-controller or shape-cast API. WHY: this skill owns kinematic intent and the fixed step; contact queries live on the physics skills.
- Do not mutably query the same movement component from two unordered systems. WHY: systems run in parallel unless `.chain()` orders them.

## Reference

The library pin on bevy-master stays **0.20.0**. Official pages stay on the unversioned site.

### Official Documentation
- [Quick Start: ECS](https://bevy.org/learn/quick-start/getting-started/ecs/)  -  Entities, `Component`, systems, `Query`, `Commands`, and `.chain()`.
- [Fixed timestep](https://bevy.org/learn/quick-start/getting-started/ecs/)  -  `Fixed` and `FixedMain` via `run_fixed_main_schedule` on the ECS schedule page.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  ECS ownership, schedules, and which Bevy skill to load.

#### Complements
- [bevy-physics-3d](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-physics-3d/SKILL.md)  -  Collision and physics solvers. Player motion stays in this skill.
- [godot-characterbody-2d](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-characterbody-2d/SKILL.md)  -  Equivalent Godot skill. Do not import Godot types.

#### Downstream / consumers
- Genre skills cover loop and encounter design.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Bevy router.
