# Lensed celestial spheres

Use this reference for what a geodesic ray lands on after it escapes: a
directional sky that stays stable when lensing compresses solid angle by orders
of magnitude, plus the accumulation and bloom that a sky with 400x point sources
in it demands. Constants are those of the `traversable-wormhole-transit`
example, whose `celestial-spheres.js` is the sky and whose `wormhole-effect.js`
owns the accumulation and bloom passes. For the integrator that produces the
directions, read [curved-ray-integrators.md](curved-ray-integrators.md).

## Contents

- The footprint contract
- Star lattice and flux-conserving point spread
- Luminosity law, temperature, and desaturation
- Galactic disc, dust, and nebulae
- Analytic planet and ring plane
- Bright sources under display clipping
- Progressive accumulation
- Bloom pyramid for compact sources
- Observed limits
- Diagnostics

## The footprint contract

Lensing conserves radiance but not solid angle. Near a lensing rim a pixel's ray
bundle can cover a huge patch of sky, and one sample of a point-sampled star
field there is noise, not signal. Every field below is therefore a function of
direction **and** of the bundle's angular width:

```text
foot = clamp(0.5 (length(dFdx(D)) + length(dFdy(D))), 0.0, 0.06)
```

`D` is the escaped direction, so the derivatives are taken through the whole
integration and automatically widen wherever the map is compressive. Rays that
never escaped get `foot = 0.06` — the maximum — so filtering hands back mean
radiance instead of a speckled point sample.

Two consumers use it directly:

```text
detail = 1.0 - smoothstep(0.0035, 0.028, foot)     fine nebula knots fade out
w      = max(foot, 2.0e-4)                          planet limb feather
e      = clamp(foot / 0.052, 0.0, 0.35)             ring-edge feather
```

## Star lattice and flux-conserving point spread

Stars live on a cube-face lattice, one candidate per cell, so a layer costs a
3x3 cell neighbourhood and no texture. Given a direction `D`, pick the dominant
axis, project to that face's `uv`, and scan the neighbourhood:

```text
cellAng = 1 / cells
s  = clamp(max(S0, 0.62 foot), S0, 0.5 cellAng)     spread radius
k  = S0^2 / s^2                                      flux-conserving peak
I  = flux k (exp(-0.5 d^2/s^2) + 0.005 exp(-d^2/(18 s^2)))
```

with `S0 = 0.00030` the intrinsic angular radius of a star. The second lobe is
the PSF wing: 3x the width, carrying 4.5% of the flux. Because the peak falls as
the width grows, total flux is invariant — compression at a lensing rim
brightens the star instead of aliasing it.

Existence and position come from hashes of the cell, never from the pixel:

```text
h  = hash33(vec3(cell, face 17 + seed))
sd = faceDirOf(face, (cell + h.xy) cellAng)
keep if h.z <= min(baseDens discDens(sd, ...), 1.0)
```

Evaluate the density at the star's own direction `sd`, not at the pixel's `D`,
or stars flicker in and out as the camera moves. Reject anything below
`I < 2.0e-4`: that is under an 8-bit step and under the bloom threshold.

Past roughly one cell per pixel, the lattice cannot be resolved and the correct
answer is the layer's analytic mean radiance — the field's own top mip, and the
physically right answer since lensing conserves radiance:

```text
meanFlux = lum 2.78 1.036                    E[u^-2/3] with u clamped, plus giants
meanRad  = (0.98, 0.96, 1.00) meanDens meanFlux 1.045 2pi S0^2 cells^2
result   = mix(sum, meanRad, smoothstep(0.30, 1.25, foot cells))
```

Three layers share one disc profile and cover three decades of population:

```text
cells =  30, density = 0.46 sDens, luminosity = 0.60  sLum, seed + 1
cells = 104, density = 0.34 sDens, luminosity = 0.18  sLum, seed + 11
cells = 300, density = 0.22 sDens, luminosity = 0.055 sLum, seed + 23
```

## Luminosity law, temperature, and desaturation

Flux follows the number-count law `N(<m) ~ 10^(0.6 m)`, which inverts to
`F ~ u^(-2/3)` for uniform `u`:

```text
u     = max(hash, 0.0016)                    clamp on the power law
giant = step(0.972, hash)                    ~3% evolved red giants
flux  = lum u^(-2/3) mix(1.0, 2.3, giant)
```

That heavy tail is the point: a handful of dominant stars over a dense faint
floor, instead of the flat field a uniform random amplitude produces.

Temperature is correlated with flux, because the main sequence is — and the
giants deliberately break the correlation, which is why the brightest stars in a
real sky are not all blue:

```text
ts = clamp(0.62 hash^6.5 + 0.38 (1 - u^0.30), 0.0, 1.0)
ts = mix(ts, 0.015 + 0.05 hash, giant)
colour = blackbody(mix(2700, 24000, ts))
```

`blackbody(T)` evaluates a piecewise fit to the Planck locus, then divides by
its own Rec. 709 luminance so temperature sets hue only and the luminosity
function alone sets brightness. Faint stars are mixed back toward white, because
below the cone threshold the eye reads a point source as colourless:

```text
tint = mix(vec3(1.0), colour, clamp(0.35 + 0.55 log2(1 + 6 flux), 0.35, 1.0))
```

No twinkle. Twinkle is atmospheric; there is no atmosphere in the scenes this
sky is for.

## Galactic disc, dust, and nebulae

One galaxy model is instanced per exterior region with a different frame, seed,
and palette. A galactic frame is a north pole plus a core direction
orthogonalised against it. Order the ingredients the way light reaches the
camera:

```text
sb    = dot(D, pole)                          sine of galactic latitude
lon   = 0.42 + 0.58 smoothstep(-0.55, 0.95, dot(D, core))
disc  = exp(-0.5 sb^2 / scaleH^2)
dpl   = exp(-0.5 sb^2 / (0.55 scaleH)^2)      dust is thinner than stars
bulge = max(dot(D, core), 0)^3.2 exp(-0.5 sb^2 / 0.11^2)
```

Dust is a column, not a paint layer. Build it from a ridged multifractal in a
domain-warped coordinate (filaments, not blobs), then attenuate with a
wavelength-dependent coefficient so the band is dimmed *and* reddened and the
dark nebulae are carved out of the light behind them:

```text
tau = dustAmp dpl lon (0.30 bulk + 1.25 smoothstep(0.34, 0.88, fil) (0.35 + 0.65 bulk))
ext = exp(-tau (1.00, 1.24, 1.52))            A ~ 1/lambda
```

Unresolved starlight is the milky band plus the bulge, tinted between a cool arm
colour and a warm bulge colour and multiplied by `ext`. Emission and reflection
nebulae are gated by a region mask so they read as a few discrete complexes
strung along the arms rather than an even wash, and they sit *inside* the disc,
so on average half the dust column lies in front of them — `sqrt(ext)`, not
`ext`. Resolved stars are attenuated by how much of the column is in front of
them, which is a proxy for depth:

```text
layer  30 (nearest): mix(vec3(1.0), ext, 0.40)
layer 104:           mix(vec3(1.0), ext, 0.75)
layer 300 (farthest): ext
```

The two regions in the example differ only by frame, seed and parameters — a
younger, bluer, thinner-dusted galaxy at `scaleH = 0.185` and an older, dustier,
redder one at `scaleH = 0.235` with `1.30x` star density and `1.45x` star
luminosity.

## Analytic planet and ring plane

A ringed gas giant is ray-traced analytically against the celestial sphere, so
it lenses exactly like the star field instead of being composited afterwards.
Sphere of angular radius `0.052`, `R = sin(ang)`:

```text
bq   = dot(D, C)
tS   = bq - sqrt(max(bq^2 - (1 - R^2), 0))         sphere entry
aP   = 1 - smoothstep(ang - w, ang + w, acos(bq))   footprint-feathered coverage
tR   = dot(C, axis) / dot(D, axis)                  ring-plane crossing
rad  = length(tR D - C) / R                         ring radius in planet radii
```

Ring optical depth is three banded regions with a ringlet modulation and a gap:

```text
C ring: smoothstep(1.12, 1.20+e) (1 - smoothstep(1.49, 1.53+e)) 0.30
B ring: smoothstep(1.52, 1.57+e) (1 - smoothstep(1.91, 1.95+e)) 0.95
A ring: smoothstep(2.02, 2.06+e) (1 - smoothstep(2.23, 2.27+e)) 0.66
ringlets: x (0.86 + 0.14 sin(173 rad))
gap:      x mix(0.18, 1.0, smoothstep(0.0, 0.006+e, abs(rad - 2.214)))
```

Composite by depth, not by fixed order: compare `tR` against `tS`, put the
nearer one in front, and return premultiplied colour with coverage in alpha so
the caller blends once. The ring shadow on the planet and the planet shadow on
the rings both come from projecting onto the light direction; skipping them is
the single most visible way this object stops reading as a solid body.

## Bright sources under display clipping

A sun in frame is two orders of magnitude brighter than anything else and
dominates the bloom, so its *rendered* image must be invariant under sub-pixel
motion. Flux invariance alone is not enough, because the display clips: ACES
sends everything above roughly `2.5` to white, so under a `420x` peak only the
bottom `~0.7%` of a feather is visible and the tone-mapped limb of a plain disc
lives in about `0.1 px`. That hard sub-pixel edge pops as it crosses the pixel
grid, and the bloom prefilter inherits the popping.

Give it a point spread wide enough for the display: flat core of radius `R`,
Gaussian limb with sigma tied to the bundle footprint, peak normalised by the
profile's own integral `pi (R^2 + sqrt(2 pi) R sigma + 2 sigma^2)`:

```text
sunR = 0.0050
sunS = 1.2 max(foot, 1.0e-5)
sunQ = max(length(D - sunDir) - sunR, 0.0)
c   += (1.00, 0.97, 0.92) 420 (sunR^2 / (sunR^2 + 2.5066283 sunR sunS + 2 sunS^2))
       exp(-0.5 sunQ^2 / sunS^2)
c   += (1.00, 0.95, 0.88) 0.55 exp(-lenD^2 / (2 0.0333^2))     the glare halo
```

Total flux is exactly `420 pi R^2` in every regime, so lensing can squeeze the
disc below a pixel and it dims into a wider splat instead of point-sampling in
and out of existence. Use the chord `length(D - sunDir)`, not `dot`: near
`cos ~ 1` a dot comparison spends all its precision against the `~1e-6`
direction noise surviving the integrator.

## Progressive accumulation

A per-pixel geodesic sky is too expensive to supersample per frame and too
high-contrast to leave at one sample, so converge it over time and reset on any
observer change:

```text
weight = accumCount > 0 ? 1/(accumCount + 1) : 1
out    = mix(previous, current, weight)          weight >= 0.999 replaces outright
accumCount = min(accumCount + 1, 512)
```

Replacing outright at full weight matters: it is what stops a stale or NaN
history from being blended into the first frame after a resize.

The jitter sequence is not a plain Halton sequence:

```text
accumCount == 0        -> jitter (0, 0)          pixel centre
accumCount <  512      -> Halton(2), Halton(3) at index accumCount + 1, minus 0.5
accumCount >= 512      -> white noise, minus 0.5
```

Frame 0 after a reset **is** the image while the observer moves, so it must sit
at the pixel centre — the mean of the converged set. Starting at Halton index 1
puts every moving frame `1/6 px` below the converged still, which snaps at every
start and stop, and a drag that hesitates for one frame restarts at index 2 or 3
with blend weight `1/2` or `1/3` — a sub-pixel hop that a bright compact source
shows plainly. In motion the sampling phase must be stationary, not
well-distributed.

## Bloom pyramid for compact sources

Every pyramid level decimates by two, so a sun with a display-space limb is one
or two texels wide at the levels that carry the halo. A 2x2 box — a single
bilinear tap — or a 4-tap corner box re-partitions a source that small between
output texels as it crosses their grid. Energy is conserved, but the shape the
coarse levels hand back up morphs with sub-texel phase and the halo breathes
while the camera moves.

Use the 13-tap downsample instead: five overlapping 2x2 boxes, half the weight
on the centre one, DC gain exactly 1.

```text
inner four taps at +/-1 texel : 0.125 each
centre tap                    : 4 x 0.03125
edge taps at +/-2             : 2 x 0.03125 each
corner taps at +/-2           : 1 x 0.03125 each
```

The rest of the chain: prefilter with a soft-knee threshold at `0.85` and knee
`0.55`, `5` levels each halving, then a 3x3 tent upsample added into the level
below with additive blending — which means the render target must not be
cleared between passes. Composite adds `bloom x 0.35` of level 0 to the
accumulated scene, then exposure `1.15`, ACES, vignette `0.34`, sRGB transfer,
and `0.03` of frame-indexed grain, in that order. Grain after the transfer is
deliberate; grain before it is reshaped by the curve and stops masking banding.

## Observed limits

- The sky is a pure function of direction, so it has no parallax. Objects on it
  are infinitely far away and any apparent motion comes from the integrator.
- The analytic mean radiance is a mean, not a blur: it is correct once cells are
  smaller than a pixel, and slightly flat in the transition band around
  `foot cells` in `[0.30, 1.25]`.
- The star lattice is a cube-face grid, so cell solid angle varies by about
  `3^(3/2)` between face centre and corner. Density is uniform per cell, not per
  steradian.
- Rendering at a fraction of the output resolution (`0.65` in the example)
  widens the effective footprint, which is self-consistent — the derivatives are
  taken in the render target — but changes the scale at which layers cross into
  mean radiance.
- Accumulation converges sampling noise, not integration error. Every sample
  runs the same step policy, so a step that is too coarse averages to the same
  wrong answer no matter how long the camera holds still.
- At `512` samples the blend weight freezes at `1/513` and the jitter switches
  to white noise, so the result becomes a rolling average holding a constant
  noise level rather than continuing to converge.
- Half-float targets are required. An 8-bit accumulation target loses the entire
  faint-star floor after the first blend.

## Diagnostics

Expose:

```text
ray-bundle footprint, and the mask where it saturates at 0.06
per-layer point-sample vs mean-radiance blend factor
star existence mask and per-cell density before the min(..., 1) clamp
dust column tau and the extinction it produces
region/HII/reflection masks separately from their colours
planet coverage, ring optical depth, and which surface won the depth test
accumulation sample count and the current blend weight
bloom prefilter output and each pyramid level
```

Read them this way: if the footprint view is saturated over a wide area the
integrator is diverging, not the sky; if the blend-factor view shows a hard ring
the layer's `cells` and the render scale disagree; if the bloom halo breathes
while the camera moves, the downsample kernel is the suspect, not the threshold.

Compare a converged still against a single frame at the same pose to separate
sampling noise from field error — they look identical in a screenshot and
completely different in motion.
