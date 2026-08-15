---
name: consistent-character-builder
description: "Runs a multi-shot production graph: Markdown character/story bibles as SSOT, Kohya/AI-Toolkit LoRA datasets, ComfyUI stacks (IP-Adapter, ControlNet, PuLID, ADetailer), and AnimateDiff/AnimateAnyone/LivePortrait with a bridge-frame loop. Trigger on identity lock across stills and video, VRAM-sized pipelines, or compounding-drift repair in episodic/ad work. Do not use for still-only ladder/contact-sheet sets (consistent-characters-2026) or for camera/negative prompt recipes (creative-prompt-engineering)."
version: 1.0.1
---

## Overview

This skill solves one problem: getting the *same character* to appear again across frames, scenes, shots, and even different generation tools, without the face, body, or wardrobe drifting.

The skill is a graph more than a sequence. Read this once before jumping into a section.

```text
                  ┌──────────────────────────────────────┐
                  │  §3  Character Bible + Story Bible   │  canonical source of truth
                  └──────────────────────────────────────┘
                       │            │              │
                       ▼            ▼              ▼
               ┌────────────┐ ┌──────────────┐ ┌──────────────┐
               │ §2.1 LoRA  │ │ §1 Midjourney│ │ §5 Platform  │
               │  dataset   │ │   --cref     │ │  reference   │
               │  prep      │ │  references  │ │   inputs     │
               └────────────┘ └──────────────┘ └──────────────┘
                       │            │              │
                       └──────┬─────┴──────┬───────┘
                              ▼            ▼
                  ┌──────────────────────────────────────┐
                  │ §6.1 Storyboard Layer (static stills)│
                  └──────────────────────────────────────┘
                                  │
                                  ▼
                  ┌──────────────────────────────────────┐
                  │ §6.2 Generation Layer (animate)      │
                  │  stacks: §2.1 LoRA + §2.2 IP-Adapter │
                  │          + §2.3 ControlNet + §2.5    │
                  │          PuLID + §4 AnimateDiff/...  │
                  └──────────────────────────────────────┘
                                  │
                                  ▼
                  ┌──────────────────────────────────────┐
                  │ §6.3 Orchestration (agent loop +     │
                  │      Bridge Technique across shots)  │
                  └──────────────────────────────────────┘
                                  │
                                  ▼
                  ┌──────────────────────────────────────┐
                  │ §2.4 ADetailer face repair (most     │
                  │      non-closeup shots)              │
                  └──────────────────────────────────────┘

Cross-cutting:  §A Seed control  ·  §B Denoise/strength  ·  §2.7 Native edit models
                §7 Triage  ·  §8 Edge cases  ·  §9 Compute  ·  §10 Sensitive contexts
```

> [!NOTE]
> **Values likely to drift; re-check before production.** Model/node names, default parameter values, and platform feature labels in this skill reflect the state of tools as of writing. Diffusion tooling changes monthly. Treat all named filenames, version numbers, default weights, and platform features as starting points to verify against current docs before locking a pipeline.

> [!NOTE]
> **Sibling skill:** prompt-engineering rules and `--sref` style-reference selection live in a separate `creative-prompt-engineering` skill if one is installed in your environment. If it isn't, follow the inline guidance here and consult Midjourney's current docs for `--sref` specifics.

## When to Use

Use this skill when the user mentions character consistency, identity preservation, face/body locking, recurring characters, character sheets, character bibles, Midjourney `--cref` / `--cw` / `--sref` parameters, LoRA training, ComfyUI workflows, ControlNet (OpenPose/Depth/Canny), IP-Adapter, InstantID, PuLID, ReferenceNet, AnimateDiff, AnimateAnyone, LivePortrait, ADetailer, seed control, native edit models (Flux Kontext, USO, OmniGen), or current-generation video platforms (Google Flow, Kling, Seedance, Runway Gen-4.x, Vidu, PixVerse). Also relevant for storyboards, music videos, anime sequences, episodic content, ad campaigns, or any multi-shot project where the same character must reappear without drift.

## Prerequisites

Recommendations elsewhere assume a 24GB+ GPU. Practical adjustments:

- **8GB VRAM (modern stack).** SD1.5 comfortable for everything. SDXL inference runnable with `--medvram` or sequential CPU offload — slow but usable. **Flux runnable in quantized form** (`fp8`, NF4, or GGUF community quants) with sequential offload — usable for stills, painful for long video. AnimateDiff `context_length = 8`, `context_overlap = 2`. Multi-image IP-Adapter: 2 references at ~0.4 instead of 3 at ~0.3. LivePortrait `load_gap = 2`. LoRA training on SD1.5 at rank 32, batch size 1, gradient checkpointing on; SDXL LoRA training is borderline — usually cheaper to rent. Native edit models in quantized form often fit here when classic stacks won't.
- **12GB VRAM.** SDXL inference comfortable. Flux quantized comfortable; full-precision Flux still needs offload. AnimateDiff `context_length = 12`. Multi-image IP-Adapter at 2 references manageable; 3 tight. PuLID-Flux usable.
- **24GB+ VRAM.** All defaults in this skill apply as written. Flux + PuLID comfortable. LoRA training on SDXL at rank 64 comfortable.
- **Cloud / no local GPU.** Lean on platform tools plus Midjourney. Reserve ComfyUI work for batched rentals (RunPod, Modal, etc.); design the pipeline to checkpoint between stages so an interruption doesn't cost the whole job.

## Procedure

### 1. The Character Bible & Story Bible Methodology

Before generating any image or video clip in a multi-shot project, check whether `character_bible.md` and `story_bible.md` exist. If they don't, look for storyboard JSONs, lyrics manifests, or treatment docs in the project directory, read them, and write the two bibles up front.

**Format: Markdown source, JSON/YAML at the boundary**

Markdown tables are the **human-editable source of truth** — easy to read, version-control diffs cleanly, edit in any text editor. ComfyUI nodes, scripted API callers, and agent loops typically need JSON or YAML. Recommended pattern:

1. Authors edit `character_bible.md` and `story_bible.md`.
2. A small script (or pre-generation step in the orchestration loop) parses the Markdown and emits `character_bible.json` / `story_bible.json` for tools that need structured input.
3. Generators read JSON. **No one hand-edits the JSON** — it is regenerated from Markdown on every run.

**Versioning the canonical references**

Reference images (`character_ref_front.png` etc.) anchor every shot's identity. If a teammate silently overwrites one, every prior shot's consistency basis is invalidated. Version reference images and record the version in the Story Bible.

### 2. Seed Control (Cross-Cutting Lever)

Deterministic seeds are the cheapest single consistency lever in diffusion. Same prompt + same seed + same model + same sampler = the same image.

- **Lock a seed per scene** during ideation. When you find a composition that works, record the seed in the Story Bible scene row so any later regeneration starts in the same neighborhood.
- **Seed sweeps** (10–30 seeds against a fixed prompt + character refs) are the right tool at project start. Curate two or three winners and reuse throughout.
- **Seeds don't transfer across major changes:** different sampler, different model, different resolution, different ControlNet, or different LoRA stack all break the lock.

### 3. Denoise / Strength — The Identity Knob

Many tools expose a "denoise strength," "image strength," or "init strength" parameter.

> **Denoise strength is inversely correlated with identity preservation.** Lower denoise = closer to the input image (identity intact, less change). Higher denoise = farther from the input (more stylistic freedom, more drift risk).

This shows up across the skill: Vid2Vid AnimateDiff (0.35–0.55), incremental denoise for aging morphs, face-restoration cleanup, inpainting touch-ups everywhere. When a tool's default isn't working, ask which direction your failure points: if outputs look too rigid / over-bound to the input, raise denoise; if identity is drifting, lower denoise and reinforce identity elsewhere.

### 4. Midjourney: Character Reference (`--cref`)

`--cref` tells Midjourney "the person in this image is who I'm drawing." Fastest path to recurring characters when you're not running a local pipeline.

**What counts as a strong reference:**
- **Resolution ≥ ~1024 px on the longer side.** Community rule-of-thumb; higher-resolution sources give cleaner crops with less compression noise.
- **Face occupies ≥ ~20% of the frame.** Rule-of-thumb derived from the encoder devoting most of its attention budget to the largest features. Crop if needed.
- **Even, neutral lighting** so harsh side-light or color casts don't get baked into every generation.
- **Single subject, plain background** so the encoder isn't disentangling.
- **Neutral or mild expression.** Strong expressions get over-learned and bleed into every output.

**Workflow:**
1. **Attach the reference URL** at the end of the prompt: `[prompt text] --cref http://url-to-your-image.png`
2. **Tune character weight (`--cw`).** Controls *how much* of the reference is carried over:
   - `--cw 100` carries identity *plus* hair and clothing.
   - `--cw 0` carries face structure only. Reach for this when the character needs different outfits or hairstyles per scene.
   - In-between values are valid; treat `--cw` as a slider, not a switch.
3. **Combine with style reference (`--sref`)** when both identity and style matter: `[prompt] --cref URL1 --sref URL2`.
4. **Fix small face issues with Vary Region** rather than rerolling the whole image.

### 5. Stable Diffusion / ComfyUI Production Tools

When you need tighter control, exact pose replication, or a permanent character asset, move to ComfyUI. Each tool addresses a different slice of the consistency problem; production setups usually stack several.

#### 5.1 LoRA Training — Long-Term Identity Asset

A LoRA is a small fine-tune that bakes a specific character into the model. Strongest form of identity preservation.

| Regime | Dataset size | Inference weight | When to use |
| :--- | :--- | :--- | :--- |
| **Quick / utility LoRA** | 10–20 curated, high-variety images | `0.7`–`1.0` | One-off project, hero with limited screen time, fast iteration |
| **Production / hero LoRA** | 20–30 curated images spanning more lighting, expression, and angles | `0.6`–`0.85` | Long-running series, character appearing in many lighting and stylistic contexts |

Above `1.0` the LoRA tends to dominate prompts and produce "overcooked" outputs; below `0.6` identity washes out. When stacking with IP-Adapter, ControlNet, or PuLID, lean toward the lower end to leave headroom.

**Dataset principles (both regimes):**
- Vary angle, lighting, and background. Without variety, the LoRA memorizes background or lighting and bleeds them into every future generation.
- Twenty mediocre images train worse than ten great ones. Curate ruthlessly.
- Tag with a unique activator token. `ohwx` and `sks` are widely cited but both have downsides. A random 5–6 letter nonce (e.g., `qzvfra`) avoids prior meaning collisions.
- Tag secondary features (clothes, background, accessories) *separately* from the activator. This decoupling lets you later prompt the character in different outfits without the outfits being baked into "identity".

**Trainers:** `Kohya_ss` or `AI Toolkit` (Ostris). Both well-maintained, comparable results, pick by UI preference.

**Rank, alpha, and prompt length — with reasoning:**
- **Rank ~64.** Higher ranks have more capacity but overfit on small character datasets, baking in incidental details as if they were identity. Rank 32–64 is the safe band.
- **Alpha ≈ rank / 2** (e.g., rank 64 → alpha 32) is the conventional ratio for character LoRAs. Alpha equal to rank trains "hotter" and converges faster but overfits sooner; alpha well below rank/2 trains slowly and may underfit.
- **~50–80 word character prompt at inference.** Long enough to encode multiple identity anchors that reinforce each other if any single one drifts; short enough to leave token budget for scene description, ControlNet hints, and negative prompts.

**Inference combo for maximum lock-in:** LoRA + Frame 0 conditioning + ~50–80 word character prompt + ControlNet. Each reinforces a different axis (identity, opening composition, descriptive grounding, pose); the stack is more robust than any single tool.

**Fixing drift in specific frames:** Inpaint with the LoRA active on just the face region. Faster than regenerating the shot and avoids breaking other elements.

#### 5.2 IP-Adapter — Instant Identity Injection (No Training)

IP-Adapter pushes a reference image's features straight into the diffusion process. Fastest path to "this person, in a new scene" when you can't afford to train a LoRA.

- **Nodes:** `IPAdapter Unified` or `IPAdapter Apply`.
- **Single-reference weight `0.5`–`0.8`.** Higher weights enforce stricter face matches but compress pose and expression variety.

**Multi-image variant** is the standard community workaround for the expression-locking failure mode. The starting recipe widely shared in ComfyUI workflows is **3 references at weight ~0.3 each**. The intuition: spreading the signal across multiple angle/expression samples gives the model a small identity manifold to interpolate within rather than a single point to copy.

- **Why 3 and not 2 or 4?** Two references rarely span enough angle/expression range to escape the single-point problem; four or more give diminishing returns on identity-manifold breadth while adding inference cost. Treat 3 × 0.3 as a defensible default.
- **Always pair with the ADetailer face-fixing pass** on video frames, since lower individual weights let face detail drift more in small face regions.

#### 5.3 ControlNet — Pose & Composition Lock

ControlNet locks the *structure* of a generation (skeleton, depth, edges) to a reference while leaving identity and texture to the rest of the stack.

- **OpenPose** matches skeleton keypoints. Best for character actions and choreography.
- **Depth / Canny** match 3D layout or hard edges. Better when silhouette and scene composition matter more than exact joint positions.
- **Workflow:** Extract the pose/depth/canny map from a reference image, feed into the ControlNet node, generate with your character identity layered on top.

#### 5.4 ADetailer — Face Repair Pass

In medium and wide shots, faces occupy a small fraction of the image's pixels, and diffusion models produce low-resolution facial artifacts at that effective resolution. ADetailer detects the face, crops it, runs a higher-resolution inpaint pass on just that crop, and blends it back in.

**Default it on** for any pipeline producing non-closeup shots. The knobs that actually matter:

- **Detection confidence threshold (default ~0.3).** Lower catches more faces (including stylized ones) at the cost of more false positives. Raise to `0.5`–`0.6` if ADetailer is grabbing background blobs or non-face regions.
- **Mask dilation (default ~4 px).** Too tight produces visible seams between the inpainted face and surrounding head; too wide pulls in hair and background that get repainted unwantedly. 4–8 px is the usable band.
- **Inpaint denoise strength (default ~0.4).** Low denoise preserves the existing face shape (good when the face is *mostly* right and just needs sharpening); high denoise lets the model regenerate features (good when the face is genuinely broken). `0.3`–`0.5` is the typical band; pushing past `0.6` risks identity drift on the inpaint pass.

**Turn it off (or restrict the detector) when:**
- The face is intentionally occluded (mask, helmet, back of head, deep shadow). The detector grabs the wrong region and "fixes" it into a face that shouldn't be there.
- The character is highly stylized (chibi, sketch, abstract). Detectors trained on real photos misfire on, or warp, stylized features toward realism. Either disable ADetailer or substitute a stylized-face detector model (e.g., anime-face YOLO weights).
- The shot is already a closeup where the base model has enough resolution to render the face correctly. Adding ADetailer can over-detail and create an uncanny "two-pass" look.

#### 5.5 PuLID — Identity Preservation for Flux

PuLID is a tuning-free identity adapter notable for *not* dragging the reference image's style with it. Older identity tools (especially IP-Adapter at high weight) leak lighting, color grading, and composition from the reference; PuLID injects just face identity, leaving the model free to express the prompted style.

- **ComfyUI node:** `ComfyUI-PuLID-Flux`. Compatibility with newer Flux variants varies by node maintainer state — check the node README.
- **Prefer over IP-Adapter on Flux** when you need wide stylistic variation around a fixed identity.

#### 5.6 InstantID — Pre-Production, Not Production

InstantID does zero-shot identity transfer well but locks expressions hard. Poor fit *directly* in video pipelines (every frame ends up wearing the same face), excellent for generating a character sheet other tools can reference.

- **Use as:** Multi-angle character sheet generator (front, three-quarter, profile, back, expression studies).
- **Then feed those sheets** into video generation tools as their reference inputs. This decouples InstantID's expression-locking from the actual video step.

#### 5.7 Native Edit Models (Flux Kontext, USO, OmniGen, …)

A separate class of 2025–26 models performs character-aware editing in a single forward pass without the full IP-Adapter + ControlNet + LoRA stack. **Flux Kontext**, **USO**, **OmniGen** and similar native edit models take an existing image plus an instruction ("put this character in a forest at night, keep the face") and produce a new image with identity preserved by the model itself.

- **When they win:** simple character relocation, costume swaps, lighting changes on existing shots. Often one node and one instruction replaces a five-node ComfyUI graph.
- **When the classic stack still wins:** strict pose replication (use ControlNet), permanent reusable identity (train a LoRA), narrow stylistic targets needing style-LoRA stacking, very long shots where temporal-aware models are still needed.
- **Pragmatic rule:** before assembling a full classic stack for a one-off edit, try a native edit model on the same task. If the output is acceptable, you've saved hours of pipeline tuning.

## Pitfalls

### 1. Compounding Drift

Multi-shot projects suffer a specific failure: different scenes are generated at different times, often by different agents or runs, and small inconsistencies compound.

> [!IMPORTANT]
> **Worked example of compounding drift.** Scene 3 added a small scar over the left eyebrow. Scene 7 was generated from a different reference and dropped the scar. Scene 12's `--cref` reference was pulled from scene 7's output and propagated the scarless version forward. By scene 18, half the project has a scar and half doesn't, with no record of which is canon. Retrofitting consistency at that point is expensive; a single shared spec from the start prevents it.

### 2. Costume / Outfit Changes Between Scenes

`--cw 0` handles wardrobe variation in Midjourney. Equivalents elsewhere:

- **LoRA:** Works cleanly only if costume was tagged separately from the activator. If it wasn't, generating in the trained costume and inpainting the new costume on top is often faster than fighting the LoRA.
- **IP-Adapter:** Use a *face-only* variant (e.g., IP-Adapter FaceID family) rather than the standard one, which carries clothing.
- **ReferenceNet (AnimateAnyone):** Swap reference to one wearing the new costume; expect touch-up inpainting on transition frames.
- **Native edit model:** "Put this character in [new outfit], keep the face" is exactly what these are built for; try this before assembling a custom stack.

### 3. Non-Human or Stylized Characters

Face-encoder-based tools (InstantID, PuLID, IP-Adapter FaceID) are trained on real human face data. They often fail or under-fire on:

- Anime / chibi / heavily stylized characters
- Non-human creatures (animals, monsters, robots)
- Characters with non-realistic proportions (huge eyes, no nose, exaggerated features)

For these, prefer:

- **Custom LoRA** as the primary identity tool. LoRA training is encoder-agnostic.
- **Full-image IP-Adapter** (not the FaceID variant) at moderate weight to carry overall design.
- **ReferenceNet** for clothing/texture details when animating.
- **Disable face-detector ADetailer** or substitute a stylized-face detector to avoid realism warping.

### 4. Hands, Distinctive Marks, and Props

These drift faster than faces because they occupy less pixel area and lack a dedicated detector pass.

- **Document them explicitly** in `character_bible.md`: hand shape, ring finger jewelry, watch, scar locations.
- **Props:** Treat recurring props as their own mini-character — give them their own reference image and prompt tokens.
- **Inpainting recovery:** For broken hands, use a hand-specific inpainting model or ControlNet hand-pose conditioning, then regenerate just the hand region.
- **Tattoos / scars:** If they vanish, inpaint them back in; if they migrate (correct shape, wrong location), the activator-token prompt needs an explicit location phrase ("scar over left eyebrow").

### 5. Aging or Transformation Arcs (Same Character at 12 and 40)

Treat each age stage as a *related but separate* Character Bible entry sharing core identity tokens (eye color, bone-structure language) but with age-specific physical specs.

- **Separate LoRAs per stage** trained on age-appropriate references — spanning 30 years in one LoRA produces a muddy average.
- **Shared modular prompt variables** with age-specific overrides: `@character_face_child`, `@character_face_adult`.
- **Transformation sequences** (gradual aging on-screen): generate endpoint stages first as fixed references, then morph between them with image-to-image at incremental denoise strengths (low denoise stays close to source, higher denoise pushes toward target).

### 6. Style Transfer (Same Character, Different Art Style)

Pairing identity tools with style tools is where leakage shows up.

- **Best stack:** Character LoRA (identity) + `--sref` or style LoRA (style) + low-weight PuLID (identity reinforcement that resists style leak).
- **Avoid** high-weight IP-Adapter on a style-shifted reference; it drags source style with it.
- **Inpaint the face last** with the character LoRA active and the style LoRA at reduced weight, so the face stays recognizable even when global style is heavy.

### 7. Recovering from a Poor Reference

You inherited a low-res, harshly-lit, or partially-occluded reference. Options ranked by effort:

1. **Upscale + face-restore** (GFPGAN, CodeFormer) the reference, then crop to the face region. Cheap and often enough.
2. **Generate cleaner references** by using the bad reference at low IP-Adapter weight to produce several new portraits, hand-pick the best, and treat that as the new golden reference (bump its version number).
3. **Re-shoot or re-source** if the original subject is accessible.
4. **Train a tiny exploratory LoRA** on what you have, generate diverse outputs, curate the best as a new reference set, then retrain. Time-consuming but recovers projects with no other path.

### 8. Sensitive Contexts and Agent Refusal

A few situations require pause before generating, not just better technical choices.

- **Real, identifiable people.** Most platforms' terms of service restrict generating real public figures, especially in misleading contexts. Local-tool LoRAs of real people raise likeness-rights questions (right of publicity, defamation; specifics vary by jurisdiction). Get explicit consent, or stick to fictional characters.
- **Minors.** Many platforms refuse generations of real-world minors entirely. Fictional minor characters in non-sexualized contexts are usually allowed but remain a frequent moderation flashpoint — keep references and outputs unambiguously age-appropriate.
- **Likeness for commercial use.** Even with consent, commercial use of a real person's likeness typically requires a separate written agreement. Don't assume a casual "yeah go ahead" covers a paid ad campaign.
- **Deepfake-adjacent work.** Replacing one real person's face with another in video — even for satire or art — sits in active legal and platform-policy territory. Verify jurisdiction-specific rules before publishing.

**If you are an agent consulting this skill:**

When a request crosses one of the above categories — train a LoRA of a named public figure, swap a real person's face into a video, generate a real minor, produce a real person's likeness for advertising — **do not silently proceed**. The actionable path:

1. **Surface the concern explicitly** to the requesting human, naming which category applies and why it matters (TOS, consent, jurisdiction).
2. **Ask for the specific authorization** the category requires: written consent for likeness, commercial-use rights for ads, confirmation that a depicted minor is fictional, etc.
3. **If authorization isn't forthcoming, refuse the specific risky operation** and offer the closest safe alternative (fictional character with similar archetype; clearly-labeled satire that doesn't impersonate; aged-up version of the character).
4. **Document the decision** in the project (a one-line note in the Story Bible is enough) so subsequent runs don't re-litigate it.

The principle: a skill that *names* a hazard but lets the agent proceed anyway provides no actual safety. Make the gate explicit and the escalation visible.

## Verification

To verify character consistency across a multi-shot project:

1. **Check Bible Adherence:** Ensure every generated shot is anchored to the `character_bible.md` and `story_bible.md`. Verify that the JSON boundary files were regenerated from Markdown and not hand-edited.
2. **Seed Lock Verification:** Confirm that the seed recorded in the Story Bible scene row is being used for regenerations of that scene.
3. **Reference Image Versioning:** Check that the reference images used for `--cref`, IP-Adapter, or LoRA training match the version numbers recorded in the Story Bible.
4. **ADetailer Pass Check:** For non-closeup shots, verify that ADetailer ran successfully without grabbing non-face regions (check detection confidence threshold and mask dilation settings).
5. **Identity Drift Inspection:** Visually inspect frames for compounding drift (e.g., scars, jewelry, eye color). If drift is detected, trace the reference chain back to the canonical source and correct the offending generation.
6. **Sensitive Context Gate:** Verify that any requests involving real people, minors, or commercial likeness have documented authorization in the Story Bible before proceeding with generation.
