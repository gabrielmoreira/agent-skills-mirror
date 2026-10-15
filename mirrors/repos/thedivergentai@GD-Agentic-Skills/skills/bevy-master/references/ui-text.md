---
name: bevy-ui-text
description: "Bevy 0.20 UI and world text: Text, Text2d, TextSpan, TextFont, TextColor, TextLayout, TextShadow, Text2dShadow. Use when a HUD node or a 2D nameplate shows a string. Keywords: Bevy, text, UI, Text, TextSpan, bevy_text, Text2d, TextFont."
---

# Bevy UI text

## When to use

Load this when a UI node or a 2D world label shows a string. Layout stays on bevy-ui-layout.

## ECS shape

- **UI:** spawn `Text` on an entity. `Text` requires `Node`, `TextFont`, `TextColor`, and `TextLayout`. The string on `Text` is the first span.
- **Feature:** `bevy_text` ships with `DefaultPlugins`. The `default_font` feature embeds a default ASCII font, so a `Text` with no custom `Font` handle still draws.
- **World text:** `Text2d` requires `TextFont`, `TextColor`, `TextLayout`, `TextBounds`, `Anchor`, and `Transform`. `Text2dShadow` offsets a second copy of the glyphs.
- **Systems:** the engine runs `update_text2d_layout` in `PostUpdate` after the string or style changes. Game systems write `Text`, `Text2d`, `TextSpan`, `TextFont`, and `TextColor`. They do not run a second layout pass.

`Text` is the HUD string. `Node` places it. One system owns later edits to that string.

```rust
#[derive(Component)]
struct ScoreLabel;

#[derive(Resource)]
struct Score(u32);

fn spawn_score(mut commands: Commands) {
    commands.spawn((
        Text::new("Score 0"),
        TextFont::from_font_size(FontSize::Px(28.0)),
        TextColor(Color::srgb(0.95, 0.95, 0.9)),
        TextLayout::new(Justify::Left, LineBreak::NoWrap),
        ScoreLabel,
        Node {
            position_type: PositionType::Absolute,
            top: Val::Px(16.0),
            left: Val::Px(16.0),
            ..default()
        },
    ));
    commands.insert_resource(Score(0));
}

fn write_score(score: Res<Score>, mut labels: Query<&mut Text, With<ScoreLabel>>) {
    if !score.is_changed() {
        return;
    }
    for mut text in &mut labels {
        text.0 = format!("Score {}", score.0);
    }
}

pub struct ScoreTextPlugin;

impl Plugin for ScoreTextPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Startup, spawn_score)
            .add_systems(Update, write_score);
    }
}
```

Extra spans are child entities with `TextSpan`. Each child keeps its own `TextFont` and `TextColor`. The parent `TextLayout` lays out the whole block. `Underline` and `Strikethrough` are components on the span that should carry that mark.

```rust
fn spawn_status_line(mut commands: Commands) {
    let root = commands
        .spawn((
            Text::new("HP "),
            TextFont::from_font_size(FontSize::Px(24.0)),
            TextLayout::justify(Justify::Center),
        ))
        .id();
    commands.spawn((
        TextSpan::new("12"),
        TextFont::from_font_size(FontSize::Px(24.0)).with_font_weight(FontWeight::BOLD),
        TextColor(Color::srgb(0.9, 0.25, 0.2)),
        ChildOf(root),
    ));
    commands.spawn((
        TextSpan::new(" / 20"),
        TextFont::from_font_size(FontSize::Px(24.0)),
        Underline,
        ChildOf(root),
    ));
}
```

A world nameplate is `Text2d` plus a transform. `Justify` only aligns lines inside the block. `Anchor` places the block on the transform.

```rust
use bevy::sprite::{Anchor, Text2dShadow};

fn spawn_nameplate(mut commands: Commands) {
    commands.spawn((
        Text2d::new("Warden"),
        TextFont::from_font_size(FontSize::Px(32.0)),
        TextColor(Color::WHITE),
        TextLayout::justify(Justify::Center),
        Text2dShadow {
            offset: Vec2::new(2.0, -2.0),
            color: Color::BLACK,
        },
        Anchor::BOTTOM_CENTER,
        Transform::from_xyz(0.0, 48.0, 0.0),
    ));
}
```

A custom face is an `AssetServer` handle stored on `TextFont`. UI drop shadows use `TextShadow`.

```rust
fn spawn_title(mut commands: Commands, assets: Res<AssetServer>) {
    let font = assets.load("fonts/Display.ttf");
    commands.spawn((
        Text::new("Inventory"),
        TextFont::from_font_size(FontSize::Px(40.0)).with_font(font),
        TextColor(Color::srgb(0.93, 0.86, 0.62)),
        TextShadow {
            offset: Vec2::new(3.0, 3.0),
            color: Color::linear_rgba(0.0, 0.0, 0.0, 0.75),
        },
    ));
}
```

```toml
[dependencies]
bevy = "0.20"
```

## Which text entity

| Need | Spawn | Do not |
| --- | --- | --- |
| HUD or menu string | `Text` on a `Node`, plus `TextFont` and `TextColor` | A second layout system after `Text` changes |
| Nameplate in the 2D world | `Text2d`, `Anchor`, and `Text2dShadow` | `Justify` as the world position |
| Two styles in one line | Child `TextSpan` entities with their own font, color, `Underline`, or `Strikethrough` | A markup string parsed by the engine |

## Scope

- Font and layout types used above: `TextFont`, `FontSize`, `FontWeight`, `TextLayout`, `Justify`, `LineBreak`.
- Emphasis is components (`Underline`, `Strikethrough`, `TextColor`) on `Text` or `TextSpan`, not a markup string.

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
| Per-entity data | `Component` + `Query` | One script that owns the whole node tree |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| An API outside the documented set | Leave it unnamed | A made-up crate or API |

Load [references/ecs-ownership.md](ui-text-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.

- Do not store emphasis in a markup string. WHY: `Underline` and `Strikethrough` are components on `Text` or `TextSpan`.
- Do not let two systems write the same `Text` or `TextSpan`. WHY: the string has one owner; a second writer races the format system.
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20**.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog. No third-party crate was selected.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.
- [UI examples](https://github.com/bevyengine/bevy/tree/latest/examples/ui) - Text and node samples on the `latest` branch.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-ui-layout](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ui-layout/SKILL.md) - The node that holds the text.

#### Complements
- [bevy-dialogue-system](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-dialogue-system/SKILL.md) - Line strings.
- [bevy-ui-theming](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ui-theming/SKILL.md) - Colors around the string.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
