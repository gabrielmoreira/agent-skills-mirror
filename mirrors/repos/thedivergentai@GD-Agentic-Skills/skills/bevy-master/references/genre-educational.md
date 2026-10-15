---
name: bevy-genre-educational
description: "Route a Bevy 0.20 educational loop. Use when prompts and choices are components, lesson totals are one resource, and grading must run after selection in one chain. Keywords: Bevy, Educational, LessonProgress, Choice, chain, genre."
---

# Bevy Educational (thin router)

Genre router. Domain work lives in the Bevy skills below.

## When to use

Load this for prompts, answers, and progress flags.

## ECS shape

- **Components** hold a prompt and each choice as plain data.
- **Resources** hold how many answers were graded and how many were correct.
- **Systems** select a choice, then grade it. `.chain()` keeps the grade after the selection.
- **Schedule:** gameplay mode changes go through bevy-state-machines.

```toml
[package]
name = "educational"
version = "0.1.0"
edition = "2021"

[dependencies]
bevy = "0.20"
```

One prompt, two choices, one progress resource.

```rust
#[derive(Component)]
struct Prompt {
    text: String,
}

#[derive(Component)]
struct Choice {
    label: String,
    correct: bool,
    picked: bool,
    graded: bool,
}

#[derive(Resource, Default)]
struct LessonProgress {
    answered: u32,
    correct: u32,
}

fn spawn_lesson(mut commands: Commands) {
    commands.spawn(Prompt {
        text: "Which way is north?".to_string(),
    });
    commands.spawn(Choice {
        label: "Up".to_string(),
        correct: true,
        picked: false,
        graded: false,
    });
    commands.spawn(Choice {
        label: "Down".to_string(),
        correct: false,
        picked: false,
        graded: false,
    });
    commands.init_resource::<LessonProgress>();
}

fn pick_first(mut choices: Query<&mut Choice>) {
    for mut choice in &mut choices {
        if choice.correct && !choice.graded && !choice.picked {
            choice.picked = true;
            break;
        }
    }
}

fn grade(mut progress: ResMut<LessonProgress>, mut choices: Query<&mut Choice>) {
    for mut choice in &mut choices {
        if choice.picked && !choice.graded {
            progress.answered = progress.answered.saturating_add(1);
            if choice.correct {
                progress.correct = progress.correct.saturating_add(1);
            }
            choice.graded = true;
            choice.picked = false;
        }
    }
}

pub struct LessonPlugin;

impl Plugin for LessonPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Startup, spawn_lesson)
            .add_systems(Update, (pick_first, grade).chain());
    }
}
```

`pick_first` and `grade` both write `Choice`, so they stay chained.

A readout only reads progress.

```rust
#[derive(Resource, Default)]
struct LessonProgress {
    answered: u32,
    correct: u32,
}

fn show_score(progress: Res<LessonProgress>) {
    let _answered = progress.answered;
    let _correct = progress.correct;
}

pub struct ScorePlugin;

impl Plugin for ScorePlugin {
    fn build(&self, app: &mut App) {
        app.init_resource::<LessonProgress>()
            .add_systems(Update, show_score);
    }
}
```

## Lesson data

| Need | Bevy idiom |
| --- | --- |
| Prompts and choices | Entities plus the domain skills linked below |
| Lesson totals | A `Resource` |
| One-shot loop notices | bevy-events-messaging |

## Routing

- [bevy-ui-text](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ui-text/SKILL.md) - Prompts.
- [bevy-ui-layout](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ui-layout/SKILL.md) - Choices.
- [bevy-save-load](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-save-load/SKILL.md) - Progress saves.
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Lesson mode.

## Scope

- Prompts, choices, and the progress resource are gameplay data you define. UI text and layout stay on the linked UI skills.

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
| Per-entity data | `Component` + `Query` | One struct that stores every entity's fields |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Read the linked Bevy pages | A made-up crate or API |

Load [references/ecs-ownership.md](genre-educational-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- No scene-tree types in Bevy code. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- No invented genre APIs. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.
- Do not pick a physics or net crate here. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20.0**. Official links stay on the unversioned learn pages.

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
- [bevy-ui-text](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ui-text/SKILL.md) - Prompts.
- [bevy-ui-layout](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ui-layout/SKILL.md) - Choices.
- [bevy-save-load](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-save-load/SKILL.md) - Progress saves.
- [bevy-state-machines](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-state-machines/SKILL.md) - Lesson mode.

#### Downstream / consumers
- None. This router does not own a second implementation.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
