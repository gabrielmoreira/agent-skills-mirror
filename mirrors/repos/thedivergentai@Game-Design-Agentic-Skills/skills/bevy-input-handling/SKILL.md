---
name: bevy-input-handling
description: "Bevy ECS skill for player input. Keywords: Bevy, ButtonInput, KeyCode, MouseButton, Gamepad."
---

# Bevy input handling

## When to use

Load this when a system should read keyboard, mouse, or gamepad state. The `bevy::input` module (docs.rs `latest`, crate 0.20.0) is the source for the names below.

## ECS shape

- **Plugin:** `InputPlugin` adds input from keyboard, mouse, gamepad, and touch. It ships inside the usual app plugins. `InputSystems` labels the systems that refresh that data.
- **Keyboard resource:** `Res<ButtonInput<KeyCode>>`. `KeyCode` is the physical key (layout-stable). `Res<ButtonInput<Key>>` is the logical key. The keyboard example uses `pressed`, `just_pressed`, and `just_released`.
- **Mouse:** `mouse_button_input_system` writes `ButtonInput<MouseButton>` from `MouseButtonInput`. `AccumulatedMouseMotion` and `AccumulatedMouseScroll` are resources reset every frame. `MouseMotion` and `MouseWheel` are the underlying events.
- **Gamepad:** `Gamepad` stores a connected pad's metadata (`GamepadButton`, `GamepadAxis`). Connection and axis changes arrive as `GamepadConnectionEvent`, `GamepadAxisChangedEvent`, and `GamepadButtonChangedEvent`. `GamepadRumbleRequest` is the force-feedback event.
- **Schedule:** read these resources from a system on `Update` (or a schedule you already chain). Do not invent an input-map resource.

## Coming from Godot

| Godot idea | Bevy idiom |
| --- | --- |
| Action just pressed | `ButtonInput::just_pressed` on `KeyCode` or `MouseButton` |
| Action held | `ButtonInput::pressed` |
| Physical WASD vs symbol keys | `KeyCode` for location, `Key` for the character |
| Mouse look delta | `AccumulatedMouseMotion` (reset each frame) |
| Controller | `Gamepad` plus the gamepad events listed above |

## Scope

- Touch and gesture modules are listed on the input index. Check those pages for event fields before writing them.
- Check the input docs for a project-wide action-map resource (named actions, rebinding) before writing one.
- Check the input docs for glyphs and device prompts before writing them.

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

- No Godot input-map, event, or device types. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No APIs this file did not open (`pressed`, `just_pressed`, `just_released` are the button methods cited). WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No third-party input crates. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

docs.rs links use the unversioned `latest` permalink. The library pin on bevy-master stays **0.20.0**.

### Official Documentation
- [Migration guides](https://bevy.org/learn/migration-guides/introduction/)  -  Unversioned hop index.
- [bevy crate](https://docs.rs/bevy/latest/bevy/)  -  Unversioned API index.
- [bevy::input](https://docs.rs/bevy/latest/bevy/input/index.html)  -  `ButtonInput`, `InputPlugin`, device modules.
- [ButtonInput](https://docs.rs/bevy/latest/bevy/input/struct.ButtonInput.html)  -  `pressed`, `just_pressed`, `just_released`, `KeyCode` and `Key`.
- [Mouse](https://docs.rs/bevy/latest/bevy/input/mouse/index.html)  -  `MouseButton`, motion and scroll resources.
- [Gamepad](https://docs.rs/bevy/latest/bevy/input/gamepad/index.html)  -  `Gamepad` and connection events.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples)  -  Example tree on the `latest` branch.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Who owns which piece of state.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md)  -  Systems and `Query`.

#### Complements
- [bevy-character-movement](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-character-movement/SKILL.md)  -  Motion that consumes this input on the fixed timestep.
- [bevy-camera-systems](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-camera-systems/SKILL.md)  -  Viewpoint that may read mouse motion.
- [godot-input-handling](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/godot-input-handling/SKILL.md)  -  Equivalent Godot skill.

#### Downstream / consumers
- [bevy-audio-systems](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-audio-systems/SKILL.md)  -  The audio control example reads `ButtonInput<KeyCode>` to pause and mute.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Design-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md)  -  Bevy router.
