# Refractive window rain

## Contents

- Droplet field
- Surface normal and refraction
- Blur and presentation
- Controls and diagnostics
- Default parameter contract
- Layer activation contract
- Background fit contract
- Blur budget
- Failure modes

## Droplet field

Build the window coverage from three exact layers: static droplets, a primary
falling layer, and a second falling layer evaluated at `1.85` times the first
layer's scale. Each moving cell uses a hashed horizontal offset, a saw-shaped
lifetime envelope, a stretched drop body, and a thin trail containing smaller
secondary droplets. Combine the layers before deriving the optical normal.

Read
[the complete fragment shader](../examples/refractive-window-rain/rain-window.frag)
for the full field. Preserve its hash functions, layer frequencies,
intensity ramps, time scaling, and trail shaping together; changing only one
usually makes the drops tile or slide visibly.

## Surface normal and refraction

Evaluate the combined coverage at the current coordinate and at two offsets:

```glsl
vec2 e = vec2(.001, 0.) * u_normal;
float cx = Drops(uv + e, t, staticDrops, layer1, layer2).x;
float cy = Drops(uv + e.yx, t, staticDrops, layer1, layer2).x;
vec2 n = vec2(cx - c.x, cy - c.x);
```

Use `n` to offset the background lookup. This is the window's optical surface
normal; do not replace it with unrelated distortion noise.

## Blur and presentation

The blur is a stochastic disc around the refracted coordinate. Its angular
start comes from `gl_FragCoord`, while each tap gets a deterministic radial
distance. Keep the loop's compile-time maximum at 64 and break at the runtime
quality uniform. Preserve aspect-fill correction, cool color shift, optional
lightning, vignette, and brightness as separable presentation controls.

## Controls and diagnostics

Expose intensity, speed, normal strength, zoom, blur amount, blur iterations,
background fit, panning, color processing, lightning, and brightness. Provide
at least final, unblurred drops, and raw-color inspection modes. Report the
active layer count and blur tap count.

## Default parameter contract

```text
intensity       0.40
speed           0.25
brightness      0.80
normal strength 0.50
zoom            2.61
blur amount     0.50
blur iterations 16
background fill true
color processing true
lightning       false
```

Reset elapsed time on a six-hour modulo when an application can run
indefinitely so floating-point time does not erode cell animation.

## Layer activation contract

```glsl
float staticDrops = smoothstep(-.5, 1., rainAmount) * 2.;
float layer1 = smoothstep(.25, .75, rainAmount);
float layer2 = smoothstep(.0, .5, rainAmount);
vec2 coverage = Drops(uv, time, staticDrops, layer1, layer2);
```

The travelling layers return both drop coverage and trail coverage. Preserve
the vector result until combination; flattening it to one scalar loses the
secondary trail droplets.

## Background fit contract

Compare screen and texture aspect ratios. Scale only one UV axis around `0.5`
so the background fills the viewport without stretching:

```glsl
if (textureAspect > screenAspect) scaleX = screenAspect / textureAspect;
else scaleY = textureAspect / screenAspect;
UV = vec2(scaleX, scaleY) * (UV - 0.5) + 0.5;
```

Pass drawing-buffer resolution, not CSS size, when device pixel ratio differs
from one because both the procedural coordinate and blur hash use
`gl_FragCoord`.

## Blur budget

Compile a fixed maximum loop of 64. Exit once the loop index exceeds the
integer quality uniform. Keep the unblurred background sample before the loop
and divide the accumulated color by the configured iteration count exactly as
the implementation does. Use one iteration as the diagnostic no-blur path.

## Failure modes

- droplets are sampled in texture UV space and stretch with the background;
- refraction uses a second noise field instead of the droplet coverage;
- blur resolution uses CSS pixels while the shader uses device pixels;
- independently randomized blur taps shimmer between identical frames;
- aspect correction stretches the background image;
- window rain is routed as world-space falling particles.
