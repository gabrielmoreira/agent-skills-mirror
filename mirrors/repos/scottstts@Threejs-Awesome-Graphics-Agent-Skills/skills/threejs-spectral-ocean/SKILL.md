---
name: threejs-spectral-ocean
description: Build large procedural oceans in Three.js from directional wave spectra. Use for WebGPU/TSL FFT oceans, multi-cascade wavelength bands, hybrid FFT plus Gerstner clear-water oceans, stylized above/below surface optics, permanently submerged Snell-window views, total internal reflection, aquatic perspective, caustic god rays, choppy displacement, spectral derivatives, Jacobian whitecaps, temporal foam, analytic sky reflection, underwater absorption, crest scatter, and GPU validation.
---

# Spectral Ocean

Treat an ocean as a sampled stochastic wave field with explicit frequency-space ownership. Do not approximate this target with a pile of Gerstner waves, scrolling normal maps, or unrelated foam noise.

## Build order

1. Define the sea-state spectrum and deterministic Gaussian seed.
2. Partition wavelengths into disjoint cascades.
3. Validate the inverse FFT independently with analytic inputs.
4. Generate and conjugate-pack the initial spectrum.
5. Evolve packed displacement and derivative fields in frequency space.
6. Inverse-transform every packed field with explicit inter-step barriers.
7. Assemble displacement, derivatives, and persistent Jacobian foam maps.
8. Shade from summed cascade displacement and derivatives.
9. Add sub-grid detail only below the resolved simulation bands.
10. Expose spectrum, height, slopes, Jacobian, and foam-history diagnostics.

Read [references/spectral-cascade-ocean-system.md](references/spectral-cascade-ocean-system.md) before implementing or auditing a spectral ocean.

Read the [spectral cascade ocean system](examples/spectral-cascade-ocean/ocean-system.js)
and its adjacent spectrum, FFT, material, and detail modules for the cascade,
FFT, derivative, Jacobian, foam-history, and shading contracts. Its WebGL2
fragment-FFT backend is an explicit compatibility tier; preserve the
production WebGPU/TSL architecture described in the reference when the target
supports it.

Read the
[hybrid clear-water ocean material](examples/hybrid-clear-water-ocean/hybrid-ocean-material.js)
when the target needs FFT displacement with authored long swell, clear shallow
refraction, animated sand-bed caustics, Beer-Lambert color, shared sky
reflection, side-aware above/below surface normals, GGX sun highlights, and
foam diagnostics.

Read the
[stylized above/below ocean material](examples/stylized-above-below-ocean/stylized-ocean-material.js)
when the target needs a stylized FFT ocean that can be inspected from both
above and below the surface: height-gradient water color, sun-path glints,
crest scatter, Jacobian foam, water-tinted seafloor caustics, and an
underwater Beer-Lambert composite driven by scene depth.

Read the
[submerged Snell ocean system](examples/submerged-snell-ocean/underwater-snell-ocean.ts)
when the camera must remain underwater beneath a WebGPU spectral surface: it
provides surface-anchored above-water structure reprojection through Snell's
window, exact water-to-air Fresnel and total internal reflection, shared HDR
sky radiance, aquatic extinction and in-scatter, differential-area caustics,
full-resolution god rays, suspended particulates, and the final HDR grade.

## Non-negotiable gates

- Require a power-of-two grid and a passing FFT impulse/frequency test.
- Keep cascade wavenumber intervals disjoint.
- Derive normals from transformed derivatives, not a detached normal texture.
- Detect breaking from the horizontal-displacement Jacobian.
- Persist foam in simulation state; do not infer all foam anew per frame.
- Submit FFT stages with the synchronization required by the active backend.
- Share sun and sky parameters between the visible sky and ocean reflection.
- Start underwater structure reprojection at the displaced interface hit point; reject samples that are offscreen, on the wrong side of the interface, or misaligned with the refracted ray.
- Gate the entire optical side from one camera-medium state; do not choose above/below behavior per triangle.
- Terminate distant underwater sightlines with a safely submerged terrain rim; do not mask an empty seabed/ocean horizon with a view-aligned scattering layer.
- Keep a deterministic seed and fixed-camera capture for comparisons.

## Route elsewhere

- Use `$threejs-water-optics` for bounded water, screen-space refraction, depth thickness, shoreline absorption, and analytic wave surfaces.
- Add `$threejs-procedural-vfx` only when crest spray or interaction splashes are required.
- Add `$threejs-visual-validation` for cross-seed, temporal, and GPU evidence.
