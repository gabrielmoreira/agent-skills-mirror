# Procedural Optimus humanoid assembly

Use this reference for a complete human-scale hard-surface robot built from
parameter curves, semantic polygon generators, exact cut operations, authored
bevels, per-corner normals, and material identities that remain readable across
white shells, black polymers, metals, rubber, glass, and emissive details.

## Contents

- Coordinate frame and assembly evidence
- Polygon mesh and modifier contract
- Loft, spine, and pillow generators
- Semantic humanoid construction
- Material identity system
- Geometry emission and ownership
- Observed limits and defects
- Diagnostics
- Failure diagnosis

## Coordinate frame and assembly evidence

The `procedural-optimus-humanoid` example uses metres, keeps `+Z` upward, faces
the figure toward `-Y`, and places the origin on the floor midway between the
ankles. The completed bounds are:

```text
minimum = (-0.2822209001, -0.1870000064, -0.0016486322) m
maximum = ( 0.2822209001,  0.1903314888,  1.7320995331) m
```

The emitted assembly contains `176` named mesh objects and `891,809` triangles
across seven semantic groups:

```text
TORSO 25   HEAD 2   ARM 22   HAND 56
HIP   27   LEG 38   FOOT 6
```

These counts are deterministic evidence. Do not merge groups or delete small fittings
before recording them; the object hierarchy is how the construction stays
inspectable.

## Polygon mesh and modifier contract

The internal mesh holds polygon faces rather than pre-triangulated buffers:

```text
v      vertex positions
f      polygon index loops
fm     material slot per face
fg     generated-face class
mats   material names by slot
mods   pending bevel and boolean operations
```

Welding uses a spatial hash and a default `2e-5 m` distance. It removes
duplicate and degenerate polygons, then reconstructs consistent winding across
each connected shell. Whole shells with negative signed volume are flipped.

Boolean difference uses a BSP polygon split with `CSG_EPS = 1e-9`. Faces of
the minuend are first separated by cutter bounds so distant polygons bypass
the BSP. The rebuilt fragments are welded at `1e-6 m` before winding repair.

Bevel ownership is angle-limited. The modifier identifies shared edges whose
face-normal dot product falls below `cos(angle)`, constructs inset face sectors,
emits the requested profile arcs, and closes bevel-vertex patches. Bevel faces
carry a generated-face class so the corner-normal stage can keep them hard
where required.

## Loft, spine, and pillow generators

`Curve1D` provides two interpolation modes. Shape-preserving cubic Hermite
slopes prevent overshoot in authored dimension tracks; a natural cubic solve
provides C2-continuous tracks where smooth curvature is required.

The section profile is a four-quadrant superellipse with independent positive
and negative half-axes and upper/lower exponents. `profile()` first samples
`512` dense points, accumulates perimeter distance, and blends arc-length and
uniform-angle spacing with the `even` parameter.

`loft()` samples station curves for axes, offsets, exponent, rotation, and
scale. Rounded caps use five rings whose radius follows
`cos(πf/2)^0.85` and whose axial distance follows `sin(πf/2)`.

`loftSpine()` fits a cubic path, computes centered tangents, and propagates its
normal by projection onto each new tangent plane. This parallel-transport frame
prevents the torsional flips produced by a fixed world-up cross product.

`pillow()` emits paired front and back surfaces from one closed outline. The
front bulge falls from a pole to the rim through `pillowBulge`; the back surface
retains explicit thickness. Panels therefore expose a real rim rather than a
single displaced sheet.

## Semantic humanoid construction

The torso owns a continuous black core plus fitted chest, back, strap, box,
recess, and wordmark panels. Front and back panel surfaces query the same core
curves, so their offsets remain tied to the body rather than hand-positioned.

The head owns a closed shell split into a glossy visor and matte hood, a crown
transition, seam curves, and an emissive sensor detail. Arms contain shoulder
caps, upper-arm shells, ring transitions, elbow housings, ribbed pads, forearm
frames, actuators, and wrists.

Each hand is a complete five-finger assembly. A wrist-local frame drives the
palm, back plate, four finger chains, thumb chain, joints, pads, and structural
members. Mirroring is performed in mesh data, after which winding is repaired.

The lower body owns a central pelvis, paired hip drums and covers, thigh cores
and shells, knees, shin shells, ankle actuators, and moulded feet. The semantic
groups remain separate even when they share a material; assembly identity is
not sacrificed to draw-call reduction in this example.

## Material identity system

The example defines fourteen named identities:

```text
M_SHELL       M_SHELL_LEG  M_BLACK      M_GLOSSBLACK
M_VISOR       M_HELMET     M_LED        M_DARKMECH
M_ALU         M_STEEL      M_RUBBER     M_FOOT
M_LOGO        M_DARKGREY
```

Every identity is a `MeshPhysicalNodeMaterial` or `MeshStandardNodeMaterial`.
Base colour, metalness, roughness, IOR, specular intensity, clearcoat, sheen,
and emission are authored as one bundle.

The object-space noise is a signed Perlin field built from a Jenkins lookup3
integer hash, quintic fade, a 16-way gradient selector, and `0.9820` amplitude
scale. Fractional Brownian accumulation removes octaves after their period
falls below roughly two pixels:

```text
band = 1 - smoothstep(0.25, 0.5, footprint × scale × octaveFrequency)
```

This derivative filter is part of the material. Without it, scales from `520`
to `1400 m^-1` alias into slowly drifting blotches.

Roughness variation maps normalized noise from `[0.25, 0.75]` into each
material's declared `base ± amount`. Bump distance is exactly
`strength × 0.0006 m`. White shell, helmet composite, cast mechanism,
aluminium, rubber, foot polymer, and dark covers use different scale/detail/
roughness tuples; one generic noise node is not substituted across them.

## Geometry emission and ownership

Before emission, pending booleans and bevels are applied. `computeCornerNormals`
groups face corners into smooth fans bounded by authored sharp edges, then
angle-weights the contributing face normals.

`toGeometry()` triangulates each polygon as a fan only at the final step. A
position is reused only when its corner normal matches within `1e-6`; sharp
fans therefore receive separate vertices. Indices are grouped by material slot
and retain the mesh's ordered material-name table.

The returned root owns the seven semantic groups. Each emitted mesh owns one
`BufferGeometry` and references one or more of the fourteen shared materials.
Disposal releases every geometry and material without touching gallery lights,
camera, or floor.

## Observed limits and defects

- The assembly is a fixed neutral pose. It does not include a skeleton, skin
  weights, joint limits, or collision envelopes for animation.
- `891,809` triangles are appropriate for a close inspection model, not an
  unrestricted crowd population. Build a deliberate LOD rather than deleting
  small parts from the canonical assembly.
- The BSP difference is exact for the declared polygon inputs but is not a
  general robust-solid kernel for arbitrary dirty meshes.
- Polygon fan triangulation assumes each emitted face is simple and convex
  after modifiers. Concave faces must be decomposed by their generator.
- Shared materials make global wireframe diagnostics inexpensive, but per-part
  destructive material mutation would affect every mesh using that identity.
- The geometry system repairs winding and normals; it does not replace a full
  inter-part clash, support, or articulation-clearance audit.

## Diagnostics

The gallery exposes four deterministic views:

```text
Complete assembly  all seven semantic groups, final materials
Wireframe topology all final triangles with shared material identities
Upper body         torso, head, arms, and hands only
Lower body         hips, legs, and feet only
```

Always record the object count, triangle count, bounds, group counts, and
material-name set. A count drift localizes lost or duplicated subassemblies
before a screenshot could explain why the silhouette changed.

## Failure diagnosis

If a panel floats, compare its surface query and offset against the owning core
curve. If a mirrored part shades inside-out, run winding repair after the
negative-axis transform. If a bevel pinches, inspect the selected edge angle,
sector inset, and local edge length before reducing segment count.

If procedural materials crawl with camera motion, verify object-space position
and derivative footprint filtering. If edges look melted, inspect corner-normal
fan boundaries rather than lowering global smoothness. If a body region is
missing, inspect the seven collection counts before geometry merging or scene
staging.
