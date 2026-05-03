---
name: rdc-analyst
description: >-
  Analyze GPU captures and frame data from RenderDoc (.rdc files), PIX, or
  similar frame debuggers. Reconstructs render pass graphs, resource dependency
  chains, material/shader bindings, and pipeline state for a captured frame.
  Use when the user wants to understand how a frame is rendered, map out render
  passes and their resource dependencies, extract draw-call structure, identify
  redundant state changes, infer engine material or shader architecture, or
  build reusable render knowledge entries — rather than debugging a specific
  visual defect or crash.
---

# RDC Analyst

Analyze GPU frame captures to reconstruct render pass graphs, resource flows, and engine structure. This skill handles analysis and knowledge-building requests; for defect debugging, use the debugger framework instead.

## Workflow

### Step 1: Identify the Input

Determine what capture data is available:

| Input Type | Examples | Action |
|------------|----------|--------|
| RenderDoc capture | `.rdc` file, texture/buffer viewer output | Proceed with pass-level analysis |
| Frame debugger log | PIX capture, Xcode GPU trace, NVIDIA Nsight export | Proceed — normalize to pass/draw-call model |
| Engine replay data | Unreal Insights, Unity Frame Debugger dump | Proceed — map to render pass abstraction |
| Text description only | "We have 3 passes: shadow, gbuffer, lighting" | Proceed with user-provided structure |
| No capture available | User has no data yet | Help user plan what to capture and with which tool |

### Step 2: Clarify the Analysis Goal

Ask the user to confirm what they need. If unclear, ask explicitly:

1. **What is the capture or input?** (file type, engine, API — D3D12, Vulkan, Metal, etc.)
2. **What analysis product do you need?**
   - Pass graph (render pass sequence with dependencies)
   - Resource dependency chain (which textures/buffers flow between passes)
   - Material/shader structure map (bindings, permutations, parameter sources)
   - Pipeline state summary (blend modes, rasterizer config per draw)
   - Knowledge entry (reusable reference doc for this rendering technique)
3. **What scope?** Full frame, a specific pass range, or a single draw call?

### Step 3: Perform the Analysis

Follow the appropriate path based on the requested product:

**Pass graph reconstruction:**
1. List all render passes in execution order
2. For each pass, record: name/label, render targets, input resources, draw count
3. Identify dependencies (pass B reads a resource written by pass A)
4. Output as a structured table or diagram description

**Resource dependency chain:**
1. Enumerate key resources (render targets, depth buffers, UAVs)
2. Track producer and consumer passes for each resource
3. Flag resources that are written but never read (potential waste)

**Material/shader analysis:**
1. Group draw calls by pipeline state object or shader combination
2. Identify material parameter sources (constant buffers, push constants)
3. Note shader permutation patterns and binding slot conventions

**Knowledge entry:**
1. Synthesize findings into a reusable reference document
2. Include: technique name, pass sequence, resource flow, shader roles, key parameters
3. Format for storage in `analyzer/common/` as a knowledge artifact

### Step 4: Validate and Deliver

Before delivering results:
- [ ] Every claim references a specific pass, draw call, or resource by name/index
- [ ] Dependencies are directional (producer -> consumer) and acyclic where expected
- [ ] Output format matches what the user requested
- [ ] Scope matches what was agreed in Step 2

## Routing Table

| User Says | Route To |
|-----------|----------|
| "Why is this triangle wrong" / "rendering bug" / "visual glitch" | **Debugger** — this is a defect, not analysis |
| "Map out the render passes" / "show me the pass graph" | **This skill** — pass graph reconstruction |
| "What resources does the shadow pass use" | **This skill** — resource dependency chain |
| "How does this engine set up materials" | **This skill** — material/shader analysis |
| "Document this rendering technique" | **This skill** — knowledge entry |

## Example

**User:** "I have a RenderDoc capture of our deferred renderer. Can you map out the pass structure and resource flow?"

**Intake response:**
> To map the pass structure, I need to confirm:
> 1. **API**: Which graphics API — D3D12, Vulkan, or Metal?
> 2. **Scope**: Full frame, or a specific section (e.g., just the lighting passes)?
> 3. **Output**: Pass graph with resource dependencies, or also material/shader breakdown?
>
> Once confirmed, I will reconstruct the pass sequence, identify render targets and input resources per pass, and produce a dependency table showing resource flow across passes.

**After intake — sample output structure:**

| Pass | Render Targets | Input Resources | Draw Calls |
|------|---------------|-----------------|------------|
| Shadow Depth | ShadowMap (D32) | — | 142 |
| GBuffer | Albedo, Normal, Depth | — | 387 |
| SSAO | AO (R8) | Depth, Normal | 1 |
| Lighting | HDR Color | Albedo, Normal, Depth, AO, ShadowMap | 1 |
| Tonemap | Backbuffer | HDR Color | 1 |

## Current Scope

This skill is part of the incubating `analyzer` framework. It provides the full intake-and-analysis workflow described above. Analysis artifacts are stored under `analyzer/common/`. As the framework matures, additional automation (template hooks, runtime contracts) will be added.
