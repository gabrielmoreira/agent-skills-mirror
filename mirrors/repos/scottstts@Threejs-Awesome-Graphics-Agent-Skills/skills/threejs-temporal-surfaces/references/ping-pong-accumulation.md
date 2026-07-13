# Touch-history frost accumulation

Use this reference for screen-space frost whose visible mask and refractive response depend on persistent touch history, reduced-resolution scene blur, static crystalline fields, and two-scale normals.

## Contents

- Exact pass graph
- Render-target ownership
- Persistent pointer state
- Frost composite
- Refraction output
- Observed defects and required corrections
- Diagnostic contract


## Exact pass graph

The frame graph owns these targets:

| Target | Resolution | Lifetime | Purpose |
| --- | --- | --- | --- |
| root | display DPR | every frame | source scene |
| vertical blur | `0.4` DPR | every frame | first separable blur axis |
| horizontal blur | `0.4` DPR | every frame | broad blurred source |
| frost composite | display DPR | every frame | scene, blur, structure, interaction |
| pointer read/write | display DPR, half-float | persistent | touched/cleared history plus tilt |
| frost noise | `0.4` DPR | once | coarse crystalline structure |
| frozen noise | display DPR | once | dense frozen structure |
| highlight noise | display DPR | once | highlight breakup |

Per-frame order is fixed:

```text
root scene
  -> vertical blur
  -> horizontal blur
  -> frost composite
  -> pointer history write and swap
  -> display output samples the new frost target
```

The frost pass therefore reads the pointer state from the previous completed
frame. Preserve that one-frame history relationship unless changing it
deliberately and validating the response.

## Render-target ownership

The single-target helper:

1. stores `renderer.autoClear`;
2. sets the requested clear mode;
3. binds the target;
4. renders;
5. restores the default target;
6. restores `autoClear`;
7. disposes the target on owner teardown.

The double-target helper writes only to `write`, exposes `read.texture` before
the draw, swaps after the draw, and returns the new `read.texture`.

```text
read = completed state
write = destination for this update
render(write, sampling read)
swap(read, write)
```

Both targets resize together. A production adaptation must define whether
resize preserves, resamples, or clears state. This implementation clears both
histories and marks static targets for regeneration on resize; keep an
explicit policy when adapting.

## Persistent pointer state

The pointer target uses:

```text
R = accumulated interaction mask
A = accumulated tilt-response mask
G/B = duplicate R in the output
```

Defaults:

```text
decay = 0.002 per 60 Hz frame,
        scaled as 0.002 * max(deltaSeconds * 60, 0.25)
noise strength = 0.16
frost-noise strength = 0.10
mask strength = 0.30
radius = 0.15 -> 0.17
corner fade = 0.50 -> 0.60
side fade = 0.00 -> 0.50
```

The update is:

```text
previous = max(previous - decay, 0)
center = pointer * 0.5 + 0.5
distance = aspect-corrected distance to center
deposit = edge-masked noisy radial brush when touching
Rnext = clamp(Rprevious + noisyDeposit, 0, 1)
Anext = clamp(Aprevious + lower-noiseDeposit, 0, 1)
```

The side and corner masks keep a circular deposit from clipping abruptly at
viewport boundaries. The alpha channel deliberately uses a less noisy brush so
device tilt can react smoothly while the visible thaw/frost boundary stays
irregular.

## Frost composite

The frost pass inverts pointer history:

```text
clearAmount = 1 - pointer.R
```

It combines three static structures:

```text
base structure = mix(frozenNoise, highlightNoise, 0.30)
coarse frost = contrast(frostNoise * 1.70 + frostAmount, 1.60)
mask = contrast(base structure + coarse frost * clearAmount, 1.80)
```

The scene treatment is coupled:

```text
blurMix = clamp(clearAmount * (mask + 0.30), 0, 1)
scene = mix(sharpScene, blurredScene, blurMix)
scene *= (0.90, 0.90, 1.03)
saturation *= 1.20
brightness *= 0.70
```

Frost color then mixes:

```text
thin tint  = (0.82, 0.86, 1.05)
thick tint = (0.92, 0.96, 1.10)
frost tint strength = 0.70
highlight tint strength = 0.80
```

The composite alpha stores the structural frost mask before the pointer is
applied. The output pass uses that alpha to gate normal-map refraction.

## Refraction output

The final pass samples two mirrored-repeat normal maps in screen coordinates:

```text
main scale size = 1200, strength = 0.30
sub scale size = 350, strength = 2.0
IOR = 1.31
thickness = 1.0
source inset = 0.17
Fresnel strength = 0.80
```

The main map also produces a grayscale height weight for the sub-map. Device
tilt rotates the view vector, with pointer alpha contributing up to `0.8`.
Refraction is mixed only where both frost alpha and the inverse pointer mask
permit it.

## Observed defects and required corrections

Keep these invariants when adapting; each one silently breaks the effect when
lost:

- Pointer decay must be frame-rate-compensated. The implementation scales it
  by delta time (`0.002 * max(deltaSeconds * 60, 0.25)`); the exact
  frame-rate-independent form is `1 - exp(-rate * deltaSeconds)`. Verify decay
  at 30, 60, and 120 FPS either way.
- Blur normalization must be guarded. The blur uses plain normalized Gaussian
  weights with an epsilon guard (`sum / max(weightSum, 1e-5)`). If an
  alpha-weighted blur is introduced, normalize RGB and alpha separately and
  guard fully transparent neighborhoods against a zero denominator.
- Pointer aspect must be owned by the actual pointer-target dimensions; assign
  it from the display size that the pointer targets use, never from a
  lower-resolution helper target.
- Static targets opt out of auto-resize. Regenerate them and clear history on
  resize, as this implementation does; a production policy may instead
  resample.
- Screen-space state follows the viewport, not the depicted surface. Do not use
  this representation for world footprints or object-bound paint.

## Diagnostic contract

Expose:

```text
root scene
vertical blur
horizontal blur
each static noise target
previous pointer R/A
current deposit R/A
next pointer R/A
frost mask before pointer
frost mask after pointer
sharp/blur mix
main and sub refraction offsets
final without refraction
final
```

Add pause and single-step controls. Verify decay at 30, 60, and 120 FPS.
