# ECS ownership - bevy-genre-educational

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |

`pick_first` and `grade` both write `Choice`, so they share one `.chain()`. `graded` stops the same choice from incrementing `LessonProgress` on later frames. `show_score` only takes `Res<LessonProgress>` and stays off that chain. Do not invent crates or types.
