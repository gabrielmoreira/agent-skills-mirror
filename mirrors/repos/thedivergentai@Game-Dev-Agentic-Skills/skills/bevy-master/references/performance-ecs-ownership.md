# ECS ownership - bevy-performance

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
fn chain_example(app: &mut App) {
    app.add_systems(Update, (write_health, read_health).chain());
}

#[derive(Component)]
struct Hp(i32);

fn write_health(mut query: Query<&mut Hp>) {
    for mut hp in &mut query {
        hp.0 -= 1;
    }
}

fn read_health(query: Query<&Hp>) {
    for hp in &query {
        let _ = hp.0;
    }
}
```
