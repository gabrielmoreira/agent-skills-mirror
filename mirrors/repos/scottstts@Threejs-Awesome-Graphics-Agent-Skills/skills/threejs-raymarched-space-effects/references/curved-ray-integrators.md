# Curved-ray numerical integrators

Use this reference for an RK4 wormhole integrator and an artistic inverse-square curved-ray accretion volume, including state reduction, disk accumulation, background lensing, and numerical diagnostics.

## Contents

- Wormhole state reduction
- Wormhole RK4 integration
- Universe selection
- accretion volume screen-volume integration
- Disk density and color
- Background lensing
- Observed defects and boundaries
- Diagnostics


## Wormhole state reduction

The wormhole renderer uses a spherically symmetric throat model. It reduces
each 3D ray to a two-dimensional integration state:

```text
y.x = signed radial coordinate l
y.y = radial momentum pL
impact parameter b = length(cross(rayOrigin, rayDirection))
throat radius Rth = 1.2
```

It constructs an orbital plane:

```text
normal = normalize(cross(origin, direction))
u = normalize(origin)
v = cross(normal, u)
```

Near-radial rays use fallback axes to avoid a zero cross product.

Initial signed coordinate:

```text
l = sqrt(max(length(origin)^2 - Rth^2, 0.001))
pL = dot(normalize(origin), direction)
```

## Wormhole RK4 integration

The derivative is:

```text
r2 = l^2 + Rth^2
dl/ds = r2 * pL
dpL/ds = b^2 * l / r2
```

The shader runs fourth-order Runge–Kutta with:

```text
maximum iterations = 920
base step = 0.0042
per-ray step jitter = +/- 0.00045
escape distance = abs(l) > 40
azimuth accumulation = step * b
```

On escape:

```text
finalDirection =
  normalize(u * cos(phi) + v * sin(phi))
```

The sign of final `l` selects which exterior universe is visible. Failure to
escape renders a bright fallback color, making iteration-cap pixels observable.

This is materially stronger than a UV swirl because the final environment
direction comes from numerical integration.

## Universe selection

The two exterior universes are independent procedural directional fields. Both
use five-octave FBM, animated coordinate drift, broad/fine structure, and
different plane orientation.

Sample those fields only after integration. Lensing must change the lookup
direction rather than distort an already rendered screen image.

A small direction-hashed grain of amplitude `0.01` reduces visible gradient
banding.

## accretion volume screen-volume integration

The black-hole effect is evaluated on a sphere surrounding the effect. Defaults:

```text
iterations = 128
step = 0.0071
ray jitter = 0.01
bending power = 0.3
core radius = 0.13
disk half-width = 0.03
```

Per step:

```text
r = length(rayPosition)
steerMagnitude = step * power / r^2
steerRange = remapClamped(r, 1 -> 0.5, 0 -> 1)
newDirection = normalize(direction - radial * steerMagnitude * steerRange)
```

The ray direction is bent toward the center only inside the configured range.
Unlike the wormhole, this is an artistic inverse-square steering field, not a
validated metric geodesic.

## Disk density and color

Disk coordinates rotate around the local Z axis with radius and time:

```text
rotation phase = radialDistance * 4.27 - time * 0.1
noise UV = rotatedPosition * 2
```

A repeated deep-noise texture is multiplied by a quadratic band across
`[-width, 0, +width]`. Radial distance, noise value, and a nearby noise sample
produce a ramp coordinate.

The three-point color ramp is:

```text
white-hot at 0.06
gold at 0.33
dark amber at 1.0
emission scale 1.95
additional emission color (1.0, 0.72, 0.26)
```

The central sphere below `originRadius` is black. Disk opacity accumulates
front-to-back into `alphaAcc`; color accumulates using remaining transmittance.

## Background lensing

After the fixed loop, the final bent direction samples a deterministic
equirectangular star texture generated from `5200` seeded stars on a sphere.

```text
final = accumulated disk color
      + remaining transmittance * star environment
```

The deterministic star field is important: lensing motion can be compared
without random stars moving between runs.

## Observed defects and boundaries

- The demonstrated accretion-volume loop advances `rayPosition` twice per
  iteration while its steering magnitude uses a single `step`. Treat the
  effective distance step as `2 * step`, or remove the duplicate advance and
  retune the complete density-and-bending system explicitly.
- accretion volume has no early exit and no termination IDs; every pixel pays the full
  iteration count.
- Its disk is detected by local band density at samples, not by a continuous
  plane-crossing test. A large step can skip a thin disk.
- The artistic inverse-square steering must not be described as general
  relativity.
- The wormhole uses a fixed high iteration cap and per-ray step jitter but has
  no CPU reference-ray tests.
- Both effects render on bounded proxy geometry; coordinate transforms must be
  verified if the proxy is nonuniformly scaled or moved far from the origin.
- The star texture is finite-resolution and can alias under extreme
  magnification.

## Diagnostics

Expose:

```text
wormhole l and pL
impact parameter and orbital-plane basis
RK4 step count and escaped/capped state
final exterior side and environment direction
accretion volume radius and steering magnitude
effective traveled distance
disk band, noise, ramp coordinate, and local alpha
accumulated alpha and remaining transmittance
core-hit mask
final bent background direction
NaN/invalid-state mask
```

Add CPU reference rays for the wormhole before claiming physical parity, and a
continuous disk-crossing variant before increasing accretion volume’s step size.
