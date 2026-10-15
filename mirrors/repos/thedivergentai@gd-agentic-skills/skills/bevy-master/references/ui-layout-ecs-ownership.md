# ECS ownership - bevy-ui-layout

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |

The startup system spawns the node. A later system is the only writer of `BackgroundColor` on buttons.

```rust
fn spawn_panel(mut commands: Commands) {
    commands.spawn((
        Node {
            width: Val::Px(200.0),
            height: Val::Px(80.0),
            ..default()
        },
        BackgroundColor(Color::srgb(0.1, 0.1, 0.1)),
    ));
}
```
