---
name: bevy-ui-layout
description: "Docs-first stub for Bevy UI layout. Godot counterpart: godot-ui-containers. Keywords: Bevy, UI, Node, Flexbox, BackgroundColor, Button."
---

# Bevy UI layout (docs-first stub)

Not a full port. Docs-first stub. Godot counterpart: godot-ui-containers.

## When to use

Load this when laying out HUD or menu nodes. Text content stays on bevy-ui-text. Colors and widget styling stay on bevy-ui-theming.

## ECS shape

- **Crate text (opened):** spawn UI with `widget::Button`, `ImageNode`, `Text`, and `Node`. Layout uses Flexbox and CSS Grid.
- **Components named:** `Node`, `BackgroundColor`, `BorderColor`, `BorderRadius`, `ComputedNode`, `GridPlacement`, `GridTrack`, `GlobalZIndex`.
- **Feature:** `bevy_ui` is a custom ECS-driven UI framework.
- **Systems:** layout and update systems are engine-owned (`bevy::ui::update` exists). Do not write a second layout pass.

## Godot idea to Bevy idiom

| Idea | Bevy idiom (idea only) |
| --- | --- |
| Container | A Node entity. Children are child entities, not Control nodes. |
| Button | widget::Button as named in the crate summary. |
| Image | ImageNode as named in the crate summary. |
| Grid | GridTrack and GridPlacement. |

## Gaps

- Flex property field names on `Node` were not opened. Do not invent `justify_content` spellings.
- `bevy_feathers` is a styled widget collection for editors. Its widget list was not opened. Do not treat it as game HUD theme.


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

- No Godot Control, Container, or anchor types. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.

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
- [bevy::ui](https://docs.rs/bevy/latest/bevy/ui/index.html) - `Node`, Flexbox and CSS Grid, `widget::Button`, `ImageNode`, `Text`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.

#### Complements
- [bevy-ui-text](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-ui-text/SKILL.md) - Text on a node.
- [bevy-ui-theming](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-ui-theming/SKILL.md) - Colors and backgrounds.
- [godot-ui-containers](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-ui-containers/SKILL.md) - Godot counterpart. Source idea only.

#### Downstream / consumers
- [bevy-ui-text](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-ui-text/SKILL.md) - Consumes layout nodes.

#### Master
- [bevy-master](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
