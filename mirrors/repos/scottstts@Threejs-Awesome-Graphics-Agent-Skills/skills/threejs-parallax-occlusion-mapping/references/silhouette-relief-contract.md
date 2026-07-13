# Silhouette relief contract

## Contents

- Height and tangent-space convention
- Adaptive view march
- Silhouette coverage
- Curved hosts and inflated shells
- Normals and sampling
- Self-shadow and shadow-map ownership
- Diagnostics
- Quality and step contract
- Curvature representations
- Shell inflation contract
- Shadow positions
- Complete bulkhead assembly
- Failure modes

## Height and tangent-space convention

Read red-channel white as the peak and convert it to depth with `1 - height`.
March the view ray in the geometry tangent frame. Clamp the grazing-angle
denominator with `minViewZ`; use more layers at grazing angles than head-on.

## Adaptive view march

Advance by one normalized layer at a time until ray depth reaches sampled
surface depth. Interpolate between the final two layers. Materialize the march
result once so color, roughness, emission, and coverage reuse it. The normal
graph needs its own call because Three.js compiles `normalNode` in a distinct
build context.

## Silhouette coverage

For bounded flat tiles, evaluate coverage from the final marched coordinate,
not the starting UV. Clamp height fetches separately when `sampleBounds` are
provided so rays cannot hit a wrapped neighboring tile. Feather only the
coverage edge; use alpha-to-coverage for antialiasing.

## Curved hosts and inflated shells

For convex hosts, add sag to sampled depth as the ray travels. Support a
curvature callback, per-axis constant curvature, or a screen-derivative
estimate. Continue a coarse horizon chase after the regular march so tall
relief can still be hit beyond the base tangent horizon. Inflate the host shell
by maximum relief height so the height-field floor remains on the original
surface and peaks can extend beyond the base silhouette.

## Normals and sampling

Derive the tangent normal from central height taps around the marched UV. When
coverage can discard fragments, use explicit LOD taps for the normal graph to
avoid derivative sampling behind discard. Keep texture gradients from the
unshifted UV footprint for regular material sampling.

## Self-shadow and shadow-map ownership

March a second ray from the hit toward the light. Weight blockers by proximity
and apply the term to direct surface response rather than emission. To carve
cast shadows, assign the coverage test to `maskShadowNode`. For full relief
shadows, write marched depth in the shadow camera and use the same marched
world position for received-shadow lookup.

## Diagnostics

Expose height, final UV offset, hit/miss distance, coverage, curved sag,
horizon threshold, normal, self-shadow occlusion, shadow-mask coverage, and
marched shadow position. Sweep front, grazing, and axial views at every quality
tier.

## Quality and step contract

Use these tiers as a coherent starting point:

```text
low     min 8   max 32 view layers
medium  min 16  max 96 view layers
high    min 32  max 160 view layers
self shadow 20 steps, strength 12, bias 0.03
```

Interpolate layer count from maximum at grazing view to minimum head-on:

```glsl
layers = mix(maxLayers, minLayers, saturate(abs(viewDir.z)));
deltaUV = viewDir.xy / max(abs(viewDir.z), minViewZ)
          * scale / layers;
```

## Curvature representations

Choose one representation per host:

```text
curvature(coord) callback -> varying curvature across rounded boxes/capsules
[ku, kv] per-axis         -> cylinders and other separable parameterizations
screen derivative estimate -> fallback when no authored curvature is available
```

For a cylinder tiled `n` times around its circumference, use curvature
`[2π / n, 0]`. The axial component remains zero, so a ray travelling along the
cylinder does not accumulate false sag.

## Shell inflation contract

```text
tileAround = circumference / aroundTiles
reliefWorld = depthScale * reliefFactor * tileAround
positionNode = positionLocal + normalLocal * reliefWorld
```

The march treats red-channel white as the shell peak and black as the base
floor. Inflating by maximum relief world height lets the march subtract depth
back toward the original host surface.

## Shadow positions

```glsl
marchedWorld = positionWorld
  + tangentWorld * reliefOffset.x * worldPerTile.x
  + bitangentWorld * reliefOffset.y * worldPerTile.y
  - normalWorld * reliefDrop;

marchedClip = projectionMatrix * viewMatrix * vec4(marchedWorld, 1);
depthNode = marchedClip.z / marchedClip.w;
receivedShadowPositionNode = marchedWorld;
```

Build this graph in the active shadow-camera context. A beauty-pass depth value
cannot be reused as the light's shadow depth.

## Complete bulkhead assembly

Read the
[complete relief assembly](../examples/silhouette-relief/silhouette-relief-system.js)
with its [procedural packed maps](../examples/silhouette-relief/bulkhead-height-maps.js)
to preserve the full worked example. It contains a front/back blast-door wall,
a sixteen-unit relief deck, two curved relief columns, and two horizontal
relief pipes. The red channel owns height, green owns emissive strips, and blue
owns panel-tone variation across all three generated maps.

Do not reduce this example to isolated cylinders: the wall demonstrates flat
bounded silhouette carving, the columns and pipes demonstrate curved horizon
handling and shell inflation, and the deck demonstrates unbounded tiled relief
without silhouette clipping.

## Failure modes

- UV wrapping lets a grazing ray hit a neighboring tile;
- the miss test clips tall relief that should bridge the base horizon;
- every PBR channel triggers another full march in one build context;
- shell inflation and relief scale use different world conversions;
- beauty alpha test is mistaken for cast-shadow carving;
- self-shadow uses the world light without transforming it into the view/tangent frame;
- height normals sample implicit derivatives after discard.
