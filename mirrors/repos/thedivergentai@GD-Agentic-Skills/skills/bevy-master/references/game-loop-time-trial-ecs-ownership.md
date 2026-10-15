# ECS ownership - bevy-game-loop-time-trial

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |

`tick_race`, `record_split`, and `cross_finish` all take `ResMut<RaceClock>`, so they share one `.chain()` on `Update`. `drive` only moves `Transform` on `FixedUpdate` and must not write the race clock. A split is recorded when the racer passes a `SplitGate`, once, via `taken`. Do not invent crates or types.
