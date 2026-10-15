# ECS ownership - bevy-testing-patterns

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |

The test inserts the resource, runs one `Update`, and reads it back. That is the same owner the game plugin uses.

```rust
#[derive(Resource)]
struct Score(u32);

fn add_point(mut score: ResMut<Score>) {
    score.0 += 1;
}

#[test]
fn score_moves_once() {
    let mut app = App::new();
    app.insert_resource(Score(0)).add_systems(Update, add_point);
    app.update();
    assert_eq!(app.world().resource::<Score>().0, 1);
}
```
