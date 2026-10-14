---
name: bevy-adapt-desktop-to-mobile
description: "Bevy ECS skill for adapting a Bevy desktop game to mobile. Keywords: Bevy, mobile, touch, UI, adapt."
---

# Bevy adapt desktop to mobile

## When to use

Load this when a desktop window game must accept touch and a smaller layout. Platform features are on bevy-platform-mobile.

## ECS shape

- **Input:** `touch` and `gestures` features exist. Action mapping lives on bevy-input-handling.
- **UI:** scale nodes with `Node` layout. Check the window docs for a dpi component before writing one. `WindowResolution` and scale-factor events exist on the window page (`WindowScaleFactorChanged`).
- **Textures:** ASTC is mentioned only as a compression feature blurb.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Mouse | Touch feature. Check the input docs for pointer unification before writing it. |
| Hover menus | Replace hover-only actions. UI picking exists as `ui_picking`. Check that feature's docs for behavior before writing it. |
| Safe margins | Unverified. |

## Scope

- No control-scheme or safe-area resource was opened.
- Check the platform docs for store and permission steps before writing them.

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

- No Godot export-preset or touch emulation names. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

- No Godot types in Bevy code. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/) - Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/) - API reference and Cargo feature list.
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-platform-mobile](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-platform-mobile/SKILL.md) - Android and touch features.
- [bevy-ui-layout](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ui-layout/SKILL.md) - Reflow the HUD.

#### Complements
- [bevy-adapt-mobile-to-desktop](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-adapt-mobile-to-desktop/SKILL.md) - The reverse adapt.
- [godot-adapt-desktop-to-mobile](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-adapt-desktop-to-mobile/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
