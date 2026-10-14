---
name: bevy-platform-desktop
description: "Bevy ECS skill for desktop windows. Keywords: Bevy, window, desktop, WindowPlugin, PrimaryWindow, winit."
---

# Bevy desktop platform

## When to use

Load this when configuring the desktop window, mode, or close behavior. Web and mobile constraints stay on their skills.

## ECS shape

- **Module:** `bevy::window` is a platform-agnostic window interface. `WindowPlugin` is part of `DefaultPlugins`.
- **Components:** `Window` is the defining component for window entities. `PrimaryWindow` marks the primary window.
- **Mode:** `WindowMode`, `PresentMode`, `WindowResolution`, `WindowPosition` are enums or structs on that page.
- **Backend feature:** `bevy_winit` is the winit window and input backend. `x11` and `wayland` are features.
- **Close:** `exit_on_primary_closed` and `exit_on_all_closed` are named functions. `WindowCloseRequested` is the event.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Window size | WindowResolution on the Window component. |
| Fullscreen | WindowMode. Check the window page for variants before writing them. |
| Quit on close | exit_on_primary_closed. |

## Scope

- Check the `Window` docs for per-field defaults before writing them.
- Check the window docs for display-server selection code before writing it. Feature names only are listed here.

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

- No Godot DisplayServer or window project-setting names. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

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
- [bevy::window](https://docs.rs/bevy/latest/bevy/window/index.html) - `Window`, `WindowPlugin`, `PrimaryWindow`, `WindowMode`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.

#### Complements
- [bevy-platform-web](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-platform-web/SKILL.md) - Wasm limits.
- [bevy-input-handling](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-input-handling/SKILL.md) - Pointer and keyboard.
- [godot-platform-desktop](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-platform-desktop/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
