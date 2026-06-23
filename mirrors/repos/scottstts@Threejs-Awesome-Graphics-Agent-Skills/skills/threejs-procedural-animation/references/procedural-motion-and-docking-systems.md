# Procedural motion and docking systems

Use this reference for phase-based launch, staging, docking, spring, rotating-frame, detachment, and debris motion with explicit coordinate frames and terminal states.

## Contents

- State contract
- Piecewise launch kinematics
- Planet-relative gravity turn
- Camera-independent shake and roll
- Stage detachment
- Spin-docking timeline
- Docking-frame decomposition
- Spring convergence and terminal lock
- Peeling and released debris
- planet-space implementation response and orientation patterns
- Failure modes and diagnostics


## State contract

Use explicit persistent state:

```ts
type ProceduralAnimationState = {
  elapsedSeconds: number
  phase: string
  position: THREE.Vector3
  velocity: THREE.Vector3
  baseQuaternion: THREE.Quaternion
  spinAngle: number
  angularVelocity: THREE.Vector3
  eventFlags: Record<string, boolean>
}
```

Keep scratch vectors/quaternions outside the state. Reset all persistent values
when restarting the sequence.

## Piecewise launch kinematics

cinematic implementation’s launch sequence uses:

```text
ignition hold = 1.2 s
ascent = 24 s
slow phase = 5 s
acceleration phase = 11 s
deceleration phase = 8 s
slow distance fraction = 0.00035
coast linear = 1.2 s
terminal deceleration = 4 s
```

`computeAscentKinematics()` solves a normalized distance curve whose position
and speed remain continuous across all three ascent phases.

For slow phase:

```text
speed = slowDistance / slowDuration
distance = speed * t
```

Solve acceleration so total normalized distance reaches one after the
acceleration and deceleration phases:

```text
remaining = 1 - slowDistance
accel =
  (
    remaining
    - slowSpeed * (accelDuration + 0.5 * decelDuration)
  )
  /
  (
    0.5 * accelDuration * (accelDuration + decelDuration)
  )

peakSpeed = slowSpeed + accel * accelDuration
decel = peakSpeed / decelDuration
```

Then integrate each phase analytically. Do not approximate this authored
timeline by repeatedly lerping position toward an endpoint.

## Planet-relative gravity turn

The launch maps normalized distance to:

```text
altitude = ascentProgress * targetOrbitAltitude + coastDistance * coastRate

groundArcDistance =
  ascentProgress^1.22 * maxGroundArcDistance * turnBlend
  + coastDistance * groundTrackRate

arcAngle = groundArcDistance / planetRadius
```

Motion constants:

```text
target altitude = 420 km in scene scale
max ground arc = 2200 km
max crossrange = 26 km
```

Construct:

```text
radial = normalize(0, cos(arcAngle), -sin(arcAngle))
tangent = normalize(0, -sin(arcAngle), -cos(arcAngle))
position = planetCenter + radial * (planetRadius + altitude)
position.x += crossrange
```

Orientation:

```text
flightDirection = normalize(lerp(radial, tangent, gravityTurn * 0.9))
base = quaternionFromUnitVectors(rocketLocalUp, flightDirection)
roll = quaternionAround(flightDirection, rollAmount)
orientation = base * roll
```

This separates trajectory direction from authored roll/vibration.

## Camera-independent shake and roll

Rocket roll:

```text
shake envelope = 1 - smoothstep(0.05, 0.9, ascentProgress)
vibration =
  (
    sin(time * 52)
    + sin(time * 31 + 0.7)
  )
  * 0.0024
  * envelope

roll =
  sin(time * 2.5) * 0.008 * envelope
  + vibration
```

The camera has a separate early launch shake envelope and offset. Keep object
vibration and camera shake separate so either can be disabled for diagnostics.

## Stage detachment

Before reparenting stage one:

```text
capture world position
capture world quaternion
capture world scale
remove from rocket
add to scene
restore captured world transform
```

The detached stage immediately receives readable separation:

```text
along offset = -3.4 m
side offset = 4.2 m
earthward offset = 1.2 m

along speed = -5.2 m/s
side speed = 5.8 m/s
earthward speed = 4.2 m/s
```

It then integrates separate along, side, and earthward scalar velocities. A
short kick phase blends into growing lag accelerations.

For the first `2 s`, orientation slerps from the captured quaternion to a
random `10–30°` tilt. Afterward, it integrates a bounded spin rate
`0.06–0.15 rad/s`.

The side direction is chosen relative to the camera so separation reads in the
shot. That is a presentation-aware choice, not a physical rule.

## Spin-docking timeline

Docking phases:

```text
Endurance spin = 3.15 rad/s
Ranger spin-up = 6.5 s
approach starts = 4.0 s
approach duration = 14.5 s
dock settle = 3.0 s
post-dock spin-down = 3.0 s
dock axial clearance = 4.1
dock radial offset = 0.35
```

Every phase uses a named `smoothstepRange(start, end, time)`. The sequence does
not hide all timing in one normalized zero-to-one value.

Endurance:

```text
currentSpinRate = lerp(3.15, 0, spinDownT)
spinAngle += currentSpinRate * dt
orientation = baseOrientation * rotation(localForward, spinAngle)
```

The docking frame is recomputed from the newly rotated Endurance every frame.

## Docking-frame decomposition

At approach start:

```text
offset = rangerPosition - dockPort
parallel = dot(offset, dockAxis)
radialVector = offset - dockAxis * parallel
radialDistance = length(radialVector)
radialDirection = normalize(radialVector)
```

Target during approach:

```text
parallelApproach =
  lerp(startParallel, dockClearance, approachT)

parallel =
  lerp(parallelApproach, dockClearance, dockT)

radialApproach =
  lerp(startRadial, dockRadialOffset, approachT)

radial =
  lerp(radialApproach, 0, dockT)
radial = lerp(radial, 0, spinDownT)

target =
  dockPort
  + dockAxis * parallel
  + radialDirection * radial
```

This preserves a readable approach corridor while progressively removing
lateral error.

## Spring convergence and terminal lock

Ranger position follows target through a vector spring:

```text
acceleration =
  (target - current) * stiffness
  - velocity * damping

velocity += acceleration * dt
current += velocity * dt
```

Stiffness increases from `5.0` to `9.8`; damping from `4.6` to `7.4` as docking
settles.

Orientation aligns local up to negative docking axis, then applies spin around
the docking axis:

```text
alignment = quaternionFromUnitVectors(localUp, -dockAxis)
spin = quaternionAround(dockAxis, rangerSpinAngle)
orientation = spin * alignment
```

Near completed docking, position receives a final `lerp` toward target. After
spin-down reaches `0.995`, copy target exactly and zero velocity. A spring alone
can retain imperceptible but destabilizing residual motion.

## Peeling and released debris

Endurance debris has two states.

Attached peel:

```text
peelT = smoothstep(peelStart, detachTime, sequenceTime)
peelDistance = maxDistance * peelT^2
position = shipTransform(localAnchor + outward * peelDistance)
orientation = shipOrientation * localBase * peelTwist
```

At release, velocity inherits rotating-frame tangential velocity:

```text
angularVelocityOfShip =
  dockAxis * currentSpinRate

tangentialVelocity =
  cross(angularVelocityOfShip, worldOffsetFromShip)

velocity =
  tangentialVelocity
  + outward * outwardSpeed
  + axis * axialSpeed
```

Released debris then integrates linear velocity and quaternion rotation from
its angular-velocity vector. Speed is capped at `95`.

This rotating-frame inheritance is the defining mechanism. Random outward
velocity alone would not match the spinning hull.

## planet-space implementation response and orientation patterns

planet-space implementation uses frame-rate-independent exponential response:

```text
alpha = 1 - exp(-lambda * dt)
value = lerp(value, target, alpha)
```

It uses this for camera blends, side-camera forward, effect intensities, color
response, and control state.

Ship orientation control separates desired forward/up from angular physics.
Quaternion targets are converted to angular error; damping acts on angular
velocity. This keeps user control and rigid-body response distinct.

For bounded camera lag, planet-space implementation uses a second-order spring with critical-like
damping ratios rather than exponential interpolation. Choose exponential
response for perceptual parameter smoothing and a spring when velocity/inertia
is part of the motion.

## Failure modes and diagnostics

Observed boundaries:

- cinematic implementation detachment randomness uses `Math.random`; seed it for replay and
  regression.
- Semi-implicit springs need a clamped `dt`, especially after tab suspension.
- The launch path is authored for one planet scale and shot duration.
- Camera-relative separation is intentionally cinematic rather than physical.
- Repeated quaternion multiplication should normalize periodically.
- Timeline phase constants are coupled; changing one duration requires
  recomputing later event boundaries.

Expose:

```text
sequence time and current phase
analytic position/speed curve
radial, tangent, and flight-direction vectors
base orientation, roll, and final orientation
stage world transform before/after reparent
detached scalar offsets/velocities
dock port, axis, parallel error, and radial error
spring target, velocity, stiffness, and damping
spin rates and accumulated angles
debris inherited tangential/outward/axial velocity
terminal lock state
```
