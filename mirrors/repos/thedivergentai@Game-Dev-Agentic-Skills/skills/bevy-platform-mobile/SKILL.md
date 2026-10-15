---
name: bevy-platform-mobile
description: "Bevy ECS skill for mobile. Keywords: Bevy, mobile, android, touch, ASTC, gestures."
---

# Bevy mobile platform

## When to use

Load this when targeting touch devices. Store listings and OS permission dialogs stay outside the crate. XR is a separate topic.

## ECS shape

- **Input:** `Touches` holds active contacts. `PinchGesture` is a message for two-finger pinch on iOS and macOS.
- **Android:** enable the `android-game-activity` feature. `android-native-activity` is the legacy activity.
- **Power:** `WinitSettings::mobile()` waits on input while focused and drops to a one-second wait when unfocused.
- **iOS edges:** `Window::preferred_screen_edges_deferring_system_gestures` takes a `ScreenEdge`.
- **Textures:** ASTC shows up as `TextureFormat::Astc` on an `Image` descriptor after the asset loads.

## Examples

```toml
[dependencies]
bevy = { version = "0.20", features = ["android-game-activity"] }
```

Mobile update mode sleeps the loop when the window is backgrounded.

```rust
use bevy::winit::WinitSettings;

fn main() {
    App::new()
        .insert_resource(WinitSettings::mobile())
        .add_plugins(DefaultPlugins)
        .run();
}
```

A stick zone turns the first contact into a unit axis. Keyboard and mouse stay on bevy-input-handling.

```rust
#[derive(Component, Default)]
struct MoveIntent {
    axis: Vec2,
}

#[derive(Resource)]
struct StickZone {
    center: Vec2,
    radius: f32,
}

fn read_stick(touches: Res<Touches>, zone: Res<StickZone>, mut intents: Query<&mut MoveIntent>) {
    let Some(touch) = touches.iter().next() else {
        return;
    };
    let offset = touch.position() - zone.center;
    let length = offset.length();
    let axis = if length <= zone.radius && length > 0.0 {
        offset / zone.radius
    } else if length > zone.radius {
        offset / length
    } else {
        Vec2::ZERO
    };
    for mut intent in &mut intents {
        intent.axis = axis;
    }
}
```

Pinch messages adjust a zoom resource. Registering messages is the engine's job for built-in gesture types.

```rust
use bevy::input::gestures::PinchGesture;

#[derive(Resource)]
struct CameraZoom(f32);

fn apply_pinch(mut pinches: MessageReader<PinchGesture>, mut zoom: ResMut<CameraZoom>) {
    for pinch in pinches.read() {
        zoom.0 = (zoom.0 + pinch.0).clamp(0.25, 4.0);
    }
}
```

Defer system gestures on every screen edge, and count ASTC images already in the asset store.

```rust
use bevy::render::render_resource::TextureFormat;
use bevy::window::PrimaryWindow;
use bevy::window::ScreenEdge;

fn defer_system_gestures(mut windows: Query<&mut Window, With<PrimaryWindow>>) {
    let Ok(mut window) = windows.single_mut() else {
        return;
    };
    window.preferred_screen_edges_deferring_system_gestures = ScreenEdge::All;
}

#[derive(Resource, Default)]
struct AstcCount(usize);

fn count_astc(images: Res<Assets<Image>>, mut count: ResMut<AstcCount>) {
    count.0 = images
        .iter()
        .filter(|(_, image)| matches!(image.texture_descriptor.format, TextureFormat::Astc { .. }))
        .count();
}
```

## Same job, Bevy types

| Design | Bevy idiom |
| --- | --- |
| Touch | `Touches` on `Update` |
| Android activity | `android-game-activity` Cargo feature |
| Safe area | `ScreenEdge` on the primary `Window`, plus UI padding from bevy-adapt-desktop-to-mobile |
| Background FPS | `WinitSettings::mobile()` |

## Scope

Packaging, signing, and store permission prompts are outside this skill. Touch, pinch, screen edges, ASTC detection, and the mobile update mode are the systems above.

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
| Per-entity data | `Component` + `Query` | A scene-tree script hung on the entity |
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

- No Godot touch-screen or safe-margin project settings. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

- No Godot types in Bevy code. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

Official pages stay on unversioned bevy.org URLs. The library pin on bevy-master stays **0.20.0**. `ScreenEdge` is a field on `Window`. Touch contacts stay on `Touches`; they are not a separate event struct.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-input-handling](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-input-handling/SKILL.md) - Other devices.
- [bevy-platform-desktop](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-platform-desktop/SKILL.md) - Window shell.

#### Complements
- [bevy-adapt-desktop-to-mobile](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-adapt-desktop-to-mobile/SKILL.md) - Layout and input adapt.
- [godot-platform-mobile](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-platform-mobile/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
