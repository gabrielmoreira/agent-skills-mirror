---
name: bevy-ui-theming
description: "Bevy ECS skill for UI theming. Keywords: Bevy, UI theme, BackgroundColor, BorderColor, feathers."
---

# Bevy UI theming

## When to use

Load this when many nodes should share colors or a widget style. There is no Godot Theme resource in Bevy.

## ECS shape

- **Per-node colors opened:** `BackgroundColor`, `BorderColor`, `BorderRadius`, `BoxShadow`, `BackgroundGradient`.
- **Feature:** `bevy_feathers` is a collection of styled widgets for editors and inspectors. Check that module for widget names before writing them.
- **Window chrome:** `WindowTheme` is an enum on bevy::window for the window theme variant. That is OS window chrome, not a UI skin.
- **Systems:** you set components. No theme inheritance system was named.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Theme resource | Your own resource of colors, copied onto BackgroundColor. No Theme type was opened. |
| Style box | BorderRadius and BoxShadow on a Node. |
| Editor widgets | bevy_feathers exists. Do not assume it skins a game HUD. |

## Scope

- Theme, stylebox, and font-theme data are yours to build. Check `bevy::ui` before assuming a built-in type.
- Check the feathers docs for widget pages before writing them.

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

- No Godot Theme or StyleBox types. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

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
- [bevy::ui](https://docs.rs/bevy/latest/bevy/ui/index.html) - Color and radius components.
- [bevy::feathers](https://docs.rs/bevy/latest/bevy/feathers/index.html) - Editor widget collection.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-ui-layout](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ui-layout/SKILL.md) - Nodes being styled.

#### Complements
- [bevy-ui-text](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ui-text/SKILL.md) - Font choices.
- [godot-ui-theming](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-ui-theming/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
