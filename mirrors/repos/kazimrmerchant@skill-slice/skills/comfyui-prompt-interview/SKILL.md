---
name: comfyui-prompt-interview
version: 1.2.1
description: "Interviews a vague image idea across 4-7 exchanges, then synthesizes a model-tuned positive prompt, negative prompt, settings table, and pipeline recommendation. Use when the user has a fragment vision and needs a ComfyUI prompt spec before generation. Not for ComfyUI node-graph wiring, repairing an existing underperforming prompt, LoRA training, or claiming an image was rendered."
risk: safe
source: openrouter-deepsearch
date_added: 2026-06-16
user-invocable: true
metadata:
  openclaw:
    emoji: "🎬"
    os: ["darwin", "linux", "win32"]
---

# comfyui-prompt-interview

Conduct a guided conversation to draw out the user's complete creative vision, then synthesize a model-appropriate prompt with all recommended settings.

**Why this skill exists:** Most people arrive with a fragment of an idea ("a warrior woman in ruins") rather than the dozen concrete decisions a good prompt encodes — lighting, lens, framing, mood, style, model. If you generate from the fragment, you get a generic result and the user iterates blindly. A short, targeted interview surfaces those decisions *before* generation, so the first prompt already reflects what they actually pictured. The goal is to convert vague intent into a precise, model-tuned specification with as little friction as possible.

## When to Use

- The user describes an image or scene idea but hasn't given enough detail for a quality prompt.
- The user says "help me think through what I want to create."
- The user has a vague concept that needs refinement.
- The user wants a structured prompt but isn't sure what to specify.
- Trigger keywords: "I want to create...", "help me make an image of...", "I have an idea for...", "help me craft a prompt", "write me a prompt for..."

If the user already handed you a fully-specified brief (subject, style, lighting, framing, model all stated), skip the interview and go straight to synthesis — re-asking what they already told you wastes their time and erodes trust.

### Do NOT use for

- **Workflow building / ComfyUI node-graph construction** → use `comfyui-character-gen`. Wiring nodes is a build task with its own failure modes.
- **Prompt debugging or fixing an underperforming prompt** → use `comfyui-prompt-engineer`. That starts from an *existing* prompt and a symptom; this skill starts from a blank page and a vision.
- **Technical explanations of how the models work internally** — the user wants a result, not a lecture.
- **Model training / LoRA fine-tuning** — a separate, much longer workflow.
- **Code generation** — out of scope.
- **Identity-preserving character generation as a build task** → use `comfyui-character-gen`. This skill can *recommend* an identity method, but wiring InstantID/InfiniteYou/PuLID is a build task.

**Warning:** Never attempt to render the actual image from inside this skill. Its only output is the prompt-and-settings specification the user takes into ComfyUI. Claiming to have "generated" an image would be false.

## Prerequisites

- The user should have a ComfyUI installation and at least one checkpoint model available. If you need to check what models are installed, consult the user's ComfyUI inventory before recommending a specific checkpoint.
- For model-specific prompt formatting rules (FLUX natural language, SDXL tag-style, SD1.5 weighted tokens, Wan video), load the reference material from `comfyui-prompt-engineer` — this skill depends on those rules for the synthesis step.
- No scripts or CLI tools are required; this is a conversational skill. No `scripts/` directory is used.
- No `references/` directory is required for this skill itself, but the agent should cross-reference `comfyui-prompt-engineer` for prompt-formatting rules during synthesis.

## Procedure

### Interview philosophy

**Ask, don't interrogate.** A wall of ten questions feels like a form and kills creative momentum. Ask one or two questions at a time, listen to what they give you, and follow up only on what's still missing. Each answer should visibly shape the next question.

**Fewer questions = better.** Aim for 4–7 exchanges. The first two or three questions resolve most of the ambiguity that actually affects the image; past that, you're polishing details the user often doesn't care about. Ask the highest-impact questions first, and stop the moment you have enough to write an excellent prompt.

**Don't ask for what you can infer.** If the user says "cinematic portrait of a warrior woman," you already know it's a person, it's a portrait, and the mood leans dramatic. Asking "is this a person?" tells them you ignored their sentence. Infer everything the words already imply and spend your question budget on what's genuinely undetermined.

### Step 1: Open with the big picture

If the user hasn't told you what they want to create, start broad:

> "What do you want to create? Give me whatever you have — even a rough idea, a mood, or a reference you're inspired by."

If they already gave you a starting concept, skip this entirely and jump to what's missing.

### Step 2: Branch by creation type

Read their answer and decide what kind of generation this is. The *type* determines which questions are relevant.

| Type | Key questions to ask | Why these matter |
|------|---------------------|-----------------|
| **Portrait / Character** | Identity method? Existing character? Expression, clothing, setting, lighting | The face and identity carry the image; lighting and expression decide whether it reads as alive or as a mannequin. |
| **Scene / Environment** | Location, time of day, mood, weather, foreground/background elements | No single subject anchors the frame, so atmosphere and layered depth do the heavy lifting. |
| **Product / Object** | Angle, background, lighting style, commercial vs. artistic | Commercial shots need clean, controlled light; the angle and background sell the object. |
| **Abstract / Concept** | Dominant colors, shapes, emotional tone, what to avoid | There's no literal subject to describe, so color and form *are* the content. |
| **Video** | Motion type, camera movement, duration needed, audio? | Motion and length drive the model choice and the whole pipeline, not just the prompt. |

### Step 3: Ask the high-impact questions

Ask only what's missing, in natural conversational language — never as a numbered bulleted list dumped on the user at once. The ordering below is by *impact on the final image*: each earlier question constrains more of the composition than the one after it.

#### For character / portrait content — in order of impact:

1. **Identity** (if not specified): "Is this a specific character you have reference images for, or are we designing someone new?" — *This decides the entire pipeline: an existing identity routes through InstantID/InfiniteYou/LoRA, a new one lets the checkpoint design freely.*
2. **Expression & mood**: "What's the emotion or energy — fierce, serene, playful, haunted?" — *Mood is what makes a portrait feel alive instead of a blank stare; it colors lighting and pose choices too.*
3. **Setting**: "Where are they, and when? (Time of day, location, interior/exterior)" — *Setting fixes the light source and the background, which together define half the frame.*
4. **Lighting**: "Any specific lighting in mind? (Golden hour, dramatic side light, soft studio, neon, candlelight)" — *Lighting is the single biggest lever on how cinematic or flat the result looks.*
5. **Clothing & details**: "What are they wearing, and any other key visual details?" — *Wardrobe and props establish era, status, and genre at a glance.*
6. **Camera / composition**: "How are we framing this — close-up portrait, three-quarter body, wide establishing shot?" — *Framing changes the aspect ratio and how much of the setting is visible.*
7. **Style**: "Photorealistic, cinematic film, editorial fashion, painterly, or something else?" — *Style selects the checkpoint and the quality-tag vocabulary.*

#### For scene / environment content — in order of impact:

1. **Setting**: "Describe the place — what does it look like, and when is it?" — *With no single subject, the place is the subject.*
2. **Mood / atmosphere**: "What feeling should hit the viewer instantly?" — *Atmosphere is what an environment shot trades on; it guides color grade and weather.*
3. **Lighting**: "What's the light source and quality?" — *Light direction and softness create the depth that makes an environment readable.*
4. **Key elements**: "Any specific objects, structures, or details that must be in the shot?" — *Anchoring landmarks keep the model from drifting into generic filler.*
5. **Style**: "Photorealistic, stylized, concept art, painterly?" — *Selects the checkpoint and how literal vs. interpretive the render should be.*

#### For video content — additional questions on top of the relevant set above:

1. **Motion**: "What's moving — the subject, the camera, or both?" — *Subject motion vs. camera motion need different models and conditioning.*
2. **Duration**: "How long? (Short 3–5s vs. long 15–60s changes the model choice.)" — *Length is the hard constraint on which video model can even produce it.*
3. **Audio**: "Do you need sound/music, or silent?" — *Audio pulls in a talking-head or sync pipeline rather than pure image-to-video.*

### Step 4: Technical questions (ask only if not obvious)

These are usually inferable from context — infer first, ask only when the answer genuinely changes the output and you can't reasonably guess it.

- **Aspect ratio**: "Standard 1:1, 16:9 cinematic, or 9:16 vertical/social?" — *Often implied by the framing answer; ask only if framing left it ambiguous.*
- **Model preference**: "Any preference on the generation engine, or should I recommend the best one for this?" — *Most users want you to choose.*
- **Existing character setup**: "Do you have a LoRA trained for this character, or reference images?" — *Only relevant once you know identity preservation is in play.*
- **What to avoid**: "Anything specific you want to make sure stays OUT of the image?" — *Cheap to ask and directly seeds the negative prompt with the user's own exclusions.*

### Step 5: Confirm and synthesize

Before generating, reflect the vision back in one or two sentences:

> "Got it. Here's how I'm reading this: ⟨one-or-two-sentence summary of their concept⟩. Let me build that prompt."

**Why reflect back:** It's a cheap checkpoint that catches misunderstandings *before* you spend the full synthesis on the wrong idea. If your summary is off, the user corrects one sentence; if it's right, they feel heard and you proceed with confidence. Then immediately generate the full four-part output — don't pause for further permission once they've confirmed.

### Output format

Always deliver all four components, clearly separated:

1. **🎯 Positive prompt** — what to make
2. **🚫 Negative prompt** — what to suppress
3. **⚙️ Recommended settings** — makes the result reproducible
4. **🔧 Pipeline recommendation** — how to actually run it

#### 🎯 Positive prompt rules

Craft the positive prompt using the model-specific rules from `comfyui-prompt-engineer`. Each model's text encoder was trained on different data — the *same words* perform differently on each, so the formatting is not cosmetic.

- **FLUX / Kontext** — Natural language, 50–100 words, **no** quality tags ("masterpiece", "8k" actively hurt FLUX because its encoder never associated them with quality). If using an identity method, describe the *scene*, not the face.
- **SDXL** — Quality tags first, trigger word second, 50–150 words, weighted syntax `(token:1.2)` supported and effective.
- **SD 1.5** — Short and tag-based, 30–80 words; long prompts dilute the limited 77-token context.
- **Wan / Video** — Concise, motion-focused, 20–50 words; verbosity competes with the motion description the model actually needs.
- If a LoRA trigger word applies, place it **first** so it isn't truncated or down-weighted by surrounding tokens.
- If using InstantID / InfiniteYou, omit facial-feature descriptions and let the identity method own the face — describing it fights the reference and muddies the result.

**Worked example (FLUX.1-dev, natural language, ~95 words):**

```text
A lone figure in a long dark coat stands beneath a glowing paper umbrella in a
narrow, rain-soaked alley at night. Towering walls are plastered with flickering
neon signage in magenta, cyan, and electric blue, the light smearing into puddles
across the wet asphalt. Steam drifts up from a street vent, catching the colored
glow. Reflections ripple underfoot and a fine drizzle blurs the distant city lights
into soft bokeh. The mood is quiet and cinematic, like a still from a noir
science-fiction film, shot on a 50mm lens with a shallow depth of field.
```

#### 🚫 Negative prompt rules

Pick the template that matches the medium, then customize it with the user's own "keep this out" answers. SDXL leans heavily on the negative prompt and rewards a detailed one, whereas FLUX.1-dev at its default guidance largely *ignores* negatives — so a long FLUX negative is mostly decorative unless you change the sampler.

Standard templates:

- **Photorealism (SDXL/SD1.5):** `(worst quality:1.4), (low quality:1.4), blurry, deformed, bad anatomy, bad hands, extra fingers, missing fingers, text, watermark, 3d render, cartoon, anime, plastic skin, airbrushed, oversaturated`
- **FLUX (minimal):** `blurry, low quality, distorted, deformed, ugly, watermark, text`
- **Video:** `static, frozen, jerky motion, low quality, blurry, distorted face, bad anatomy, glitch, artifacts, flickering`

**Worked example (FLUX minimal, customized for the alley scene):**

```text
blurry, low quality, distorted, deformed, extra limbs, watermark, text, signature,
daytime, sunny sky, clear weather, people crowd, dry pavement, cartoon, 3d render
```

> *Validation note:* On FLUX.1-dev at guidance 1.0 this negative is **inert**. To make it take effect, switch to a CFG-capable sampler/guider (CFG ≈ 2.0), which roughly doubles render time. For a purely atmospheric scene like this, leaving the negative minimal and accepting that it's mostly inactive is the right trade — don't pay 2× render time to suppress artifacts FLUX rarely produces here anyway.

#### ⚙️ Recommended settings table

Give exact values, each with its valid range and the failure mode you're steering around — vague settings force the user to re-discover these limits by trial and error.

**Worked example (FLUX.1-dev for the neon-alley scene):**

| Parameter | Value | Valid range / why |
|-----------|-------|-------------------|
| Model | FLUX.1-dev (fp8) | Best prompt adherence for a multi-element scene; reads natural language and composes the umbrella, signage, steam, and reflections coherently without quality tags. |
| Sampler | `euler` | FLUX is tuned for simple ODE samplers; `euler` is the reference choice. Ancestral samplers (`euler_a`) add noise that softens the neon edges. |
| Scheduler | `simple` | Pairs with `euler`. `karras`/`beta` can mute FLUX's fine high-frequency detail. |
| Steps | 25 | 20–30 for dev. Below 18 the signage text turns to mush; above 32 is wasted compute with no visible gain. |
| Guidance (CFG) | 3.5 | This is FLUX's distilled "guidance" embed, not classic CFG. Stay 3.0–4.0: above ~5 the neon posterizes and bands, below ~2.5 the scene goes flat and gray. |
| Resolution | 896×1152 px | FLUX native ≈ 1.0 MP and tolerates off-square better than SDXL. The 7:9 portrait suits a standing figure; 1024×1024 also works. |
| Negative prompt | Inactive at guidance 1.0 | To activate, swap to a `CFGGuider` node at CFG ≈ 2.0 (≈ 2× render time). Skip unless artifacts actually appear. |
| Identity method | None | Atmospheric scene with no recognizable face — no InstantID/InfiniteYou needed. |
| LoRA | None (optional: cinematic-film LoRA @ 0.5) | Keep a style LoRA ≤ 0.6; above ~0.7 it overrides the prompt's specific color story and flattens the neon palette. |
| Upscale | `4x-UltraSharp` @ 1.5×, denoise 0.30 | Denoise > 0.5 invents new detail and can warp the signage; 0.25–0.35 sharpens the neon and rain without changing the composition. |

#### 🔧 Pipeline recommendation

One to three sentences naming the workflow pattern and *why it fits this specific concept* — the user should understand the reasoning, not just copy a node list.

**Worked example (for the neon-alley scene):**

> Single-pass FLUX.1-dev with a light upscale tail. Load FLUX.1-dev (fp8) → KSampler (`euler`/`simple`, 25 steps, guidance 3.5) at 896×1152 → upscale with `4x-UltraSharp` at 1.5× and denoise 0.30 to crisp the neon signage and rain reflections. Skip all identity and face-detailer nodes — there's no prominent face to preserve here, so adding them would only slow the graph (keeping it ~12s on a 4090) and risk hallucinating a face into a figure meant to read as anonymous. Iterate the seed freely until the umbrella's glow and the puddle reflections line up the way you pictured.

### Decision rules for model selection

When you recommend a model/pipeline, match it to the user's stated goal. The "best" model is entirely goal-dependent — the checkpoint that nails a single referenced face is the wrong tool for a wide environment shot.

| User's goal | Recommended model | Why |
|-------------|-------------------|-----|
| Photorealistic portrait, new character | SDXL checkpoint (e.g., RealVisXL V5.0) | Strongest at cinematic lighting and full-figure anatomy without a trained LoRA. |
| Photorealistic portrait, existing character | SDXL + InstantID/InfiniteYou/PuLID + LoRA | Identity preservation requires a face-reference pipeline layered on the checkpoint. |
| Atmospheric scene / environment | FLUX.1-dev | Best prompt adherence for multi-element scenes; reads natural language and composes coherently. |
| Stylized / artistic / painterly | SDXL or SD1.5 with style LoRA | Style LoRAs are most mature on SD architectures; FLUX style LoRAs are less established. |
| Product / commercial shot | SDXL photoreal checkpoint | Clean controlled light, high detail, commercial-grade output. |
| Short video (3–5s) | Wan 2.1 / CogVideoX | Short-form video models handle brief clips efficiently. |
| Long video (15–60s) | Wan 2.1 (long) or multi-segment pipeline | Length is the hard constraint on which video model can produce it. |
| Talking head / lip-sync | LatentSync / SadTalker pipeline | Audio-driven facial motion requires a dedicated sync pipeline. |

### Integration with other skills

After delivering the four-part output, offer concrete next steps:

- **Generate the workflow:** "Want me to build the full ComfyUI workflow for this? I'll check your inventory and configure every node." (Hands off to `comfyui-character-gen`.)
- **Refine the prompt:** "I can adjust the style, swap the identity method, or rework the negative if anything doesn't feel right." (Hands off to `comfyui-prompt-engineer`.)
- **Save as a character profile:** "If this becomes a recurring character, I can create a profile so we always have her settings ready."

## Examples

### Example interview (character, end-to-end)

**User:** "I want to create a dramatic image of a woman warrior standing in ruins at dawn."

**Assistant:**
> "Love the concept. A few things that'll lock in the look:
> 1. Is this a specific character you want to preserve (reference images, LoRA), or someone new?
> 2. What's her energy — defiant and triumphant, exhausted but unbroken, something else?
> 3. Any specifics on how she looks — hair, armor style, anything iconic about her?"

**User:** "New character. Defiant and triumphant. Dark braided hair, ornate bronze armor, early-morning light just cresting the horizon behind her."

**Assistant:**
> "Got it — framing this as a heroic-aftermath shot: she's won, the sun rises behind her, rubble at her feet. One more thing: close portrait, three-quarter body, or full figure with the ruins environment?"

**User:** "Full figure, show the ruins and the dawn sky."

**Assistant:**
> "Perfect. Here's how I'm reading it: a defiant new warrior woman in ornate bronze armor, full-figure among dawn-lit ruins, cinematic and triumphant. Building that now."

Then the assistant delivers the complete four-part output:

#### 🎯 Positive prompt (SDXL / RealVisXL, tags-first, ~110 words)

```text
cinematic full-body photograph, a defiant warrior woman standing victorious among
ancient crumbling stone ruins, ornate engraved bronze plate armor, long dark
braided hair catching the wind, determined triumphant expression, early dawn light
cresting the horizon directly behind her, warm golden rim lighting, soft
atmospheric haze, scattered rubble and broken pillars at her feet, dramatic sky
with deep orange and soft pink gradients, shallow depth of field, 35mm lens,
photorealistic, highly detailed skin texture, intricate metal detailing,
volumetric god rays, epic heroic composition, color-graded film still
```

#### 🚫 Negative prompt (photoreal SDXL template, customized)

```text
(worst quality:1.4), (low quality:1.4), blurry, out of focus, deformed, bad anatomy,
bad hands, malformed fingers, extra fingers, missing fingers, fused limbs, text,
watermark, signature, logo, 3d render, cgi, cartoon, anime, plastic skin, airbrushed,
oversaturated, modern clothing, jeans, sneakers, wristwatch, sunglasses, cluttered
background, harsh midday sun, jpeg artifacts
```

#### ⚙️ Recommended settings

| Parameter | Value | Valid range / why |
|-----------|-------|-------------------|
| Model | RealVisXL V5.0 (SDXL) | Photoreal SDXL checkpoint; strongest at cinematic lighting and full-figure anatomy without a trained LoRA. |
| Sampler | `DPM++ 2M Karras` | Deterministic, converges cleanly by ~30 steps; avoids the seed-to-seed drift of ancestral samplers on full-body shots. |
| Steps | 30 | 25–35 is the SDXL sweet spot. Below 22 the armor engraving smears; above 40 wastes compute for no visible gain. |
| CFG scale | 5.5 | Stay 4.0–7.0 for photoreal SDXL. Above ~7 over-saturates and "fries" skin; below ~4 the model ignores the armor detail. |
| Resolution | 832×1216 px | Native SDXL 2:3 portrait (≈ 1.0 MP), correct for a standing full figure. Off-ratio (e.g., 512×768) or > 1.5 MP native triggers duplicated limbs/body-doubling. |
| Face fix | `FaceDetailer`, denoise 0.40, bbox 0.50 | Recovers the eyes after upscale. Skip if her face is < 128 px in frame — below that it invents detail that won't match. |
| Upscale | `4x-UltraSharp` @ 2.0×, denoise 0.35 | Denoise > 0.5 invents a new face; 0.30–0.40 sharpens the engraved-armor texture without changing identity. |
| Identity method | None | New character with no references — let the checkpoint design her. |
| LoRA | None (optional: cinematic-film style LoRA @ 0.4–0.6) | Above ~0.7 a style LoRA overpowers anatomy and warps the armor plating. |

#### 🔧 Pipeline recommendation

> Single-pass SDXL with a light detailing tail. RealVisXL V5.0 → KSampler (`DPM++ 2M Karras`, 30 steps, CFG 5.5) at 832×1216 → `FaceDetailer` at denoise 0.40 to recover the eyes → upscale with `4x-UltraSharp` at 2.0× and denoise 0.35 for the engraved-armor texture. No identity lock is needed because she's a new character, so the graph stays fast (~15s on a 4090) and you can iterate seeds freely until the dawn rim-light reads heroic rather than flat. If you later want her recurring, train a LoRA from your favorite renders and switch the LoRA cell on.

Then the assistant offers next steps (build the workflow / refine the prompt / save as a character profile).

## Pitfalls

- **Re-asking what was already stated.** If the user said "cinematic portrait," do not ask "is this a person?" or "what's the framing?" — infer from their words. Re-asking signals you weren't listening and erodes trust.
- **Dumping all questions at once.** A wall of 7 questions feels like a form. Ask 1–2 at a time, in conversational language. Never present the numbered checklist to the user.
- **Exceeding 7 exchanges.** Past 4–7 exchanges you're polishing details the user doesn't care about. Stop the moment you have enough to write an excellent prompt.
- **Quality tags on FLUX.** "masterpiece", "8k", "best quality" actively hurt FLUX because its T5 encoder never associated them with quality. These tags are for SDXL/SD1.5 only.
- **Describing facial features when using InstantID/InfiniteYou.** Describing the face fights the reference image and muddies the result. Let the identity method own the face.
- **Long prompts on SD 1.5.** SD1.5 has a 77-token context limit; long prompts get truncated or dilute the signal. Keep SD1.5 prompts to 30–80 words.
- **Verbose video prompts.** Wan/video models need motion-focused descriptions; verbosity competes with the motion description the model actually needs. Keep to 20–50 words.
- **LoRA trigger word not first.** If a LoRA trigger word is buried mid-prompt, surrounding tokens can truncate or down-weight it. Place it first.
- **Style LoRA strength too high.** Above ~0.7 a style LoRA overrides the prompt's specific color story and flattens the palette. Keep style LoRAs ≤ 0.6.
- **Off-ratio or oversized resolution on SDXL.** Off-ratio (e.g., 512×768) or > 1.5 MP native triggers duplicated limbs/body-doubling. Stay at native SDXL ≈ 1.0 MP.
- **Upscale denoise too high.** Denoise > 0.5 invents new detail and can warp faces or signage. Keep upscale denoise at 0.25–0.40.
- **FLUX negative prompt treated as active.** On FLUX.1-dev at default guidance (1.0), the negative prompt is inert. Don't waste a long negative on FLUX unless you switch to a CFG-capable sampler (≈ 2× render time).
- **Claiming to have generated an image.** This skill only outputs the prompt-and-settings specification. Never claim to have rendered the actual image.
- **Asking irrelevant questions for the creation type.** Asking a landscape generator about "clothing" or a product shot about "expression" wastes an exchange. Branch by type first.

## Verification

Confirm the interview and synthesized prompt against this checklist before delivering to the user:

- [ ] Interview stayed within 4–7 exchanges and asked high-impact questions first.
- [ ] Questions were branched by creation type (portrait / scene / product / abstract / video) — no irrelevant questions asked.
- [ ] Nothing inferable from the user's concept was re-asked.
- [ ] The vision was reflected back (Step 5) and confirmed before synthesis.
- [ ] All four output components delivered: positive prompt, negative prompt, settings table, pipeline recommendation.
- [ ] Positive prompt formatted for the target model (SDXL tags-first / FLUX natural language / SD1.5 weighted / Wan motion-focused) — no quality tags on FLUX.
- [ ] Trigger word placed first when a LoRA applies; facial features omitted when InstantID/InfiniteYou handles identity.
- [ ] Settings table gives exact values with their valid ranges and failure modes (not bare numbers).
- [ ] Model/pipeline recommendation matches the Decision Rules table for the user's stated goal.
- [ ] Next-step offer made (build workflow / refine prompt / save character profile).

```text
# Quick verification pass
1. Confirm creation type detected and only relevant questions asked (<= 7 exchanges).
2. Confirm the vision summary was reflected back and approved.
3. Check the positive prompt matches target-model rules (no "masterpiece" on FLUX; tags-first on SDXL).
4. Check the negative template matches the medium (photoreal / FLUX-minimal / video) and is customized with the user's exclusions.
5. Verify the settings table is complete (model, sampler, steps, CFG/guidance, resolution, identity/LoRA if used) and every value carries a range + failure mode.
6. Verify the pipeline recommendation maps to a known pattern and the model-selection table, and explains *why* it fits this concept.
7. Offer next steps (workflow build / refine / save profile) only after all four components are delivered.
```

## Related skills

- `comfyui-prompt-engineer` — Applies the model-specific prompt rules (FLUX / SDXL / SD1.5 / Wan syntax, quality tags, negative templates, CFG) that this interview feeds its synthesized vision into. Use it when an existing prompt underperforms and needs diagnosis.
- `comfyui-character-gen` — Builds the identity-preserving workflow / node graph (InfiniteYou, FLUX Kontext, PuLID, InstantID, IP-Adapter) recommended at the end of the interview. Use it when the user wants the actual runnable workflow, not just the prompt.
