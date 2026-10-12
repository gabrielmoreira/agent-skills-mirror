---
name: bevy-adapt-2d-to-3d
description: "Docs-first stub for moving a Bevy game from 2D to 3D. Godot counterpart: godot-adapt-2d-to-3d. Keywords: Bevy, 2D, 3D, adapt, camera, sprite."
---

# Bevy adapt 2D to 3D (docs-first stub)

Not a full port. Docs-first stub. Godot counterpart: godot-adapt-2d-to-3d.

## When to use

Load this when a 2D design should gain a 3D camera and meshes. Keep gameplay components. Swap render and motion representations.

## ECS shape

- **Cameras:** `Camera2d` and `Camera3d` are already documented on bevy-camera-systems. An entity should not keep both as if they were one camera mode unless that skill says so.
- **Draw:** `Sprite` is 2D. Meshes and `StandardMaterial` are 3D (bevy-3d-materials).
- **Features:** the crate page separates `2d` and `3d` profiles. Enabling 3D does not delete 2D types.
- **Motion:** bevy-character-movement stays the locomotion skill. A 3D velocity is still your component until a solver exists.

## Godot idea to Bevy idiom

| Idea | Bevy idiom (idea only) |
| --- | --- |
| Sprite actor | A mesh entity plus the same gameplay components. |
| 2D camera | Camera3d via bevy-camera-systems. |
| Tile world | No tilemap type. See bevy-tilemap and bevy-3d-world-building. |

## Gaps

- A conversion helper that rewrites entities from 2D to 3D was not opened.
- Physics solver choice is still open on both physics skills.


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

- No Godot node convert-to-3D operations. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.

- No Godot types in Bevy code. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No Creation Station content. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No umbrella skill over Godot and Bevy. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- Do not mark this row `ported`. It is `docs_mapped`. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/) - Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/) - Unversioned API index. Feature list opened for 0.20.0.
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](../SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](ecs-composition.md) - Components and systems.
- [bevy-camera-systems](camera-systems.md) - Camera2d and Camera3d.
- [bevy-3d-world-building](3d-world-building.md) - Level assembly.

#### Complements
- [bevy-adapt-3d-to-2d](adapt-3d-to-2d.md) - The reverse adapt.
- [godot-adapt-2d-to-3d](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-adapt-2d-to-3d/SKILL.md) - Godot counterpart. Source idea only.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](../SKILL.md) - Bevy router.
