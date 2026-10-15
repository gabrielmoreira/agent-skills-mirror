---
name: bevy-adapt-desktop-to-mobile
description: "Bevy ECS skill for adapting a Bevy desktop game to mobile. Keywords: Bevy, mobile, touch, UI, adapt."
---

# Bevy adapt desktop to mobile

## When to use

Load this when a desktop window game must accept touch and a smaller layout. Platform features are on bevy-platform-mobile.

## ECS shape

- **Input:** `Touches` lists active contacts. Action mapping lives on bevy-input-handling.
- **UI:** enlarge `Node` hit targets and pad the root with a safe-inset `Resource`. `WindowResolution` sets the logical size and an optional scale-factor override. `WindowScaleFactorChanged` reports a live dpi change.
- **Textures:** ASTC is a compressed texture format for mobile GPUs. Upload still goes through `Assets<Image>`.

```rust
fn configure_window(mut windows: Query<&mut Window>) {
    let Ok(mut window) = windows.single_mut() else {
        return;
    };
    window.resolution.set(720.0, 1280.0);
    window.resolution.set_scale_factor_override(Some(2.0));
}
```

```rust
#[derive(Resource, Default)]
struct LastTouch(Option<Vec2>);

fn track_touch(touches: Res<Touches>, mut last: ResMut<LastTouch>) {
    last.0 = touches.iter().next().map(|touch| touch.position());
}
```

```rust
#[derive(Component)]
struct TouchTarget;

#[derive(Component)]
struct HudRoot;

#[derive(Resource)]
struct SafeInsets {
    top: f32,
    bottom: f32,
}

fn enlarge_targets(mut nodes: Query<&mut Node, With<TouchTarget>>) {
    for mut node in &mut nodes {
        node.min_width = Val::Px(88.0);
        node.min_height = Val::Px(88.0);
    }
}

fn pad_hud(insets: Res<SafeInsets>, mut roots: Query<&mut Node, With<HudRoot>>) {
    for mut node in &mut roots {
        node.padding = UiRect {
            top: Val::Px(insets.top),
            bottom: Val::Px(insets.bottom),
            left: Val::Px(12.0),
            right: Val::Px(12.0),
        };
    }
}
```

```rust
use bevy::window::WindowScaleFactorChanged;

fn follow_dpi(
    mut scale_events: MessageReader<WindowScaleFactorChanged>,
    mut ui_scale: ResMut<UiScale>,
) {
    for event in scale_events.read() {
        ui_scale.0 = event.scale_factor as f32;
    }
}
```

```toml
[dependencies]
bevy = "0.20"
```

## Adapt choices

| Need | Bevy approach |
| --- | --- |
| Pointer | `Touches` for contacts. Pointer position on a desktop window is `Window::cursor_position`. |
| Hover-only menus | Actions that require a hover state need a pressed or tapped path as well. |
| Safe margins | `SafeInsets` resource applied as `Node` padding. |

## Scope

- Store listings and OS permission dialogs are outside this skill. Layout, touch, and dpi live in the systems above.
- Platform packaging stays on bevy-platform-mobile.

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
| Per-entity data | `Component` + `Query` | A script field copied onto the entity |
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

- No export-preset or touch-emulation names in Bevy code. WHY: `Touches`, `Window`, and `UiScale` are the documented Bevy pieces.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

Official links stay on bevy.org. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-platform-mobile](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-platform-mobile/SKILL.md) - Android and touch features.
- [bevy-ui-layout](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ui-layout/SKILL.md) - Reflow the HUD.

#### Complements
- [bevy-adapt-mobile-to-desktop](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-adapt-mobile-to-desktop/SKILL.md) - The reverse adapt.
- [godot-adapt-desktop-to-mobile](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-adapt-desktop-to-mobile/SKILL.md) - Same topic on the Godot track.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
