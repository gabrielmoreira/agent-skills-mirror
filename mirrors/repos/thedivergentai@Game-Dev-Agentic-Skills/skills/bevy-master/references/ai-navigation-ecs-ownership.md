# ECS ownership - bevy-ai-navigation

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |
| Mode | `Brain` component | read in `tick_policy` |
| Shared path | `PatrolRoute` resource | read-only in policy |
| Retarget | `RetargetClock` resource | one system ticks it |
| Output | `Goal` then `DesiredVelocity` | `FixedUpdate` chain: policy, then steer |

`tick_policy` writes `Goal`. `steer` reads `Goal` and writes `DesiredVelocity`. They must stay `.chain()`ed. Neither system writes `Transform`.
