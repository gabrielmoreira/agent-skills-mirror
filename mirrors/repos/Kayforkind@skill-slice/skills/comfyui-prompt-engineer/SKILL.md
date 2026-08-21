---
name: comfyui-prompt-engineer
version: 1.1.1
description: "Crafts checkpoint-specific ComfyUI prompt pairs (FLUX, SDXL, SD1.5, Wan, AnimateDiff) with matching negatives, CFG ranges, and identity-method rules (InstantID, PuLID, FaceID, Kontext, character LoRA). Use when generating or adapting prompt text for a known model stack. Not for interviewing a vague idea (comfyui-prompt-interview), wiring node-graph JSON (comfyui-workflow-builder), or installing/launching ComfyUI (comfyui)."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
---

## Overview
Generates optimized prompts tailored to a specific model and identity method. Diffusion checkpoints do not share a prompt language. Each family was trained with a different text encoder on a different caption distribution, so the same sentence lands differently depending on the target. This skill picks the rules that match the checkpoint and the identity-preservation method actually in the stack.

## When to Use
Activate this skill when the job-to-be-done is **crafting or refining the prompt text** for a ComfyUI generation. Triggers on requests to:
- Generate a new positive/negative prompt pair for a specific checkpoint (FLUX, SDXL, SD1.5, Wan, AnimateDiff)
- Refine or debug an existing prompt that is underperforming on a given model
- Adapt a prompt when switching checkpoints (e.g., an SDXL prompt that needs to run on FLUX)
- Tailor a prompt to an identity method (InstantID, PuLID, IP-Adapter FaceID, FLUX Kontext, character LoRA)
- Build a model-appropriate negative prompt
- Recommend a CFG range that matches the model + identity-method stack
- Include the correct trigger word and feature handling when a character LoRA is in play

## Prerequisites
- ComfyUI installed and target checkpoint identified.
- Character profile available at `projects/{project}/characters/{name}/profile.yaml` (if using a character LoRA or specific identity).
- Optional: the Examples section below for fuller prompt pairs; the model-rule tables in Procedure for CFG ranges. This skill crafts prompt text for a known checkpoint — it does not interview a vague idea (use `comfyui-prompt-interview` for that).

## Procedure

### 1. Identify Target Model and Identity Method
Determine the checkpoint family (FLUX, SDXL, SD1.5, Wan, AnimateDiff) and the identity method (InstantID, PuLID, IP-Adapter FaceID, FLUX Kontext, Character LoRA) in use.

### 2. Load Character Profile
If using a character LoRA or specific identity, read the character profile from `projects/{project}/characters/{name}/profile.yaml` to get the trigger word and canonical feature list. Do not invent details.

### 3. Apply Model-Specific Rules

#### FLUX.1 (dev / schnell / Kontext)
- **Style**: Natural-language descriptions. FLUX uses a T5-XXL text encoder alongside CLIP and parses sentences rather than comma-separated booru tags.
- **CFG**: 3.5–4 (very low) for `dev`; `schnell` runs near CFG 1. High CFG over-saturates color and "fries" the image.
- **Quality tags**: Minimal. Strings like `masterpiece, best quality` add token noise.
- **Negative prompts**: Keep short. Guidance-distilled FLUX barely responds to a negative branch.
- **Length**: Medium (50–100 words).
- **Structure**: `{subject description}, {setting}, {lighting}, {camera/style}`.

#### SDXL (RealVisXL, Juggernaut XL, DreamShaper XL, etc.)
- **Style**: Quality tags at the front help significantly. SDXL has two CLIP text encoders trained on quality-rated captions.
- **CFG**: 7–9. Needs real guidance pressure; below ~6 it looks washed out, above ~10 it over-saturates.
- **Quality tags**: Include `masterpiece, best quality, photorealistic`.
- **Length**: Medium-long (50–150 words).
- **Structure**: `{quality tags}, {trigger word}, {subject}, {details}, {setting}, {style}`.
- **Weighted syntax**: Supported, e.g. `(important:1.3)`. Keep weights modest (1.1–1.4).

#### SD 1.5
- **Style**: Tag-based. Community SD1.5 checkpoints are heavily booru/tag trained.
- **CFG**: 7–8.
- **Quality tags**: Essential.
- **Length**: Shorter (30–80 words). Hard 77-token window; anything past it is truncated.
- **Structure**: `{quality}, {trigger}, {subject}, {details}, {style tags}`.

#### Wan 2.1 / 2.2 (Video)
- **Style**: Concise motion descriptions. The sampler animates whatever action you describe.
- **CFG**: 5–7.
- **Quality tags**: Minimal.
- **Length**: Short (20–50 words).
- **Focus**: Describe the motion, not just the appearance.
- **Structure**: `{subject}, {action/motion}, {setting}, {quality}`.

#### AnimateDiff
- **Style**: Same as the base model (SD1.5 or SDXL) for content. Add explicit camera and subject motion keywords.
- **Length**: Same as the base model.

### 4. Apply Identity-Method Modifiers
Do not re-describe in text what the method already injects.

- **InstantID**: Injects identity through a ControlNet-style face branch. DO NOT describe specific facial features. Describe clothing, pose, setting, lighting. Keep CFG at 4–5.
- **PuLID**: Lighter identity-injection. Can include minimal facial descriptions. CFG 5–7. Use "fidelity" mode to lock closer to reference.
- **IP-Adapter FaceID**: Encodes reference face into an image-prompt embedding. Describe the style you want, not the face. Use base model's standard CFG.
- **FLUX Kontext (Editing)**: Instruction-conditioned editing model. Describe the EDIT, not the full image. Be specific about what to change and what to preserve.
- **Character LoRA**: Fine-tuned weights bound to a trigger word. ALWAYS include the trigger word first. Don't describe features the LoRA has learned—focus on what varies: pose, clothing, setting, lighting.

### 5. Assemble Negative Prompt
- **Universal Negative (SDXL / SD1.5)**: `(worst quality:1.4), (low quality:1.4), blurry, deformed, bad anatomy, bad hands, extra fingers, missing fingers, extra limbs, fused fingers, text, watermark, signature, jpeg artifacts, username, error`
- **Photorealism Negative**: `3d render, cartoon, anime, illustration, painting, drawing, cgi, plastic skin, smooth skin, airbrushed, video game, doll, mannequin, oversaturated, artificial lighting`
- **Video Negative (Wan / AnimateDiff)**: `static, frozen, jerky motion, low quality, blurry, distorted face, bad anatomy, glitch, artifacts, flickering, jittery, unnatural movement`
- **FLUX Negative**: `blurry, low quality, distorted, deformed, ugly, watermark, text`

### 6. Reference Implementation
The rules above are encoded in a strict TypeScript reference implementation. Use this as the single source of truth for prompt assembly.

```typescript
// Domain types
export type ModelFamily = "flux" | "sdxl" | "sd15" | "wan" | "animatediff";
export type IdentityMethod = "none" | "instantid" | "pulid" | "ipadapter-faceid" | "flux-kontext" | "character-lora";

export interface CfgRange { readonly min: number; readonly max: number; }
export interface CharacterProfile {
  readonly name: string;
  readonly triggerWord: string | null;
  readonly facialFeatures: readonly string[];
  readonly hair: string;
}
export interface PromptRequest {
  readonly model: ModelFamily;
  readonly identity: IdentityMethod;
  readonly profile: CharacterProfile;
  readonly scene: string;
  readonly extraNegatives?: readonly string[];
}
export interface PromptResult {
  readonly positive: string;
  readonly negative: string;
  readonly cfg: CfgRange;
  readonly notes: readonly string[];
}

// Rule tables
const MODEL_RULES: Readonly<Record<ModelFamily, ModelRules>> = {
  flux: { cfg: { min: 3.5, max: 4 }, qualityTags: [], baseNegative: FLUX_NEGATIVE, maxWords: 100 },
  sdxl: { cfg: { min: 7, max: 9 }, qualityTags: ["masterpiece", "best quality", "photorealistic"], baseNegative: UNIVERSAL_NEGATIVE, maxWords: 150 },
  sd15: { cfg: { min: 7, max: 8 }, qualityTags: ["masterpiece", "best quality"], baseNegative: UNIVERSAL_NEGATIVE, maxWords: 80 },
  wan: { cfg: { min: 5, max: 7 }, qualityTags: ["high quality"], baseNegative: VIDEO_NEGATIVE, maxWords: 50 },
  animatediff: { cfg: { min: 7, max: 8 }, qualityTags: ["masterpiece", "best quality"], baseNegative: VIDEO_NEGATIVE, maxWords: 80 },
};

const IDENTITY_RULES: Readonly<Record<IdentityMethod, IdentityRules>> = {
  none: { describeFace: true, requireTrigger: false, cfgOverride: null, note: "No identity conditioning — describe the face fully." },
  instantid: { describeFace: false, requireTrigger: false, cfgOverride: { min: 4, max: 5 }, note: "Facial features omitted — InstantID provides them." },
  pulid: { describeFace: true, requireTrigger: false, cfgOverride: { min: 5, max: 7 }, note: "Minimal facial description allowed — PuLID is robust." },
  "ipadapter-faceid": { describeFace: false, requireTrigger: false, cfgOverride: null, note: "Describe style, not face — FaceID holds identity." },
  "flux-kontext": { describeFace: false, requireTrigger: false, cfgOverride: { min: 3.5, max: 4 }, note: "Describe the edit instruction, not the full image." },
  "character-lora": { describeFace: false, requireTrigger: true, cfgOverride: null, note: "Trigger word first — LoRA conditions later tokens." },
};

// Assembly logic
export function buildPrompt(request: PromptRequest): PromptResult {
  // 1. Validate inputs
  // 2. Apply quality tags (if model requires)
  // 3. Add trigger word (if identity requires)
  // 4. Add facial features (if identity allows)
  // 5. Add scene description
  // 6. Assemble negative prompt
  // 7. Return result with CFG and notes
}
```

## Pitfalls
- **Hardcoding secrets**: Never hardcode secrets in prompt scripts or workflow JSON. Workflow files are routinely shared and embedded in PNG metadata. Read credentials from environment variables.
- **Untrusted custom nodes**: ComfyUI custom nodes are arbitrary Python that runs in your process on load. An untrusted node pack is a remote-code-execution risk. Prefer well-maintained packs.
- **Version drift**: ComfyUI's node API and conditioning format change between releases. Pin ComfyUI and custom-node versions. Treat a version bump as something to re-validate.
- **Over-describing identity**: InstantID, PuLID, and IP-Adapter FaceID approximate a face from a reference. Re-describing facial features in text fights the injected conditioning. Expect to iterate on weight and CFG; do not promise pixel-perfect likeness in a single pass.
- **Ignoring token limits**: SD1.5 has a hard 77-token window. Exceeding it truncates the prompt mechanically.
- **Missing motion keywords**: For Wan and AnimateDiff, if you only describe appearance, you get a near-static clip. Motion description is the highest-leverage element.

## Verification
Confirm the prompt pair before delivering it to the user:
- [ ] Target model identified and the matching rule set applied (FLUX / SDXL / SD1.5 / Wan / AnimateDiff).
- [ ] CFG recommendation matches the model + identity-method stack (identity range wins when present).
- [ ] Quality tags handled per model — minimal for FLUX/Wan, front-loaded for SDXL/SD1.5.
- [ ] Trigger word included first when a character LoRA is used.
- [ ] Facial features omitted when InstantID / IP-Adapter FaceID provides the identity.
- [ ] A positive prompt and a matching negative prompt were both produced.
- [ ] Prompt length sits within the model's recommended range.

```powershell
# Quick verification pass
1. Confirm the target checkpoint and identity method
2. Generate one test image with the drafted positive + negative pair
3. Check quality-tag handling matches the model (no "masterpiece" on FLUX)
4. Verify CFG sits in the recommended range for the method stack
5. Confirm identity holds (features not double-specified for InstantID/FaceID)
6. Adjust weights/CFG and re-run only after the single test image passes
```

## Examples

### Example 1: FLUX portrait with InstantID
**Positive:**
```
photorealistic portrait, wearing a charcoal wool coat, standing on a rainy city
street at night, neon reflections, cinematic side lighting, shallow depth of field,
shot on Sony A7IV, 85mm lens
```
**Negative:**
```
blurry, low quality, distorted, deformed, ugly, watermark, text
```
**CFG:** 4–5 (InstantID range)

### Example 2: SDXL with a character LoRA
**Positive:**
```
masterpiece, best quality, sage_character, photorealistic portrait of a woman,
detailed skin texture with freckles, emerald green eyes, auburn copper hair,
standing on a rooftop at sunset, wind blowing hair, golden hour lighting,
cinematic composition, RAW photo quality, 8k uhd, film grain
```
**Negative:**
```
(worst quality:1.4), (low quality:1.4), blurry, deformed, bad anatomy,
bad hands, extra fingers, missing fingers, extra limbs, fused fingers,
text, watermark, signature, jpeg artifacts, username, error
```
**CFG:** 7–9

### Example 3: Wan video (talking head)
**Positive:**
```
young woman with auburn hair, talking naturally with gentle hand gestures,
seated at a modern desk, soft studio lighting, high quality
```
**Negative:**
```
static, frozen, jerky motion, low quality, blurry, distorted face,
bad anatomy, glitch, artifacts, flickering, jittery, unnatural movement
```
**CFG:** 5–7

## Related skills
- `comfyui-character-gen` — builds the identity-preserving workflow / node graph that these prompts feed into (InfiniteYou, FLUX Kontext, PuLID, InstantID, IP-Adapter).
