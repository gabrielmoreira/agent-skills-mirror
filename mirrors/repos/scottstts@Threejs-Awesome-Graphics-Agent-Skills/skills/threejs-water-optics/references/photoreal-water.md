# Photoreal shallow water

The `photoreal-water` example couples a gravity-capillary spectrum, local
heightfield disturbances, refracted bed radiance and aperture diffraction.
Read [the implementation](../examples/photoreal-water/photoreal-water.js)
for the complete GLSL passes and their JavaScript orchestration.

## Contents

- Integration contract
- Spectrum and surface intersection
- Local disturbances
- Dispersive caustics and bed radiance
- Glints and diffraction
- Limits
- Diagnostics

## Integration contract

```js
const water = await createPhotorealWater(gl);
water.setSize(bufferWidth, bufferHeight);
water.addDrop(worldX, worldZ);
water.render(seconds, { pos, f, r, u }, sunDirection, true);
// pos is metres; f/r/u and sunDirection are unit vectors in world space.
water.dispose();
```

The caller supplies a dedicated WebGL2 context and a perspective camera basis.
The vertical field of view is 64 degrees. Water uses world XZ with Y up.
The camera remains above the interface. The final pass writes to the default
framebuffer and owns tone mapping and output encoding; do not encode twice.
The final boolean advances the discrete ripple field; pass false while paused.
Size uses drawing-buffer pixels, independently of CSS dimensions.
The pebble image is an optical bed asset, loaded from the skill's assets.
The effect owns its programs, textures, buffers and framebuffers.

## Spectrum and surface intersection

The patch has 256 × 256 samples over 4.6 m and target RMS slope 0.078.
The deterministic seed is 7. A directional spectrum combines a 0.62 m peak,
a 1.6 m swell and a short-wave cutoff at 0.045 m.

```text
k = 2π (nx, nz) / 4.6 m
ω = sqrt(9.81 k + 7.4e-5 k³)
ωq = floor(ω / (2π/60 s)) (2π/60 s)
```

The spectrum evolves at `seconds * 0.9`. Two complex pairs pack height and
derivatives through horizontal and vertical Stockham passes. The resolved
texture stores height, two slopes and squared slope magnitude, with mipmaps.
The ray intersects the heightfield through three fixed-point updates.
A second field is rotated by the matrix `(0.8,-0.6,0.6,0.8)` and scaled by
0.41, with weight 0.10. A third rotated field contributes near-view slopes
at scale 0.13. Cubic B-spline filtering smooths the two principal slope bands.
Mip variance widens the specular distribution instead of preserving aliased
point highlights at distance.

## Local disturbances

The disturbance window is 256 × 256 samples over 7 m, snapped to whole texels.
It stores height and velocity in ping-pong RGBA16F targets.

```text
v = (v + 0.9 (four-neighbour average height - h)) * 0.9955
h = (h + v) * 0.9985
```

Border damping blends toward open water; samples shifted outside the window
are zeroed. A second pass computes central-difference slopes and a Laplacian.
Default drops use radius 0.022 in window UV and strength 0.07.
The field updates once per advancing render and stops after 900 calm frames.
Keep this cadence when comparing runs; it is a frame-based discrete model.

## Dispersive caustics and bed radiance

A 256² grid refracts sunlight to a receiver at mean depth 1.6 m.
Nine periodic instances cover the 1024² RGB caustic target.
Each colour uses its own index: 1.3315, 1.3335 and 1.3365.
The rasterized differential area controls additive intensity, clamped to 40.
The green flat-interface shift registers the periodic receiver pattern.
The view ray refracts with index 1.3335 and intersects the shelving bed with
two corrective depth evaluations. The pebble texture contributes colour and
coarse luminance relief, combined with cobble and sand zones.
Absorption is `(0.40,0.074,0.088)` per metre; scattering is
`(0.028,0.052,0.068)` per metre. Extinction uses their sum and the refracted
view-path length. The ripple Laplacian modulates local caustic focusing.
Exact unpolarized dielectric Fresnel weights reflection and transmission.

## Glints and diffraction

The sun lobe is Beckmann, with `a² = 0.00012 + 1.2 * variance`.
The aperture PSF uses a 512² Fourier transform, a near-hexagonal round stop,
five scratches, deterministic dust and eight wavelength bands from 440–650 nm.
FFT convolution applies the PSF to thresholded HDR glints. RG and B occupy
two complex grids. Bloom, exposure 0.63, ACES, saturation, shadow tint,
vignette, output power 1/2.2 and grain complete the image.

## Limits

Caustics use a constant receiver depth while the viewed bed varies in depth.
Ripple focusing is a curvature approximation, separate from the RGB grid.
Surface intersection has a fixed iteration budget and assumes an air-side view.
RGBA32F renderability enables glare; the half-float fallback omits it.
The effect is a complete shallow-water compositor, not a mesh material.
Use `$threejs-spectral-ocean` for open-ocean cascades and interface crossings.

## Diagnostics

`final` enables the complete calibrated image. `caustics` displays the RGB
receiver target. `no-post` removes glare and bloom while retaining display
treatment. `glare` isolates the diffraction target through the display pass.
Inspect the receiver before changing bed exposure or extinction coefficients.
Compare equal buffer sizes and times; grain and discrete ripple cadence vary
with time and frame count.
