---
name: bevy-camera-systems
description: "Docs-first stub for Bevy cameras. Godot counterpart: godot-camera-systems. Not a full port. Keywords: Bevy, Camera, Camera2d, Camera3d, Transform."
---

# Bevy camera systems (docs-first stub)

Not a full port. A camera is an entity with camera components and a `Transform`. Follow and shake are not copied from Godot.

## When to use

Load this when a view must render 2D or 3D. `bevy::camera` on docs.rs `latest` (0.20.0) and the `two_passes` example embedded there are the sources for the names below.

## ECS shape

- **Components:** `Camera` is the viewpoint (projection and render target). A `Camera` with no render graph errors at runtime. `Camera2d` enables the 2D graph and requires `Camera`, `Projection`, and `Frustum`. `Camera3d` enables the main 3D graph and requires `Camera` and `Projection`. 3D space is right-handed: X right, Y up, Z back, so forward is -Z.
- **Spawn:** the example uses `commands.spawn((Camera3d::default(), Transform::from_xyz(...).looking_at(Vec3::ZERO, Vec3::Y)))`. A second camera sets `Camera { order: 1, clear_color: ClearColorConfig::None, ..default() }` so it draws on top without clearing.
- **Query:** systems may take `(&mut Camera, &GlobalTransform)` with `With<Camera3d>`. `Camera::viewport_to_world_2d` maps a viewport position to a 2D world position for an orthographic camera along Z.
- **Schedule:** spawn on `Startup`. A follow system, if you write one, is your own `Update` system over `Transform`. This file does not name a follow component.

## Godot idea to Bevy idiom

| Idea | Bevy idiom (idea only) |
| --- | --- |
| Current camera | An entity with `Camera2d` or `Camera3d` |
| Camera pose | `Transform` on that entity |
| Draw order / overlay | `Camera.order` and `ClearColorConfig::None` |
| Screen point to 2D world | `viewport_to_world_2d` with `GlobalTransform` |

## Gaps

- Camera follow, look-at smoothing, and screen shake were not on the opened pages. Do not invent those components.
- Custom `CameraRenderGraph` setup was named as a requirement, not opened as a recipe.
- Split-screen and render-target textures were not opened beyond the `order` field in the example.


## Expert Knowledge Delta

Library target in prose: **Bevy 0.20.0**. Lattice URLs stay unversioned.

Opened canon only: `Component`, `Resource`, `Query`, `Commands`, `Startup`, `Update`, `Fixed` / `FixedMain` (`bevy::time`), `.chain()`, `Plugin`, `DefaultPlugins`, `MinimalPlugins`. Messages and observers are an ownership slot. This file does not invent their struct APIs. Systems run in parallel unless `.chain()` orders the ones that conflict.

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
| An API this skill did not open | A Gaps row | A fabricated crate (solver, navmesh module, net, XR) |

Load `references/a-gate-notes.md` for the same table plus the gap rule.

## NEVER

- Do not put `/0.20.0/` in lattice URLs. WHY: permalinks stay on `latest`. The 0.20.0 pin belongs in prose once.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: those rows are gaps, blocked, or revisit.

- No Godot camera node types. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No shake, spring-arm, or follow APIs this file did not open. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No third-party camera crates. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No Creation Station content. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No umbrella skill over Godot and Bevy. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- Do not mark this row `ported`. It is `docs_mapped`. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/)  -  Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/)  -  Unversioned API index.
- [bevy::camera](https://docs.rs/bevy/latest/bevy/camera/index.html)  -  `Camera`, `Camera2d`, `Camera3d`.
- [Camera](https://docs.rs/bevy/latest/bevy/camera/struct.Camera.html)  -  Viewpoint, `viewport_to_world_2d`, required render graph.
- [Camera3d](https://docs.rs/bevy/latest/bevy/camera/struct.Camera3d.html)  -  Right-handed 3D camera.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch.

### Related Skills

#### Prerequisites
- [bevy-master](../SKILL.md)  -  Who owns which piece of state.
- [bevy-ecs-composition](ecs-composition.md)  -  Spawn tuples and systems.

#### Complements
- [bevy-input-handling](input-handling.md)  -  Mouse motion a camera system may read.
- [bevy-character-movement](character-movement.md)  -  Actor the view may track. Tracking logic is still a gap here.
- [godot-camera-systems](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-camera-systems/SKILL.md)  -  Godot counterpart. Source idea only.

#### Downstream / consumers
- [bevy-asset-scenes](asset-scenes.md)  -  Scenes that include a camera entity.

#### Master
- [bevy-master](../SKILL.md)  -  Bevy router.
