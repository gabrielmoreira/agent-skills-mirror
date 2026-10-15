# ECS ownership - bevy-ui-text

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |
| The string on one label | `Text` or `Text2d` | the one system that formats it |
| A styled run inside that string | child `TextSpan` | the system that spawns or rewrites that span |

`Score` is the resource. `ScoreLabel` marks the one `Text` that may change. `write_score` is the only system that mutably queries that `Text`.

```rust
#[derive(Component)]
struct ScoreLabel;

#[derive(Resource)]
struct Score(u32);

fn write_score(score: Res<Score>, mut labels: Query<&mut Text, With<ScoreLabel>>) {
    if !score.is_changed() {
        return;
    }
    for mut text in &mut labels {
        text.0 = format!("Score {}", score.0);
    }
}
```
