---
name: bevy-ai-navigation
description: "Bevy ECS skill for AI navigation policy. Keywords: Bevy, AI, chase, patrol, navigation, ECS."
---

# Bevy AI navigation

## When to use

Load this when an actor must chase, patrol, or wait, and you need to see which Bevy skill owns the next step. Path data and any future nav crate stay on bevy-navigation. Transform integration stays on bevy-character-movement. Line-of-sight sensors stay on bevy-spatial-queries until a solver exists.

## ECS shape

- **Components:** a mode flag can be an enum `Component` (see bevy-state-machines for the pattern). Goal position can be your own component. No agent, radius, or layer type was opened.
- **Resources:** a shared patrol table can be a `Resource` you define. No navigation resource was opened.
- **Systems:** read the mode and write a desired velocity or waypoint on `Update` or `Fixed`. Use `.chain()` so policy runs before movement. Do not name a Godot-style agent callback.
- **Schedule:** `Fixed` / `FixedMain` when the result feeds the movement step.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Chase vs patrol | Enum component plus a system. Not a navigation agent |
| Retarget throttle | Your timer resource or a fixed-step counter. Check the navigation docs before assuming a retarget API. |
| Crowd / avoidance | Crowd and avoidance belong on bevy-navigation. Check that skill before naming radii. |
| Bake vs obstacle | Bake and obstacle handling belong on bevy-navigation. |
| Line of sight | Line of sight belongs on bevy-spatial-queries. |

## Scope

- No Bevy navigation module was opened, so node-agent versus server, bake, links, and layers have no Bevy names.
- Sensors that need a cast belong with bevy-physics-2d and bevy-physics-3d once you choose a physics solver.
- Formations and stuck recovery are design notes only.

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

- No Godot navigation agent or server types. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No named third-party navigation or physics crate. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented path, bake, or avoidance APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/) - Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/) - Unversioned API index. No AI navigation module was opened.
- [Assets](https://bevy.org/assets/) - Official asset catalog. No AI plugin was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, `Resource` pairing via bevy-data-resources, systems, and `.chain()`.
- [bevy::state](https://docs.rs/bevy/latest/bevy/state/index.html) - App states are not per-entity patrol modes. Per-entity flags stay components (bevy-state-machines).

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - ECS ownership.
- [bevy-navigation](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-navigation/SKILL.md) - Paths and navigation meshes.
- [bevy-state-machines](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Enum components for a mode flag.

#### Complements
- [bevy-character-movement](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-character-movement/SKILL.md) - Integrates a waypoint or velocity.
- [bevy-spatial-queries](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-spatial-queries/SKILL.md) - Sensors and spatial queries.
- [godot-ai-navigation](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-ai-navigation/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
