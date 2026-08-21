---
name: game-custom-physics-solvers
version: 1.0.1
description: "Use when implementing physics simulation math from scratch instead of a built-in engine — SAT, GJK/EPA collision detection, impulse-based and constraint (Gauss-Seidel/PBD) resolution, numerical integrators (semi-implicit Euler, Verlet, RK4), Verlet cloth/rope/soft-body, spatial partitioning (grids, quadtrees, sweep-and-prune), and particle/SPH fluid solvers. Triggers on: SAT, separating axis theorem, GJK, EPA, Verlet integration, impulse resolution, constraint solver, Position Based Dynamics, broadphase, sweep and prune, SPH, fluid solver, fixed timestep, deterministic lockstep. Not for Godot RigidBody/Jolt (use physics-system), Unreal Chaos/PhysX (use unreal-engine), Unity physics (use unity-engine), or visual-only particle rendering."
risk: safe
source: opus
date_added: 2026-06-27
---

# Custom Physics Solvers & Advanced Math

Build a physics simulation by hand — collision detection, integration, and constraint resolution from first principles — when a built-in engine is unavailable, too heavy, or doesn't fit (deterministic lockstep, specialized soft bodies, custom fluids, tiny dependency-free builds).

## When to Use

Activate this skill when the task involves **writing the solver yourself** rather than configuring an engine's built-in physics. Specific triggers:

- **Collision detection from scratch**: SAT for convex polygons/polyhedra, GJK + EPA for general convex shapes, circle/AABB/capsule tests.
- **Integration**: choosing and implementing semi-implicit (symplectic) Euler, Verlet, or RK4 with a **fixed timestep**.
- **Resolution**: impulse-based response (restitution + friction) or constraint solvers (sequential impulses / Gauss–Seidel, **Position-Based Dynamics**).
- **Soft bodies**: Verlet cloth, rope, and pressure-based soft bodies built from particles + distance constraints.
- **Broadphase**: spatial hashing/uniform grids, quadtrees/octrees, sweep-and-prune to avoid O(n²) pair checks.
- **Fluids**: particle systems and SPH (smoothed-particle hydrodynamics) solvers.
- **Deterministic lockstep**: cross-platform reproducible simulations requiring fixed-point or carefully managed float strategies.

### Do Not Use For

| If the task is… | Use instead |
|---|---|
| Godot built-in RigidBody/CharacterBody/Jolt | `physics-system` |
| Unreal Chaos / PhysX bodies | `unreal-engine` |
| Unity built-in / DOTS physics | `unity-engine` |
| Just rendering particles (no simulation math) | the relevant VFX/particles skill |

If a production engine's physics fits, use it — a hand-rolled solver is more code, more bugs, and slower than Jolt/PhysX unless you specifically need determinism, custom behavior, or a tiny dependency-free build.

## Prerequisites

- Solid understanding of vector math (dot/cross products, projection, normalization). See `math-and-vectors` skill if needed.
- The target language has no suitable physics library, or the project explicitly requires a custom solver (determinism, size, specialization).
- A profiling setup (even a simple frame-time counter) — custom solvers need performance validation as body counts grow.

## Procedure

### 1. Establish the Fixed Timestep Loop (Non-Negotiable)

A variable `dt` makes integration **non-deterministic and explosive** — the same collision resolves differently at 30 vs 144 fps, and large frames tunnel through walls. Always accumulate real time and step the simulation at a constant `dt`, then interpolate the *render* state.

```
accumulator += frameDeltaTime;
while (accumulator >= FIXED_DT) {     // e.g. FIXED_DT = 1/60
    step(FIXED_DT);                   // ALL physics advances by a constant dt
    accumulator -= FIXED_DT;
}
float alpha = accumulator / FIXED_DT; // interpolate rendering between states
render(lerp(prevState, currState, alpha));
```

This single rule prevents most "physics feels different on my machine" bugs. Set `FIXED_DT` once and never change it at runtime.

### 2. Choose and Implement the Integrator

| Integrator | Use it for | Avoid when |
|---|---|---|
| **Semi-implicit (symplectic) Euler** | Default rigid-body integration; stable, cheap, energy-conserving enough | — |
| **Verlet** | Particle systems, cloth, rope, soft bodies (position + previous position) | You need explicit velocity each step |
| **RK4** | High-accuracy orbital/ballistic where error must stay tiny | Real-time many-body (4× the cost) |

**Semi-implicit Euler** — update VELOCITY first, then position with the NEW velocity:

```cpp
v += (force / mass) * dt;
x += v * dt;                 // stable; plain (explicit) Euler updates x with OLD v and drifts/explodes
```

**Verlet** — velocity is implicit in (current - previous) position:

```cpp
Vec2 temp = pos;
pos = pos + (pos - prevPos) + accel * dt * dt;   // (pos - prevPos) carries momentum
prevPos = temp;
```

> **HARD RULE**: Never use explicit (forward) Euler for dynamics. It gains energy and blows up. Semi-implicit Euler or Verlet only.

### 3. Implement Broadphase (Before Narrowphase)

Never run narrowphase on all N² pairs. Choose based on your scene:

- **Uniform grid / spatial hash**: fast for evenly sized objects. Hash `floor(x/cellSize), floor(y/cellSize)` into a dictionary; check neighboring cells.
- **Quadtree / Octree**: varied sizes; subdivides adaptively.
- **Sweep-and-prune**: good for many bodies along one axis. Sort by min-AABB on one axis, sweep, test overlap on remaining axes.

### 4. Implement Narrowphase Collision Detection

**SAT (Separating Axis Theorem)** — for two convex shapes, if there exists an axis (each face normal of both shapes) on which their projections don't overlap, they're separated. The axis of **minimum overlap** gives the collision normal and penetration depth.

```cpp
// SAT core idea (2D convex): project both shapes onto each candidate axis.
for (Vec2 axis : allEdgeNormals(a, b)) {
    auto [minA, maxA] = project(a, axis);
    auto [minB, maxB] = project(b, axis);
    float overlap = std::min(maxA, maxB) - std::max(minA, minB);
    if (overlap <= 0) return NO_COLLISION;        // a separating axis exists
    if (overlap < minOverlap) { minOverlap = overlap; collisionNormal = axis; }
}
// minOverlap + collisionNormal define the MTV (minimum translation vector).
```

SAT works great for boxes/convex polygons; axis count explodes for high-vertex 3D shapes.

**GJK** — tells you *if* two convex shapes intersect (and the closest distance if not) using support functions and a simplex. Scales to any convex shape. Pair with **EPA** to recover penetration depth + normal when they do intersect.

**Compute and store the contact manifold** — normal, penetration, contact point(s). Resolution needs all three.

### 5. Implement Resolution

**Impulse-based** (rigid bodies): along the contact normal, apply an impulse `j` from relative velocity, restitution `e`, and inverse masses; then apply a **friction impulse** along the tangent clamped by the Coulomb cone (`|jt| ≤ μ·jn`).

```cpp
// Impulse magnitude along the contact normal.
float invMassSum = a.invMass + b.invMass;
Vec2 rv = b.vel - a.vel;
float velAlongNormal = dot(rv, normal);
if (velAlongNormal > 0) return;                  // already separating — do nothing
float j = -(1 + e) * velAlongNormal / invMassSum;
Vec2 impulse = j * normal;
a.vel -= a.invMass * impulse;
b.vel += b.invMass * impulse;                    // static bodies use invMass = 0
```

**Positional correction**: velocity impulses alone leave objects slightly sunk. Add Baumgarte/slop correction to push out residual penetration without injecting energy. Use a small `slop` (e.g. 0.01–0.05 units) and a correction `percent` like 0.2–0.8.

**Constraint solvers** (joints, stacks, soft bodies): solve constraints iteratively:
- **Sequential impulses / Gauss–Seidel**: run multiple iterations per step; more iterations = stiffer, more stable stacks.
- **Position-Based Dynamics (PBD)**: projects positions to satisfy constraints directly; backbone of cloth/rope.

### 6. Soft Bodies & Cloth (Verlet + Constraints)

1. Represent the body as **particles** (mass points) integrated with Verlet.
2. Connect them with **distance constraints** (structural, shear, bend springs for cloth).
3. Each step, **relax constraints** several iterations: move particle pairs back toward their rest length. More iterations → stiffer cloth. This is PBD in miniature and is far more stable than stiff spring forces.

> **HARD RULE**: Do not use stiff springs to simulate rigid connections. High spring constants force a tiny timestep and introduce instability. Prefer PBD/constraint projection for stiff behavior.

### 7. Fluids (SPH)

- Treat fluid as particles carrying mass; each frame compute **density** and **pressure** from neighbors within a smoothing radius `h`, then **pressure + viscosity forces** drive motion.
- A neighbor search over a **spatial grid** is mandatory — naive all-pairs SPH is O(n²) and unusable past a few hundred particles. Hash particles into a grid keyed by the smoothing radius.
- SPH is touchy: timestep, smoothing radius, and stiffness are coupled. Start from known-good parameters and change one at a time.

## Pitfalls

1. **Variable timestep**: the root cause of non-determinism and explosions. Always fixed-step + accumulator + render interpolation. No exceptions.
2. **Explicit (forward) Euler for dynamics**: gains energy and blows up. Use semi-implicit Euler or Verlet.
3. **Skipping broadphase**: O(n²) narrowphase dies past a few hundred bodies. Add a grid/quadtree/SAP first.
4. **Velocity-only resolution**: objects sink and jitter. Add positional correction with slop.
5. **Tunneling**: fast/thin objects pass through thin walls in one step. Use sub-stepping or continuous collision (conservative advancement / swept tests).
6. **Too few solver iterations**: stacks and joints feel mushy or jitter. Increase Gauss–Seidel iterations (trade CPU for stability).
7. **Floating-point determinism assumptions**: if you need cross-platform lockstep, plain floats may diverge — consider fixed-point or a single reference platform. Do not assume `float` arithmetic is identical across CPUs, compilers, or build settings.
8. **Stiff springs instead of constraints**: high spring constants force a tiny timestep. Prefer PBD/constraint projection for stiff behavior.
9. **All-pairs SPH neighbor search**: unusable at scale. Hash particles into a grid keyed by the smoothing radius.
10. **Forgetting friction tangent impulse**: applying only the normal impulse makes objects slide forever on surfaces. Compute the tangent impulse and clamp by the Coulomb cone.
11. **Not handling invMass = 0 for static bodies**: division by zero or incorrect impulse distribution. Static/kinematic bodies must have `invMass = 0` and `invInertia = 0`.

## Verification

Run through this checklist after implementing the solver:

- [ ] Simulation runs on a **fixed timestep** with an accumulator; rendering interpolates between states using `alpha`.
- [ ] Dynamics use semi-implicit Euler / Verlet / RK4 (never explicit Euler).
- [ ] A broadphase culls pairs before narrowphase (grid / quadtree / sweep-and-prune).
- [ ] Narrowphase produces normal + penetration + contact point (SAT or GJK/EPA).
- [ ] Resolution applies normal + friction impulses **and** positional correction (Baumgarte/slop).
- [ ] Constraint/PBD solver runs enough iterations for stable stacks/cloth (test with a stack of 10+ boxes).
- [ ] Fast objects don't tunnel (sub-stepping or swept tests at the chosen dt — test with a high-velocity projectile vs. thin wall).
- [ ] SPH/soft-body neighbor search uses spatial partitioning, not all-pairs.
- [ ] If lockstep determinism is required, the float/fixed-point strategy is explicit and documented.
- [ ] Energy is conserved over long runs: place a bouncing ball with restitution 1.0 in a closed box and verify it doesn't gain or lose significant energy over 60 seconds.

### Quick Smoke Test (PowerShell)

If you have a build output (e.g. a C++ executable or a script), run a timed test:

```powershell
# Run the simulation binary for 60 seconds of sim time, capture output
$proc = Start-Process -FilePath ".\build\physics_sim.exe" -ArgumentList "--duration 60 --bodies 100" -NoNewWindow -Wait -PassThru
Write-Host "Exit code: $($proc.ExitCode)"
# Exit code 0 with stable output = pass; non-zero or NaN in output = fail
```

For a Godot/Unity script-based solver, run the scene and check the output log for NaN/Infinity:

```powershell
Get-Content .\godot_project\logs\physics.log | Select-String -Pattern "NaN|Infinity|ERROR"
# No matches = clean
```

## Examples

### Minimal Fixed-Timestep Game Loop (C++)

```cpp
const float FIXED_DT = 1.0f / 60.0f;
float accumulator = 0.0f;

void onFrame(float frameDeltaTime) {
    accumulator += frameDeltaTime;
    // Clamp to prevent spiral-of-death after stalls
    if (accumulator > FIXED_DT * 5) accumulator = FIXED_DT * 5;

    while (accumulator >= FIXED_DT) {
        previousState = currentState;
        step(FIXED_DT);
        accumulator -= FIXED_DT;
    }
    float alpha = accumulator / FIXED_DT;
    render(lerp(previousState, currentState, alpha));
}
```

### Distance Constraint Relaxation (PBD, Pseudocode)

```cpp
void satisfyConstraint(Particle& a, Particle& b, float restLength) {
    Vec2 delta = b.pos - a.pos;
    float dist = length(delta);
    if (dist == 0) return;
    Vec2 dir = delta / dist;
    float correction = (dist - restLength) / (a.invMass + b.invMass);
    a.pos += dir * correction * a.invMass * 0.5f;
    b.pos -= dir * correction * b.invMass * 0.5f;
}
// Call this N times per step (N = iteration count, e.g. 5–20)
```

## Related Skills

- **physics-system** — Godot's built-in bodies/Jolt. Use it instead unless you specifically need a custom solver.
- **unreal-engine** / **unity-engine** — Production engines whose physics (Chaos/PhysX) you'd normally use over a hand-rolled solver.
- **math-and-vectors** — Supporting linear algebra these solvers build on.
- **shader skills** — GPU compute paths for particle/fluid solvers if CPU throughput is insufficient.

## References

Load these reference files when you need deeper detail on a specific algorithm:

- **Separating Axis Theorem, GJK, and EPA** — collision-detection literature. Search for "SAT collision detection" and "GJK EPA penetration depth" for canonical implementations.
- **Position-Based Dynamics (Müller et al.)** — the PBD paper for constraint projection methods.
- **Sequential-impulse constraint solving (Catto, Box2D)** — for rigid-body constraint solvers.
- **Verlet integration for cloth/rope** — classic particle-based soft body methods.
- **SPH (Müller, Charypar, Gross)** — "Particle-Based Fluid Simulation for Interactive Applications" for real-time fluids.
- **"Fix Your Timestep!" (Gaffer on Games)** — the definitive reference for the fixed-step/interpolation loop.
