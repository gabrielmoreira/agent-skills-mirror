# ECS ownership - bevy-genre-sports

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
struct ScoreLine {
    team: u8,
    points: u32,
}

fn add_point(mut lines: Query<&mut ScoreLine>) {
    for mut line in &mut lines {
        line.points += 1;
    }
}
```
