# ECS ownership - bevy-genre-open-world

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
struct Resident {
    cell: i32,
}

#[derive(Resource)]
struct PlayerCell(i32);

fn read_cell(cell: Res<PlayerCell>, residents: Query<&Resident>) {
    let _here = cell.0;
    for resident in &residents {
        let _near = (resident.cell - cell.0).abs() <= 1;
    }
}
```
