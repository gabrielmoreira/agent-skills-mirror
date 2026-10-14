---
name: bevy-project-templates
description: "Bevy ECS skill for project templates. Keywords: Bevy, template, cargo, features, 2d, 3d, ui."
---

# Bevy project templates

## When to use

Load this when choosing a starting Cargo feature set. App construction details stay on bevy-project-foundations. This file does not ship a template repository.

## ECS shape

- **Profiles on the crate page:** `default` (2d, 3d, ui, audio), `2d`, `3d`, `ui`. Example snippet shows `default-features = false` plus a profile feature. The sample version string on that page said 0.18; the library target on bevy-master stays 0.20.0.
- **Minimal app:** the crate docs show `App::new().add_systems(Update, ...).run()`.
- **Windowed games:** `DefaultPlugins` remains the plugin set named on the plugins page.
- **No repo:** do not invent a template URL.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| 2D starter | Cargo feature profile 2d plus DefaultPlugins. |
| 3D starter | Profile 3d. |
| UI tool | Profile ui. Feathers is optional and unopened. |
| Headless | default_app is described as a baseline without a renderer. |

## Scope

- Official example binaries were not copied. Link the examples tree only.
- Check your project template for gitignore and CI files before assuming Bevy provides them.

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

- No Godot project.godot template or export presets. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

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
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub.
- [bevy-project-foundations](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-project-foundations/SKILL.md) - Cargo app shell.

#### Complements
- [bevy-platform-desktop](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-platform-desktop/SKILL.md) - Windowed targets.
- [godot-project-templates](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-project-templates/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
