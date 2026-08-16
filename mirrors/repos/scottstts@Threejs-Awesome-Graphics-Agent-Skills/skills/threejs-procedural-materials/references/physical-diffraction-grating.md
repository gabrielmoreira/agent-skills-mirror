# Physical diffraction grating

Use this reference for reflective embossed foil whose colour is produced by a
wave-optical grating under a real emitter direction, rather than by a rainbow
texture, a time-driven UV band, or framebuffer colour separation.

## Contents

- Surface and layer contract
- Embossed microstructure fields
- Spectral reconstruction
- Phase-grating response
- Strip-emitter integration
- Stable object-space frame
- Observed limits and defects
- Diagnostics

## Surface and layer contract

The `physical-diffraction-grating` example is a three-layer card:

```text
z = -0.042   0.065-unit dark physical backing
z = -0.006   printed art, emissive intensity 0.82, roughness 0.58
z = +0.006   additive diffraction and clearcoat radiance
```

All three layers share a `6.45`-unit height and a width of
`6.45 × 1024 / 1536 = 4.30` units. A generated alpha texture rounds the card
with a radius equal to `0.065` of texture size.

The optical layer writes no painted hue and never changes opacity from a motif.
Black optical output contributes nothing; HDR radiance can exceed `1.0` and is
handled by ACES tone mapping at exposure `1.05`.

The implementation is a pure TSL node graph. `Fn` owns each optical function,
`If` gates physical branches, `Loop` evaluates both the finite Bessel recurrence
and bounded diffraction/emitter integrations, and `MeshBasicNodeMaterial.colorNode`
owns the resulting radiance. No native shader source string is embedded.

## Embossed microstructure fields

UV selects which groove field exists, not the returned spectral colour. The
star field uses an `8.5 × 11.5` cell grid. Four independent hashes control
presence, cell offset, star shape, local groove angle, pitch, and relief. The
cell contains either a four-point sparkle or five-point star boundary:

```text
sparkle4 = pow(0.5 + 0.5*cos(4*a), 7.5)
star5    = pow(0.5 + 0.5*cos(5*a), 5.2)
boundary = 0.070 + 0.205 * mix(sparkle4, star5, step(0.60, h2))
```

Three continuous stripe families use coordinates:

```text
(0.86u - 1.28v) × 5.0 + 0.12
(0.92u - 1.18v) × 3.9 - 0.06
(0.78u - 1.42v) × 2.8 + 0.18
```

Their half-width/softness pairs are `(0.032, 0.020)`, `(0.030, 0.019)`, and
`(0.027, 0.018)`. The families remain continuous until the card boundary; a
secondary vertical window would incorrectly clip a long spectral streak.

Laminate micro-normal height combines value noise at UV scales `310`, `760`,
and `92` with weights `0.48`, `0.22`, and `0.30`. The height is deliberately
small: `0.00014 × laminate`, plus `0.00010 × foilMask` detail.

## Spectral reconstruction

Wavelength lies in `[380, 720] nm`. The TSL graph evaluates the analytic CIE 1931
XYZ matching-curve approximation, transforms XYZ to linear sRGB, clamps
negative components, and weights the result by a `5250 K` blackbody spectrum
relative to its value at `560 nm`.

The blackbody constant is exact in nanometre-kelvin units:

```text
c2 = 1.4387769e7 nm·K
log B(λ,T) = -5 log λ - log(exp(c2/(λT)) - 1)
relative B = exp(log B(λ,T) - log B(560,T))
```

This spectral conversion is why hue changes with light, view, pitch, and order.
No UV value enters `spectralColor`.

## Phase-grating response

For incident direction `wi`, outgoing direction `wo`, normal `n`, groove
direction `G`, and periodic direction `T`:

```text
q        = wi + wo
qAcross  = dot(q, T)
qAlong   = dot(q, G)
λ_m      = pitchNm × abs(qAcross) / m
```

The example evaluates orders `m = 1..3`. Finite coherent length and microscopic
azimuth disorder form a normalized Gaussian density:

```text
σcoherence = 0.376 × λ / (coherenceUm × 1000)
σeffective = max(sqrt(σazimuth² + σcoherence²), 0.0025)
density    = exp(-0.5(qAlong/σeffective)²)
             / (2.50662827463 × σeffective)
```

Default pitch is `1180 nm`, relief is `86 nm`, coherent length is `14.5 µm`,
and azimuth sigma is `0.013`.

The sinusoidal relief phase and order efficiency are:

```text
phase = 2π × reliefNm × (n·wi + n·wo) / λ
efficiency_m = J_m(phase)²
```

`J_m` uses an eight-step recurrence after the leading `(x/2)^m / m!` term.
An aluminium-like Fresnel factor `0.84 + 0.16(1-n·wi)^5`, blaze envelope
`exp(-0.95(m-1)^2)`, and scale `0.165` complete the per-order weight.

## Strip-emitter integration

The fixed emitter centre is `(-1.95, 3.75, 5.35)`, its normalized axis begins
as `(0.94, -0.26, 0)`, its normalized emitting normal begins as
`(0.20, -0.54, -0.82)`, and its half-length is `4.9` world units.

Exactly `21` midpoint samples approximate the strip integral. The incident
direction uses a far-field approximation, `normalize(lightCenter + axis*s)`,
so it stays nearly constant across the card. After summation:

```text
diffracted *= (2 × halfLength / 21) × lightPower × gain
lightPower = 128
gain       = 5.1
```

The base grating contributes `0.018`, stripe gratings contribute `1.00`, and
star gratings contribute `1.10` inside their physical masks.

## Stable object-space frame

The material receives two world-space axes computed from the card object's
actual world quaternion every frame. The node graph projects the first axis onto
the geometric tangent plane and derives the second with a cross product.

This is required even for a planar card. Deriving grooves from world X/Y would
make the foil pattern slide when the object rotates; deriving them from camera
space would make the pattern follow the viewer. The optical frame must rotate
with the embossed object.

## Observed limits and defects

- The response models a one-dimensional sinusoidal reflective phase grating,
  low diffraction orders, and one far-field strip emitter; it is not a full
  wavefront solver.
- The visible lobe depends strongly on emitter direction. An uncalibrated light
  can legitimately return almost no diffraction.
- UV may define physical groove placement, angle, pitch, and relief, but using
  it to paint hue or motif opacity breaks the contract.
- A near-field line segment varies incident direction across the card enough to
  terminate long spectral ribbons prematurely.
- An unnormalized angular lobe loses energy as it narrows. The `1/(sqrt(2π)σ)`
  normalization is mandatory.
- The art texture is presentation input and remains outside the reusable
  material package; the material accepts any printed substrate texture.

## Diagnostics

The calibrated mode uses all default constants. `Stripe gratings` sets the
existing star-enable uniform to zero. `Shallow relief` changes relief from
`86 nm` to `24 nm`, exposing Bessel order-efficiency dependence. `Broad
azimuth` changes sigma from `0.013` to `0.080`, exposing lobe broadening and
peak-energy reduction.

When the effect looks like a painted rainbow, verify in order:

1. spectral colour receives wavelength only;
2. motif masks select groove fields but do not tint or change alpha;
3. object axes update from the world quaternion;
4. the emitter and camera lie on the reflecting side;
5. angular density includes its sigma normalization;
6. additive radiance is evaluated before tone mapping.
