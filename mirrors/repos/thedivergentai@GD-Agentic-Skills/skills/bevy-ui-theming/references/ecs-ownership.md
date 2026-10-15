# ECS ownership - bevy-ui-theming

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |
| UI palette | `UiPalette` resource | insert in `Startup`; one `Update` system copies it onto `BackgroundColor` |

`toggle_theme` writes `UiPalette`. `paint_panels` is the only system that writes `BackgroundColor`, and `.chain()` runs it after the swap.

```rust
fn toggle_theme() {}

fn paint_panels() {}

fn register(app: &mut App) {
    app.add_systems(Update, (toggle_theme, paint_panels).chain());
}
```
