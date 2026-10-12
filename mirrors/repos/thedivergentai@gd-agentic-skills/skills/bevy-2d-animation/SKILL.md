---
name: bevy-2d-animation
description: "Docs-first stub for Bevy 2D sprite animation. Godot counterpart: godot-2d-animation. Keywords: Bevy, sprite, animation, AnimationPlayer, AnimationClip, 2D."
---

# Bevy 2D animation (docs-first stub)

Not a full port. Docs-first stub. Godot counterpart: godot-2d-animation.

## When to use

Load this when a 2D actor needs clip playback on a sprite entity. Pair with bevy-animation for the player and clip types. Pair with bevy-animation-graph when clips must blend.

## ECS shape

- **Components:** `Sprite` (bevy::sprite) on the visible entity. `AnimationPlayer` and `AnimationTargetId` / `AnimatedBy` (bevy::animation) link a clip to that entity.
- **Resources:** clip assets are `AnimationClip` handles, not a global player.
- **Systems:** `advance_animations` and `animate_targets` are the engine systems named on the animation page. Gameplay code should not reimplement them.
- **Schedule:** those systems are engine-owned. Gameplay that reacts to a finished clip chains after them.

## Godot idea to Bevy idiom

| Idea | Bevy idiom (idea only) |
| --- | --- |
| Sprite frames | Sprite plus an AnimationClip. Atlas layout was not a struct on the sprite page. |
| Cutout bones | AnimationTargetId identifies which curves hit which entity. A 2D cutout rig was not opened. |
| Looping | RepeatAnimation is the repetition enum on the animation page. |

## Gaps

- The sprite page lists `Sprite`, `SpritePlugin`, `Anchor`, and `Text2d`. It does not list a texture-atlas or sprite-frames type. Do not invent one.
- `animated_field` exists as a macro on the animation page. This pass did not open its argument rules.
- Skeletal 2D cutout weights are unverified.


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

- No Godot AnimatedSprite or sprite-frames types. WHY: a Godot port, an unopened API, or a public lie fails the docs-first bar.

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
- [bevy::sprite](https://docs.rs/bevy/latest/bevy/sprite/index.html) - `Sprite`, `SpritePlugin`.
- [bevy::animation](https://docs.rs/bevy/latest/bevy/animation/index.html) - `AnimationPlayer`, `AnimationClip`, `animated_field`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-animation](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-animation/SKILL.md) - AnimationPlayer and AnimationClip.

#### Complements
- [bevy-animation-graph](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-animation-graph/SKILL.md) - Blend clips.
- [godot-2d-animation](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/godot-2d-animation/SKILL.md) - Godot counterpart. Source idea only.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/gd-agentic-skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
