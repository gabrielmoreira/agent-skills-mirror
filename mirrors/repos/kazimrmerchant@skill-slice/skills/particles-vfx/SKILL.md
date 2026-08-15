---
name: particles-vfx
version: 1.1.1
description: "Implements Godot 4.3+ visual particle VFX with GPUParticles2D/3D and ParticleProcessMaterial (emission, trails, subemitters, attractors, collision). Use when adding fire, smoke, rain, explosions, or polish bursts that are visual flavor, not gameplay state. Not for reading GPU particle positions for hit/loot logic, Three.js particles, or Compatibility-renderer trails/attractors."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Particle Systems in Godot 4.3+

All examples target Godot 4.3+ and avoid deprecated APIs. The particle stack was reworked in Godot 4 (process logic moved into `ParticleProcessMaterial`, and `Particles*` nodes were renamed to `GPUParticles*`), so 3.x tutorials reference properties that no longer exist. Each example is shown in GDScript first, then C#, because the two share identical concepts but differ in casing and null-handling idioms.

> **Related skills:** **shader-basics** for custom particle shaders, **3d-essentials** for lighting and environment that affect particles, **2d-essentials** for 2D rendering context, **tween-animation** for code-driven VFX timing, **godot-optimization** for particle performance tuning.

## When to Use

Reach for this skill when an effect is *visual flavor* rather than *gameplay state* — something the player sees but the simulation does not depend on. Concretely:

- **Environmental ambiance** (fire, smoke, rain, dust): continuous emitters that run for the lifetime of a scene. These tell the player where they are and whether a space is safe or hostile.
- **Combat and interaction feedback** (explosions, impact sparks, magic): short, loud bursts that confirm "something happened." Feedback timing matters more than realism, so these lean on `one_shot` + `explosiveness`.
- **Polish layers** (trails, subemitters, turbulence): secondary motion that makes a base effect feel alive instead of static.
- **Performance-tuned variants**: the same effect authored at several quality tiers so it can scale from desktop GPUs down to web/mobile.

### Do NOT use for:

- **High-count systems on CPU when a GPU is available.** CPU particles run every particle's physics on the main thread — a few thousand will stall your frame while the GPU sits idle. `GPUParticles` offload that work to the graphics card and scale to tens of thousands cheaply.
- **Reading GPU particle positions for gameplay logic.** GPU particle state lives in VRAM and is never read back to the CPU. There is no real-time `get_particle_position()` in GDScript/C#. If you need exact positions (spawning loot where a spark landed, hit detection), use `Area2D`/`Area3D` physics nodes, or fall back to `CPUParticles` when the count is small enough that readback is affordable.
- **Trails or attractors under the Compatibility renderer.** Those features depend on compute/advanced rendering paths that only Forward+ and Mobile implement. The Compatibility renderer does not error — it silently ignores them — so an effect that looks correct in the editor can ship broken on a web export. Always verify on your real target.
- **Brute-forcing density by cranking `amount`.** Each particle costs fill rate (overdraw) regardless of processing backend. Doubling `amount` to fix a "too sparse" look often just halves your framerate on weaker GPUs. Tune `lifetime`, scale, and the emission shape first.
- **Using `fixed_fps` for precise timing.** Locking the update rate too low makes fast effects stutter when the real framerate drifts. Leave it at `0` (match render FPS) and use `speed_scale` for global time control such as slow-mo.
- **Setting `color` while using a `color_ramp`.** `color` is multiplied over every frame of the ramp, so a leftover tint skews the whole gradient. Always reset `color` to white (`Color.WHITE` / `Colors.White`) before assigning a ramp.

## Prerequisites

- **Godot 4.3 or later.** The particle API was reworked in Godot 4; 3.x properties do not exist.
- **Renderer awareness:** Trails, attractors, and collision require **Forward+** or **Mobile** renderer. The **Compatibility** renderer silently ignores these features.
- **Node naming convention:** Examples assume a child node named `GPUParticles2D` (or `GPUParticles3D`). Adjust the node path in `get_node_or_null` / `GetNodeOrNull` if your scene uses a different name.
- **Windows host (PowerShell):** When running Godot from the command line on Windows, use PowerShell syntax. Example: `& "C:\Program Files\Godot\Godot_v4.3-stable_win64.exe" --path .` to launch the project editor.

## Procedure

### 1. Choose GPU vs CPU Particles

| Node                | Processing | Features                                | Use For                        |
|---------------------|------------|-----------------------------------------|--------------------------------|
| `GPUParticles2D`    | GPU        | Full features, high counts, trails      | Most 2D effects                |
| `GPUParticles3D`    | GPU        | Full features, attractors, collision    | Most 3D effects                |
| `CPUParticles2D`    | CPU        | Simpler, no trails/attractors           | Low-end devices, few particles |
| `CPUParticles3D`    | CPU        | Simpler, no trails/attractors           | Low-end devices, few particles |

**Rule of thumb:** Default to GPU particles. The GPU processes particles in parallel and never blocks game logic. Switch to CPU particles only when (a) targeting hardware without a capable renderer (some web/low-end devices), or (b) you genuinely need the CPU to know where each particle is (e.g. spawning a node at a particle's location).

> You can convert between GPU and CPU particles in the editor: select the node → toolbar → **Convert to CPUParticles2D/3D** (or vice versa). This copies equivalent settings.

### 2. Understand the Architecture

A particle node separates *behavior* from *appearance*:

```
GPUParticles2D/3D
├── Process Material (ParticleProcessMaterial)   ← physics, emission, color
├── Draw Pass 1 (Mesh)                           ← what each particle looks like
└── (Optional) Draw Pass 2-4                     ← additional meshes per particle
```

### 3. Minimal Node Setup

1. Add a **GPUParticles2D** (or 3D) node.
2. In Inspector → Process Material → **New ParticleProcessMaterial**. Without a process material the node emits nothing.
3. Set **Amount** (particles alive at once). Start low and raise only if the effect reads as too sparse.
4. Configure emission, direction, velocity, gravity (see below).
5. (2D) Set **Texture** for particle appearance (e.g. `Texture2D` or `AtlasTexture`).
6. (3D) Set **Draw Pass 1** mesh (e.g. `QuadMesh` for camera-facing billboards, or a custom mesh for volumetric debris).

### 4. Configure Key Node Properties

These live on the `GPUParticles2D/3D` node itself (not the material):

| Property          | Type     | Description                                         |
|-------------------|----------|-----------------------------------------------------|
| `emitting`        | `bool`   | Start/stop emission                                 |
| `amount`          | `int`    | Total particles alive at once                       |
| `lifetime`        | `float`  | Seconds each particle lives                         |
| `one_shot`        | `bool`   | Emit once then stop                                 |
| `preprocess`      | `float`  | Simulate this many seconds before the first frame   |
| `speed_scale`     | `float`  | Time multiplier for particle physics                |
| `explosiveness`   | `float`  | 0.0 = spread over lifetime, 1.0 = all at once       |
| `fixed_fps`       | `int`    | Lock particle update rate (0 = match render FPS)    |
| `local_coords`    | `bool`   | Particles move with the node (true) or stay in world (false) |
| `draw_order`      | `enum`   | Index, Lifetime, or Reverse Lifetime                |
| `amount_ratio`    | `float`  | Fraction of particles to emit (0.0–1.0)             |
| `visibility_aabb` | `AABB`   | (3D) Custom bounding box for culling. Auto-calculated by default. |
| `visibility_rect` | `Rect2`  | (2D) Custom bounding rectangle for culling. Auto-calculated by default. |

### 5. Wire Up One-Shot vs Continuous Emission

A continuous emitter is simply switched `emitting` on. A one-shot emitter must be **armed and restarted** each time you want a fresh burst — otherwise a second trigger does nothing because the system already ran to completion.

The script below resolves the child node once via `get_node_or_null`, asserts the dependency in debug builds, and guards every public method so a missing node produces a clear log line rather than a crash.

```gdscript
extends Node2D
## Drives a single GPUParticles2D child for both continuous and burst use.

@onready var _particles: GPUParticles2D = get_node_or_null(^"GPUParticles2D")

func _ready() -> void:
	assert(_particles != null, "FireEffect expects a GPUParticles2D child named 'GPUParticles2D'")

func start_continuous() -> void:
	if _particles == null:
		push_error("start_continuous: particle node is missing")
		return
	_particles.one_shot = false
	_particles.emitting = true

func stop_continuous() -> void:
	if _particles == null:
		return
	_particles.emitting = false

func trigger_burst() -> void:
	# restart() rewinds the simulation to t=0 so a brand-new burst plays on every
	# call, even if a previous burst is still mid-flight.
	if _particles == null:
		push_error("trigger_burst: particle node is missing")
		return
	_particles.one_shot = true
	_particles.restart()
	_particles.emitting = true
```

```csharp
using Godot;

public partial class FireEffect : Node2D
{
    private GpuParticles2D _particles;

    public override void _Ready()
    {
        _particles = GetNodeOrNull<GpuParticles2D>("GPUParticles2D");
        if (_particles is null)
        {
            GD.PushError("FireEffect expects a GpuParticles2D child named 'GPUParticles2D'.");
        }
    }

    public void StartContinuous()
    {
        if (_particles is null)
        {
            GD.PushError("StartContinuous: particle node is missing.");
            return;
        }
        _particles.OneShot = false;
        _particles.Emitting = true;
    }

    public void StopContinuous()
    {
        if (_particles is null) return;
        _particles.Emitting = false;
    }

    public void TriggerBurst()
    {
        if (_particles is null)
        {
            GD.PushError("TriggerBurst: particle node is missing.");
            return;
        }
        _particles.OneShot = true;
        _particles.Restart();
        _particles.Emitting = true;
    }
}
```

### 6. Spawn and Auto-Free Transient Bursts

Transient effects (explosions, footstep puffs) are instanced at a world position, played once, and discarded. If you forget the discard step they accumulate in the tree and leak memory.

```gdscript
## Spawns a one-shot burst at a world position and frees it after it finishes.
func spawn_burst(burst_scene: PackedScene, world_position: Vector2) -> void:
	assert(burst_scene != null, "spawn_burst requires a non-null PackedScene")
	if burst_scene == null:
		push_error("spawn_burst: burst_scene is null")
		return

	var instance: Node = burst_scene.instantiate()
	var particles := instance as GPUParticles2D
	if particles == null:
		push_error("spawn_burst: scene root is not a GPUParticles2D")
		instance.queue_free()
		return

	particles.global_position = world_position
	particles.one_shot = true
	add_child(particles)
	particles.restart()
	particles.emitting = true

	# Free after the last particle dies. +0.5s margin absorbs frame-timing jitter.
	var cleanup_delay: float = particles.lifetime + 0.5
	get_tree().create_timer(cleanup_delay).timeout.connect(particles.queue_free)
```

```csharp
using System;
using Godot;

public partial class BurstSpawner : Node2D
{
    public void SpawnBurst(PackedScene burstScene, Vector2 worldPosition)
    {
        ArgumentNullException.ThrowIfNull(burstScene);

        Node instance = burstScene.Instantiate();
        if (instance is not GpuParticles2D particles)
        {
            GD.PushError("SpawnBurst: scene root is not a GpuParticles2D.");
            instance.QueueFree();
            return;
        }

        particles.GlobalPosition = worldPosition;
        particles.OneShot = true;
        AddChild(particles);
        particles.Restart();
        particles.Emitting = true;

        float cleanupDelay = particles.Lifetime + 0.5f;
        SceneTreeTimer timer = GetTree().CreateTimer(cleanupDelay);
        timer.Timeout += particles.QueueFree;
    }
}
```

### 7. Build a ParticleProcessMaterial (Factory Pattern)

Rather than mutating a material inline, use **pure factory functions** that build and return a fully configured `ParticleProcessMaterial`. Each validates its inputs so degenerate values are caught at the call site.

#### Emission Shape

The emission shape defines *where* particles are born — the single biggest factor in an effect's silhouette.

| Shape             | Description                                    |
|-------------------|------------------------------------------------|
| `Point`           | All particles spawn at the origin              |
| `Sphere`          | Random position within a sphere volume         |
| `Sphere Surface`  | Random position on the sphere surface only     |
| `Box`             | Random position within a box volume            |
| `Ring`            | Random position on a ring/torus                |
| `Points`          | Spawn at positions sampled from a texture/mesh |
| `Directed Points` | Spawn at positions with normals from a mesh    |

```gdscript
class_name FireMaterialFactory
extends RefCounted
## Pure builders for a fire ParticleProcessMaterial.

static func _make_sphere_emitter(radius: float) -> ParticleProcessMaterial:
	assert(radius > 0.0, "Emission sphere radius must be > 0, got %f" % radius)
	var mat := ParticleProcessMaterial.new()
	mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	mat.emission_sphere_radius = maxf(radius, 0.0001)
	return mat
```

```csharp
using System;
using Godot;

public static class FireMaterialFactory
{
    private static ParticleProcessMaterial MakeSphereEmitter(float radius)
    {
        if (radius <= 0.0f)
        {
            throw new ArgumentOutOfRangeException(
                nameof(radius), radius, "Emission sphere radius must be greater than 0.");
        }

        return new ParticleProcessMaterial
        {
            EmissionShape = ParticleProcessMaterial.EmissionShapeEnum.Sphere,
            EmissionSphereRadius = radius,
        };
    }
}
```

#### Direction, Velocity & Gravity

`direction` + `spread` set the cone particles launch into; velocity range sets speed; gravity bends the path over time. Enforce `min <= max` because an inverted range doesn't error — Godot samples a meaningless range and the speed variation disappears.

```gdscript
static func _configure_motion(mat: ParticleProcessMaterial, min_speed: float, max_speed: float) -> void:
	assert(mat != null, "_configure_motion requires a ParticleProcessMaterial")
	assert(min_speed >= 0.0, "Minimum velocity cannot be negative, got %f" % min_speed)
	assert(max_speed >= min_speed, "Maximum velocity must be >= minimum velocity")

	mat.direction = Vector3(0.0, 1.0, 0.0)   # upward
	mat.spread = 30.0                          # degrees of cone scatter
	mat.initial_velocity_min = min_speed
	mat.initial_velocity_max = max_speed
	mat.gravity = Vector3(0.0, -9.8, 0.0)      # Earth gravity
```

```csharp
    private static void ConfigureMotion(ParticleProcessMaterial material, float minSpeed, float maxSpeed)
    {
        ArgumentNullException.ThrowIfNull(material);
        if (minSpeed < 0.0f)
            throw new ArgumentOutOfRangeException(nameof(minSpeed), minSpeed, "Minimum velocity cannot be negative.");
        if (maxSpeed < minSpeed)
            throw new ArgumentOutOfRangeException(nameof(maxSpeed), maxSpeed, "Maximum velocity must be >= minimum velocity.");

        material.Direction = new Vector3(0.0f, 1.0f, 0.0f);
        material.Spread = 30.0f;
        material.InitialVelocityMin = minSpeed;
        material.InitialVelocityMax = maxSpeed;
        material.Gravity = new Vector3(0.0f, -9.8f, 0.0f);
    }
```

#### Scale Over Lifetime

`scale_min`/`scale_max` set each particle's base size at birth. `scale_curve` multiplies that base by a factor sampled across the particle's **normalized age** (0.0 = birth, 1.0 = death). Shrinking the curve to 0 at death makes particles fade out by size instead of popping.

#### Color Over Lifetime

**HARD RULE:** Always reset `color` to `Color.WHITE` / `Colors.White` before assigning a `color_ramp`. A leftover `color` tint is multiplied over every frame of the ramp and skews the entire gradient.

### 8. Load Reference Files for Advanced Features

Load these reference files from `references/` when you need the corresponding feature:

| Feature | Reference File | When to Load |
|---------|---------------|--------------|
| Fire, explosion, dust recipes | `references/vfx-recipes.md` | When implementing any of the three core VFX recipes with full GDScript wiring and recommended `ParticleProcessMaterial` settings |
| Trails | `references/trails.md` | When setting up `trail_enabled` with `RibbonTrailMesh` or `TubeTrailMesh`; includes trail-mesh-type comparison |
| Subemitters | `references/subemitters.md` | When a particle needs to spawn another particle scene at birth/collision/death; includes trigger modes, scene setup, and limitations |
| Attractors & Collision | `references/attractors-and-collision.md` | When using `GPUParticlesAttractor*3D` or `GPUParticlesCollision*3D`; includes full setup of each type |
| Flipbook Animation | `references/flipbook-animation.md` | When using sprite-sheet animated particles; includes `CanvasItemMaterial` frame layout setup |

### 9. Trails (Forward+ and Mobile ONLY)

Set `trail_enabled = true` on `GPUParticles2D/3D` and assign a trail `Mesh`:
- `RibbonTrailMesh` for flat 2D-style ribbons
- `TubeTrailMesh` for volumetric 3D trails

Also set `trail_material` on the node and tune `trail_section_length` (shorter = smoother but more geometry). **The Compatibility renderer will show nothing** — trails require Forward+ or Mobile.

> **Load `references/trails.md`** for the full setup and trail-mesh-type comparison.

### 10. Subemitters

A particle can spawn *another* particle scene at lifecycle events (birth, collision, death, or manual trigger). Configure via `ParticleProcessMaterial.sub_emitter_mode` plus the `sub_emitter` property on the parent node, which expects a `PackedScene` whose root is another `GPUParticles` node.

> **Load `references/subemitters.md`** for trigger modes, scene setup, GDScript/C# parity, and limitations.

### 11. Attractors & Collision (3D, Forward+/Mobile ONLY)

- `GPUParticlesAttractor*3D` (Box / Sphere / Vector Field): pulls particles toward a region.
- `GPUParticlesCollision*3D` (Box / Sphere / SDF / HeightField): lets particles bounce off geometry.

**HARD RULE:** The particles themselves must opt in. Enable `attractor_interaction_enabled` and `collision_mode` on the `ParticleProcessMaterial`, or the attractor/collider nodes will have no effect even when present in the scene. No 2D equivalents exist.

> **Load `references/attractors-and-collision.md`** for full setup of each attractor and collision type.

### 12. Turbulence

Set `turbulence_enabled = true` on the `ParticleProcessMaterial` and tune:
- `turbulence_noise_strength` (0.5–2.0 typical)
- `turbulence_noise_scale` (lower = larger, slower swirls)
- `turbulence_noise_speed` (animates the noise field over time)
- `turbulence_noise_offset` (decorrelate multiple emitters so they don't swirl in sync)

### 13. Flipbook Animation (2D)

Two cooperating settings drive sprite-sheet animated particles:
- `ParticleProcessMaterial.anim_speed_min`/`anim_speed_max`: how fast a particle advances through frames over its lifetime.
- `CanvasItemMaterial.particles_anim_h_frames`/`particles_anim_v_frames`: the sheet's grid layout.

Apply the `CanvasItemMaterial` to the `GPUParticles2D` node's `material` property, or the frame layout is never read and every particle shows the whole sheet.

> **Load `references/flipbook-animation.md`** for the full setup with GDScript + C# parity.

## Examples

### Common VFX Recipes

- **Fire** (2D): continuous emitter with hot-to-cool color ramp and scale-down curve. Continuous because flame is ongoing; the ramp + shrink sell the rising, cooling motion.
- **Explosion burst** (3D or 2D): `one_shot = true` with high `amount`, short `lifetime`, `explosiveness = 1.0` so every particle launches on the same frame. An explosion that lingers reads as slow and unconvincing.
- **Dust / footstep puff**: small `one_shot` burst that scales *up* while fading alpha to 0, mimicking how a real puff expands and dissipates.

> **Load `references/vfx-recipes.md`** for ready-to-use, fully-typed GDScript wiring and recommended `ParticleProcessMaterial` settings for all three.

## Pitfalls

1. **Compatibility renderer silently drops trails, attractors, and collision.** No error is printed. An effect that looks correct in the editor (Forward+) can ship broken to a web export (Compatibility). Always test on your actual export target.

2. **Forgetting `restart()` on one-shot bursts.** A one-shot system that already ran to completion will emit nothing on a second `emitting = true`. Always call `restart()` before re-arming.

3. **Leaking transient particle instances.** One-shot bursts instanced at runtime must be `queue_free()`d after `lifetime + margin`. Without this, they accumulate in the scene tree and leak memory.

4. **Setting `color` while using `color_ramp`.** The `color` property is multiplied over every frame of the ramp. Always reset to `Color.WHITE` / `Colors.White` before assigning a ramp.

5. **Cranking `amount` to fix sparse-looking effects.** Each particle costs fill rate (overdraw). Doubling `amount` often halves framerate on weaker GPUs. Tune `lifetime`, scale, and emission shape first.

6. **Using `fixed_fps` for timing control.** A low fixed rate makes fast effects stutter when real framerate drifts. Leave at `0` and use `speed_scale` for slow-mo or global time control.

7. **Expecting GPU particle readback.** GPU particle state lives in VRAM and is never read back to the CPU. There is no `get_particle_position()`. Use `Area2D`/`Area3D` for gameplay-relevant hit detection, or `CPUParticles` for small-count position access.

8. **Missing opt-in for attractors/collision.** Attractor and collider nodes in the scene have zero effect unless `attractor_interaction_enabled` and `collision_mode` are set on the `ParticleProcessMaterial`.

9. **Wrong `local_coords` setting.** `true` for effects attached to a moving emitter (exhaust on a car); `false` for world-anchored effects (rain, ground dust). Getting this wrong makes particles either drag incorrectly or stay frozen in world space.

10. **Missing `preprocess` on ambient effects.** Without `preprocess`, fire/smoke/dust start from empty on the first frame the player sees them. Set `preprocess` to a value ≥ `lifetime` so they appear already-running.

11. **Flipbook `CanvasItemMaterial` not applied.** If the `CanvasItemMaterial` with `particles_anim_h_frames`/`particles_anim_v_frames` is not set on the `GPUParticles2D` node's `material` property, every particle shows the whole sprite sheet instead of individual frames.

## Verification

Work through this checklist before considering a particle effect "done." Each item maps to a concrete failure it prevents:

- [ ] Particle `amount` is the minimum that still reads correctly — extra particles cost overdraw every frame.
- [ ] `lifetime` matches the intended visual duration — neither vanishing abruptly nor lingering and cluttering.
- [ ] `one_shot` is enabled for burst effects **and** `restart()` is called on each trigger.
- [ ] `preprocess` is set for always-visible ambient effects so they appear already-running on the first frame.
- [ ] Emission shape matches the source geometry (sphere for explosions, box for area fog).
- [ ] `color_ramp` fades alpha to 0 at the end so particles dissolve smoothly.
- [ ] `scale_curve` shrinks (or grows-then-fades for puffs) particles over lifetime.
- [ ] `local_coords` is set intentionally — `true` for moving emitters, `false` for world-anchored effects.
- [ ] One-shot particles are freed with `queue_free()` after `lifetime` + margin.
- [ ] `visibility_rect` (2D) or `visibility_aabb` (3D) is sized to the effect's real extent.
- [ ] `fixed_fps` is left at `0` unless you have a specific reason to lock it.
- [ ] Renderer-dependent features (trails, attractors, collision) are confirmed working on the actual export target — not just the editor.
- [ ] `color` is reset to `Color.WHITE` / `Colors.White` before assigning a `color_ramp`.
- [ ] Attractor/collision opt-in flags (`attractor_interaction_enabled`, `collision_mode`) are set on the `ParticleProcessMaterial` when using attractor/collider nodes.
- [ ] Dynamic quality scaling is wired up — lowering `amount_ratio` or substituting `CPUParticles` on web/low-end targets so the effect degrades gracefully.

### Quick Runtime Check (PowerShell)

```powershell
# Launch the project and check for particle-related errors in the editor log
& "C:\Program Files\Godot\Godot_v4.3-stable_win64.exe" --path . --verbose 2>&1 | Select-String -Pattern "particle|Particle|GPU|trail|attractor|collision"
```

If the output contains warnings about unsupported features under the Compatibility renderer, switch the project renderer to Forward+ or Mobile, or remove the renderer-dependent features for that export target.

## Related Skills

- **shader-basics**: Custom particle shaders when `ParticleProcessMaterial` can't express the look — stylized dissolves, custom lighting, or per-particle data.
- **3d-essentials**: How particles interact with 3D environments, lighting, and camera perspective (billboarding, depth sorting, shadow casting).
- **2d-essentials**: The 2D rendering context particles live in, including `CanvasItemMaterial`, blend modes, and `Texture2D`/`AtlasTexture` usage.
- **tween-animation**: Code-driven VFX timing — sequencing emitters, ramping `speed_scale`, or choreographing multi-stage effects.
- **godot-optimization**: Particle performance tuning — the deciding factor in whether a dense effect holds framerate on your weakest target hardware.
