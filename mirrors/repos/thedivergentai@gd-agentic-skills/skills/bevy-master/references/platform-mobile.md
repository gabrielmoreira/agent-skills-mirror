---
name: bevy-platform-mobile
description: "Docs-first stub for Bevy mobile. Godot counterpart: godot-platform-mobile. Keywords: Bevy, mobile, android, touch, ASTC, gestures."
---

# Bevy mobile platform (docs-first stub)

Not a full port. Docs-first stub. Godot counterpart: godot-platform-mobile.

## When to use

Load this when targeting touch devices. Safe-area and store-listing steps were not opened. XR is not this skill.

## ECS shape

- **Input features:** `touch` (enabled by bevy_window) and `gestures` (enabled by bevy_window).
- **Android:** `android-game-activity` is the default Android activity. `android-native-activity` is marked legacy.
- **Textures:** `compressed_image_saver` mentions ASTC for mobile via an environment variable. The variable name's behavior was not opened beyond that blurb.
- **Log:** `bevy::log` says it configures platform log handlers including Android. Handler setup was not opened.

## Godot idea to Bevy idiom

| Idea | Bevy idiom (idea only) |
| --- | --- |
| Touch | The touch feature. Button mapping was not opened. See bevy-input-handling for keyboard and mouse. |
| Android activity | android-game-activity feature. |
| Safe area | Unverified. No safe-area type was on the window page summary. |

## Gaps

- iOS-specific features were not named in the opened feature list except `ScreenEdge` on the window page, which documents a winit iOS screen-edge correspondence. Rules were not opened.
- Store packaging, permissions, and safe-area insets were not opened.


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

- No Godot touch-screen or safe-margin project settings. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.

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
- [bevy::window](https://docs.rs/bevy/latest/bevy/window/index.html) - `ScreenEdge` mentions winit iOS. Touch events were not listed as their own struct in the opened summary.

### Related Skills

#### Prerequisites
- [bevy-master](../SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](ecs-composition.md) - Components and systems.
- [bevy-input-handling](input-handling.md) - Other devices.
- [bevy-platform-desktop](platform-desktop.md) - Window shell.

#### Complements
- [bevy-adapt-desktop-to-mobile](adapt-desktop-to-mobile.md) - Layout and input adapt.
- [godot-platform-mobile](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-platform-mobile/SKILL.md) - Godot counterpart. Source idea only.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](../SKILL.md) - Bevy router.
