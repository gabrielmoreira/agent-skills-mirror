---
name: game-performance-profiling
version: 1.1.1
description: "Use when a game drops frames, stutters, or must hit a frame budget — engine-agnostic profiling and optimization: CPU-vs-GPU bottleneck diagnosis, millisecond frame budgets, draw-call batching/instancing, overdraw and fill rate, LOD and culling, GC-free code and object pooling, memory layout (AoS vs SoA, cache misses), job/worker systems, and capture tools (Unity Profiler, Unreal Insights/stat, RenderDoc, PIX, Tracy, Superluminal). Triggers on profiling, frame budget, bottleneck, CPU bound, GPU bound, draw calls, batching, instancing, overdraw, fill rate, LOD, culling, object pooling, garbage collection, cache miss, SoA, job system, RenderDoc, Tracy. Not for Godot-editor profiling workflow (use game-godot-performance-optimization), Godot debugger/breakpoint diagnostics (use game-godot-debugging-profiling), authoring shaders/VFX (use technical-art-vfx), or server tick and bandwidth budgets (use game-multiplayer-netcode)."
risk: safe
source: opus
date_added: 2026-06-27
---

# Game Performance Profiling & Optimization

You cannot optimize what you have not measured. Profile first, find the one bottleneck that actually gates the frame, fix it, then measure again — guessing wastes days on code that was never the problem.

## When to Use

Activate when the task involves:

- A game that **drops frames, stutters, hitches, or misses a target framerate** (30 / 60 / 120 / VR 90).
- Deciding whether the frame is **CPU-bound or GPU-bound** and which stage is the bottleneck.
- Cutting **draw calls** via batching, instancing, atlasing, or material merging.
- Diagnosing **overdraw / fill-rate** limits (transparents, particles, full-screen effects).
- Adding **LOD, occlusion/frustum culling, or HLOD** to reduce what's drawn.
- Removing **garbage-collection spikes** and per-frame allocations; adding **object pooling**.
- Improving **memory layout** (AoS→SoA, cache locality) and moving work to **job/worker threads**.
- Reading a **capture** from Unity Profiler, Unreal Insights/`stat`, RenderDoc, PIX, Tracy, or Superluminal.

**Trigger keywords:** profiling, frame budget, frame time, bottleneck, CPU bound, GPU bound, draw calls, set-pass calls, batching, GPU instancing, overdraw, fill rate, LOD, frustum/occlusion culling, object pool, garbage collection, GC alloc, cache miss, SoA/AoS, job system, RenderDoc, PIX, Unreal Insights, Tracy, Superluminal, stat unit.

### Do NOT use for

- **Godot-editor profiling workflow** (Godot Profiler UI, monitors, orphan nodes, `VisibleOnScreenNotifier`) — use `game-godot-performance-optimization`. This skill owns the cross-engine theory and native capture tools; defer to the Godot skill for editor-specific steps.
- **Godot debugger diagnostics** (breakpoints, `push_error`/`assert`, remote debug, stack traces) — use `game-godot-debugging-profiling`; this skill profiles cost, not correctness.
- **Authoring the shading/effects themselves** (writing the shader, building the post chain) — use `technical-art-vfx`. This skill *measures and reduces* the cost; that skill *creates* the look.
- **Asset creation** (mesh decimation source art, UV/lightmap layout, texture authoring) — see `game-blender-asset-pipeline`; this skill decides the LOD budgets and flags the offenders.
- **Algorithmic correctness / data-structure design in the abstract** — this skill is about runtime frame cost, not Big-O homework.
- **Server tick CPU and per-client bandwidth budgeting** for networked play — owned by `game-multiplayer-netcode` (this skill profiles the local frame).

## Prerequisites

- **Target hardware access.** Profiling on a dev workstation hides console/mobile stalls. Reproduce on the actual target device before optimizing.
- **A profiler or capture tool installed.** At minimum one of: Unity Profiler, Unreal Insights, RenderDoc, PIX, Tracy, or Superluminal.
- **A reproducible scenario.** A deterministic or semi-deterministic gameplay sequence you can replay for before/after captures.
- **Windows host (PowerShell) is primary.** Path notes assume Windows where applicable. Cross-engine capture tools (RenderDoc, PIX, Tracy, Superluminal) run on Windows.

## Procedure

### Step 1 — Measure → fix one thing → measure again

1. **Reproduce on the target hardware** (NOT the dev workstation — a fast PC hides console/mobile stalls).
2. **Capture a profile.** Read the timeline, not averages — chase the spikes and the long pole.
3. **Find THE bottleneck** (one stage gates the frame). Form a hypothesis.
4. **Change one thing.** Re-capture. Confirm the number moved.
5. **Repeat** until in budget. Stop when you hit budget — don't gold-plate.

Optimizing without a before/after capture is how you "speed up" code that wasn't the bottleneck.

### Step 2 — Find the bottleneck: CPU vs GPU

The frame is `max(CPU_time, GPU_time)` — they overlap. If GPU time ≫ CPU, you're **GPU-bound**; lowering CPU work does nothing.

1. **GPU-bound test:** drop resolution by half. If frame time falls a lot → fill/GPU bound. If unchanged → CPU bound.
2. **CPU-bound test:** the GPU sits idle waiting on the CPU to submit; the render thread or main thread is the long pole.
3. **Split CPU further:** main thread (gameplay/scripts), render thread (draw submission), worker/job threads (jobs), GC.

```text
Unity:  Profiler → CPU Usage vs GPU module; Unreal: `stat unit` (Frame/Game/Draw/GPU ms).
If Draw (render thread) is high → too many draw calls / state changes (CPU-side).
If GPU is high → fill rate, shader cost, or vertex/overdraw (GPU-side).
```

### Step 3 — Frame budget: think in milliseconds, not FPS

FPS is non-linear; **milliseconds add up**. Budget per subsystem against the target.

| Target | Frame budget | Typical split (game / render / GPU) |
|---|---|---|
| 30 fps | 33.3 ms | ~16 / ~6 / ≤33 |
| 60 fps | 16.6 ms | ~8 / ~4 / ≤16 |
| 90 fps (VR) | 11.1 ms | ~5 / ~3 / ≤11 |
| 120 fps | 8.3 ms | tight; instancing + jobs mandatory |

Going 60→120 fps means **halving** total time, not "a bit faster." Always reason in ms.

### Step 4 — Draw calls: batch, instance, atlas

Each draw call + state/material change costs CPU on the render thread. Reduce **set-pass/state changes** first, then call count.

1. **Static batching:** merge static meshes sharing a material into one buffer.
2. **GPU instancing:** one mesh, many transforms in a single call (foliage, crowds, bullets).
3. **Texture atlasing / material merging:** fewer materials → fewer state changes → auto-batchable.
4. **Dynamic batching** (small meshes) helps on CPU but has its own cost — measure it.

```csharp
// Unity: draw 1023 instances of one mesh in a single GPU-instanced call.
Matrix4x4[] xforms = BuildTransforms();          // up to 1023 per batch
Graphics.DrawMeshInstanced(mesh, 0, instancedMat, xforms);
// vs. 1023 GameObjects = 1023 draw calls + culling + transform overhead.
```

### Step 5 — Overdraw & fill rate (GPU)

Fill-rate bound = the GPU shades the same pixels many times. Worst offenders: stacked **transparents**, **particles**, and **full-screen post**.

1. Render opaque **front-to-back** so the depth test rejects hidden pixels early; use a **depth prepass** for expensive shading.
2. Shrink particle quads, use **soft particles** and atlases, cap transparent layers.
3. Do heavy post at lower resolution where acceptable; combine passes.

### Step 6 — LOD & culling: draw less

1. **Frustum culling:** skip what's off-screen (engine default; keep bounds tight).
2. **Occlusion culling:** skip what's hidden behind other geometry.
3. **LOD / HLOD:** swap to cheaper meshes/shaders with distance; merge distant clusters.
4. **Distance/cadence culling:** disable far-away tick, animation, and VFX entirely.

### Step 7 — Kill allocations & GC spikes; pool instead

Managed allocations in the hot path trigger **GC stalls** (frame hitches). Allocate up front, reuse, and never `new` per frame.

```csharp
// Object pool: reuse instead of Instantiate/Destroy (which allocs + triggers GC).
public class Pool<T> where T : Component {
    readonly Stack<T> _free = new();
    readonly T _prefab; readonly Transform _root;
    public Pool(T prefab, Transform root, int warm) {
        _prefab = prefab; _root = root;
        for (int i = 0; i < warm; i++) _free.Push(Make());
    }
    T Make() { var t = Object.Instantiate(_prefab, _root); t.gameObject.SetActive(false); return t; }
    public T Get() { var t = _free.Count > 0 ? _free.Pop() : Make(); t.gameObject.SetActive(true); return t; }
    public void Release(T t) { t.gameObject.SetActive(false); _free.Push(t); }
}
```

GC-free habits: avoid LINQ/closures/boxing in `Update`; cache arrays and `StringBuilder`; don't concatenate strings per frame; reuse collections (`list.Clear()` not `new List`).

### Step 8 — Memory layout & jobs (data-oriented)

1. **Cache misses dominate** tight loops. Prefer **SoA** (`float x[N], y[N]`) over **AoS** (`struct{ x,y,z,...}[N]`) when you iterate one field over many entities — you load only what you touch.
2. Keep hot data **contiguous and small**; chasing pointers/components thrashes cache.
3. **Job/worker systems** (Unity DOTS/Burst, Unreal `ParallelFor`/Tasks) spread embarrassingly-parallel work across cores; design for no shared mutable state.

### Engine-specific capture commands

```text
Unity:   Profiler (CPU/GPU/Memory/Rendering modules), Frame Debugger (draw-call breakdown),
         Memory Profiler, Profile Analyzer; DOTS/Burst + Job System; GPU Instancing,
         SRP Batcher, static/dynamic batching, LOD Group, Occlusion Culling.
Unreal:  Unreal Insights (Timing/Memory/Networking), `stat unit` / `stat scenerendering` /
         `stat gpu`, GPU Visualizer (ProfileGPU), `r.ScreenPercentage`, Significance Manager,
         Nanite/HLOD/LOD, draw-call merging, ISMC/HISM instancing.
Godot 4: built-in Profiler + Frame profiler, monitors (draw calls, video mem), MultiMesh
         for instancing, Occlusion culling, VisibilityRange LOD, RenderingServer stats.
Cross:   RenderDoc / PIX (GPU frame capture), Tracy & Superluminal (CPU sampling/timeline).
```

## Examples

**Stutter every couple of seconds, FPS otherwise fine:**
- **Cause:** periodic GC collection from per-frame managed allocations.
- **Fix:** profile allocations (Unity: GC Alloc column / Profiler markers), remove per-frame `new`/LINQ/boxing, pool spawned objects, reuse buffers; confirm the spike is gone.

**Lowering script cost didn't improve frame time at all:**
- **Cause:** the frame is GPU-bound, so CPU savings are hidden behind GPU time.
- **Fix:** half the resolution to confirm GPU/fill bound; then attack overdraw, shader cost, and draw calls instead of CPU logic.

## Pitfalls

1. **Optimizing without a before/after capture.** "Speeding up" code that was never the bottleneck wastes days. Always capture, change one thing, re-capture.
2. **Profiling on the dev workstation.** A fast PC hides console/mobile stalls. Reproduce on target hardware.
3. **Reading averages instead of the timeline.** Averages hide the spikes that cause perceived stutter. Watch the 1% low / frame-time graph.
4. **Optimizing the idle side.** If GPU-bound, CPU savings are invisible. Run the half-resolution test first.
5. **Per-frame allocations in hot paths.** LINQ, closures, boxing, string concatenation, and `new` in `Update` trigger GC stalls. Zero allocations in hot paths.
6. **Ignoring set-pass/state changes.** Reducing draw call count without reducing material/state changes may not help — state changes are the expensive part.
7. **Dynamic batching without measuring.** Dynamic batching has its own CPU cost; for larger meshes it can be a net loss.
8. **Transparent/particle overdraw.** Stacked transparents and full-screen post shade the same pixels many times. Render opaque front-to-back; cap transparent layers.
9. **Loose bounds on frustum culling.** Oversized bounding volumes cause the engine to draw off-screen objects. Keep bounds tight.
10. **Gold-plating past budget.** Stop when you hit the frame budget. The second-worst bottleneck is irrelevant until the worst is gone.

## Verification

- [ ] A before/after capture exists on **target hardware**; changes are validated by a measured delta, not by feel.
- [ ] The frame is classified CPU-bound vs GPU-bound (e.g. half-resolution test) before optimizing.
- [ ] Budgets are expressed in milliseconds per subsystem against the target framerate.
- [ ] Draw calls / set-pass changes are reduced via instancing, atlasing, or material merging.
- [ ] Overdraw on transparents/particles/post is bounded; opaque draws front-to-back (depth prepass where needed).
- [ ] Frustum + occlusion culling and distance LOD are in place; off-screen/distant work is skipped.
- [ ] Hot paths perform zero managed allocations; spawned objects are pooled and buffers reused.
- [ ] GC/stall spikes are eliminated (no per-frame LINQ/closures/boxing/string concat).
- [ ] Tight per-entity loops use cache-friendly layout (SoA) and parallel jobs where applicable.
- [ ] Frame-time graph / 1% lows are checked for smoothness, not just average FPS.
- [ ] A GPU capture (RenderDoc/PIX) confirms the costly pass before guessing at GPU fixes.

## Related skills

- **technical-art-vfx** — Authors the shaders/post this skill measures and budgets; overdraw and variant cost originate there.
- **game-multiplayer-netcode** — Owns server tick CPU and bandwidth budgets; this skill profiles the local client frame.
- **game-blender-asset-pipeline** — Produces the LOD meshes, atlases, and decimated geometry that draw-call/overdraw fixes rely on.
- **game-ai-behavior** — Time-slice and stagger perception/pathfinding flagged as main-thread spikes here.
- **game-godot-performance-optimization** — Godot-editor profiling workflow (Profiler UI, monitors, pooling in GDScript).
- **game-godot-debugging-profiling** — Godot debugger, breakpoints, and error-handling diagnostics.

### External resources

- Unity "Optimizing graphics performance" / "Understanding the managed heap"; DOTS Best Practices.
- Unreal Insights & `stat` command reference; "Profiling and Optimization" docs.
- RenderDoc and PIX documentation; Tracy and Superluminal profiler guides.
