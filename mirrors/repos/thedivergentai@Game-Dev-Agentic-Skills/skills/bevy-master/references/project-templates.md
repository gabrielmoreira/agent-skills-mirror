---
name: bevy-project-templates
description: "Bevy ECS skill for project templates. Keywords: Bevy, template, cargo, features, 2d, 3d, ui."
---

# Bevy project templates

## When to use

Load this when choosing a starting Cargo feature set. App construction details stay on bevy-project-foundations. This file does not ship a template repository.

## ECS shape

- **Profiles:** `default` enables `2d`, `3d`, `ui`, and `audio`. Turn default features off and pick one profile when the binary should stay smaller.
- **Windowed games:** `DefaultPlugins` brings the window, input, and the renderer for the features you enabled.
- **Headless:** `MinimalPlugins` schedules the app with no window and no renderer. Pair it with `default-features = false`.

## Examples

A 2D crate disables the default set and enables the `2d` profile only. Swap the feature for `3d` or `ui` when that is the whole binary.

```toml
[package]
name = "game"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = { version = "0.20", default-features = false, features = ["2d"] }
```

The 2D starter spawns a camera. The 3D starter does the same with a 3D camera. Both assume `DefaultPlugins`.

```rust
fn setup_2d(mut commands: Commands) {
    commands.spawn(Camera2d);
}

pub struct FlatPlugin;

impl Plugin for FlatPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Startup, setup_2d);
    }
}

fn main() {
    App::new().add_plugins((DefaultPlugins, FlatPlugin)).run();
}
```

```rust
fn setup_3d(mut commands: Commands) {
    commands.spawn((Camera3d::default(), Transform::from_xyz(0.0, 2.0, 6.0)));
}

pub struct ScenePlugin;

impl Plugin for ScenePlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Startup, setup_3d);
    }
}
```

A headless tool uses `MinimalPlugins` and a plain update system.

```rust
fn tick(mut frames: ResMut<FrameCount>) {
    frames.0 += 1;
}

#[derive(Resource, Default)]
struct FrameCount(u32);

fn main() {
    App::new()
        .add_plugins(MinimalPlugins)
        .init_resource::<FrameCount>()
        .add_systems(Update, tick)
        .run();
}
```

## Same job, Bevy types

| Design | Bevy idiom |
| --- | --- |
| 2D starter | Cargo feature `2d`, `DefaultPlugins`, `Camera2d` |
| 3D starter | Cargo feature `3d`, `DefaultPlugins`, `Camera3d` |
| UI tool | Cargo feature `ui` plus `DefaultPlugins` |
| Headless | `default-features = false` and `MinimalPlugins` |

## Scope

Gitignore and CI files belong to the repository, not to the engine. The feature flag and the plugin set above are the starting point.

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

Load [references/ecs-ownership.md](project-templates-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No Godot project.godot template or export presets. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

- No Godot types in Bevy code. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

Official pages stay on unversioned bevy.org URLs. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub.
- [bevy-project-foundations](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-project-foundations/SKILL.md) - Cargo app shell.

#### Complements
- [bevy-platform-desktop](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-platform-desktop/SKILL.md) - Windowed targets.
- [godot-project-templates](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-project-templates/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
