# Layered procedural VFX systems

Use this reference for ship-conforming reentry plasma, generated wakes, instanced analytic sparks, dissolving debris, dense-swap pools, and scene-relative HDR contribution.

## Contents

- Reentry representation
- Reentry shell shading
- Wake construction
- Instanced spark contract
- Debris dissolve and pool ownership
- HDR contribution
- Observed limitations
- Diagnostics


## Reentry representation

A complete reentry system is not one particle emitter. It composes:

```text
ship-shaped front shell
  + expanding capsule core wake
  + larger low-opacity haze wake
  + two asymmetric side shear lobes
```

The shell is a clone of the actual ship mesh, scaled by `1.005`. This is the
key silhouette decision: plasma follows authored hull topology instead of a
generic sphere or cone.

The wake origin is found from sampled ship vertices. For the current local fall
direction, select the support point with the greatest dot product. Build an
orthonormal wake frame by projecting local up away from the fall direction,
falling back to local right when nearly parallel.

```text
wake forward = normalized fall direction
wake up = projected local up
wake right = cross(up, forward)
wake origin = hull support point along fall direction
```

The `reentry-plasma` example demonstrates the same grammar standalone: closed
layered wake shells with authored per-shell configs, flow-axis deformation,
advected filament fields, and opacity shaping, without requiring a host ship
mesh. Its shell constants are its own contract; read the example for exact
values.

## Reentry shell shading

The shell mask uses actual flow-facing geometry:

```text
facing = saturate(dot(normalWorld, -fallDirectionWorld))
facing mask = smoothstep(0.18, 0.96, facing)
```

Two world-space noise bands move along fall direction:

```text
coarse frequency = 3.6
fine frequency = 11.2
coarse/fine mix = 0.62 / 0.38
fine filament exponent = 3.1
flow speed basis = time * 5.4 + external flow * 0.08
```

The shell shader separates:

- core heat from flow-facing area;
- Fresnel envelope around silhouette;
- a shock band requiring high facing, rim response, and filaments.

Color hierarchy is explicit:

```text
hot core: orange -> near white
ion envelope: magenta -> violet
outer sheath: violet -> cyan
shock: white -> blue
```

The final shell uses additive blending, no depth write, depth test on, double
sided, and negative polygon offset. Treat the additive multiplier as part of
the scene’s HDR calibration, not a portable physical unit.

## Wake construction

Each wake is a generated capsule-profile tube. Along normalized length `t`:

```text
z = -trailLength * t
radial spread = 1 + t^1.24 * expansion
axial spread = 1 + 0.1 * t
profile turbulence = 1 + sin(theta * 3.3 + t * 8.7) * 0.1 * t
```

Dimensions relative to ship length:

```text
profile length = 0.74
profile radius = 0.068
trail length = 1.55

core: 52 radial x 26 longitudinal, expansion 1.9
haze: 40 x 20, radius 1.2x, length 1.05x, opacity 0.28
lobes: 28 x 14, half profile, length 0.88x, opacity 0.34
```

Wake shading uses elliptical profile distance, a front gate, tail fade,
coarse/fine longitudinal noise, Fresnel, and separate core/envelope/filament
colors. The core and haze use different scales and speeds instead of one mesh
with changed opacity.

## Instanced spark contract

Preallocate a fixed sprite pool of `12000`. Every instance stores:

```text
startPosition vec3
startVelocity vec3
acceleration vec3
spawnTimeSeconds float
```

Lifetime is `1.3 s`; velocity decay rate is `16`. Spark size falls linearly to
zero:

```text
scale = max((1.3 - age) * 0.4 / 1.3, 0)
```

The fragment is a circular sprite with radius `0.4`. HDR color interpolates
from `(1, 0.5, 0) * 80` toward dark red. Spawn adds random X/Z velocity in
`[-2, 2]`.

The pool is fixed-capacity and material attributes are per instance. No entity
owns an individual mesh.

## Debris dissolve and pool ownership

Debris spheres use:

```text
radius = 0.45
lifetime = random 2 -> 4 seconds
mass = 0.1
friction = 0.4
restitution = 0.8
gravity scale = 1.2
```

Per-instance material data:

```text
isOrange
removalTimeSeconds
```

Geometry-space noise creates a spatial dissolve against remaining lifetime.
The material also adds a Fresnel-shaped color response, a directional fake-AO
tint, and a low environment term of `0.05`.

When an instance is removed, the render system swaps the last live instance
into the vacant slot and copies:

- the 4x4 instance matrix;
- every custom attribute slice;
- the entity-to-index mapping.

This dense-swap invariant is the reusable pooling mechanism. Updating only
`mesh.count` without copying custom attributes would attach old effect state to
the moved instance.

## HDR contribution

The compact signals are intentionally bright before bloom:

```text
spark core multiplier: 80
homing projectile multiplier: 30
laser multiplier: 10
```

These values are evidence of relative hierarchy inside one calibrated scene,
not universal exposure-independent constants. Preserve the relationship:

```text
spark flash > projectile > laser > ordinary surface
```

Validate all three in the raw HDR buffer and with bloom disabled.

## Observed limitations

- Spark position multiplies an already integrated decayed velocity by elapsed
  time again. This is dimensionally inconsistent but visually deliberate.
  Preserve it only when that trajectory is explicitly required.
- Acceleration uses `a * t^2` rather than `0.5 * a * t^2`, also an artistic
  choice.
- Spark randomization uses `Math.random`, so captures are not deterministic.
  Replace it with a seeded generator for regression work.
- The reentry wake disables depth test. This avoids hull intersections but can
  draw through unrelated geometry. Validate camera and occluder assumptions.
- The shell and wakes are analytic procedural meshes, not fluid simulation.
  Do not describe them as physically simulated plasma.

## Diagnostics

Expose:

```text
fall direction and support point
shell facing/core/envelope/shock masks
coarse and fine wake noise
wake profile distance and tail fade
raw HDR emission by layer
bloom contribution by layer
spark age, velocity, and pool occupancy
debris remaining time and dissolve threshold
instance index/entity mapping
overdraw and depth-test modes
```
