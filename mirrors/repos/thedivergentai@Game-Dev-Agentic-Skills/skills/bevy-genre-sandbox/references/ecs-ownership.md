# ECS ownership - bevy-genre-sandbox

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |

```rust
#[derive(Component)]
struct PlacedCell {
    kind: u16,
}

fn read_cells(cells: Query<&PlacedCell>) {
    for cell in &cells {
        let _ = cell.kind;
    }
}
```
