---
name: bevy-platform-web
description: "Ship a Bevy 0.20 app to the browser: wasm32 canvas Window, one of webgl2 or webgpu, and asset paths the page can serve. Use when the same ECS app must run in a browser. Keywords: Bevy, wasm, web, webgl2, webgpu, canvas, Window."
---

# Bevy web platform

## When to use

Load this when the same app should run in a browser. Packaging pipelines are not specified here.

## ECS shape

- **Features opened:** `web` (browser APIs, wasm32 only), `webgl2` (limitations so Wasm can use WebGL2), `webgpu` (overrides webgl2; Wasm with WebGPU only).
- **Asset note:** `http` and `https` features enable remote asset download and warn about security. `web_asset_cache` caches downloads and currently never invalidates entries.
- **Clipboard:** `clipboard_image` says it is not supported on WASM.
- **Window:** the same `Window` component describes the canvas. Set `canvas`, `fit_canvas_to_parent`, and `resolution` on the primary window.

## Feature choice

| Need | Bevy path |
| --- | --- |
| Browser build | `wasm32-unknown-unknown`. Enable `webgl2` or `webgpu` in Cargo; those two features conflict. |
| Graphics backend | `webgl2` or `webgpu`. Enable one. |
| Remote assets | `http` or `https`. `web_asset_cache` stores downloads and does not invalidate them. |

## Scope

- The canvas is a `Window`. Point `canvas` at a DOM id and turn on `fit_canvas_to_parent` so the canvas tracks its parent.
- `webgl2` and `webgpu` are Cargo features. They are not components. Enable one of them for a wasm32 target.
- `clipboard_image` is not available on wasm. Text clipboard stays on the window APIs that default features already include.

## Examples

```toml
[dependencies]
bevy = { version = "0.20", features = ["webgl2"] }
```

Open the primary window on a canvas element and keep it sized to that element's parent.

```rust
use bevy::window::{PrimaryWindow, WindowResolution};

fn main() {
    App::new()
        .add_plugins(DefaultPlugins.set(WindowPlugin {
            primary_window: Some(Window {
                title: "Browser".into(),
                canvas: Some("#bevy".into()),
                fit_canvas_to_parent: true,
                prevent_default_event_handling: true,
                resolution: WindowResolution::new(1280, 720),
                ..default()
            }),
            ..default()
        }))
        .run();
}
```

A running app can still retarget the canvas and the logical resolution.

```rust
use bevy::window::PrimaryWindow;

fn bind_canvas(mut windows: Query<&mut Window, With<PrimaryWindow>>) {
    let Ok(mut window) = windows.single_mut() else {
        return;
    };
    if window.canvas.is_none() {
        window.canvas = Some("#bevy".to_string());
    }
    window.fit_canvas_to_parent = true;
    window.resolution.set(1280.0, 720.0);
}
```

Load a relative asset path. Remote `http` URLs need the `http` or `https` feature; this path stays inside the asset folder the bundler serves.

```rust
fn spawn_sprite(mut commands: Commands, asset_server: Res<AssetServer>) {
    let image = asset_server.load("sprites/player.png");
    commands.spawn((Camera2d, Sprite::from_image(image)));
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
| Browser canvas | `Window.canvas` and `fit_canvas_to_parent` | A title-only window with no canvas id |
| Graphics backend | Exactly one of `webgl2` or `webgpu` | Enabling both Cargo features |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Check the official documentation | A made-up crate or API |

Load [references/ecs-ownership.md](references/ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- Do not name another engine's HTML export presets in Bevy Cargo features. WHY: the browser target is `wasm32-unknown-unknown` plus `webgl2` or `webgpu`.
- Do not import another engine's node types into Bevy systems. WHY: those types are not components and will not schedule.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: this skill only names documented Bevy crates and modules.

## Reference

Official links stay on unversioned `latest` pages. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-platform-desktop](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-platform-desktop/SKILL.md) - Window component shared with desktop.

#### Complements
- [godot-platform-web](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-platform-web/SKILL.md) - Godot package for browser builds.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
