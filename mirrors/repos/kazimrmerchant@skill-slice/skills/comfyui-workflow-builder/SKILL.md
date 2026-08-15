---
name: comfyui-workflow-builder
version: 1.3.1
description: >
  Use when generating, building, creating, designing, or repairing ComfyUI API-format workflow
  JSON from a natural-language description (txt2img, img2img, inpainting, ControlNet, LoRA stacking,
  upscaling, face detailing, FLUX, Wan I2V). Load when the user asks for a node graph, pipeline
  JSON, or runnable ComfyUI prompt that must use correct class_types, connection wires
  [nodeId, outputIndex], inventory-backed model filenames, and model-native resolutions.
  Do not use for ComfyUI install/server setup, custom node development, Python scripting,
  model training, GPU buying advice, or pure architectural explanations of diffusion.
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

# ComfyUI Workflow Builder

Turn a plain-language request — *"an SDXL portrait with two LoRAs and a depth ControlNet"* — into **ComfyUI API-format** workflow JSON that loads and runs on the first submit.

A graph only runs if **every** `class_type` is installed, **every** model filename exists on disk, and **every** connection reads an output slot that exists on its source node. Get any one wrong and ComfyUI rejects the prompt before a single pixel is rendered.

**Guiding principle:** validate against the machine's real inventory before you hand anything over. Never emit a node, model, or wire the target cannot honor.

---

## When to Use

Load this skill when the user wants **workflow authoring**, not teaching or ops.

**Trigger signals:**

- Build / generate / create / design a ComfyUI workflow
- API-format or loadable node-graph JSON
- Pipeline from prompt → image/video
- Specific techniques as a graph: LoRAs stacked, ControlNet, inpainting, img2img, upscale, FaceDetailer/ADetailer
- Multi-stage wiring: "FLUX.1 generation → upscale → face detail"
- User pastes a broken workflow and asks to fix connections, indices, or model names

**Positive trigger examples:**

- "I need a txt2img workflow with two LoRAs stacked"
- "Generate a ComfyUI workflow for inpainting with SDXL"
- "Set up a workflow from text prompt to final image using Juggernaut XL"
- "img2img pipeline with SD 1.5"
- "Upscale after generation in ComfyUI"
- "Wire a face-detailing workflow"
- "Wan 2.1 image-to-video, 4-second gentle pan"

**Do NOT use for:**

- ComfyUI install, server start, port/firewall, hardware shopping
- Custom node development or Python node packages
- Model training / LoRA fine-tuning loops
- "How does latent diffusion work?" math/architecture lessons
- Convert A1111/Forge UI to raw Python automation (unless user explicitly wants API glue)
- Pure Midjourney vs SD quality debate

---

## Prerequisites

### Inventory (portable — this folder does not ship `state/inventory.json`)

Do **not** assume a machine file `state/inventory.json`. Build an inventory from one of:

1. **User-named files** — checkpoints, LoRAs, ControlNets they actually have. Invent nothing.
2. **Live ComfyUI** (if a server is running) — `GET http://127.0.0.1:8188/object_info` for installed `class_type`s; ask the user (or list their models dir) for filenames.
3. **Optional local JSON** — if the user *provides* an inventory object, use it. Shape:

```json
{
  "vramGb": 24,
  "nodes": ["CheckpointLoaderSimple", "CLIPTextEncode", "EmptyLatentImage", "KSampler", "VAEDecode", "SaveImage"],
  "models": [
    { "filename": "example.safetensors", "kind": "checkpoint", "baseModel": "sdxl" }
  ]
}
```

Mark every graph **unvalidated** until filenames and `class_type`s are confirmed. Output-index, architecture, sampler, and strength tables live **in this SKILL.md** (Step 3–4). This skill does not ship a `references/` pack.

Official API format: [docs.comfy.org — workflow API format](https://docs.comfy.org/development/api-development/workflow-api-format). Wires are `[sourceNodeId, outputIndex]`.

### Eval assets

This skill ships evaluation assets under `eval/`:

| Path | Role |
|------|------|
| `eval/EVAL.md` | What "good" looks like; benchmark strategy; sandbox notes |
| `eval/test-cases.yaml` | Capability cases (SDXL, indices, LoRA chain, ControlNet, SD1.5, FLUX, Wan) |
| `eval/trigger-tests.yaml` | should_trigger / should_not_trigger phrases |
| `eval/benchmark.yaml` | Benchmark configuration |
| `eval/run-eval.sh` | Eval runner |
| `eval/results/` | Eval outputs (typically gitignored) |

Run evals from the skill root:

```bash
bash eval/run-eval.sh
bash eval/run-eval.sh --skill-only
bash eval/run-eval.sh --case TC-001
```

---

## Procedure

### Step 1 — Parse the request

Extract decisions that **change which nodes exist**:

| Decision | Options | Graph impact |
|----------|---------|--------------|
| **Output type** | image / video / audio | Entire backbone (SaveImage vs VHS_VideoCombine, etc.) |
| **Source material** | text-only / reference image(s) / video | Whether `LoadImage` / `VAEEncode` / vision encoders appear |
| **Base architecture** | sd15 / sdxl / flux / wan / svd | Loader family, resolution, CFG rules |
| **Identity method** | none / LoRA / PuLID / InstantID / IP-Adapter-FaceID | Mutually exclusive families — pick one early |
| **Quality level** | draft / production | Steps, upscaler, FaceDetailer on/off |
| **Specials** | ControlNet type, inpaint, lip-sync, sampler preference | Known sub-graphs |

If architecture is ambiguous ("portrait of X"), **do not guess** — resolve from inventory in Step 2 (prefer the strongest installed base that matches any named LoRA/ControlNet).

### Step 2 — Read the inventory

Collect the portable inventory (user names, `/object_info`, or a JSON they supplied). Answer these before emitting a single node:

1. **Which checkpoint / UNET matches intent?** Prefer real filenames over invented "best" names.
2. **Which identity stacks exist?** No PuLID model → do not emit PuLID nodes.
3. **Which ControlNets exist?** Enable depth/pose/canny only when a matching file is listed.
4. **Which custom nodes are installed?** Impact Pack, VideoHelperSuite, IP-Adapter, PuLID live outside core ComfyUI.
5. **What is `vramGb`?** Caps resolution, batch, ControlNet count, and whether FaceDetailer + upscale can chain.

### Step 3 — Choose a pipeline pattern

Map intent + inventory onto a **known-good backbone**. Pattern-first is faster and less error-prone than free-form assembly.

| Pattern | When | Backbone (→ = output feeds input) |
|---------|------|-----------------------------------|
| Text-to-image (SD/SDXL) | Plain prompt, no ref image | `CheckpointLoaderSimple` → `CLIPTextEncode`×2 → `EmptyLatentImage` → `KSampler` → `VAEDecode` → `SaveImage` |
| Text-to-image (FLUX) | FLUX.1-dev style fidelity | `UNETLoader` + `DualCLIPLoader` + `VAELoader` → encode → `FluxGuidance` → `KSampler` (cfg 1.0) → decode → save |
| Image-to-image | Edit existing image | `LoadImage` → `VAEEncode` → `KSampler` (denoise 0.35–0.75) → decode |
| Inpainting | Masked region only | `LoadImage` + mask → `VAEEncodeForInpaint` → `KSampler` (low-mid denoise) → decode |
| LoRA character / style | Trained concept | `LoraLoader`×N, MODEL+CLIP chained through each |
| ControlNet | Pose / depth / canny structure | `ControlNetLoader` → `ControlNetApplyAdvanced` on **conditioning**, not latent |
| Identity-preserved | Specific face | PuLID / InstantID / IP-Adapter-FaceID (+ optional `FaceDetailer`) |
| Upscale | More resolution | `IMAGE` → `UltimateSDUpscale` / `ImageUpscaleWithModel` → `SaveImage` |
| Image-to-video (Wan / SVD) | Highest-quality motion | `UNETLoader` → `WanImageToVideo` / `SVD_img2vid_Conditioning` → `KSampler` → decode → `VHS_VideoCombine` |
| Image-to-video (AnimateDiff) | Fast motion on SD1.5/SDXL | `ADE_AnimateDiffLoaderGen1` + motion LoRA + context options |
| Talking head | Speaking character | image → video → voice → lip-sync (`LivePortrait` / `SadTalker`) |

### Step 4 — Emit the workflow JSON

ComfyUI API format is a **flat object**: keys are unique node IDs, values are nodes.

#### Type schema

```typescript
/** A wire to another node's output slot: [sourceNodeId, outputIndex]. */
export type NodeConnection = readonly [nodeId: string, outputIndex: number];

/** A node input is either a literal value or a wire to another node's output. */
export type NodeInputValue = string | number | boolean | NodeConnection;

/** One node in the graph. `class_type` is the registered ComfyUI node name. */
export interface WorkflowNode {
  readonly class_type: string;
  readonly inputs: Readonly<Record<string, NodeInputValue>>;
}

/** The whole workflow: unique node id -> node. */
export type ComfyWorkflow = Readonly<Record<string, WorkflowNode>>;
```

#### Emission rules (non-negotiable)

| Rule | Why it matters |
|------|----------------|
| Node IDs are unique string keys | Duplicate keys silently overwrite; part of the graph vanishes |
| Connected inputs are `[sourceId, index]` arrays | Bare strings are treated as literals |
| `outputIndex` is 0-based and in range for the **source** type | Most common silent failure |
| Filenames match inventory exactly | No fuzzy match; casing/extension matter |
| Seeds are large integers | State random vs fixed so the user knows reproducibility |
| Prefer `KSampler` / `KSamplerAdvanced` | Older sampler nodes drift out of support |

Stable ID styles: sequential (`"1"`...`"12"`) or semantic (`"ckpt"`, `"pos"`, `"neg"`, `"samp"`). Pick one style per graph; do not mix without reason.

#### Architecture defaults

| Base | Loaders | Native size | Typical steps | CFG / guidance | Notes |
|------|---------|-------------|---------------|----------------|-------|
| SD 1.5 | `CheckpointLoaderSimple` | 512×512 (multiples of 64) | 20–30 | cfg 5–8 | Many AnimateDiff / older ControlNets |
| SDXL | `CheckpointLoaderSimple` | 1024×1024 | 25–35 | cfg 5–7.5 | Do **not** use 512 as primary latent |
| FLUX.1 | `UNETLoader` + `DualCLIPLoader` + `VAELoader` | 1024×1024 | 20–28 | **FluxGuidance ~3.5**, sampler **cfg 1.0** | Never `CheckpointLoaderSimple` for split FLUX weights |
| Wan 2.1 I2V | UNET + CLIP(type wan) + VAE + CLIP Vision | 832×480 (480p) | ~30 | cfg ~6, `uni_pc` / simple | Frame `length` drives duration |
| SVD | SVD conditioning nodes | ~576 height class | model-specific | model-specific | Verify nodes in inventory |

#### Sampler and scheduler defaults (safe picks)

Prefer well-supported names that core ComfyUI ships. Do not invent exotic sampler strings.

| Base | `sampler_name` | `scheduler` | Notes |
|------|----------------|-------------|-------|
| SD 1.5 / SDXL general | `dpmpp_2m_sde` or `dpmpp_2m` | `karras` | Reliable quality/speed tradeoff |
| SDXL when user wants smoother | `euler_ancestral` | `normal` | More variation; less "locked" |
| FLUX.1 | `euler` | `simple` | Pair with `FluxGuidance` + cfg `1.0` |
| Wan I2V | `uni_pc` | `simple` | Match common Wan recipes |

#### Strength and denoise ranges

| Parameter | Typical range | Guidance |
|-----------|---------------|----------|
| LoRA `strength_model` / `strength_clip` | 0.6–1.0 (style often 0.6–0.85; character 0.8–1.0) | Over 1.0 can overcook; under 0.4 may be invisible |
| ControlNet `strength` | 0.6–0.95 | 0.85 is a strong starting point for depth/pose |
| ControlNet `end_percent` | 0.7–1.0 | Ending early (e.g. 0.85) frees late steps for texture |
| Img2img `denoise` | 0.35–0.75 | Low = keep structure; high = rewrite |
| Inpaint `denoise` | 0.5–0.85 | Hole fill usually needs more change than light img2img |
| FaceDetailer `denoise` | 0.3–0.5 | Too high rewrites identity; too low does nothing |

#### KSampler required inputs (never leave dangling)

Every `KSampler` must have literals or wires for: `seed`, `steps`, `cfg`, `sampler_name`, `scheduler`, `denoise`, `model`, `positive`, `negative`, `latent_image`.

#### Output-index quick reference

| class_type | Outputs (index → type) |
|------------|-------------------------|
| `CheckpointLoaderSimple` | 0 MODEL, 1 CLIP, 2 VAE |
| `LoraLoader` | 0 MODEL, 1 CLIP |
| `CLIPTextEncode` | 0 CONDITIONING |
| `EmptyLatentImage` | 0 LATENT |
| `KSampler` / `KSamplerAdvanced` | 0 LATENT |
| `VAEDecode` | 0 IMAGE |
| `VAEEncode` / `VAEEncodeForInpaint` | 0 LATENT |
| `LoadImage` | 0 IMAGE, 1 MASK |
| `ControlNetLoader` | 0 CONTROL_NET |
| `ControlNetApplyAdvanced` | 0 positive CONDITIONING, 1 negative CONDITIONING |
| `UNETLoader` | 0 MODEL |
| `DualCLIPLoader` / `CLIPLoader` | 0 CLIP |
| `VAELoader` | 0 VAE |
| `CLIPVisionLoader` | 0 CLIP_VISION |
| `CLIPVisionEncode` | 0 CLIP_VISION_OUTPUT |
| `FluxGuidance` | 0 CONDITIONING |
| `WanImageToVideo` | 0 positive, 1 negative, 2 latent |
| `IPAdapterUnifiedLoader` | 0 MODEL, 1 IPADAPTER (typical) |
| `SaveImage` | (sink — no graph outputs) |

### Step 5 — Validate before delivery

Never present a graph you have only eyeballed. Missing nodes, bad indices, and phantom files are invisible in a quick read and fatal on submit.

Run generated JSON through a **strict, multi-issue** validator: shape first, then semantics. Report every problem in one pass.

**Validation checklist:**

1. **JSON validity** — parses cleanly. No trailing commas, no unquoted keys.
2. **Inventory match** — every `class_type` in `inventory.nodes`; every model filename in `inventory.models`.
3. **Connection audit** — every `["node_id", index]` points at a real node and a legal output index. `CheckpointLoaderSimple` → `[MODEL, CLIP, VAE]` = `[0, 1, 2]` is the usual offender.
4. **No dangling required inputs** — every required field is a literal or a wire.
5. **Live path for add-ons** — LoRAs chained into sampler/encoders; ControlNet outputs feed sampler conditionings.
6. **Architecture rules** — FLUX not on `CheckpointLoaderSimple`; SDXL not at 512 primary; SD1.5 not forced through SDXL-only nodes.
7. **Resolution + VRAM** — latent matches native training size; stack fits `vramGb`.
8. **Seed policy stated** — fixed for reproducibility or random for variety.

### Step 6 — Deliver

Save the validated workflow JSON to the appropriate path and provide a delivery header.

**Offline (file delivery):**

```powershell
# Windows PowerShell — save workflow to project folder
Set-Content -Path "projects\<project>\workflows\<descriptive>_v1.json" -Value $json
```

**Online (hand off to comfyui-api):**

Pass the validated JSON to the `comfyui-api` skill for queuing into a running ComfyUI instance.

**Delivery handoff template** (prose header, not comments inside JSON):

```text
Workflow: <pattern name>
Base: <filename + baseModel>
Add-ons: <LoRAs / ControlNet / identity / upscale or none>
Size: <WxH>, steps=<n>, cfg/guidance=<...>, seed=<fixed N | random>
VRAM profile: <vramGb> — <any reductions made>
Validation: inventory-checked | unvalidated (missing inventory)
Save as: projects/<project>/workflows/<descriptive>_vN.json
Next: queue via comfyui-api (online) or load in ComfyUI (offline)
```

---

## Decision tree (quick)

```
Is the output video?
  yes → Wan/SVD/AnimateDiff pattern (inventory decides which)
  no  → image path

Is there an init image?
  yes → img2img or inpaint (mask?)
  no  → txt2img

Which base is installed and intended?
  flux → split loaders + FluxGuidance
  sdxl → CheckpointLoaderSimple @ 1024
  sd15 → CheckpointLoaderSimple @ 512

Any LoRAs? → chain LoraLoader(s) on MODEL+CLIP
Any ControlNet? → apply on conditioning
Identity face lock? → one of PuLID / InstantID / IP-Adapter-FaceID
Production quality? → optional FaceDetailer / upscale if VRAM allows

Validate → deliver
```

---

## Repairing a broken workflow

When the user pastes a failing graph (API JSON or UI export):

1. **Normalize format** — If the payload has top-level `nodes` + `links` (UI format), convert to the flat API map (`id` → `{ class_type, inputs }`) before editing. Prefer re-emitting API format rather than half-editing UI format.
2. **Inventory gate** — List every `class_type` and every model-like string; mark missing installs.
3. **Index audit** — For each `[sourceId, i]`, confirm `sourceId` exists and `i` is legal for that source's `class_type` (use the output-index table).
4. **Live-path audit** — Confirm LoRA/ControlNet/IP-Adapter outputs actually reach `KSampler` / decode / save (no orphan loaders).
5. **Architecture audit** — FLUX split loaders + guidance; SDXL not at 512; matching `baseModel` across ckpt/LoRA/ControlNet.
6. **Minimal fix first** — Correct wires and filenames before redesigning the pipeline. Only rewrite the pattern if the architecture is fundamentally wrong.
7. **Re-validate** — Run the same checklist as greenfield generation; state what you changed.

### Common repair scenarios

| Symptom / ComfyUI error | Likely cause | Fix |
|-------------------------|--------------|-----|
| `Prompt outputs failed validation` / type mismatch on CLIP | CLIP wired from checkpoint index `0` | Wire CLIP from index `1` |
| `Value not in list` for ckpt/lora | Hallucinated or renamed file | Replace with exact inventory filename |
| Node type missing | Custom pack not installed | Swap to core pattern or list required pack |
| LoRA "does nothing" | Sampler still on raw checkpoint MODEL | Chain through last `LoraLoader` |
| Structure ignored with ControlNet present | Control image not on apply node / sampler still on raw conditioning | Wire apply outputs into sampler pos/neg |

---

## Examples

### Example 1: SD 1.5 txt2img (basic)

```json
{
  "1": {
    "class_type": "CheckpointLoaderSimple",
    "inputs": { "ckpt_name": "deliberate_v2.safetensors" }
  },
  "2": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "text": "anime character portrait, clean line art, soft cel shading, vibrant colors",
      "clip": ["1", 1]
    }
  },
  "3": {
    "class_type": "CLIPTextEncode",
    "inputs": {
      "text": "photorealistic, blurry, lowres, extra limbs, watermark",
      "clip": ["1", 1]
    }
  },
  "4": {
    "class_type": "EmptyLatentImage",
    "inputs": { "width": 512, "height": 768, "batch_size": 1 }
  },
  "5": {
    "class_type": "KSampler",
    "inputs": {
      "seed": 448201193557,
      "steps": 28,
      "cfg": 7.0,
      "sampler_name": "dpmpp_2m",
      "scheduler": "karras",
      "denoise": 1.0,
      "model": ["1", 0],
      "positive": ["2", 0],
      "negative": ["3", 0],
      "latent_image": ["4", 0]
    }
  },
  "6": {
    "class_type": "VAEDecode",
    "inputs": { "samples": ["5", 0], "vae": ["1", 2] }
  },
  "7": {
    "class_type": "SaveImage",
    "inputs": { "filename_prefix": "sd15_anime", "images": ["6", 0] }
  }
}
```

---

## Pitfalls

### Hallucinated node names

Base models often emit JSON that *looks* right but uses node names that don't exist on the target install:

- `SDXLClipTextEncode` (not a real node — use `CLIPTextEncode`)
- `LoadDiffusionModel` when the install only has `UNETLoader`
- Custom node names from packs that aren't installed

**Fix:** Always cross-reference `inventory.nodes` before emitting.

### Wrong output index on CheckpointLoaderSimple

The most common silent failure: wiring CLIP from `CheckpointLoaderSimple` output index `0` (which is MODEL) instead of index `1` (CLIP).

| Output index | Type |
|--------------|------|
| 0 | MODEL |
| 1 | CLIP |
| 2 | VAE |

### Wrong resolution for base model

- SDXL/FLUX at 512×512 → produces garbage or artifacts. Use 1024×1024 (or equivalent aspect ratio at ~1 megapixel).
- SD 1.5 at 1024×1024 → wastes compute, may produce artifacts. Use 512×512 (or 512×768 for portraits).

### FLUX double-guidance burn

Using FLUX with `cfg: 7` and no `FluxGuidance` node causes either double-guidance burn or no guidance at all.

**Fix:** FLUX requires `FluxGuidance` (~3.5) and sampler `cfg: 1.0`. Never use `CheckpointLoaderSimple` for split FLUX weights — use `UNETLoader` + `DualCLIPLoader` + `VAELoader`.

### LoRA stacking without chaining

Stacking LoRAs without chaining MODEL+CLIP through each loader means only the last (or first) LoRA takes effect.

**Fix:** Chain `LoraLoader` nodes: checkpoint MODEL → LoRA1 MODEL → LoRA2 MODEL → KSampler. Same for CLIP.

### ControlNet on latent instead of conditioning

`ControlNetApplyAdvanced` must be applied to **conditioning** (positive/negative), not to the latent image. Wiring it to the latent produces a type error or silent no-op.

### VRAM-busting stacks on small cards

Multiple full-res ControlNets + FaceDetailer + 2× upscale on 8 GB VRAM → CUDA OOM.

**Fix:** Respect `vramGb` from inventory. Reduce batch size, ControlNet count, or skip post-detailing on low-VRAM cards.

### Deprecated or architecture-mismatched nodes

SD1.5-only loaders for an SDXL/FLUX request. The graph may "load" then produce garbage — worse than a hard error.

### Silent dead subgraphs

LoRAs and ControlNets that don't sit on the path reaching `KSampler` / decode / save are dead weight. They load but never execute.

---

## Verification

Complete **all** items before declaring a workflow done:

- [ ] **JSON validity** — parses cleanly. No trailing commas, no unquoted keys.
- [ ] **Inventory match** — every `class_type` in `inventory.nodes`; every model filename in `inventory.models`.
- [ ] **Connection audit** — every `["node_id", index]` points at a real node and a legal output index.
- [ ] **No dangling required inputs** — every required field is a literal or a wire.
- [ ] **Live path for add-ons** — LoRAs chained into sampler/encoders; ControlNet outputs feed sampler conditionings.
- [ ] **Architecture rules** — FLUX not on `CheckpointLoaderSimple`; SDXL not at 512 primary; SD1.5 not forced through SDXL-only nodes.
- [ ] **Resolution + VRAM** — latent matches native training size; stack fits `vramGb`.
- [ ] **Seed policy stated** — fixed for reproducibility or random for variety.
- [ ] **Delivery path** — online → `comfyui-api`; offline → `projects/{project}/workflows/{descriptive}_vN.json`.

### Success criteria

A finished deliverable must satisfy all of the following:

1. **Valid API JSON** — object keyed by unique node IDs; each value has `class_type` + `inputs`.
2. **Real class_types** — every name is in `inventory.nodes` (or a documented core ComfyUI node the user confirmed).
3. **Real model filenames** — exact strings from `inventory.models` (casing + extension).
4. **Correct wires** — `[sourceNodeId, outputIndex]` only; indices in range for the source type.
5. **Model-native resolution** — SD1.5 ~512, SDXL/FLUX ~1024, Wan 480p ~832×480 (or inventory-backed variants).
6. **VRAM-aware** — batch, ControlNet count, and post-detailing fit `vramGb`.
7. **No silent dead subgraphs** — LoRAs and ControlNets must sit on the path that actually reaches `KSampler` / decode / save.

---

## Agent operating notes

1. **Inventory before creativity.** Hallucinated "better" model names are failures even if the graph structure is perfect.
2. **Prefer patterns over invention.** Start from a table pattern; only then customize prompts, seeds, and strengths.
3. **One identity method.** Do not stack PuLID + InstantID + FaceID unless the user insists and inventory supports a known recipe.
4. **Fail loud.** If required nodes are missing, say which pack provides them and offer a reduced core-only alternative.
5. **Stay in API format** unless the user explicitly needs UI-format export.
6. **Do not replace the graph with Python** unless the user asked for automation glue around an already-valid workflow.
7. **When uncertain about a custom node's output arity**, check inventory metadata or omit that node rather than guessing an index.

---

## Related skills

- **`comfyui`** — install, launch, manage nodes/models, run workflows (runtime owner). This chair authors **API-format workflow JSON** only.
- Queue/run a validated graph against a live server with `comfyui`, not a missing `comfyui-api` sibling.

---

## Version history

| Version | Notes |
|---------|--------|
| 1.1.0 | Initial publishable skill: six-stage pipeline, validator, SDXL/FLUX/LoRA/ControlNet/PuLID/Wan examples |
| 1.2.0 | Stronger trigger/description frontmatter; img2img + inpaint examples; pitfalls, VRAM tables, eval path docs; decision tree |
| 1.3.0 | Sampler/scheduler defaults; strength/denoise ranges; KSampler required-input list; upscale example; repair procedure; delivery handoff template |
| 1.3.1 | Restructured to production-grade SKILL.md format with progressive disclosure; preserved all hard rules, inventory discipline, and validation requirements |
