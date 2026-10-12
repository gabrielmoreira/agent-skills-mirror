---
name: bevy-ai-navigation
description: "Docs-first stub for Bevy AI navigation policy. Godot counterpart: godot-ai-navigation. Not a full port. Keywords: Bevy, AI, chase, patrol, navigation, ECS, gaps."
---

# Bevy AI navigation (docs-first stub)

Not a full port. This file routes movement decisions. It does not implement a navigation mesh.

## When to use

Load this when an actor must chase, patrol, or wait, and you need to see which Bevy skill owns the next step. Path data and any future nav crate stay on bevy-navigation. Transform integration stays on bevy-character-movement. Line-of-sight sensors stay on bevy-spatial-queries until a solver exists.

## ECS shape

- **Components:** a mode flag can be an enum `Component` (see bevy-state-machines for the pattern). Goal position can be your own component. No agent, radius, or layer type was opened.
- **Resources:** a shared patrol table can be a `Resource` you define. No navigation resource was opened.
- **Systems:** read the mode and write a desired velocity or waypoint on `Update` or `Fixed`. Use `.chain()` so policy runs before movement. Do not name a Godot-style agent callback.
- **Schedule:** `Fixed` / `FixedMain` when the result feeds the movement step.

## Godot idea to Bevy idiom

| Idea | Bevy idiom (idea only) |
| --- | --- |
| Chase vs patrol | Enum component plus a system. Not a navigation agent |
| Retarget throttle | Your timer resource or a fixed-step counter. No opened retarget API |
| Crowd / avoidance | Gap on bevy-navigation. Do not invent radii |
| Bake vs obstacle | Gap on bevy-navigation |
| Line of sight | Gap on bevy-spatial-queries |

## Gaps

- No Bevy navigation module was opened, so node-agent versus server, bake, links, and layers have no Bevy names.
- Sensors that need a cast are blocked on the same unpicked physics solver as bevy-physics-2d and bevy-physics-3d.
- Formations and stuck recovery are design notes only.


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

- No Godot navigation agent or server types. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No named third-party navigation or physics crate. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No invented path, bake, or avoidance APIs. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No Creation Station content. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- No umbrella skill over Godot and Bevy. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.
- Do not mark this row `ported`. It is `docs_mapped`. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.

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
- [bevy-master](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-master/SKILL.md) - ECS ownership.
- [bevy-navigation](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-navigation/SKILL.md) - Path and mesh gap.
- [bevy-state-machines](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-state-machines/SKILL.md) - Enum components for a mode flag.

#### Complements
- [bevy-character-movement](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-character-movement/SKILL.md) - Integrates a waypoint or velocity.
- [bevy-spatial-queries](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-spatial-queries/SKILL.md) - Sensor gap.
- [godot-ai-navigation](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-ai-navigation/SKILL.md) - Godot counterpart. Source idea only.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
