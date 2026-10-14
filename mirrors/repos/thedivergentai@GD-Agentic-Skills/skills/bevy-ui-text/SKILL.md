---
name: bevy-ui-text
description: "Bevy ECS skill for UI text. Keywords: Bevy, text, UI, Text, bevy_text, Text2d."
---

# Bevy UI text

## When to use

Load this when a UI node or a 2D world label shows a string. Layout stays on bevy-ui-layout.

## ECS shape

- **UI:** the ui crate summary says spawn `Text` with `Node`.
- **Feature:** `bevy_text` provides text functionality. `default_font` includes a default ASCII font.
- **World text:** `Text2d` is on the sprite page, with `Text2dShadow`.
- **Systems:** `update_text2d_layout` is named on the sprite page for 2D text. Check the UI text docs for layout system names before writing them.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Label | Text on a UI node. |
| World label | Text2d. |
| Rich tags | Unverified. Do not invent BBCode. |

## Scope

- Check the `bevy::text` module for font, span, and justification types before writing them.
- Check the text docs for rich-text effects and inline images before writing them.

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

- No Godot RichTextLabel or BBCode. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

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
- [bevy::ui](https://docs.rs/bevy/latest/bevy/ui/index.html) - `Text` named in the crate summary.
- [bevy::sprite](https://docs.rs/bevy/latest/bevy/sprite/index.html) - `Text2d`.
- [bevy::text](https://docs.rs/bevy/latest/bevy/text/index.html) - Text module reference (`bevy_text`).

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-ui-layout](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ui-layout/SKILL.md) - The node that holds the text.

#### Complements
- [bevy-dialogue-system](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-dialogue-system/SKILL.md) - Line strings.
- [godot-ui-rich-text](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-ui-rich-text/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
