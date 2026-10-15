---
name: bevy-ui-theming
description: "Theme a Bevy HUD from one palette resource copied onto BackgroundColor, BorderColor, BoxShadow, and BackgroundGradient. Use when many nodes share colors or a marker such as Danger picks a different fill. WindowTheme is OS chrome only. Keywords: Bevy, UI theme, UiPalette, BackgroundColor, BorderColor, BackgroundGradient, feathers."
---

# Bevy UI theming

## When to use

Load this when many nodes should share colors or a widget style. Store the palette in one resource and copy it onto each node's color components.

## ECS shape

- **Per-node colors:** `BackgroundColor`, `BorderColor`, `BorderRadius`, `BoxShadow`, `BackgroundGradient`.
- **Editor widgets:** `bevy::feathers` is a collection of styled widgets for editors and inspectors. Game HUDs use `Node` plus the color components below.
- **Window chrome:** `WindowTheme` on `Window` picks the OS window variant (`Light` or `Dark`). That is window chrome, not a UI skin.
- **Systems:** one system writes the color components from the palette resource. A second system, chained before it, swaps the palette.

A panel carries fill, border, radius, and one drop shadow. The palette is the only color source.

```rust
#[derive(Component)]
struct Panel;

#[derive(Resource, Clone)]
struct UiPalette {
    panel: Color,
    border: Color,
    shadow: Color,
}

fn dark_palette() -> UiPalette {
    UiPalette {
        panel: Color::srgb(0.12, 0.13, 0.16),
        border: Color::srgb(0.35, 0.38, 0.45),
        shadow: Color::srgba(0.0, 0.0, 0.0, 0.45),
    }
}

fn spawn_panel(mut commands: Commands) {
    let palette = dark_palette();
    commands.spawn((
        Panel,
        Node {
            width: Val::Px(280.0),
            height: Val::Px(160.0),
            border: UiRect::all(Val::Px(2.0)),
            border_radius: BorderRadius::all(CornerRadius::circular(Val::Px(8.0))),
            ..default()
        },
        BackgroundColor(palette.panel),
        BorderColor::all(palette.border),
        BoxShadow::new(
            palette.shadow,
            Val::Px(0.0),
            Val::Px(4.0),
            Val::Px(0.0),
            Val::Px(12.0),
        ),
    ));
    commands.insert_resource(palette);
}
```

A danger marker is a type variation: same panel shape, different fill. The two queries are disjoint, so one system may own every `BackgroundColor` write.

```rust
#[derive(Component)]
struct Panel;

#[derive(Component)]
struct Danger;

#[derive(Resource)]
struct UiPalette {
    panel: Color,
}

fn paint_panels(
    palette: Res<UiPalette>,
    mut panels: Query<&mut BackgroundColor, (With<Panel>, Without<Danger>)>,
    mut danger: Query<&mut BackgroundColor, (With<Panel>, With<Danger>)>,
) {
    let danger_fill = Color::srgb(0.55, 0.15, 0.15);
    for mut color in &mut panels {
        color.0 = palette.panel;
    }
    for mut color in &mut danger {
        color.0 = danger_fill;
    }
}
```

Swap the whole palette, then let `paint_panels` copy it. The chain keeps the writer after the swap.

```rust
#[derive(Resource, Clone, Copy, PartialEq, Eq, Default)]
enum ThemeKind {
    #[default]
    Dark,
    Light,
}

#[derive(Component)]
struct Panel;

#[derive(Component)]
struct Danger;

#[derive(Resource, Clone)]
struct UiPalette {
    panel: Color,
    border: Color,
    shadow: Color,
}

fn dark_palette() -> UiPalette {
    UiPalette {
        panel: Color::srgb(0.12, 0.13, 0.16),
        border: Color::srgb(0.35, 0.38, 0.45),
        shadow: Color::srgba(0.0, 0.0, 0.0, 0.45),
    }
}

fn light_palette() -> UiPalette {
    UiPalette {
        panel: Color::srgb(0.93, 0.94, 0.96),
        border: Color::srgb(0.55, 0.58, 0.64),
        shadow: Color::srgba(0.0, 0.0, 0.0, 0.18),
    }
}

fn paint_panels(
    palette: Res<UiPalette>,
    mut panels: Query<&mut BackgroundColor, (With<Panel>, Without<Danger>)>,
    mut danger: Query<&mut BackgroundColor, (With<Panel>, With<Danger>)>,
) {
    let danger_fill = Color::srgb(0.55, 0.15, 0.15);
    for mut color in &mut panels {
        color.0 = palette.panel;
    }
    for mut color in &mut danger {
        color.0 = danger_fill;
    }
}

fn toggle_theme(
    keys: Res<ButtonInput<KeyCode>>,
    mut kind: ResMut<ThemeKind>,
    mut palette: ResMut<UiPalette>,
) {
    if keys.just_pressed(KeyCode::F5) {
        *kind = match *kind {
            ThemeKind::Dark => ThemeKind::Light,
            ThemeKind::Light => ThemeKind::Dark,
        };
        *palette = match *kind {
            ThemeKind::Dark => dark_palette(),
            ThemeKind::Light => light_palette(),
        };
    }
}

pub struct ThemePlugin;

impl Plugin for ThemePlugin {
    fn build(&self, app: &mut App) {
        app.insert_resource(dark_palette())
            .init_resource::<ThemeKind>()
            .add_systems(Update, (toggle_theme, paint_panels).chain());
    }
}
```

A header uses a linear gradient instead of a flat fill. Stops are automatic, so they space evenly from top to bottom.

```rust
fn spawn_header(mut commands: Commands) {
    let gradient = LinearGradient::to_bottom(vec![
        ColorStop::auto(Color::srgb(0.15, 0.25, 0.45)),
        ColorStop::auto(Color::srgb(0.08, 0.1, 0.16)),
    ]);
    commands.spawn((
        Node {
            width: Val::Percent(100.0),
            height: Val::Px(72.0),
            ..default()
        },
        BackgroundGradient(vec![Gradient::Linear(gradient)]),
    ));
}
```

`WindowTheme` is OS chrome. It does not recolor `Node` entities.

```rust
use bevy::window::WindowTheme;

fn spawn_window(mut commands: Commands) {
    commands.spawn(Window {
        title: "Game".into(),
        window_theme: Some(WindowTheme::Dark),
        ..default()
    });
}
```

## Scope

- Theme colors, borders, radius, shadow, and gradients are components you set from your palette.
- `bevy::feathers` skins editor widgets. It does not replace the palette resource on a game HUD.

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
| Per-entity data | `Component` + `Query` | A free-floating struct outside the `World` |
| App-wide config or clock | `Resource` | Copy the value onto every entity |
| Stable simulation step | `FixedMain` and the `Fixed` clock | Tie simulation to raw frame `Update` |
| Startup spawn | `Commands` in `Startup` | Spawn from a render system |
| Cross-system notice that is not shared state | Message or observer slot in `bevy-events-messaging` | A new event type invented in this file |
| Shared UI colors | `UiPalette` plus one paint system | A new color written in every spawn system |
| A header wash | `BackgroundGradient` with `LinearGradient` | A second `BackgroundColor` on the same node |
| Editor chrome | `bevy::feathers` widgets | Reusing feathers as the game HUD skin |

Load [references/ecs-ownership.md](ui-theming-ecs-ownership.md) for the ownership table.

## NEVER

- Do not pin `/0.20.0/` in docs URLs. WHY: links stay on `latest`; the 0.20 target is stated once in prose.
- Do not mutably query the same component from two unordered systems. WHY: the schedule runs systems in parallel unless `.chain()` orders them.
- Do not invent a physics, navigation, networking, or XR crate here. WHY: this skill only names documented Bevy crates and modules.
- Do not treat `WindowTheme` as a HUD skin. WHY: it only selects OS window chrome (`Light` or `Dark`).
- No invented APIs or unnamed third-party crates as the chosen solver. WHY: Bevy code stays idiomatic ECS and uses only documented Bevy APIs.

## Reference

The library pin on bevy-master stays **0.20**.

### Official Documentation
- [Assets](https://bevy.org/assets/) - Official asset catalog.
- [Examples](https://github.com/bevyengine/bevy/tree/latest/examples#examples) - Example tree on the `latest` branch.
- [ECS](https://bevy.org/learn/quick-start/getting-started/ecs/) - `Component`, systems, `Query`, `Startup`, `Update`, and `.chain()`.
- [Plugins](https://bevy.org/learn/quick-start/getting-started/plugins/) - `Plugin`, `DefaultPlugins`, `MinimalPlugins`, and `add_plugins`.
- [UI examples](https://github.com/bevyengine/bevy/tree/latest/examples/ui) - Nodes, colors, and widget samples.

### Related Skills

#### Prerequisites
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Hub and schedules.
- [bevy-ecs-composition](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ecs-composition/SKILL.md) - Components and systems.
- [bevy-ui-layout](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ui-layout/SKILL.md) - Nodes being styled.

#### Complements
- [bevy-ui-text](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-ui-text/SKILL.md) - Font choices.

#### Downstream / consumers
- None yet.

#### Master
- [bevy-master](https://github.com/thedivergentai/Game-Dev-Agentic-Skills/blob/main/skills/bevy-master/SKILL.md) - Bevy router.
