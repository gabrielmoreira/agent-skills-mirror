---
name: technical-art-vfx
version: 1.0.1
description: "Authors HLSL/GLSL shaders, G-buffer pass order, PBR/BRDF, HDR post chains (bloom/ACES/SSAO), and compute GPU particles or VAT. Use for dissolve, fresnel, triplanar, or moving sim onto the GPU. Not a frame-budget profiler (game-performance-profiling) and never a DCC export or skeletal-IK chair."
risk: safe
source: opus
date_added: 2026-06-27
---

# Technical Art, Shaders & VFX

Shaders are tiny programs that run per-vertex and per-pixel in parallel on the GPU. The key mental model is the pipeline stages and what data each stage can read. Most "why is it black?" problems become obvious once you trace which space your data lives in and whether the inputs are actually bound.

## When to Use

Activate this skill when the task involves any of the following:

- **Authoring or debugging HLSL/GLSL** vertex, fragment, geometry, tessellation, or compute shaders.
- **Ordering render passes**: depth prepass, shadow map, G-buffer, opaque, transparent, post-process.
- **Choosing forward vs deferred** rendering and understanding the tradeoffs for a target platform.
- **Implementing PBR** and common shader techniques: fresnel, dissolve, triplanar, parallax/POM, vertex displacement, toon/cel, rim light.
- **Post-processing chains**: bloom, tonemapping (ACES), color grading (LUT), SSAO, motion blur, DOF, chromatic aberration, vignette.
- **Compute-shader work**: GPU particles, fluid/cloth/boids simulation, image processing, prefix-sum, structured buffer manipulation.
- **Particle systems** (CPU vs GPU), emitters/modules, soft particles, vertex animation textures (VAT).
- **Debugging shader correctness or performance**: black output, wrong space, NaNs, overdraw, variant explosion.

**Trigger keywords:** shader, HLSL, GLSL, shader graph, vertex/fragment/pixel shader, compute shader, dispatch, thread group, render pass, deferred, G-buffer, forward+, PBR, BRDF, fresnel, dissolve, triplanar, parallax, post-process, bloom, tonemap, ACES, LUT, SSAO, DOF, particle, GPU particles, VAT, billboard.

### Do not use for

- **CPU-side gameplay logic** that merely triggers an effect — own the shader/VFX, not the spawn decision.
- **General frame-time optimization and profiling methodology** — that is `performance-profiling` (RenderDoc capture, draw-call batching, CPU/GPU bottleneck analysis). This skill owns authoring the shading; that skill owns measuring/optimizing the frame.
- **DCC/asset authoring pipelines** (Blender export, UVs, LODs, collision) — see `blender-asset-pipeline`.
- **Skeletal animation/IK** of characters — see `runtime-animation`. VAT crowd animation in materials is in-scope here.

## Prerequisites

- A rendering engine or framework with shader authoring capability (Unity URP/HDRP, Unreal, Godot 4, custom DirectX/Vulkan/OpenGL, WebGL, etc.).
- A GPU with compute shader support if doing GPU simulation or GPU particles.
- A graphics debugger: **RenderDoc** (Windows/Linux) or **PIX** (Windows, Xbox) for capturing and inspecting render passes.
- Understanding of basic linear algebra (vectors, matrices, dot/cross products) and the graphics pipeline.

## Procedure

### 1. Hold the pipeline in your head

Before writing any shader code, map out which pipeline stage your work targets and what data is available at that stage:

```text
Vertex shader      -> per-vertex: object->world->view->clip space, pass varyings
[Tessellation]     -> subdivide patches (displacement, terrain)
[Geometry]         -> emit/kill primitives (rare; grass, billboards) — often costly
Rasterizer         -> interpolates varyings per pixel
Fragment/Pixel     -> per-pixel: sample textures, lighting, output color
Output merger      -> depth test, blending, write to render target
```

Compute shaders sit **outside** this graphics pipeline: they run arbitrary parallel work over thread groups and write to buffers/textures. They are dispatched independently and can share resources with the graphics pipeline via UAVs/SRVs.

### 2. Choose forward vs deferred

| | Forward (+ Forward+) | Deferred |
|---|---|---|
| Lights | Cost scales with lights × objects (Forward+ culls per-tile) | Decoupled: shade once per pixel from a G-buffer |
| Transparency | Native | Hard (needs forward pass on top) |
| MSAA | Easy | Harder (G-buffer MSAA is costly) |
| Material variety | Flexible | Constrained by G-buffer layout |
| Use when | Mobile/VR, few lights, lots of transparency | Many dynamic lights, opaque-heavy scenes |

**Decision rule:** If the scene has many dynamic lights and is mostly opaque, use deferred. If it needs heavy transparency, runs on mobile/VR, or has very diverse material types, use forward (or forward+ with tile culling).

### 3. Author a minimal lit fragment shader (HLSL)

This example combines fresnel rim lighting with a dissolve effect:

```hlsl
// Inputs: world normal N, view dir V, light dir L, base color,
//         dissolve mask sample + animated threshold.
float3 ShadeSurface(float3 N, float3 V, float3 L, float3 albedo,
                    float dissolveSample, float dissolveThreshold)
{
    // Dissolve: discard pixels below an animated threshold; glow at the edge.
    clip(dissolveSample - dissolveThreshold);              // alpha-test cutout

    // Lambert + a cheap fresnel rim.
    float  ndl    = saturate(dot(N, L));
    float  fres   = pow(1.0 - saturate(dot(N, V)), 5.0);   // Schlick-style rim
    float3 diffuse = albedo * ndl;
    float3 rim     = float3(0.4, 0.8, 1.0) * fres;

    // Edge-glow band near the dissolve front.
    float edge = smoothstep(dissolveThreshold, dissolveThreshold + 0.05, dissolveSample);
    float3 burn = lerp(float3(1.0, 0.4, 0.05), 0.0, edge);

    return diffuse + rim + burn;
}
```

### 4. Implement common shader techniques

- **Triplanar mapping**: Blend three axis-projected texture samples weighted by `abs(N)` to eliminate UV stretching on surfaces without good UVs. Normalize the weights so they sum to 1.
- **Parallax / POM**: Offset UVs by view-space height to fake depth on flat geometry. Parallax Occlusion Mapping ray-marches the height field for more convincing results but costs more ALU.
- **Vertex displacement**: Push vertex positions along the normal by a noise or height texture sample. Good for wind, waves, growth effects. Requires enough tessellation or vertex density.
- **Toon / cel shading**: Quantize `ndl` into discrete bands using `floor` or `smoothstep` thresholds. Add an outline pass (inverted hull or post-process edge detection).
- **Rim light**: Use fresnel `pow(1 - dot(N, V), power)` to add a glow at grazing angles. Cheap and effective for stylized looks.

### 5. Implement PBR correctly

Metal/roughness workflow inputs: `albedo, metallic, roughness, normal, AO`.

1. Use a microfacet BRDF: GGX/Trowbridge-Reitz normal distribution, Smith geometry function, Schlick Fresnel approximation.
2. **Author in linear color.** Convert sRGB textures to linear on read (hardware sRGB format or manual `pow(c, 2.2)`).
3. **Tonemap (ACES or similar) at the very end** of the post-process chain, then apply gamma correction for the output display.
4. Most "too dark" or "too bright" bugs are linear-vs-sRGB mistakes. Verify the texture import format and the output blend state.

### 6. Write a compute shader for GPU simulation

Dispatch threads in groups; each thread updates one element of a structured buffer. Ping-pong two buffers or use atomics for inter-thread communication. Choose group sizes that are multiples of 32 (NVIDIA warp) or 64 (AMD wavefront) for occupancy.

```hlsl
// particle_update.compute  — integrate N particles on the GPU.
RWStructuredBuffer<Particle> Particles;
cbuffer Params { float dt; float3 gravity; uint count; };

[numthreads(64,1,1)]
void CSMain(uint3 id : SV_DispatchThreadID) {
    if (id.x >= count) return;                  // guard the tail
    Particle p = Particles[id.x];
    p.vel += gravity * dt;
    p.pos += p.vel * dt;
    p.life -= dt;
    Particles[id.x] = p;
}
// CPU: dispatch( ceil(count/64), 1, 1 ); then draw via DrawProceduralIndirect.
```

GPU particles scale to millions because update + render never round-trip to the CPU. The indirect draw args buffer can be written by the same or a follow-up compute pass.

### 7. Order the post-processing chain correctly

Order matters. A typical chain:

```text
SceneColor(HDR) -> [SSAO mult] -> Bloom(threshold->downsample->blur->upsample add)
                -> Tonemap(ACES) -> Color grade(LUT) -> [DOF, MotionBlur]
                -> Chromatic aberration -> Vignette -> Output(LDR, gamma)
```

**Rules:**
- Do bloom and DOF in **HDR linear, before tonemapping**. Bloom thresholds on HDR values; tonemapping compresses them.
- Do color grading (LUT) typically **after tonemapping** so the LUT operates on display-referred values.
- Each pass is a full-screen triangle (or quad) sampling the previous render target.
- SSAO multiplies ambient occlusion into the HDR scene color before lighting or as a screen-space multiply.

### 8. Choose CPU vs GPU particles

- **CPU particles**: Flexible per-particle gameplay (collision callbacks, small counts, per-particle logic). Good for gameplay-critical effects.
- **GPU particles**: Huge counts (millions), simulation in compute, indirect draw, no gameplay feedback. Good for ambient/environmental effects.
- **Soft particles**: Fade near opaque geometry by comparing particle depth to scene depth (kills hard intersection lines). Sample the depth buffer in the fragment shader and fade alpha based on the difference.
- **VAT (vertex animation textures)**: Bake mesh/crowd animation into a texture sampled in the vertex shader. Animate thousands of instances with zero skinning cost. The vertex shader reads the animation frame from a texture using UVs derived from time and vertex ID.

### 9. Debug a misbehaving shader

1. **Output intermediates as color.** Visualize `N * 0.5 + 0.5` to verify normals, output UVs as `float4(uv, 0, 1)` to verify coordinates.
2. **Confirm the coordinate space.** Lighting math must share one space (typically world or view). A light direction in object space applied to a world-space normal produces garbage.
3. **Check texture bindings.** An unbound texture reads as black (or default). Use RenderDoc/PIX to inspect the actual bound resources at the draw call.
4. **Sanitize against NaNs.** Use `max(x, 1e-5)` before `pow`, `normalize`, or `divide`. One NaN can propagate through bloom and blow out the screen.
5. **Capture in RenderDoc.** Before guessing, capture the frame, find the draw call, and inspect vertex output, bound textures, and render target state.

## Best Practices

1. **Work in linear color, tonemap last.** Convert sRGB on read; apply gamma only at output.
2. **Mind your spaces.** Be explicit about object/world/view/clip/tangent space; document in comments which space a variable is in. Lighting math must share one space.
3. **Avoid divergent dynamic branches in hot pixels.** Prefer `step/lerp/smoothstep` over `if`; divergent branches kill warp/wavefront efficiency.
4. **Tame shader variants.** Every `#pragma multi_compile`/keyword multiplies compile time and memory. Strip unused permutations in the build.
5. **Guard compute tails** (`if (id >= count) return;`) and pick group sizes that are multiples of 32/64.
6. **Reduce overdraw** for transparents/particles (atlas, soft particles, smaller quads); it is usually fill-rate, not vertex, bound.
7. **Capture in RenderDoc** to inspect inputs/outputs of a misbehaving pass before guessing.
8. **Protect against NaNs** (`max(x, 1e-5)` before `pow/normalize/divide`); one NaN can blow out bloom across the screen.

## Examples

### Engine mappings

```text
Unity:   ShaderLab + HLSL (URP/HDRP), Shader Graph, ComputeShader + Graphics.Dispatch,
         VFX Graph (GPU particles) and Shuriken (CPU), custom Renderer Features for passes,
         post via Volume framework.
Unreal:  Material Editor (node graph) + Custom HLSL nodes, Niagara (GPU/CPU particles,
         data interfaces), post-process materials, custom render passes via plugins.
Godot 4: Godot shading language (GLSL-like) spatial/canvas/particle shaders, GPUParticles
         + process shaders, Environment/CompositorEffect for post, RenderingDevice compute.
```

### Debugging scenarios

**Scenario: "My shader output is solid black."**
- **Cause:** Usually unlit/wrong space/zero light, or sampling an unbound texture.
- **Fix:** Output `N*0.5+0.5` and UVs as color to verify inputs. Confirm light direction and ensure linear/sRGB on samples. RenderDoc the pass to see the actual bound resources.

**Scenario: "Bloom flickers and over-blooms randomly."**
- **Cause:** NaN/Inf in HDR scene color feeding the bright-pass threshold.
- **Fix:** Clamp/sanitize scene color (`max` with small epsilon, reject NaN) before threshold. Verify exposure/tonemap order — bloom must run in HDR pre-tonemap.

**Scenario: "Compute shader produces garbage on some threads."**
- **Cause:** Missing tail guard or race condition on shared buffer.
- **Fix:** Add `if (id.x >= count) return;` at the top of CSMain. If using atomics or shared memory, verify group sync barriers (`GroupMemoryBarrierWithGroupSync()`).

## Pitfalls

- **Linear vs sRGB mismatch**: Forgetting to convert sRGB textures to linear on read, or applying gamma twice. This is the #1 cause of "too dark" or "washed out" output.
- **Wrong coordinate space for lighting**: Light direction in world space, normal in object space (or vice versa). Always pick one space and transform everything into it.
- **NaN propagation**: A single NaN pixel in HDR scene color can spread through bloom's blur passes and contaminate the entire screen. Always sanitize inputs to `pow`, `normalize`, and division.
- **Shader variant explosion**: Each `multi_compile` keyword doubles (or more) the number of shader permutations. Compile times and memory balloon. Strip unused keywords in production builds.
- **Unguarded compute tail**: Without `if (id.x >= count) return;`, threads past the end of the buffer read/write garbage memory or crash.
- **Post-process order errors**: Running bloom after tonemapping (in LDR) produces flat, unconvincing glow. Running color grading before tonemapping produces unexpected hue shifts.
- **Overdraw on transparents/particles**: Transparent materials and particle quads can generate massive overdraw. Use soft particles, texture atlasing, and tight quad sizing to reduce fill-rate pressure.
- **Dynamic branches in fragment shaders**: `if` statements with divergent branches across a warp/wavefront serialize execution. Use `step/lerp/smoothstep` for branchless alternatives.
- **G-buffer layout constraints in deferred**: Adding a new material property requires extending the G-buffer, which costs bandwidth and may exceed MRT limits on mobile.

## Verification

- [ ] Lighting math is done in a single, explicit coordinate space; spaces are documented in the shader comments.
- [ ] Color is processed in linear space; sRGB textures are converted on read and gamma applied only at output.
- [ ] Tonemapping (e.g., ACES) happens before LDR color grading; bloom/DOF run in HDR pre-tonemap.
- [ ] Forward vs deferred is chosen to fit the light count, transparency needs, and target hardware.
- [ ] Hot pixel shaders avoid divergent dynamic branches (use `step/lerp/smoothstep`) and guard against NaNs with `max(x, 1e-5)`.
- [ ] Compute dispatches guard the tail thread (`if (id >= count) return;`) and use group sizes that are multiples of 32/64.
- [ ] GPU particles update in compute and draw via indirect draw without CPU round-trips.
- [ ] Transparent/particle passes minimize overdraw (soft particles, atlasing, tight quads).
- [ ] Shader variant/keyword permutations are pruned to control compile time and memory.
- [ ] A misbehaving pass is captured in RenderDoc/PIX and its bound inputs/outputs verified before code changes.
- [ ] Post-process chain order is correct: SSAO → bloom → tonemap → color grade → DOF/motion blur → CA/vignette → output.

## Related Skills

- **performance-profiling** — RenderDoc/PIX capture, draw-call batching, overdraw and GPU-bottleneck analysis.
- **runtime-animation** — Skeletal animation that this skill can complement with VAT/crowd shading.
- **blender-asset-pipeline** — Authors the meshes, UVs, and textures shaders consume.
- **custom-physics-solvers** — Math (vectors, integration) reused in compute-shader simulations.

### External Resources

- "Real-Time Rendering" (Akenine-Möller et al.) — pipeline, BRDFs, shadows.
- LearnOpenGL / The Book of Shaders — GLSL fundamentals and techniques.
- Filament PBR documentation; ACES tonemapping references; RenderDoc docs.
