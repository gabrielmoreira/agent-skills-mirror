# GPU-culled flower field

Use this reference for very large procedural flower populations whose candidate
sites remain implicit, whose visible set is compacted on the GPU, and whose
geometry changes representation with projected distance without losing species
identity.

## Contents

- Virtual address space and storage contract
- Ecology and deterministic identity
- Hierarchical visibility compaction
- Distance-tiered flower geometry
- Wind, contact, and ground coupling
- Frame and resource ownership
- Observed limits and defects
- Diagnostics

## Virtual address space and storage contract

The `gpu-culled-flower-field` example addresses a square `gridSize × gridSize`
population by one `u32` candidate ID. The hot path reconstructs the grid
coordinate and a wide stochastic jitter directly in WGSL:

```wgsl
gridX = candidateId % gridSize
gridZ = candidateId / gridSize
jitter = hashU32(candidateId * 11 + seed)
root.xz = latticeRoot + decodedJitter * spacing * 8.60
```

No matrix, position, species, colour, wind phase, or scale record exists per
candidate. The only population-sized allocations are three visible-ID buffers,
each storing one `u32` per accepted flower. The implementation caps each tier at
`16 MiB`, for a `48 MiB` maximum three-tier working set, and supports a maximum
`2048 × 2048 = 4,194,304` virtual candidates on the baseline limits used by the
example.

The draw contract contains exactly eight indirect records, in this order:

```text
near stem 60       near petals 528      near centre 48
mid stem 24        mid petals 132       mid centre 18
far stem 6         far head 6
```

## Ecology and deterministic identity

The lattice is only an address space. Density comes from three rotated
value-noise octaves with weights `0.56`, `0.29`, and `0.15`; octave frequency
multipliers are `2.07` and `1.91`. Rotating each octave prevents a visible
axis-aligned interpolation grid.

The meadow probability is:

```text
broad  = organicField(root.xz, 0.024, 307)
detail = organicField(root.xz, 0.071, 401)
patch  = mix(0.10, 0.92, smoothstep(0.31, 0.73,
         broad * 0.78 + detail * 0.22))
keep   = density * patch * distanceDensity
```

Species selection is independent per candidate. The exact cumulative cutoffs
for the eight species are `0.25`, `0.41`, `0.45`, `0.56`, `0.74`, `0.89`, and
`0.93`. A second hash selects one of five dominant petal variants. Ecology
controls presence; it never paints large-scale species bands.

## Hierarchical visibility compaction

The hierarchy uses `32 × 32 = 1024` candidates per tile and a compute
workgroup size of `256`. One reset pass clears indirect counts. A tile pass
tests a conservative tile centre/radius against distance and clip bounds, then
atomically appends surviving tile IDs while incrementing an indirect dispatch
count.

The candidate pass launches indirectly: one workgroup per surviving tile, four
batches of `256` lanes, and one candidate per lane per batch. Accepted IDs are
atomically appended into near, middle, or far storage according to `24 m` and
`52 m` tier boundaries in the default profile. A one-workgroup finalize pass
fans each tier count out to every draw record that consumes the tier.

Flat compaction is a diagnostic/reference path. It runs the same acceptance
and tier functions over every candidate, so differences isolate hierarchy and
dispatch ownership rather than ecology or geometry.

## Distance-tiered flower geometry

Near stems use two crossed ribbons with five longitudinal segments. Near
petals use a `4 × 2` curved grid per petal and analytic derivatives for the
normal. Middle stems use two longitudinal segments; middle petals use a `2 × 1`
grid with the same species and dominant variant.

Petal count is species-dependent: the base counts are `5`, `6`, `8`, or `9`,
then the dominant variant adds `0`, `1`, or `2`. When mixed variants are
enabled, `62%` of slots keep the dominant variant and the remainder split
between a compatibility pair. The atlas has `8` species columns and `5`
variant rows.

Far flowers retain a rooted stem plus a six-vertex procedural head. The head
reconstructs species, scale, petal count, variant, and colour. It does not
collapse the field to one generic billboard colour.

## Wind, contact, and ground coupling

Stem position combines authored lean, two-frequency wind, and moving contact:

```text
static lean  ∝ along^curvePower
wind         ∝ (sin(1.1t + phase) + 0.32 sin(0.63t + 0.4phase)) along²
contact bend ∝ influence along²
```

Roots therefore remain fixed. Flower-head orientation comes from the terminal
stem tangent sampled at `along = 0.92` and `1.0`; heads follow bent stems rather
than remaining world-up.

The painted grass atlas is part of the colour contract for ground and stems.
It has `3 × 2` tiles, mirrored repeat coordinates, and explicit mip sampling
for stem palette matching. Removing it changes the field identity, not merely
the inspection stage.

## Frame and resource ownership

The reusable system owns the WebGPU device, canvas context, shader modules,
pipelines, bind groups, visible-ID buffers, indirect records, depth texture,
timestamp queries, and readback buffers. Its caller supplies each frame's
view-projection matrix, camera position, elapsed seconds, pixel size, and
contact state. The field compares the supplied view-projection against the
last compacted frame and automatically marks culling dirty when the camera or
projection changes.

Resize destroys and recreates only the depth texture. Grid-size changes rebuild
the three visible buffers, tile buffer, and dependent bind groups. Disposal
destroys every owned GPU texture, buffer, and query set.

## Observed limits and defects

- The system requires WebGPU storage buffers, compute, indirect dispatch, and
  indirect draws; it has no WebGL fallback.
- Each visible tier reserves for the full candidate count. This is bounded but
  intentionally trades memory for overflow-free atomics.
- Tile rejection is conservative. It reduces tests but cannot provide exact
  occlusion culling.
- Ground relief is excluded from candidate-root reconstruction. Introducing
  terrain displacement requires the ground and flower roots to share one
  callable height field.
- The far tier preserves identity but not atlas alpha detail or curved petals.
- A split CPU/GPU placement stack is a defect: it removes the zero-record
  contract and makes culling and drawing disagree about identity.

## Diagnostics

Use the four gallery modes as contract checks:

```text
Hierarchical compact  tile pass + indirect candidate pass + tiered draws
Direct reference      every candidate executes the same acceptance functions
Flat compaction       every candidate is compacted without the tile hierarchy
One petal variant     compatibility mixing disabled, species shape retained
```

Read back near/middle/far counts, surviving tile count, candidate tests,
four-byte ID memory, frame percentiles, submit time, and GPU render/cull time.
If direct and compact paths disagree visually, inspect root reconstruction,
acceptance, and draw-count fan-out before tuning culling margins.
