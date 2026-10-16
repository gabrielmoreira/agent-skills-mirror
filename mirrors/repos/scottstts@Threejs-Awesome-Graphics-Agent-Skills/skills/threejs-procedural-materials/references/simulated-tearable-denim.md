# Simulated tearable denim

The `simulated-tearable-denim` example couples an implicit woven-fabric solve
to material connectivity, twill shading, explicit yarns and frayed fibres.
Read [the entry point](../examples/simulated-tearable-denim/simulated-tearable-denim.js)
for reusable exports and the complete modular TypeScript/WGSL system.

## Contents

- Integration contract
- Material and initial state
- Implicit mechanics and failure
- Grips and detached pieces
- Weave, threads and fibres
- Limits
- Diagnostics

## Integration contract

```js
const denim = new TearableDenim(device, outputFormat);
await denim.initialize(settledDenimDrape());
denim.setSize(bufferWidth, bufferHeight, cssWidth, cssHeight);
denim.update(deltaSeconds, inputClockMilliseconds);
const encoder = device.createCommandEncoder();
denim.encode(encoder, outputView, seconds);
device.queue.submit([encoder.finish()]);
await device.queue.onSubmittedWorkDone();
```

The caller owns the device, canvas configuration, camera, input binding and
frame scheduling. Use a dedicated device and destroy it when the effect ends;
`dispose()` releases the effect's snapshot/readback state, not the device.
The renderer owns HDR resolution, shadows, MSAA, tone mapping and sRGB encoding.
Avoid a second display transform. Size arguments separate drawing-buffer and
CSS pixels so picking remains aligned at every DPR.
The material plane is world XY, with positive Z toward the viewer.
Assign `denim.camera` before updating grips or encoding a frame.
Supply pointer times and `update` times on the same millisecond clock.

## Material and initial state

Denim is a warp-faced 3/1 twill: repeat 4, warp-over count 3.
The mechanical coupon is 0.62 × 0.4 m, with nine warps and six picks per span.
Its rotation is 0.06 rad, compression `(0.025,-0.002)` and shear 0.06.
Two collar rows stay pinned. A 2.5 mm perturbation seeds buckling.
The wear zone shares structural and visible causes: warped cellular interiors
weaken warp floats most, while retained ligaments arrest openings.
The material thickness is 0.7 mm; cloth friction is 0.45.

```text
weft: strength 8.5 N, softening opening 0.4 mm
warp: strength 11 N, softening opening 0.4 mm
warp cross-section: width 0.7 mm, height 0.26 mm
weft cross-section: width 0.4 mm, height 0.16 mm
```

The settled-position asset carries a magic value, version, node count and
mechanics/scene hash. `loadDrape` rejects incompatible state; `settleDrape`
then runs 420 damage-free steps, with kinetic damping through step 360.
The reset snapshot contains positions, spans, tails and the yarn field.

## Implicit mechanics and failure

The fixed timestep is 1/120 s and gravity is `(0,0,-9.81)` m/s².
Each step uses two Newton iterations, two PCG iterations and two coarse sweeps.
The multigrid hierarchy stops coarsening at 400 nodes.
The Newton update tolerance is 1e-5 m and the history tolerance is 1.
Yarn extension, crimp, compression, bending, crossing friction, shear locking,
self-contact and grips participate in the coupled solve.
Damage and slip advance from the accepted state rather than a display mesh.
Strength and cross-section decrease together with abrasion.
Warp strength loss is 0.9 at full wear; weft strength loss is 0.45.
The per-yarn field tracks absent material and transfers its consequences to
span forces, crossing load sharing and visible openings.
After release, four Newton iterations run for 0.1 s to resolve elastic recoil.
Do not replace this solver with breakable distance springs or XPBD linen.

## Grips and detached pieces

Four simultaneous grip slots support independent pointers.
GPU picking evaluates material presence and a connected patch window.
`Hand` limits handle speed to 2.5 m/s and acceleration to 60 m/s².
Pinching lifts by 2 mm; drag adds lift at factor 0.35, capped at 5 cm.
The wheel depth factor is 0.00006 m per deltaY unit.
Grip release first removes its anchor from connectivity analysis, then opens
the grip after that analysis applies. This ordering lets a held torn piece
remain cloth until the pointer lets go.
Topology searches mounted nodes and current grip cores, labels detached pieces
and updates their rigid-mode correction. It coalesces overlapping readbacks.
There is no collision floor: released pieces fall freely.

## Weave, threads and fibres

The 128² tile represents one twill repeat. Every mip level averages the analytic
weave using 8 × 8 stratified samples per texel.
Near the camera, analytic yarn hits and the damage field select actual material;
farther away, footprint filtering blends toward the prefiltered tile.
Connectivity-corrected surface points keep openings tied to remaining material.
Freed yarns round according to linear density and packing, rather than retaining
their flattened woven cross-section. Loose ends use the thread-tail solve.
An edge-distance field drives retained fibre roots and the pale frayed band.
Fibre shading combines diffuse cylinder response, a longitudinal specular lobe
and Charlie/Neubelt fuzz sheen. Four-sample MSAA covers yarn ribbons;
subpixel fibres use alpha blending without depth writes.
Both key and overhead shadow maps render the cloth and explicit threads.

## Limits

The engine requires ten storage buffers per shader stage and up to a 256 MiB
storage binding, with a 512 MiB maximum buffer allocation limit.
The frame budget drops backlog beyond five simulation substeps per update.
Rest detection sleeps below 0.003 m/s for 0.4 s; grips wake the solve.
Inactive plane-contact uniform slots remain reserved to preserve WGSL layouts.
The example has no floor renderer, floor asset, scene props or sound playback.
The cloth renderer consumes its own GPU state; it is not a Three.js material.

## Diagnostics

`normals` displays the surface frame normal, `wear` displays visible abrasion,
and `presence` maps warp presence to red and pick presence to green.
These modes preserve coverage and expose the sheet surface; explicit threads
and fibres retain their own shading. `final` retains the complete material.
Check holes in picking, sheet coverage and shadows against the same yarn state.
For plain-weave GPU XPBD cloth, use the sibling `simulated-cloth` example.
