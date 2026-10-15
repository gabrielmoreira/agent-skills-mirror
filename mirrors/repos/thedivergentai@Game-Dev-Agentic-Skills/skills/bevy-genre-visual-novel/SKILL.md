---
name: bevy-genre-visual-novel
description: "Thin Bevy genre router for Visual novel. Keywords: Bevy, Visual novel, genre, ECS, router."
---

# Bevy Visual novel (thin router)

Genre router. Domain work lives in the Bevy skills below.

## When to use

Load this for dialogue, portraits, and choice flags.

## ECS shape

- **Components** hold the genre's per-entity flags as plain data. This file does not name new engine types.
- **Resources** hold run-wide counters (score, wave index, seed) via bevy-data-resources.
- **Systems** read those components on `Update` or the fixed timestep from bevy-master. Order them with `.chain()` when a later system must see the result.
- **Schedule:** gameplay mode changes go through bevy-state-machines. Do not invent a genre plugin.

## Routing

- [bevy-dialogue-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-dialogue-system/SKILL.md) - Lines.
- [bevy-ui-text](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ui-text/SKILL.md) - Body text.
- [bevy-ui-layout](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ui-layout/SKILL.md) - Choice buttons.
- [bevy-save-load](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-save-load/SKILL.md) - Route flags.

## Scope

Lines, the visible character index, and route flags are resources. Choice rows are entities. A full script parser stays data you load into those resources.

## Examples

```toml
[package]
name = "visual-novel"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = "0.20"
```

One resource owns the script index and the flags later scenes read.

```rust
#[derive(Clone)]
struct Line {
    speaker: String,
    body: String,
}

#[derive(Resource)]
struct Script {
    lines: Vec<Line>,
    index: usize,
    flags: Vec<String>,
}

fn current_line(script: &Script) -> Option<&Line> {
    script.lines.get(script.index)
}

fn advance(script: &mut Script) {
    if script.index + 1 < script.lines.len() {
        script.index += 1;
    }
}

fn set_flag(script: &mut Script, flag: &str) {
    if !script.flags.iter().any(|f| f == flag) {
        script.flags.push(flag.to_string());
    }
}
```

Space advances. Number keys pick a choice and write its flag.

```rust
#[derive(Component)]
struct Choice {
    key: KeyCode,
    flag: String,
    next_index: usize,
}

#[derive(Clone)]
struct Line {
    speaker: String,
    body: String,
}

#[derive(Resource)]
struct Script {
    lines: Vec<Line>,
    index: usize,
    flags: Vec<String>,
}

fn advance(script: &mut Script) {
    if script.index + 1 < script.lines.len() {
        script.index += 1;
    }
}

fn set_flag(script: &mut Script, flag: &str) {
    if !script.flags.iter().any(|f| f == flag) {
        script.flags.push(flag.to_string());
    }
}

fn read_advance(keys: Res<ButtonInput<KeyCode>>, mut script: ResMut<Script>) {
    if keys.just_pressed(KeyCode::Space) {
        advance(&mut script);
    }
}

fn read_choice(
    keys: Res<ButtonInput<KeyCode>>,
    choices: Query<&Choice>,
    mut script: ResMut<Script>,
) {
    for choice in &choices {
        if keys.just_pressed(choice.key) {
            set_flag(&mut script, &choice.flag);
            script.index = choice.next_index.min(script.lines.len().saturating_sub(1));
        }
    }
}

pub struct NovelPlugin;

impl Plugin for NovelPlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(Script {
            lines: vec![Line {
                speaker: "Guide".to_string(),
                body: "The gate is shut.".to_string(),
            }],
            index: 0,
            flags: Vec::new(),
        })
        .add_systems(Update, (read_advance, read_choice).chain());
    }
}
```

Startup spawns two choices. The portrait name is a component on its own entity.

```rust
#[derive(Component)]
struct Portrait {
    name: String,
}

#[derive(Component)]
struct Choice {
    key: KeyCode,
    flag: String,
    next_index: usize,
}

#[derive(Resource)]
struct Script {
    lines: Vec<Line>,
    index: usize,
    flags: Vec<String>,
}

#[derive(Resource, Default)]
struct ShownLine {
    speaker: String,
    portrait: String,
    body: String,
}

#[derive(Clone)]
struct Line {
    speaker: String,
    body: String,
}

fn current_line(script: &Script) -> Option<&Line> {
    script.lines.get(script.index)
}

fn spawn_scene(mut commands: Commands) {
    commands.spawn(Portrait {
        name: "guide".to_string(),
    });
    commands.spawn(Choice {
        key: KeyCode::Digit1,
        flag: "opened_gate".to_string(),
        next_index: 1,
    });
    commands.spawn(Choice {
        key: KeyCode::Digit2,
        flag: "walked_away".to_string(),
        next_index: 2,
    });
}

fn show_portrait(
    portraits: Query<&Portrait>,
    script: Res<Script>,
    mut shown: ResMut<ShownLine>,
) {
    let Some(line) = current_line(&script) else {
        return;
    };
    let Some(portrait) = portraits.iter().next() else {
        return;
    };
    shown.speaker = line.speaker.clone();
    shown.portrait = portrait.name.clone();
    shown.body = line.body.clone();
}
```

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

- No Godot types in Bevy code. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented genre APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- Do not pick a physics or net crate here. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Official pages stay on the unversioned `latest` branch.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - ECS ownership and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Spawn and query shape.

#### Complements
- [godot-genre-visual-novel](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/godot-genre-visual-novel/SKILL.md) - Visual novel on the Godot engine, same depth.
- [bevy-dialogue-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-dialogue-system/SKILL.md) - Lines.
- [bevy-ui-text](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ui-text/SKILL.md) - Body text.
- [bevy-ui-layout](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ui-layout/SKILL.md) - Choice buttons.
- [bevy-save-load](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-save-load/SKILL.md) - Route flags.

#### Downstream / consumers
- None. This router does not own a second implementation.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
