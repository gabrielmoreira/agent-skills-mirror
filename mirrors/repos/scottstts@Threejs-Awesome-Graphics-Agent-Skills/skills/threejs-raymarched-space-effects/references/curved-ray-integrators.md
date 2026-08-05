# Curved-ray numerical integrators

Use this reference for two wormhole throat integrators and an artistic inverse-square curved-ray accretion volume, including state reduction, observer transport, disk accumulation, background lensing, and numerical diagnostics. For metric-derived Schwarzschild null-geodesic integration with interpolated disk crossings and Doppler-shifted emission, read the `schwarzschild-geodesic-black-hole` example directly. For what a wormhole ray lands on once it escapes, read [lensed-celestial-spheres.md](lensed-celestial-spheres.md).

## Contents

- Two throat models
- Fixed-radius throat: state reduction
- Fixed-radius throat: RK4 integration
- Shaped throat: metric and observer frame
- Shaped throat: adaptive RK4 integration
- Universe selection
- Accretion-volume integration
- Disk density and color
- Background lensing
- Observed defects and boundaries
- Diagnostics


## Two throat models

Both models are spherically symmetric and ultrastatic, so both reduce every 3D
ray to a planar problem with one conserved quantity. They differ in the shape
function `r(l)` and therefore in step policy and cost:

- **Fixed-radius throat.** `r(l) = sqrt(l^2 + Rth^2)`: one smooth hyperbolic
  neck, no free lensing width. A uniform step is adequate everywhere. Cheap,
  and the distortion is broad and soft.
- **Shaped throat.** A cylindrical neck of half-length `a` joined to lensing
  shoulders of width `W`, so the throat radius is exactly constant across the
  neck and the lensing is concentrated in a band you control independently of
  the throat size. This is what produces a razor-thin rim around a
  crystal-ball sphere instead of a soft fisheye. It needs an adaptive step,
  because the curvature scale collapses from `~r` far away to `M` at the
  shoulder. The `traversable-wormhole-transit` example implements this model.

Constants below belong to one model or the other; do not mix them.

## Fixed-radius throat: state reduction

Reduce each 3D ray to a two-dimensional integration state:

```text
y.x = signed radial coordinate l
y.y = radial momentum pL
impact parameter b = length(cross(rayOrigin, rayDirection))
throat radius Rth = 1.2
```

Construct an orbital plane:

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

## Fixed-radius throat: RK4 integration

The derivative is:

```text
r2 = l^2 + Rth^2
dl/ds = r2 * pL
dpL/ds = b^2 * l / r2
```

Run fourth-order Runge–Kutta with:

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

## Shaped throat: metric and observer frame

The `traversable-wormhole-transit` example integrates

```text
ds^2 = -dt^2 + dl^2 + r(l)^2 (dtheta^2 + sin^2 theta dphi^2)
```

with the shape function and its derivative:

```text
x       = 2 (|l| - a) / (pi M)
r(l)    = rho                                          for |l| <= a
r(l)    = rho + M (x atan(x) - 0.5 ln(1 + x^2))        otherwise
dr/dl   = 0                                            for |l| <= a
dr/dl   = sign(l) (2/pi) atan(x)                       otherwise
```

`l` is proper radial distance and is negative on the far side: one global
coordinate runs straight through the neck into the other exterior region, so
there is no handoff and no second chart. The lensing parameter follows from the
lensing width by `W = 1.42953 M`. The example fixes

```text
rho = 1.0            (the unit of length)
W / rho = 0.05       ->  M = 0.05 / 1.42953 = 0.03497...
2a / rho = 0.01      ->  a = 0.005
```

Because the metric is ultrastatic and spherically symmetric, every null
geodesic stays in the plane spanned by the observer's radial vector and the
ray's tangential component. That reduction is exact, removes the polar
coordinate singularity, and leaves three variables with one conserved quantity
`b = r^2 dpsi/dt`:

```text
y      = (l, psi, p_l)
dl/dt   = p_l
dpsi/dt = b / r^2
dp_l/dt = b^2 (dr/dl) / r^3
```

The observer cannot be a Cartesian camera, because no global Cartesian chart
survives the neck. Carry a point on the sphere plus a tangent frame instead:

```text
U = unit sphere point       A, B = tangent frame,  A x B = U
l = signed radial coordinate
yaw, pitch -> uCamRot, whose columns are the camera x/y/z axes
              written in (e_l, A, B) components
```

Per ray, seeded from that frame:

```text
n     = uCamRot * normalize(vec3(px 2 tan(fov/2), py 2 tan(fov/2), -1))
m     = length(n.yz)                       tangential magnitude
tHat  = normalize(n.y A + n.z B)           (fall back to A when m < 1e-9)
b     = r(l_cam) * m                       conserved angular momentum
y     = (l_cam, 0, n.x)
```

Motion is a step in `l` plus a parallel transport of the frame along a great
circle. For a displacement of length `d` whose components in `(e_l, A, B)` are
`(cl, ca, cb)`:

```text
l += cl d
t  = normalize(ca A + cb B)
rotate U, A, B about (U x t) by  d |(ca, cb)| / max(r(l), 1e-4)
re-orthogonalise: U normalized, A -= (A.U) U, B = U x A
```

Speed must scale with the local sphere radius or the neck is impassably slow
and the far field is impassably large:

```text
v = speed dt clamp(0.35 r(l), 0.10, 14.0)      speed = 1.0, x4 while sprinting
```

## Shaped throat: adaptive RK4 integration

The step is chosen from the local curvature scale: `M` at the shoulder, `~r`
far away, and unbounded inside the neck, where `r` is constant so the solution
is linear and RK4 is exact for any `h`.

```text
k = 0.15                                     step coefficient
|l| <= a : h = min((a - |l|) / max(|p_l|, 1e-4) + k M, 40 (a + rho))
|l| >  a : h = k min(r, M + 0.9 (|l| - a))
h = max(h, 1e-5)
```

Standard RK4 on `y` with the derivative above, capped at `1024` iterations.
`k = 0.15` holds the worst case — a ray grazing the lensing rim — within about
`0.13 px` of a `40000`-step solution at 1080p and a 50 degree field of view,
for roughly `25-98` steps per ray.

Termination, tested before each step:

```text
escaped: r > 260 and (dr/dl) p_l > 0        asymptotically flat and receding
escaped: abs(l) > 1e7                       numerical runaway, treat as escaped
capped : the iteration limit was reached
```

The asymptotic direction is rebuilt in the frame carried around by the swept
angle `psi`, from the radial component `(dr/dl) p_l` and the tangential
component `b / r`:

```text
uf =  U cos(psi) + tHat sin(psi)
tf = -U sin(psi) + tHat cos(psi)
D  = (dr/dl) p_l uf + (b / r) tf            normalize; fall back to uf if degenerate
```

## Universe selection

The sign of `l` at termination selects the exterior region, and each region owns
an independent directional field:

- A cheap pairing is two procedural directional fields with five-octave FBM,
  animated coordinate drift, broad/fine structure, and different plane
  orientation. A small direction-hashed grain of amplitude `0.01` reduces
  visible gradient banding.
- The `traversable-wormhole-transit` example instead evaluates one galaxy model
  twice, under different galactic frames, palettes and seeds, and filters it by
  the ray-bundle footprint. See
  [lensed-celestial-spheres.md](lensed-celestial-spheres.md).

Whichever field is used, sample it only after integration. Lensing must change
the lookup direction rather than distort an already rendered screen image.

Orient the far region deliberately. A ray fired straight down the neck exits
along one fixed axis, so put that region's brightest structure on that axis;
otherwise the throat reads as a black hole rather than a window.

## Accretion-volume integration

The `curved-ray-accretion-volume` example is evaluated on a sphere surrounding
the effect. Defaults:

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
- The accretion volume has no early exit and no termination IDs; every pixel
  pays the full iteration count.
- Its disk is detected by local band density at samples, not by a continuous
  plane-crossing test. A large step can skip a thin disk.
- The artistic inverse-square steering must not be described as general
  relativity.
- The fixed-radius throat uses a fixed high iteration cap and per-ray step
  jitter but has no CPU reference-ray tests.
- Rays that wind the photon sphere at `|l| ~ 0` never escape. Their exit
  direction is wherever the integrator happened to be pointing, which speckles
  pixel to pixel. They sample effectively the whole sphere, so hand them the
  maximum footprint and let filtering return the mean radiance instead of a
  point sample; a flat fallback color is a diagnostic, not a shipping image.
- Raising the iteration cap does not remove those pixels. It only moves the
  boundary; the winding set is measure-nonzero at any cap.
- The shaped throat's step policy is tuned to `rho = 1`. Changing `rho`, `W`, or
  `a` changes the curvature scale, so re-measure the step coefficient against a
  high-step solution instead of assuming `0.15` still holds.
- The shaped throat is integrated in a plane per pixel with no CPU reference
  rays either; parity claims need an independent CPU integrator first.
- Both accretion effects render on bounded proxy geometry; coordinate
  transforms must be verified if the proxy is nonuniformly scaled or moved far
  from the origin.
- The star texture is finite-resolution and can alias under extreme
  magnification.

## Diagnostics

Expose:

```text
wormhole l and pL, or (l, psi, p_l) for the shaped throat
impact parameter / conserved b and the orbital-plane basis
RK4 step count and escaped/capped state
final exterior side and environment direction
ray-bundle footprint used to filter the celestial sphere
accretion-volume radius and steering magnitude
effective traveled distance
disk band, noise, ramp coordinate, and local alpha
accumulated alpha and remaining transmittance
core-hit mask
final bent background direction
NaN/invalid-state mask
```

Read them this way: a step-count view that saturates over a wide band means the
step policy has collapsed, not that the scene is expensive; a capped-ray view
should be a thin ring around the throat rim, and a filled disc means the escape
radius is too large for the iteration cap.

Add CPU reference rays for either wormhole before claiming physical parity, and
a continuous disk-crossing variant before increasing the accretion volume's step
size.
