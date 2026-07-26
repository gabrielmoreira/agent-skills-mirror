# Vehicle lofts, section tracks, and the paint projector

Use this reference for complete vehicle-scale hard-surface objects: one
continuous body loft driven by named parameter curves, sections that open into a
recess without changing topology, offset superellipse volumes, spanwise airfoil
lofts, authored outline plates with holes and warps, a two-plane paint
projector, load-deflected tyres, slot-tagged mesh writers, and the orientation
guard that catches inside-out closed bodies.

## Contents

- Frame and dimension contract
- Parameter-curve section tracks
- Semantic sections and the recess parameter
- Offset superellipse volumes
- Apertures that share one parameterisation
- Spanwise airfoil lofts
- Authored plates: holes, bevels, warps
- Steering-axis placement
- Two-plane paint projector
- Tyres: measured carcass and baked deflection
- Slot-tagged writers and the orientation guard
- Observed limits
- Diagnostics

## Frame and dimension contract

One table owns every dimension; nothing is nudged afterwards. Both vehicle
examples use `+Y` up and `+Z` toward the nose, origin on the ground plane, and
author only the `+X` half.

```text
formula-one-race-car   wheelbase 3.400  overall width 1.900  front tyre 0.720 OD
                       front axle z +1.720   rear axle z −1.680
                       hub centres derived: width/2 − tyreWidth/2 − clearance
sport-motorcycle       wheelbase 1.400  rake 23.5°  triple offset 0.030
                       seat 0.830  front 120/70-17 (0.300 R)  rear 180/55-17
```

Derived quantities stay derived. The car's ride plane rakes from the reference
plane, so every floor and diffuser station reads it rather than carrying its own
height:

```js
const floorY = (z) => {
  const t = clamp01((D.frontAxleZ - z) / (D.frontAxleZ - D.rearAxleZ));
  return D.plankY + D.rakeRise * smooth01(t);   // 0.0345 m + 0.0455 m of rake
};
```

## Parameter-curve section tracks

A body is a table of named curves in `z`, each evaluated at every station. The
interpolant must be C1 **and** overshoot-free: a per-segment ease has zero slope
at every knot, which prints a visible ripple onto the lofted surface — the body
reads as a stack of terraces under grazing light. Use shape-preserving monotone
cubic (Fritsch–Carlson) tangents.

```js
function curve1(knots) {                    // knots: [[x, y], ...]
  // secant slopes d[i], then m[i] = 0 where the sign flips,
  // else the average; finally rescale when a² + b² > 9 (monotonicity limit).
}
const HULL = paramTrack({ yRim: [...], wRim: [...], halfW: [...], tub: [...] });
const loops = stationsFrom(D.noseTipZ, D.engineCoverEndZ, 168, 0.35)
  .map((z) => ringFromHalf(chassisPts(HULL(z)), z, 96 / 2 + 1));
```

`stationsFrom(z0, z1, count, ease)` biases stations toward both ends, which is
where curvature is highest. The car's hull is 168 longitudinal rings at 96 ring
resolution: one loft from nose tip to engine-cover exit.

## Semantic sections and the recess parameter

The half-section is a fixed set of NAMED control points, so a curve can move
"max width" or "rim height" along the body without changing topology. The
cockpit is not a hole cut into a closed shell: the section itself opens into a
recess and closes again.

```text
13 points, top centreline → deck/rim → flank → bottom centreline
  tub  > 0.004  → open:  floor width = wTub, wall at 0.62 of the recess height
  tub == 0      → closed: floor width = 0.30·wRim, wall at 0.42
```

That single branch is what lets nose, survival cell, cockpit and engine cover be
ONE continuous surface. A padded liner is emitted separately as an OPEN sheet
from the same section points, contracted 4.5 mm toward the recess axis — closing
that ring would lid the cockpit.

## Offset superellipse volumes

Volumes that are not on the centreline (sidepods, headrest, gearbox, tank, tail)
use four superellipse quadrants with independent exponents, plus an undercut.

```js
podPts({ xIn, xOut, yTop, yBot, nTop: 6.6, nBot: 2.4, nIn: 2.6,
         undercut: 0.58, ucY: 0.17, ucW: 0.36, shelf: 0.26 })
```

The exponents carry the design language: a very high `nTop` produces a flat aero
shelf meeting the flank on a hard crease, while ~2.6 gives a soft crown. The
undercut is a Gaussian in height applied only outboard of the section centre —
that term, not the outline, is what creates the coke-bottle.

## Apertures that share one parameterisation

An inlet is a real aperture, and its lip ring's OUTER outline IS the volume's own
front section, so mouth, lip and shell cannot drift apart:

```js
const outer = podPts(POD(POD_FRONT_Z), 64);
const inner = outer.map(([x, y]) => [cx + (x - cx) * 0.815, cy + (y - cy) * 0.660]);
const lip = plate(spline2(outer, 110, { closed: true }), {
  thickness: 0.026, bevel: 0.0065,
  holes: [spline2(inner, 96, { closed: true }).reverse()],   // holes wind opposite
});
```

The throat then lofts from `inner`, contracting to 0.54 and shifting 0.100 m
inboard, so the duct is visibly open rather than a painted black hole.

## Spanwise airfoil lofts

Wing elements are real lofts of cambered sections. Every station owns chord,
incidence, camber, camber position, blunt trailing-edge thickness, and dihedral —
the parameters an aerodynamicist works in, not a scaled slab.

```js
airfoilLoop(n, { thick, camber, camberPos, teThick, leRadius })
// cosine spacing packs resolution into the leading edge;
// closed loop = upper LE→TE, blunt TE, lower TE→LE with the LE pole shared once
```

Negative camber and negative incidence are what make an inverted wing read
correctly from any angle. Tip capping is per-end: an element that meets the
centreline must NOT be capped there, or the mirrored half shows a seam.

```text
front wing main plane: 44 stations, chord 0.288 → 0.240, incidence −0.050 → −0.120
                       camber −0.030 → −0.076, dihedral −0.06 → −0.36
```

## Authored plates: holes, bevels, warps

Endplates, fences, strakes and louvres are authored 2D outlines in real metres,
extruded with a bevel, then deformed by a 3D warp. The warp is where curl comes
from, so the plate is generated curled rather than bent afterwards:

```js
plate(outline, { thickness: 0.008, bevel: 0.0024, holes: [slotA, slotB],
  warp: (z, y, w) => V3(0.8950 + w + curl(z, y), y, z) });
// curl = 0.052 · up^1.7 · back^1.20  → outwash grows toward the top rear
```

## Steering-axis placement

For a two-wheeler the steering geometry is the spine. Derive an axis frame once
and place every front-end part at a stated distance along it; rake and
triple-clamp offset then propagate to yokes, bars, calipers and fender with no
hand-placed transform.

```js
const AX = { up:  V3(0, cos(rake), −sin(rake)),
             fwd: V3(0, sin(rake),  cos(rake)) };
const forkPt  = (L, s = 0) => V3(s, axleY + AX.up.y * L, axleZ + AX.up.z * L);
const steerPt = (L) => forkPt(L).addScaledVector(AX.fwd, −tripleOffset);
```

## Two-plane paint projector

A livery is a PROJECTOR, not a per-part unwrap: one canvas painted in the side
elevation `(z, y)` and one in the plan view `(z, x)`. Bodywork samples whichever
plane its world normal faces, so the scheme stays continuous across nose,
chassis, sidepod and engine-cover boundaries exactly like a real wrap.

```js
const wUp   = pow(saturate(N.y), 4.0);                       // plan weight
const wSide = pow(N.x.abs(), 4.0).add(pow(N.z.abs(), 4.0).mul(0.40));
const topW  = wUp.div(wUp.add(wSide).add(0.0004));           // NORMALISED
const underKill = smoothstep(-0.12, -0.55, N.y).mul(smoothstep(0.36, 0.17, P.y));
```

Two rules make it work. The blend must be normalised so a 45° shoulder commits
to one plane instead of taking half the paint from each and printing the graphic
twice. And a downward-facing surface low in the frame is structural, so the
under-kill mask stops flank graphics smearing onto the underbody.

The side canvas carries two stacked layers that differ ONLY in glyph handedness;
which layer paints which flank depends on the upload's Y orientation, so expose
it as a switch (`sideSwap`) rather than assuming.

## Tyres: measured carcass and baked deflection

Revolve a measured half-section — bead, sidewall bulge, shoulder, crown — then
bake the contact patch as GEOMETRY:

```js
// squash only the lower arc, and widen the sidewall where it flattens
const groundY = -(R - drop);            // drop 0.0135 front / 0.0150 rear
if (y < groundY) {
  ny = lerp(y, groundY, smooth01(min(over * 1.35, 1)));
  widen = 1 + 0.085 * smooth01(min(over, 1)) * clamp01(abs(x) / (R * 0.5));
}
```

Emit a second, undeflected carcass for the rolling presentation and swap
geometry when it spins — a baked flat cannot be rotated, it would orbit with the
wheel. Mirroring a wheel mirrors its UVs too, so the opposite flank needs the
sidewall wordmark sampled in reverse or the moulded lettering reads backwards.

## Slot-tagged writers and the orientation guard

Every emitted mesh carries a material SLOT, and the writer records its triangle
count. On a black-on-black machine the slot field is the only way to check
finish ownership at all.

```js
add(parent, geometry, material, name, { slot });   // records { name, tris, slot }
pair(parent, geometry, material, name);            // author +X, mirror to −X
instance(parent, geometry, material, matrices, name);
```

A loft's winding depends on whether its station table runs `+Z` or `−Z` and on
how its section is wound. Rather than police that by hand across forty tables,
check the enclosed signed volume of every closed body and flip winding and
normals when it is negative:

```js
function orient(geometry) {                 // 87 fixups on the motorcycle
  if (signedVolume(geometry) < 0) flipGeometry(geometry);
  return geometry;
}
```

Silent inversion is the most common failure in generated hard surfaces: it
survives a wireframe check and only shows up as wrong light.

## Observed limits

- Emitted budgets at full tessellation: 62 geometries / 375,964 unique triangles
  for the car; 267 parts / 303,708 triangles for the motorcycle. Both are
  close-inspection budgets, not game budgets.
- Corner hardware is emitted ONCE per axle and mirrored per side. Mirroring
  flips winding and UV handedness, so a mirrored wheel needs its own material
  variant for any lettered texture.
- `mergeGeometries` is unavailable on some builds; keep a manual merge that
  copies position, normal and uv and offsets indices, and promote to `Uint32`
  above 65,535 vertices.
- Plate holes must wind opposite to their outline or the extruder fills them.
- A parameter track is only as smooth as its knot spacing: two knots closer than
  one station spacing reintroduce the terracing the monotone interpolant exists
  to avoid.
- The projector is a world-space field. Two bodies at different world positions
  cannot share one graphic unless both are inside the paint plane's `z` band —
  the `inBand` step is what keeps everything outside it unpainted.

## Diagnostics

Expose, and read in this order:

```text
per-part triangle/vertex table, sorted by triangle count
assembly topology (wireframe over the whole model, ground hidden)
material slots as stable per-slot hues
world normals as colour
bare structure (paint coverage forced to zero)
projector plane weight as a two-colour field
rolling carcass (undeflected geometry swapped in)
bodywork removed / glass removed
measured envelope vs the dimension contract
orientation-guard fixup count
```

The measured envelope is the cheap regression: build the bounding box and
compare length, width, height and wheelbase against the contract. The motorcycle
returns 2.016 × 0.704 × 1.105 m against published 2.025 × 0.710 × 1.100, which
is the tolerance an authored body should hold. A projector-plane view that shows
one graphic twice on a shoulder means the plane blend lost its normalisation; a
slot view with a surprise hue means a part was added without its slot.
