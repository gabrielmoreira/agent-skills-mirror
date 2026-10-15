# ECS ownership - bevy-3d-lighting

Who owns each piece of state, and on which schedule.

Target: **Bevy 0.20+**.

| Need | Owner | Schedule |
| --- | --- | --- |
| Per-entity | `Component` + `Query` | `Update` or `FixedMain` |
| App-wide | `Resource` | insert in `Startup` |
| Spawn | `Commands` | `Startup` or the runtime schedule |
| Ordered mutation | `.chain()` | same schedule |
| Plugin setup | `Plugin` `build` | before run |
| Sun shadow atlas size | `DirectionalLightShadowMap` resource | insert once in `Startup` |
| Cascade distances | `CascadeShadowConfig` on the sun entity | spawn with the `DirectionalLight` |
| Which point lights cast | `PointLight.shadow_maps_enabled` | one `Update` system; chain any other writer |

`keep_nearest_point_shadows` is the only system that should write `PointLight` after spawn. A second writer in the same schedule must be `.chain()`ed with it or the shadow budget races.
