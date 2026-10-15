---
name: bevy-input-handling
description: "Bevy ECS skill for player input. Keywords: Bevy, ButtonInput, KeyCode, MouseButton, Gamepad."
---

# Bevy input handling

## When to use

Load this when a system should read keyboard, mouse, or gamepad state. The `bevy::input` module on Bevy 0.20 is the source for the names below.

## ECS shape

- **Plugin:** `InputPlugin` adds input from keyboard, mouse, gamepad, and touch. It ships inside the usual app plugins. `InputSystems` labels the systems that refresh that data.
- **Keyboard resource:** `Res<ButtonInput<KeyCode>>`. `KeyCode` is the physical key (layout-stable). `Res<ButtonInput<Key>>` is the logical key. The keyboard example uses `pressed`, `just_pressed`, and `just_released`.
- **Mouse:** `mouse_button_input_system` writes `ButtonInput<MouseButton>` from `MouseButtonInput`. `AccumulatedMouseMotion` and `AccumulatedMouseScroll` are resources reset every frame. `MouseMotion` and `MouseWheel` are the underlying events.
- **Gamepad:** `Gamepad` stores a connected pad's metadata (`GamepadButton`, `GamepadAxis`). Connection and axis changes arrive as `GamepadConnectionEvent`, `GamepadAxisChangedEvent`, and `GamepadButtonChangedEvent`. `GamepadRumbleRequest` is the force-feedback event.
- **Schedule:** read these resources from a system on `Update` (or a schedule you already chain). Do not invent an input-map resource.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Action just pressed | `ButtonInput::just_pressed` on `KeyCode` or `MouseButton` |
| Action held | `ButtonInput::pressed` |
| Physical WASD vs symbol keys | `KeyCode` for location, `Key` for the character |
| Mouse look delta | `AccumulatedMouseMotion` (reset each frame) |
| Controller | `Gamepad` plus the gamepad events listed above |

## Scope

Keyboard, mouse, and gamepad state live on `ButtonInput` and `Gamepad`. Named actions, a jump buffer, a radial stick deadzone, and the last active device are resources you define. Glyph art is a UI concern once that device flag is set.

## Examples

```toml
[dependencies]
bevy = "0.20"
```

Read edges in `Update`. `FixedUpdate` can run zero or several times per frame, so a press sampled there is dropped or repeated. Store the edge on an intent component and let the fixed step consume it.

```rust
#[derive(Component, Default)]
struct MoveIntent {
    axis: Vec2,
    jump: bool,
}

fn read_keys(keys: Res<ButtonInput<KeyCode>>, mut intents: Query<&mut MoveIntent>) {
    let mut axis = Vec2::ZERO;
    if keys.pressed(KeyCode::KeyA) || keys.pressed(KeyCode::ArrowLeft) {
        axis.x -= 1.0;
    }
    if keys.pressed(KeyCode::KeyD) || keys.pressed(KeyCode::ArrowRight) {
        axis.x += 1.0;
    }
    if keys.pressed(KeyCode::KeyW) || keys.pressed(KeyCode::ArrowUp) {
        axis.y += 1.0;
    }
    if keys.pressed(KeyCode::KeyS) || keys.pressed(KeyCode::ArrowDown) {
        axis.y -= 1.0;
    }
    let jump = keys.just_pressed(KeyCode::Space);
    for mut intent in &mut intents {
        intent.axis = axis;
        if jump {
            intent.jump = true;
        }
    }
}

use bevy::input::mouse::AccumulatedMouseMotion;

fn look(motion: Res<AccumulatedMouseMotion>, mut cameras: Query<&mut Transform, With<LookCam>>) {
    for mut tf in &mut cameras {
        tf.rotate_y(-motion.delta.x * 0.002);
        tf.rotate_local_x(-motion.delta.y * 0.002);
    }
}

#[derive(Component)]
struct LookCam;
```

A radial deadzone drops stick drift, then rescales the remaining range so full deflection still reaches length 1. The jump buffer keeps a press that landed a few frames early.

```rust
#[derive(Component, Default)]
struct MoveIntent {
    axis: Vec2,
    jump: bool,
}

fn radial_deadzone(stick: Vec2, deadzone: f32) -> Vec2 {
    let mag = stick.length();
    if mag <= deadzone || mag == 0.0 {
        return Vec2::ZERO;
    }
    let scaled = ((mag - deadzone) / (1.0 - deadzone)).clamp(0.0, 1.0);
    stick / mag * scaled
}

fn read_pad(pads: Query<&Gamepad>, mut intents: Query<&mut MoveIntent>) {
    let Some(pad) = pads.iter().next() else {
        return;
    };
    let stick = Vec2::new(
        pad.get(GamepadAxis::LeftStickX).unwrap_or(0.0),
        pad.get(GamepadAxis::LeftStickY).unwrap_or(0.0),
    );
    let axis = radial_deadzone(stick, 0.15);
    let jump = pad.just_pressed(GamepadButton::South);
    for mut intent in &mut intents {
        if axis.length_squared() > 0.0 {
            intent.axis = axis;
        }
        if jump {
            intent.jump = true;
        }
    }
}

#[derive(Resource)]
struct JumpBuffer {
    remaining: f32,
    window: f32,
}

fn arm_jump_buffer(time: Res<Time>, mut intents: Query<&mut MoveIntent>, mut buffer: ResMut<JumpBuffer>) {
    let dt = time.delta_secs();
    buffer.remaining = (buffer.remaining - dt).max(0.0);
    for mut intent in &mut intents {
        if intent.jump {
            buffer.remaining = buffer.window;
            intent.jump = false;
        }
    }
}

#[derive(Clone, Copy, PartialEq, Eq, Default)]
enum DeviceKind {
    #[default]
    Keyboard,
    Gamepad,
}

#[derive(Resource, Default)]
struct LastDevice(DeviceKind);

fn track_device(
    keys: Res<ButtonInput<KeyCode>>,
    mouse: Res<ButtonInput<MouseButton>>,
    pads: Query<&Gamepad>,
    mut last: ResMut<LastDevice>,
) {
    if keys.get_pressed().next().is_some() || mouse.get_pressed().next().is_some() {
        last.0 = DeviceKind::Keyboard;
    }
    for pad in &pads {
        if pad.get_pressed().next().is_some() {
            last.0 = DeviceKind::Gamepad;
        }
    }
}

pub struct InputHandlingPlugin;

impl Plugin for InputHandlingPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(JumpBuffer {
            remaining: 0.0,
            window: 0.12,
        })
        .init_resource::<LastDevice>()
        .add_systems(Update, (read_pad, track_device, arm_jump_buffer).chain());
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

- No Godot input-map, event, or device types. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No APIs this file did not open (`pressed`, `just_pressed`, `just_released` are the button methods cited). WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No third-party input crates. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- `bevy crate` - API index for this skill's types.
- `bevy::input` - `ButtonInput`, `InputPlugin`, and the device modules.
- `ButtonInput` - `pressed`, `just_pressed`, `just_released`, `KeyCode`, and `Key`.
- `bevy::input::mouse` - `MouseButton`, motion, and scroll resources.
- `bevy::input::gamepad` - `Gamepad` and connection events.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Who owns which piece of state.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md)  -  Systems and `Query`.

#### Complements
- [bevy-character-movement](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-character-movement/SKILL.md)  -  Motion that consumes this input on the fixed timestep.
- [bevy-camera-systems](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-camera-systems/SKILL.md)  -  Viewpoint that may read mouse motion.
- [godot-input-handling](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-input-handling/SKILL.md)  -  Equivalent Godot skill.

#### Downstream / consumers
- [bevy-audio-systems](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-audio-systems/SKILL.md)  -  The audio control example reads `ButtonInput<KeyCode>` to pause and mute.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Bevy router.
