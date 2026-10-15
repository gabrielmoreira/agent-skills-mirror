---
name: bevy-adapt-mobile-to-desktop
description: "Bevy ECS skill for adapting a Bevy mobile game to desktop. Keywords: Bevy, desktop, mouse, keyboard, adapt, window."
---

# Bevy adapt mobile to desktop

## When to use

Load this when a touch-first game gains a window, mouse, and keyboard. Window setup is bevy-platform-desktop.

## ECS shape

- **Window:** `Window`, `WindowMode`, and `PrimaryWindow`.
- **Input:** keyboard, mouse, and gamepad features are named on the crate page and already used by bevy-input-handling.
- **Pointer:** `CursorOptions` on the primary window. `CursorGrabMode::None`, `Confined`, or `Locked`.

## Desktop choices

| Need | Bevy idiom |
| --- | --- |
| On-screen buttons | Keyboard and mouse via bevy-input-handling, writing the same intent component. |
| Wider layout | A wider `WindowResolution` on the primary `Window`. |
| Pointer lock | `CursorOptions.grab_mode = CursorGrabMode::Locked` and `visible = false`. |

## Scope

- Keyboard and mouse write a `MoveIntent` component. Touch buttons can keep writing that same component.
- Window mode, resolution, present mode, and cursor grab live on the primary window entity.

## Examples

```toml
[package]
name = "desktop_port"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = "0.20"
```

Open a windowed 1920x1080 view and lock the pointer while aiming.

```rust
use bevy::window::{
    CursorGrabMode, CursorOptions, MonitorSelection, PresentMode, PrimaryWindow, WindowMode,
    WindowResolution,
};

fn desktop_window(mut windows: Query<&mut Window, With<PrimaryWindow>>) {
    for mut window in &mut windows {
        window.mode = WindowMode::Windowed;
        window.resolution = WindowResolution::new(1920, 1080);
        window.title = "Desktop".to_string();
        window.present_mode = PresentMode::AutoVsync;
    }
}

fn unlock_framerate(mut windows: Query<&mut Window, With<PrimaryWindow>>) {
    for mut window in &mut windows {
        window.present_mode = PresentMode::AutoNoVsync;
    }
}

fn borderless(mut windows: Query<&mut Window, With<PrimaryWindow>>) {
    for mut window in &mut windows {
        window.mode = WindowMode::BorderlessFullscreen(MonitorSelection::Current);
    }
}

#[derive(Component)]
struct Aiming;

fn grab_cursor(
    mut cursors: Query<&mut CursorOptions, With<PrimaryWindow>>,
    aiming: Query<(), With<Aiming>>,
) {
    let locked = !aiming.is_empty();
    for mut cursor in &mut cursors {
        cursor.visible = !locked;
        cursor.grab_mode = if locked {
            CursorGrabMode::Locked
        } else {
            CursorGrabMode::None
        };
    }
}
```

WASD replaces on-screen sticks. The gameplay system reads `MoveIntent`, not the key codes.

```rust
use bevy::window::{MonitorSelection, PrimaryWindow, VideoModeSelection, WindowMode};

#[derive(Component, Default)]
struct MoveIntent(Vec2);

fn read_wasd(keys: Res<ButtonInput<KeyCode>>, mut intents: Query<&mut MoveIntent>) {
    let mut dir = Vec2::ZERO;
    if keys.pressed(KeyCode::KeyA) {
        dir.x -= 1.0;
    }
    if keys.pressed(KeyCode::KeyD) {
        dir.x += 1.0;
    }
    if keys.pressed(KeyCode::KeyW) {
        dir.y += 1.0;
    }
    if keys.pressed(KeyCode::KeyS) {
        dir.y -= 1.0;
    }
    for mut intent in &mut intents {
        intent.0 = dir;
    }
}

fn toggle_fullscreen(
    keys: Res<ButtonInput<KeyCode>>,
    mut windows: Query<&mut Window, With<PrimaryWindow>>,
) {
    if !keys.just_pressed(KeyCode::F11) {
        return;
    }
    for mut window in &mut windows {
        window.mode = match window.mode {
            WindowMode::Windowed => {
                WindowMode::Fullscreen(MonitorSelection::Primary, VideoModeSelection::Current)
            }
            _ => WindowMode::Windowed,
        };
    }
}
```

Captured look uses the frame's summed motion.

```rust
use bevy::input::mouse::AccumulatedMouseMotion;

#[derive(Component)]
struct LookRig;

fn apply_look(
    motion: Res<AccumulatedMouseMotion>,
    mut rigs: Query<&mut Transform, With<LookRig>>,
) {
    for mut transform in &mut rigs {
        transform.rotate_y(-motion.delta.x * 0.002);
    }
}

pub struct LookPlugin;

impl Plugin for LookPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Update, apply_look);
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
| Per-entity data | `Component` + `Query` | A value stored off the entity |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Check the official docs first | A made-up crate or API |

Load [references/ecs-ownership.md](adapt-mobile-to-desktop-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No second input path that bypasses `MoveIntent`. WHY: keyboard, mouse, and touch must write the same component so gameplay stays device-agnostic.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Permalinks stay unversioned.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [Window examples](https://github.com/bevyengine/bevy/tree/latest/examples/window) - `WindowMode`, present mode, and pointer grab.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-platform-desktop](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-platform-desktop/SKILL.md) - Window.
- [bevy-input-handling](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-input-handling/SKILL.md) - Keyboard, mouse, gamepad.

#### Complements
- [bevy-adapt-desktop-to-mobile](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-adapt-desktop-to-mobile/SKILL.md) - The reverse adapt.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
