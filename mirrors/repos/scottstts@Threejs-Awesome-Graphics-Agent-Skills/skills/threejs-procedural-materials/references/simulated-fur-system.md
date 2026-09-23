# Simulated fur system

Use this reference for a groomed surface whose stylized fiber shading,
deformation, and hand interaction remain coupled. The
[simulated fur example](../examples/simulated-fur/simulated-fur.js) owns the
character, root distribution, strand compute, ribbon material, hand rig, and
contact response. Its factory accepts an initialized WebGPU renderer, scene,
camera, orbit controls, and an optional environment texture.

## Contents

1. Strand and host geometry contract
2. Root placement and grooming
3. Verlet compute and hand contact
4. Tapered ribbon shading
5. Interactive contract
6. Reusable API contract
7. Limits and observed failure patterns
8. Diagnostics
9. Failure diagnosis

## Strand and host geometry contract

The effect uses `P = 6` points per strand and
`S = 64 * round(420000 / 64) = 420032` strands. Each strand therefore contains
five segments. The stylized head is a radial surface with raised ears and
cheeks; the body, paws, and tail have separate analytic shapes. Head roots use
head-local coordinates and follow its animated pivot. Other roots use
body-local coordinates. The root stores its rest length, normal, groom flow,
pattern channels, and head/body-space flag.

Use fixed coat colors: main `#f2903b`, cream `#fff3e2`, stripe `#c8521a`, and
blush `#ff8b9c`. The skin and hair share the same four pattern channels: cream,
stripe, ear-tip, and blush. Body patterning adds a chest mask and a dorsal
stripe. Tail patterning adds rings near its end. Hair length is `0.12 m` on the
head, `0.13 m` on the body and tail, and `0.05 m` on each paw before the local
variations below.

## Root placement and grooming

Estimate each part's surface area from `12000` sampled Jacobians. Choose a part
proportional to its area, sample an approximately uniform sphere direction or
tail parameter pair, and accept it only when the sampled Jacobian is below
`1.15 *` the measured maximum. Cull head roots inside the body, body roots
inside the head/paws/tail, paw roots inside the body, and tail roots inside the
body. This prevents buried roots where separately authored shapes overlap.

Head flow combines the surface normal with cheek, muzzle, belly, ear, and fluff
regions. Body flow turns downward across the chest, paws flow forward, and the
tail follows its Frenet frame. The groom direction is projected onto the local
tangent plane and receives a small random angular offset. Strand length also
varies with a three-octave clump field, surface color region, and per-strand
random value. Build the rest pose once and retain the same root and rest data
throughout the simulation.

Root generation currently uses `Math.random()` for direction, acceptance,
length variation, strand jitter, hand finger phases, and some character timing.
The distribution is repeatable in law but not bitwise-identical between
initializations. Do not claim a deterministic seed unless a seeded random
provider is added to every generation and animation path.

## Verlet compute and hand contact

Each step reads current and previous point positions. For points after the
root, integrate damped Verlet motion and add a slow root-position-dependent
gust. Blend toward a groomed angular rest direction with stiffness decreasing
from root to tip. The exact constants are:

```js
const fur = {
  damping: 0.9,
  gravity: [0, -1.6 / 3600, 0],
  wind: 0.00022,
  kink: 0.16,
  rootStiffness: 0.42,
  tipStiffness: 0.14,
  combGain: 1.4,
  combDecay: 0.994,
  floor: -0.87,
  ribbonWidth: 0.0034,
};
```

Keep the point above the root's normal-offset skin and above the floor, then
project it onto the exact rest segment length. This last projection is the
inextensibility constraint; no unconstrained spring may stretch the fur. The
comb vector is stored per strand, decays every compute step, adds to the groom
flow, and is updated by hand-contact motion projected into the root tangent
plane. Clamp its magnitude to `1.3`.

Each positive `update(deltaSeconds)` issues one strand compute dispatch.
`deltaSeconds` is capped at `1/30 s` for hand and character response, but the
Verlet damping, gravity, and wind impulses are fixed per dispatch rather than
scaled by elapsed time. Strand motion therefore depends on the render update
rate; keep this behavior when matching the calibrated interaction.

The hand has palm, thumb, four articulated fingers, nails, forearm, and sleeve.
Transform palm and finger capsules to world space each step. Bound the broad
contact check by one hand sphere, then project strand points out of intersecting
capsules. Add capsule motion scaled by mode friction and update the persistent
comb direction. Clamp capsule displacement to `0.08 m` per step. Fur-floor and
skin clearances are separate from capsule contact.

## Tapered ribbon shading

Render each strand as five camera-facing quads. At a point, estimate tangent
from adjacent strand points, cross it with the view direction for the ribbon
side, and offset the centerline by `0.0034 m` at the root, tapering linearly to
`15%` at the tip. Fade the last `20%` of strand length and soften the lateral
edges with `1 - |side|⁴`. Keep the hair mesh unculled because its per-instance
deformed bounds are not tracked by the static bounding sphere.

The custom direct-light response uses the groomed tangent and surface normal
for diffuse response, two longitudinal specular lobes, silhouette-dependent
transmission, random per-strand value, and a root-to-tip brightness ramp. Add a
soft occlusion term around the hand. The shadow pass uses the same deformed
strand position and ribbon width; do not substitute rigid root geometry for
hair shadows.

## Interactive contract

On pointer down, raycast the analytic head/body/paw/tail proxies. A hit begins
petting and disables orbit input; a miss leaves camera orbit available. While
the pointer is held over the surface, move the hand target along the hit
surface normal. Animate finger curl toward the fur, then use the resulting
capsule positions as the actual contact geometry. Hover, pet, and scratch use
different lift, friction, and hand-occlusion strengths.

Scratch mode begins after the pressed pointer stays below `90 px/s` for more
than `0.22 s`. It adds a `7 Hz` finger oscillation and increases pleasure and
hair combing. Releasing the pointer restores orbit controls. Pointer leave
hides the hand when no pet gesture is active. Bind camera pan separately from
the primary pointer, which is reserved for petting.

## Reusable API contract

Call `createSimulatedFur({ renderer, scene, camera, controls, envMap })` after
initializing WebGPU. The returned object exposes `creature`, `hair`, `hand`,
`proxies`, `update`, pointer methods, `setDebugMode`, interaction state, and
`dispose`. `renderer.compute` advances the complete strand buffer; the caller
provides an initialized camera and OrbitControls. An optional environment
texture is used by the face and nose materials; the strand shader does not
sample it. Keep renderer lifecycle, camera construction, presentation geometry,
DOM controls, and event listeners outside this module.

## Limits and observed failure patterns

- The system is WebGPU-only and requires TSL compute support. It has no CPU or
  WebGL fallback.
- `420032 × 6` vec4 position records, rest positions, previous positions, root
  attributes, comb state, and ribbon rendering form a high fixed memory and GPU
  workload. There is no reduced strand-count tier.
- Roots use unseeded `Math.random()`, so screenshots and exact strand layouts
  cannot be reproduced bit for bit across reloads.
- The solver has hand-capsule, skin-clearance, and floor projection but no
  strand-strand collision. Dense self-contact can interpenetrate.
- The one-dispatch-per-update solver is frame-rate dependent because its
  gravity, wind, and damping increments are not multiplied by delta time.
- The skin proxy follows the analytic host shape, not each individual hair
  strand. Long hair silhouettes and collision surfaces therefore differ.
- Camera-facing ribbons become ill-conditioned when strand tangent and view
  direction are nearly parallel; the side-vector epsilon prevents division by
  zero but cannot remove that view-dependent orientation.
- The custom ribbon pass and fur shadow-position node depend on Three.js WebGPU
  node-material behavior. Check installed-version support before adapting.

## Diagnostics

`final` shows the complete creature, groom, and hand response. `skin` hides
hair to inspect the analytic host. `strands` isolates the full strand field.
`contact` displays translucent wireframe host proxies used by pointer and
finger ray tests. Keep diagnostic branches separate from the final shading and
compute path.

Monitor the following when diagnosing issues:

- `skin`: root coverage, ear/paw/body overlap, and the face/body transform split;
- `strands`: root density, length variation, silhouette gaps, taper, and shadow
  consistency;
- `contact`: proxy alignment with the rendered host and the finger ray hit;
- interaction metric: idle, hover, pet, or scratch transitions and controls
  enablement after release;
- coat color: shared main, cream, stripe, and blush uniforms across skin and hair;
- WebGPU compute errors and strand-buffer memory when initialization stalls.

## Failure diagnosis

If roots float inside the host, inspect sampled surface Jacobians and the part
overlap cull predicates. If the hair stretches, check the final rest-segment
projection before changing stiffness. If brushing leaves no visible trail,
verify the transformed capsule displacement, tangent-plane projection, comb
gain, and per-step decay. If pointer movement rotates the camera while petting,
check that a hit disables controls on pointer down and that every release or
cancel re-enables them. If the hand follows the cursor but the fur does not
move, inspect the hand broad-phase bound and the world-space capsule uniforms.
