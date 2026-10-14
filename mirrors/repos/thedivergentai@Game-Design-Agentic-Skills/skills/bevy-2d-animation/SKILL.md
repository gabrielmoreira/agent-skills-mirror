---
name: bevy-2d-animation
description: "Bevy ECS skill for 2D sprite animation. Keywords: Bevy, sprite, animation, AnimationPlayer, AnimationClip, 2D."
---

# Bevy 2D animation

## When to use

Load this when a 2D actor needs clip playback on a sprite entity. Pair with bevy-animation for the player and clip types. Pair with bevy-animation-graph when clips must blend.

## ECS shape

- **Components:** `Sprite` (bevy::sprite) on the visible entity. `AnimationPlayer` and `AnimationTargetId` / `AnimatedBy` (bevy::animation) link a clip to that entity.
- **Resources:** clip assets are `AnimationClip` handles, not a global player.
- **Systems:** `advance_animations` and `animate_targets` are the engine systems named on the animation page. Gameplay code should not reimplement them.
- **Schedule:** those systems are engine-owned. Gameplay that reacts to a finished clip chains after them.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Sprite frames | Sprite plus an AnimationClip. Atlas layout was not a struct on the sprite page. |
| Cutout bones | AnimationTargetId identifies which curves hit which entity. Check the animation docs.rs page for cutout-rig field names before writing them. |
| Looping | RepeatAnimation is the repetition enum on the animation page. |

## Scope

- The sprite page lists `Sprite`, `SpritePlugin`, `Anchor`, and `Text2d`. It does not list a texture-atlas or sprite-frames type. Do not invent one.
- `animated_field` exists as a macro on the animation page. Check that page for its argument rules before writing them.
- Skeletal 2D cutout weights are unverified.

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

- No Godot AnimatedSprite or sprite-frames types. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

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
- [bevy::sprite](https://docs.rs/bevy/latest/bevy/sprite/index.html) - `Sprite`, `SpritePlugin`.
- [bevy::animation](https://docs.rs/bevy/latest/bevy/animation/index.html) - `AnimationPlayer`, `AnimationClip`, `animated_field`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-animation](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-animation/SKILL.md) - AnimationPlayer and AnimationClip.

#### Complements
- [bevy-animation-graph](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-animation-graph/SKILL.md) - Blend clips.
- [godot-2d-animation](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-2d-animation/SKILL.md) - Equivalent Godot skill.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
