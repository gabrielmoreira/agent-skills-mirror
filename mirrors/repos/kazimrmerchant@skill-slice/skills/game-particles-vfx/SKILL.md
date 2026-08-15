---
name: game-particles-vfx
version: 1.1.1
description: "Implements Godot 4.3+ visual particle FX with GPUParticles2D/3D, ParticleProcessMaterial, emission shapes, subemitters, trails, attractors, and collision recipes (fire, smoke, sparks). Use when the effect is visual flavor the simulation does not depend on. Not for reading GPU particle positions as gameplay hit detection; never treat Compatibility-renderer trails or attractors as supported."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# Particle Systems in Godot 4.3+

All examples target Godot 4.3+ and avoid deprecated APIs. The particle stack was reworked in Godot 4 (process logic moved into `ParticleProcessMaterial`, and `Particles*` nodes were renamed to `GPUParticles*`), so 3.x tutorials reference properties that no longer exist. Each example is shown in GDScript first, then C#, because the two share identical concepts but differ in casing and null-handling idioms.

> **Related skills:** **shader-basics** for custom particle shaders, **3d-essentials** for lighting and environment that affect particles, **2d-essentials** for 2D rendering context, **tween-animation** for code-driven VFX timing, **godot-optimization** for particle performance tuning.

## When to Use

Reach for this skill when an effect is *visual flavor* rather than *gameplay state* — something the player sees but the simulation does not depend on:

- **Environmental ambiance** (fire, smoke, rain, dust): continuous emitters that run for the lifetime of a scene. These tell the player where they are and whether a space is safe or hostile.
- **Combat and interaction feedback** (explosions, impact sparks, magic): short, loud bursts that confirm "something happened." Feedback timing matters more than realism, so these lean on `one_shot` + `explosiveness`.
- **Polish layers** (trails, subemitters, turbulence): secondary motion that makes a base effect feel alive instead of static.
- **Performance-tuned variants**: the same effect authored at several quality tiers so it can scale from desktop GPUs down to web/mobile.

### Do Not Use

Each prohibition prevents a specific, hard-to-debug failure mode:

- **Don't use `CPUParticles` for high-count systems when a GPU is available.** CPU particles run every particle's physics on the main thread; a few thousand will stall your frame. `GPUParticles` offload that work to the graphics card and scale to tens of thousands cheaply.
- **Don't read GPU particle positions for gameplay logic.** GPU particle state lives in VRAM and is never read back to the CPU — there is no real-time `get_particle_position()`. If you need exact positions (spawning loot where a spark landed, hit detection), use `Area2D`/`Area3D` physics nodes, or fall back to `CPUParticles` when the count is small enough that readback is affordable.
- **Don't expect trails or attractors under the Compatibility renderer.** Those features depend on compute/advanced rendering paths that only Forward+ and Mobile implement. The Compatibility renderer doesn't error — it silently ignores them — so an effect that looks correct in the editor can ship broken on a web export. Verify on your real target.
- **Don't crank `amount` to brute-force density.** Each particle costs fill rate (overdraw) regardless of processing backend. Doubling `amount` to fix a "too sparse" look often just halves your framerate on weaker GPUs. Tune `lifetime`, scale, and the emission shape first.
- **Don't rely on `fixed_fps` for precise timing.** Locking the update rate too low makes fast effects stutter when the real framerate drifts. Leave it at `0` (match render FPS) and reach for `speed_scale` when you need global time control such as slow-mo.
- **Don't set `color` while using a `color_ramp`.** `color` is multiplied over every frame of the ramp, so a leftover tint skews the whole gradient. Always reset `color` to white (`Color.WHITE` / `Colors.White`) before assigning a ramp.

## Prerequisites

- **Godot 4.3+** — the particle stack was reworked in Godot 4; 3.x APIs do not apply.
- **Renderer awareness**: Trails, attractors, and collision require **Forward+** or **Mobile** renderer. The **Compatibility** renderer silently ignores them. Confirm your project renderer at Project → Project Settings → Rendering → Renderer.
- **Windows host (primary)**: All paths use Windows conventions. PowerShell is the default terminal. Project paths follow `C:\Users\<user>\<project>\` format. When running Godot from CLI in PowerShell, use `&` to invoke the executable if it contains spaces:
  ```powershell
  & "C:\Godot\Godot_v4.3-stable_win64.exe" --path "~\MyProject"
  ```
- **Reference files**: Load these from the skill's `references/` directory when you need the detailed setup for a specific feature:
  - `references/vfx-recipes.md` — ready-to-use GDScript wiring and `ParticleProcessMaterial` settings for fire, explosion, and dust effects.
  - `references/trails.md` — full trail setup and trail-mesh-type comparison.
  - `references/subemitters.md` — trigger modes, scene setup, GDScript/C# parity, and limitations.
  - `references/attractors-and-collision.md` — full setup of each attractor and collision type.
  - `references/flipbook-animation.md` — full flipbook setup with GDScript + C# parity.

## Procedure

### 1. Choose GPU vs CPU Particles

| Node                | Processing | Features                                | Use For                        |
|---------------------|------------|-----------------------------------------|--------------------------------|
| `GPUParticles2D`    | GPU        | Full features, high counts, trails      | Most 2D effects                |
| `GPUParticles3D`    | GPU        | Full features, attractors, collision    | Most 3D effects                |
| `CPUParticles2D`    | CPU        | Simpler, no trails/attractors           | Low-end devices, few particles |
| `CPUParticles3D`    | CPU        | Simpler, no trails/attractors           | Low-end devices, few particles |

**Rule of thumb:** default to GPU particles because the GPU processes particles in parallel and never blocks game logic. Switch to CPU particles only when targeting hardware without a capable renderer (some web/low-end devices), or when you genuinely need the CPU to know where each particle is (e.g. spawning a node at a particle's location).

> You can convert between GPU and CPU particles in the editor: select the node → toolbar → **Convert to CPUParticles2D/3D** (or vice versa). This copies equivalent settings.

### 2. Understand the Architecture

A particle node separates *behavior* from *appearance*:

```
GPUParticles2D/3D
├── Process Material (ParticleProcessMaterial)   ← physics, emission, color
├── Draw Pass 1 (Mesh)                           ← what each particle looks like
└── (Optional) Draw Pass 2-4                     ← additional meshes per particle
```

### 3. Minimal Setup

1. Add a **GPUParticles2D** (or 3D) node.
2. In Inspector → Process Material → **New ParticleProcessMaterial**. Without a process material the node emits nothing.
3. Set **Amount** (particles alive at once). Start low and raise only if the effect reads as too sparse.
4. Configure emission, direction, velocity, gravity (see steps 5–7 below).
5. (2D) Set **Texture** for particle appearance (e.g. `Texture2D` or `AtlasTexture`).
6. (3D) Set **Draw Pass 1** mesh (e.g. `QuadMesh` for camera-facing billboards, or a custom mesh for volumetric debris).
7. Test in the editor viewport — particles should appear immediately when `emitting` is `true`.

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

A continuous emitter you simply switch `emitting` on. A one-shot emitter must be *armed and restarted* each time you want a fresh burst — otherwise a second trigger does nothing because the system already ran to completion.

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
        if (_particles is null) { GD.PushError("StartContinuous: particle node is missing."); return; }
        _particles.OneShot = false;
        _particles.Emitting = true;
    }

    public void StopContinuous()
    {
        if (_particles is null) { return; }
        _particles.Emitting = false;
    }

    public void TriggerBurst()
    {
        if (_particles is null) { GD.PushError("TriggerBurst: particle node is missing."); return; }
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

	# Free after the last particle dies. The +0.5s margin absorbs frame-timing jitter.
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

### 7. Configure the ParticleProcessMaterial

Use pure factory functions that build and return a fully configured `ParticleProcessMaterial`. Each validates its inputs so degenerate values (negative radius, inverted min/max range) are caught at the call site.

**Emission Shape** — defines where particles are born; the single biggest factor in an effect's silhouette:

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

static func _make_sphere_emitter(radius: float) -> ParticleProcessMaterial:
	assert(radius > 0.0, "Emission sphere radius must be > 0, got %f" % radius)
	var mat := ParticleProcessMaterial.new()
	mat.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_SPHERE
	mat.emission_sphere_radius = maxf(radius, 0.0001)
	return mat

static func _configure_motion(mat: ParticleProcessMaterial, min_speed: float, max_speed: float) -> void:
	assert(mat != null, "_configure_motion requires a ParticleProcessMaterial")
	assert(min_speed >= 0.0, "Minimum velocity cannot be negative, got %f" % min_speed)
	assert(max_speed >= min_speed, "Maximum velocity must be >= minimum velocity")
	mat.direction = Vector3(0.0, 1.0, 0.0)
	mat.spread = 30.0
	mat.initial_velocity_min = min_speed
	mat.initial_velocity_max = max_speed
	mat.gravity = Vector3(0.0, -9.8, 0.0)
```

```csharp
using System;
using Godot;

public static class FireMaterialFactory
{
    private static ParticleProcessMaterial MakeSphereEmitter(float radius)
    {
        if (radius <= 0.0f)
            throw new ArgumentOutOfRangeException(nameof(radius), radius, "Emission sphere radius must be greater than 0.");

        return new ParticleProcessMaterial
        {
            EmissionShape = ParticleProcessMaterial.EmissionShapeEnum.Sphere,
            EmissionSphereRadius = radius,
        };
    }

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
}
```

**Scale Over Lifetime** — `scale_min`/`scale_max` set each particle's base size at birth. `scale_curve` multiplies that base by a factor sampled across the particle's normalized age (0.0 = birth, 1.0 = death). Shrinking the curve to 0 at death makes particles fade out by size instead of popping.

**Color Over Lifetime** — `color_ramp` (a `GradientTexture1D`) maps particle age to color. Always reset `color` to white before assigning a ramp so the ramp isn't tinted by a stale `color` value.

### 8. Add Advanced Features (load reference files as needed)

- **Trails** (Forward+ and Mobile only): Set `trail_enabled = true` on the node and assign a trail mesh (`RibbonTrailMesh` for flat 2D-style ribbons, `TubeTrailMesh` for volumetric 3D trails). Also set `trail_material` and tune `trail_section_length`. → Load `references/trails.md` for full setup.

- **Subemitters**: A particle can spawn another particle scene at lifecycle events (birth, collision, death, or manual trigger). Configure via `ParticleProcessMaterial.sub_emitter_mode` plus the `sub_emitter` property on the parent node, which expects a `PackedScene` whose root is another `GPUParticles` node. → Load `references/subemitters.md` for trigger modes and scene setup.

- **Attractors & Collision** (3D, Forward+/Mobile only): `GPUParticlesAttractor*3D` (Box / Sphere / Vector Field) pulls particles toward a region. `GPUParticlesCollision*3D` (Box / Sphere / SDF / HeightField) lets particles bounce off geometry. Particles must opt in: enable `attractor_interaction_enabled` and `collision_mode` on the `ParticleProcessMaterial`. → Load `references/attractors-and-collision.md` for full setup.

- **Turbulence**: Set `turbulence_enabled = true` on the `ParticleProcessMaterial`. Tune `turbulence_noise_strength` (0.5–2.0 typical), `turbulence_noise_scale` (lower = larger, slower swirls), and `turbulence_noise_speed` (animates the noise field). Use `turbulence_noise_offset` to decorrelate multiple emitters so they don't swirl in sync.

- **Flipbook Animation** (2D): `ParticleProcessMaterial.anim_speed_min`/`anim_speed_max` control frame advance speed. `CanvasItemMaterial.particles_anim_h_frames`/`particles_anim_v_frames` describe the sheet's grid layout. Apply the `CanvasItemMaterial` to the `GPUParticles2D` node's `material` property. → Load `references/flipbook-animation.md` for full setup.

### 9. Use Common VFX Recipes

- **Fire** (2D): continuous emitter with hot-to-cool color ramp and scale-down curve. → Load `references/vfx-recipes.md`.
- **Explosion burst** (3D or 2D): `one_shot = true`, high `amount`, short `lifetime`, `explosiveness = 1.0`. → Load `references/vfx-recipes.md`.
- **Dust / footstep puff**: small `one_shot` burst that scales up while fading alpha to 0. → Load `references/vfx-recipes.md`.

## Pitfalls

- **Compatibility renderer silently drops trails/attractors/collision**: No error is thrown — the effect simply doesn't render. Always verify on your actual export target, not just the editor.
- **One-shot re-trigger does nothing without `restart()`**: A finished one-shot system won't emit again on a second `emitting = true` call. Always call `restart()` before setting `emitting = true` for repeated bursts.
- **Transient burst scenes leak if not freed**: Always schedule `queue_free()` after `lifetime + 0.5s` margin for instanced one-shot effects.
- **`color` tints `color_ramp`**: A non-white `color` multiplies over every frame of the ramp. Reset to `Color.WHITE` / `Colors.White` before assigning a ramp.
- **Inverted `min`/`max` velocity range**: Godot doesn't error — it samples a meaningless range and your speed variation disappears. Always validate `min <= max`.
- **Overdraw from high `amount`**: Each particle costs fill rate regardless of backend. Doubling `amount` to fix sparseness often halves framerate on weaker GPUs. Tune `lifetime`, scale, and emission shape first.
- **`fixed_fps` too low causes stutter**: Leave at `0` (match render FPS). Use `speed_scale` for slow-motion or global time control.
- **GPU particle positions unreadable from CPU**: There is no `get_particle_position()`. Use `Area2D`/`Area3D` for gameplay hit detection, or `CPUParticles` if you need per-particle CPU access.
- **`local_coords` wrong for the use case**: `true` for effects attached to a moving emitter (exhaust on a car), `false` for world-anchored effects (rain, ground dust). Getting this wrong makes particles either drag with the emitter or float free unexpectedly.
- **`visibility_rect`/`visibility_aabb` not sized to effect**: If too small, particles get culled while still on-screen. If too large, the effect keeps rendering long after it leaves view. Auto-calculated by default; only override if you see culling issues.

## Verification

Work through this checklist before considering a particle effect "done":

- [ ] Particle `amount` is the minimum that still reads correctly — extra particles cost overdraw every frame.
- [ ] `lifetime` matches the intended visual duration — particles neither vanish abruptly nor linger and clutter.
- [ ] `one_shot` is enabled for burst effects **and** `restart()` is called on each trigger.
- [ ] `preprocess` is set for always-visible ambient effects so they appear already-running on the first frame.
- [ ] Emission shape matches the source geometry (sphere for explosions, box for area fog).
- [ ] `color_ramp` fades alpha to 0 at the end so particles dissolve smoothly.
- [ ] `scale_curve` shrinks (or grows-then-fades for puffs) particles over lifetime.
- [ ] `local_coords` is set intentionally — `true` for moving emitters, `false` for world-anchored effects.
- [ ] One-shot particles are freed with `queue_free()` after `lifetime` + a small margin.
- [ ] `visibility_rect` (2D) or `visibility_aabb` (3D) is sized to the effect's real extent.
- [ ] `fixed_fps` is left at `0` unless you have a specific reason to lock it.
- [ ] Renderer-dependent features (trails, attractors, collision) are confirmed working on the actual export target.
- [ ] Dynamic quality scaling is wired up for target hardware tiers — lowering `amount_ratio` or substituting `CPUParticles` on web/low-end targets.

### Quick Verification Commands (PowerShell)

```powershell
# Check Godot version to confirm 4.3+
& "C:\Godot\Godot_v4.3-stable_win64.exe" --version

# Run the project headless to check for particle-related errors in output
& "C:\Godot\Godot_v4.3-stable_win64.exe" --path "~\MyProject" --headless 2>&1 | Select-String -Pattern "particle|Particle|GPUParticles|CPUParticles|shader|material"

# Export to web target and verify renderer-dependent features survive the build
& "C:\Godot\Godot_v4.3-stable_win64.exe" --path "~\MyProject" --export-release "Web" "~\MyProject\builds\web\index.html"
```

## Related Skills

- **shader-basics**: Custom particle shaders when `ParticleProcessMaterial` can't express the look — stylized dissolves, custom lighting, or per-particle data.
- **3d-essentials**: How particles interact with 3D environments, lighting, and camera perspective (billboarding, depth sorting, shadow casting).
- **2d-essentials**: The 2D rendering context particles live in — `CanvasItemMaterial`, blend modes, `Texture2D`/`AtlasTexture` usage.
- **tween-animation**: Code-driven VFX timing — sequencing emitters, ramping `speed_scale`, choreographing multi-stage effects.
- **godot-optimization**: Particle performance tuning — the deciding factor in whether a dense effect holds framerate on your weakest target hardware.
