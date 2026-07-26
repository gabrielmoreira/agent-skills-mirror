---
name: threejs-spectral-ocean
description: Build large procedural oceans in Three.js from directional wave spectra. Use for WebGPU/TSL FFT oceans, multi-cascade wavelength bands, hybrid FFT plus Gerstner clear-water oceans, stylized above/below surface optics, permanently submerged Snell-window views, total internal reflection, forward-refracted structures through an interface, pixel-footprint spectral LOD, aquatic perspective, caustic god rays, choppy displacement, spectral derivatives, Jacobian whitecaps, windrow and temporal foam, analytic sky reflection, underwater absorption, crest scatter, and GPU validation.
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
provides exact water-to-air Fresnel with a derivative-filtered critical-angle
mask, total internal reflection against a physically bright upwelling underside,
an energy-conserving transmitted-sun lobe, forward projection of above-water
structures into the window, shared HDR sky radiance, aquatic extinction and
in-scatter, footprint-faded differential-area caustics, full-resolution god rays,
suspended particulates, and the final HDR grade.

## Non-negotiable gates

- Require a power-of-two grid and a passing FFT impulse/frequency test.
- Keep cascade wavenumber intervals disjoint.
- Derive normals from transformed derivatives, not a detached normal texture.
- Detect breaking from the horizontal-displacement Jacobian.
- Persist foam in simulation state; do not infer all foam anew per frame.
- Submit FFT stages with the synchronization required by the active backend.
- Share sun and sky parameters between the visible sky and ocean reflection.
- Transport opposite-medium structures by FORWARD projection: rasterize their own vertices at their refracted screen positions. On an open interface, never trace a water pixel backward to a source screen position, and never gate transported radiance on whether a direction's vanishing point lands on screen. (A bounded pool seen only from air can still use the screen-space offset in `$threejs-water-optics`; an ocean whose camera changes medium cannot.)
- Bracket a water-side crossing solve by the critical angle (`tan θc ≈ 1.1346` times the ray's own distance from the interface), not by the camera-to-source span.
- Scale spectral LOD by PIXEL FOOTPRINT — `distance² · pixelAngle / heightGap` — and apply it to vertex displacement, derivatives, and every band that rides them. Fade each band to its own mean when the band is an albedo or radiance term.
- Filter the critical-angle domain test over about one output pixel; never filter the interface normal itself to stabilize what is transported through it.
- Gate the entire optical side from one camera-medium state; do not choose above/below behavior per triangle.
- Terminate distant underwater sightlines with a safely submerged terrain rim; do not mask an empty seabed/ocean horizon with a view-aligned scattering layer.
- Keep a deterministic seed and fixed-camera capture for comparisons.

## Route elsewhere

- Use `$threejs-water-optics` for bounded water, screen-space refraction, depth thickness, shoreline absorption, and analytic wave surfaces. Its screen-space refraction is valid there because the camera stays in air and the volume is bounded; it is not a substitute for this skill's forward projection across an open interface.
- Add `$threejs-procedural-vfx` only when crest spray or interaction splashes are required.
- Add `$threejs-visual-validation` for cross-seed, temporal, and GPU evidence.
