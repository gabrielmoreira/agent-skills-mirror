---
name: creative-prompt-engineering
description: "Structures prompts for image/video generators: camera-first scaffolds, engine grammar (Runway, Midjourney --sref/--sw, Flux paragraphs, Kling beat windows, Luma + vectors, Veo/Flow anchors), weighted vs bare negatives, and draft-then-quality credit spend. Trigger on writing or repairing prompts, choosing an engine, artifact suffixes, or suppressing Veo speech for an external track. Not /identity-lock stacks (LoRA, IP-Adapter, contact sheets) and not timeline NLE assembly."
version: 1.0.1
last_verified: 2026-06
---

# Creative Prompt Engineering

A director's reference for prompting AI image and video generators. Provides recipes and the reasoning behind them so you can adapt when a model updates, a regional restriction changes, or a scene doesn't behave as expected.

> [!NOTE]
> Generative tooling moves fast. Model version numbers, tier names, exposed parameters (seeds, CFG, start-frames), and regional availability reflect the author's best snapshot, not a vendor-confirmed spec. Treat version-specific claims as starting points to verify in each vendor's current docs.

---

## When to Use

- Writing or debugging prompts for any supported image or video generator.
- Planning multi-shot video projects requiring character or environment consistency.
- Choosing which model fits a job (motion fidelity vs. lip-sync vs. budget).
- Suppressing artifacts, watermarks, unwanted native audio (Veo speech), or stuttery motion.
- Troubleshooting silent generation failures or degraded output.
- Building character bibles, continuity workflows, or bridge-frame pipelines.
- Optimizing credit spend across draft/quality tiers.

---

## Prerequisites

- Access to at least one generative platform (Runway, Midjourney, Flux, Kling, Luma, Veo/Flow, Seedance, Pika, Hailuo, Stable Diffusion, or the assistant's native `generate_image` tool).
- For post-processing: FFmpeg installed for audio stripping (`-an`) and splicing.
- For advanced inpainting/outpainting: Photoshop Generative Fill, ComfyUI, or AUTOMATIC1111 WebUI.
- For upscaling finals: Topaz Photo/Video AI, Real-ESRGAN, or Magnific.
- Windows host is primary (PowerShell). Path notes assume `~\agent-skills\library\creative-prompt-engineering\` as the skill root.

---

## Procedure

### 1. Universal Prompt Architecture

Generative models follow prompts more reliably when each part addresses one concern. Modern text encoders (CLIP for SDXL, T5 for Flux and Veo, model-specific encoders elsewhere) process prompts as ordered sequences where earlier tokens receive stronger conditioning weight, and adjacency is read as semantic association. Mixing camera, subject, and style into one run-on sentence forces the model to guess which words modify which.

**Default order:**

`[Camera Movement] → [Subject / Action] → [Environment] → [Optics & Lighting] → [Style / Genre] → [Technical Details]`

**Why this order:** Camera first frames *how we're seeing the scene* before *what's in it*, anchoring spatial reasoning. Subject and environment establish the scene. Optics and lighting modify an existing scene rather than compete for attention. Style and technical specs come last so they color the whole image instead of overriding composition.

This is a default, not a rule. Some prompts read more naturally subject-first; some short Midjourney prompts skip whole categories. Use it as a checklist for what might be missing — and as a structural lever when the model is specifically ignoring one element.

**Example:**

> "Slow dolly-in, low-angle tracking shot of a focused female astronaut in a white space suit walking through a dark, mist-filled volcanic crater. Rim lighting casts a bright halo. Volumetric fog glows blue. 35mm anamorphic film style, high contrast, photorealistic, 8K resolution."

### 2. Artifact Cleanup String

Append a cleanup suffix on text-to-video prompts to push the model away from training-distribution regions that produced watermarks, mangled text, and stuttery motion:

> `...hyper-realistic, 24fps, cinematic film grain, accurate physics, no artifacts, no text, no logos, no watermark.`

### 3. Negative Prompts

For photorealistic output, weighted negative prompts help on platforms that support weighting.

> [!IMPORTANT]
> The `(term:weight)` syntax below is SDXL / AUTOMATIC1111 / ComfyUI convention; weights above `1.0` increase avoidance pressure. **Most hosted video tools (Runway, Veo, Kling, Luma, Pika) expose a plain negative-prompt field with no weighting — paste the bare term and drop the `(...:1.3)` wrapper, or it will be read as literal text.**

- **Quality**: `(blurry:1.3), low quality, noise, jpeg artifacts`
- **Anatomy**: `(extra fingers:1.4), fused limbs, bad proportions, distorted face` — usually the highest-value negative, since hands and limbs remain a weak point even in recent diffusion models.
- **Aesthetic conflict**: `3D render, CGI, cartoon` — only useful when targeting photorealism; otherwise it fights your positive prompt.
- **Cleanup**: `watermark, text overlay, logo, border`

> [!NOTE]
> Treat negatives as nudges, not hard bans. When positive and negative collide ("cartoon style" in the positive and "cartoon" in the negative), the positive usually wins because it carries direct conditioning signal while the negative only steers sampling. If the negative term keeps appearing, raise its weight (where supported) or remove the conflicting positive cue rather than stacking more negatives.

### 4. Model-Specific Prompting

Each engine was trained on a different captioning regime, so identical prompts produce very different results. The notes below describe observed field behavior — practical heuristics, not internal facts.

#### Runway (Gen-3 / Gen-4 family)

- **Grammar**: responds best to direct, declarative shot descriptions written in the style of a script supervisor's notes. Conversational phrasing ("please show me...") dilutes the signal.
- **Motion verbs**: active present participles — *dissolving, melting, unfolding, stretching, blooming* — cue temporal change clearly and are reliable.
- **Example**:
  > "Crane shot rising up, showing a blooming rose growing and unfolding its petals rapidly. Vibrant red color. Morning sun rays, volumetric dust motes, macro lens."

#### Midjourney (V6 and later)

- **Style references**: `--sref [code]` locks aesthetic tone by pointing the model at a precomputed style embedding — the most reliable lever for batch visual consistency.
- **Style weighting**: `--sw [0–1000]` tunes how strongly that style overrides text. Low values (~100–300) preserve subject fidelity; higher (~700+) let style dominate.
- **Example**:
  > "A futuristic cyberpunk skyline at night --sref 1234567890 --sw 500"

#### Flux.1

- **Grammar**: Flux uses a T5 encoder that benefits from paragraph-length natural language. Short staccato prompts under-utilize it. Describe foreground first (where attention tends to concentrate), then midground, then background.
- **Optics**: naming camera bodies and lenses ("Hasselblad X2D, 85mm, f/2.8") triggers texture and depth-of-field patterns learned from professional-photography captions — a stronger signal than generic "high quality" phrasing.
- **Example**:
  > "A detailed close-up shot of a vintage silver pocket watch resting on a dark velvet cloth. The background is a warm, soft-focus library. Shot on Hasselblad X2D, f/2.8 aperture, 85mm lens, Rembrandt side lighting."

#### Kling (3.0 family)

- **Length**: rough field convention is 80–150 words. Shorter prompts give too much freedom; much longer prompts overflow attention and the tail gets ignored. Use as a starting band, not a rule.
- **Temporal markers**: Kling honors *coarse* segmentation (`0–2s: ...; 2–4s: ...`) better than most engines, useful for choreographing a beat or two. Sub-second adherence is unreliable; if you need frame-accurate timing, split into shorter clips and stitch.
- **Negative prompting**: the UI exposes a negative field; high-value entries include *flickering, frozen lips, extra limbs, warping hands.*

#### Luma Dream Machine / Ray

Luma supports two distinct camera modes — pick the one that matches your shot intent:

- **Lock the camera, animate the subject** — start the prompt with *"fixed viewpoint of"* or *"still camera shot of"*. Luma reads sentence-initial phrases as global scene constraints, so leading with this anchors the camera and lets subject action play out.
- **Compound camera motion** — Luma is one of the few engines that explicitly accepts vector combinations joined with `+`, e.g. *"slow orbit right + tilt up."* Use when layered camera motion is the point of the shot.

These are complementary, not contradictory: the first is for shots where the camera should hold still; the second is for shots where multiple camera moves are part of the design.

#### Google Flow & Veo 3

> [!IMPORTANT]
> **Veo is the model; Flow is Google's product wrapping it** (with Scene Builder, multi-shot orchestration, and a co-director assistant). Veo accessed via the Gemini API gives you the model without Flow's features. The advice below applies to Veo broadly; Scene Builder specifics apply only inside Flow.

- **Persistent anchors**: Flow's Scene Builder retains named entities across shots. Reusing the exact same character names, clothing colors, and environment phrases across prompts reduces continuity drift. Paraphrasing increases the risk that the reference resolver treats it as a different entity — it doesn't always break continuity, but it's the most common reason consistency suddenly fails.
- **Pacing**: Veo is notably responsive to rhythm tags ("slow", "snap", "frenetic"), useful for matching cuts to a beat.
- **Example**:
  > "High angle, wide tracking shot of a cute Pixar-style orange cat jumping excitedly onto a wooden table in a sunny kitchen. Vibrant colors, smooth 3D rendering, claymation style, playful mood."

##### Suppressing Veo's Native Speech (for music videos)

Veo generates audio alongside video, including dialogue. For music-video work where you'll overlay an external song, generated speech causes lip-sync mismatch.

**The principle**: Veo's audio pathway appears to be cued by verbs and nouns that imply *audible vocal production*. The cue affects both the audible track *and* the mouth-shape generation in the video, which is why audio-stripping alone doesn't fix the problem — the lips still form recognizable words that won't match your external track.

- **Avoid verbs that imply vocalization**: `singing`, `speaking`, `saying`, `reciting`, `chanting`, `rapping`, `narrating`, `yelling`, `whispering`, `humming`, `screaming`. Extend the principle to new verbs as you encounter them.
- **Use action verbs that describe expression without vocal production**: `performing expressively`, `moving to the rhythm`, `gazing emotionally`, `dancing`, `walking`, `lips parting softly`, `mouthing wordlessly`.
- **Append to negative prompt**: `no dialogue, no speech, no audible voice`.
- **Example (music-video close-up)**:
  > "Medium close-up of a young woman performing expressively on a dark stage, colorful spotlights sweeping across her face, lips parting softly as she gazes upward. No audible speech, no dialogue. Slow dolly-in, cinematic depth of field, concert lighting."

**Fallback order — primary fix first, then layered safety nets:**

1. **Verb swap (primary)** — only this prevents the *mouth movement* from generating recognizable speech shapes. Get this right or the video itself is unusable for lip-sync against external audio.
2. **Switch to I2V** with a still portrait — image-to-video pipelines suppress speech more reliably than pure T2V because the start frame removes the speech-implying context.
3. **Switch to a no-audio model** for that shot (Kling, Runway, Luma) — sidesteps Veo's audio pathway entirely.
4. **Strip audio in post** (FFmpeg `-an`) — always removes the audible track, but does *nothing* about wrong mouth shapes. Use as cleanup after the visual is right, not as the fix.

#### Native Image Generation (`generate_image` tool)

Useful for stills, UI mockups, logos, and product visuals. Art-direction discipline matters more than length.

- **UI mockups**: produce the interface alone — no laptop, phone, or hand frame — unless the user asks for context. Device frames eat resolution and force a re-crop.
- **Prompt structure**: `[Subject] + [Color palette / HSL accents] + [Aesthetic — e.g. glassmorphism, dark mode] + [Layout details] + [Medium tags — vector, 3D render, clean layout]`.
- **Example**:
  > "A sleek dark-mode dashboard UI for a smart home manager, glassmorphic card layout, glowing blue and violet ambient accents, minimalist icons, Outfit typography, clean interface, high-fidelity mockup."

### 5. Camera & Lighting Vocabulary

Film-industry vocabulary is over-represented in training captions, so professional terms give a tighter prior than vague descriptions. Saying "Rembrandt lighting" is far more specific than "nice side light on the face."

#### Camera Movements

| Term | Description | Best for |
| :--- | :--- | :--- |
| **Static / locked-off** | Camera stationary | Dialogue, contemplative beats |
| **Dolly in / out** | Camera moves toward / away from subject | Dramatic reveals, emotional close-ups |
| **Pan** | Camera rotates horizontally on a fixed axis | Establishing shots, horizontal motion |
| **Tilt** | Camera rotates vertically on a fixed axis | Tall structures, head-to-toe reveals |
| **Orbit / arc** | Camera moves in a circular path around the subject | 360° character or product reveals |
| **Tracking / follow** | Camera moves alongside a moving subject | Walking, running, chases |
| **Crane up / down** | Camera moves vertically through space | Grand reveals, establishing scale |
| **Dolly zoom (Vertigo)** | Zoom in while dollying out (or reverse) | Disorientation, psychological tension |
| **Rack focus** | Shift focal plane between depths | Redirecting attention without cutting |
| **Whip pan** | Very fast horizontal rotation, motion-blurred | Transitions, energy spikes |

**One primary camera move per shot** is the safer default. Stacking two complex movements (orbit + dolly zoom + crane up) makes the model interpolate competing motion vectors; current video models often resolve those conflicts by warping subjects or bending backgrounds. Adding a pacing modifier ("slow", "smooth", "rapid") to one dominant move usually looks cleaner than ambitious combinations.

**Exceptions worth knowing**: Luma is explicitly built for compound camera vectors via `+`. Runway and Kling handle compound motion better than they used to, but pick the move that matters most and only add a secondary one if the first generation looks too static.

Reliable scaffold: `[Camera direction] + [Pace] + [Subject action] + [Atmosphere]`.

#### Lighting Setups

- **Rembrandt lighting**: key light at ~45° creating a small triangle of light below the eye on the shadow side of the face. Reads as classical, intimate.
- **Rim / back lighting**: separates subject from background by haloing the silhouette. Worth trying on close-ups where you want strong subject–background separation.
- **High-key / low-key**: high-key fills the frame evenly (commercials, comedy); low-key keeps deep shadows (noir, horror).
- **Practical light**: lamps, screens, or fires visible in frame as the apparent source. Reads as grounded and naturalistic.
- **Volumetric lighting**: visible light rays through fog, dust, or smoke. Strong cinematic prior — but compositionally heavy, so don't stack with busy backgrounds.
- **Color temperature**: explicit Kelvin values are more predictable than vague adjectives. "Tungsten interior (3200K)" or "cool daylight (5600K)" steer reliably across models; words like "warm" or "cool" land differently across models, across seeds within one model, and across different parts of the same image. Use the Kelvin value when you care.

### 6. Effects & Transition Prompt Recipes

These are *prompt patterns*, not cinematography vocabulary. They tend to work across multiple video models with light editing.

- **Metamorphic morph**: `[Subject A] seamlessly morphing into [Subject B] using fluid organic transitions, volumetric light`
- **Particle disintegration**: `[Subject] disintegrating into a burst of glowing cosmic dust particles in slow motion, high contrast`
- **Glitch / datamosh**: `[Subject] with chromatic aberration, color channel separation, digital glitch art interference`
- **Liquid pour-in / reveal**: `liquid [material] pouring in and forming [subject], reflective surface, slow motion`
- **Shatter / freeze**: `[Subject] frozen mid-motion, then shattering into glass fragments, slow motion`

If a recipe doesn't trigger cleanly in T2V, switch to image-to-video and use a single keyframe of the desired end state to guide the model.

### 7. AI Video Model Selection (rough 2026 snapshot)

Pick by the strength you need to preserve — character likeness, motion fidelity, audio sync, or budget — rather than by familiarity. Versions and capabilities move fast; verify with vendor docs before committing.

| Model family | Typical strength | Notable feature | Licensing |
| :--- | :--- | :--- | :--- |
| **Veo (Gemini API)** | Overall quality, native audio | Strong text adherence | Proprietary |
| **Google Flow** | Multi-shot orchestration on top of Veo | Scene Builder, co-director assistant | Proprietary |
| **Kling** | Subject binding, lip-sync | Start/end-frame conditioning, longer continuous clips | Proprietary |
| **Runway Gen-4 family** | Character consistency from a single reference | World/object consistency engine | Proprietary |
| **Hailuo (Minimax)** | Human motion, dance | Physics simulation for complex bodies | Proprietary |
| **Seedance (ByteDance)** | Multi-modal input (text + image + audio + video) | Dual-channel audio | Proprietary |
| **Luma Ray / Dream Machine** | HDR, in-place edits, compound camera moves | Modify Video, Character Reference | Proprietary |
| **Pika** | Stylized effects (squish, melt, explode) | Pikaffects | Proprietary |
| **CogVideoX (Zhipu)** | Self-hosted, LoRA-trainable | Runs on a consumer GPU | Open source |
| **Wan (Alibaba)** | Open-source editing (VACE) | Pose transfer, video repainting | Open source |

> [!WARNING]
> **Capability preconditions vary across these platforms** in ways that affect what techniques you can actually use:
> - **Seed exposure**: reliable on Luma, Pika, CogVideoX, Wan, and most API access. Limited or absent on Veo (Gemini app), Kling consumer UI, Hailuo, and Seedance.
> - **Start-frame conditioning** (required for the Bridge Technique): supported on Kling, Runway Gen-3/Gen-4, Luma Ray, and most open-source pipelines. Not universally exposed on Veo/Flow surfaces or older Pika tiers.
> - **Regional availability**: Kling, Hailuo, Seedance, and Wan often require non-US payment methods, region settings, or VPN access. If a paid signup fails, regional restriction is the most likely cause before billing issues.

### 8. Continuity & Consistency Workflows

A model has no memory between generations. Continuity is something *you* impose with reference assets, seeds, and bridge frames.

#### Character Bible

For any project spanning multiple shots with a recurring character:

1. **Multi-angle references** — front, side, 3/4, and back. More angles let the reference encoder triangulate identity rather than guess at occluded features.
   - **Single-image fallback** (the common case): generate the missing angles before starting the bible. Run image-to-image against your one reference with prompts like *"same character, side view, same clothing, neutral lighting, full body"*. Stitch the synthesized angles in. They'll be slightly off-model, but more useful than asking the encoder to hallucinate angles from a single front view.
2. **Feature description (50–80 words, reused verbatim across shots)** — physical features, clothing, distinctive marks.
   - *Why ~50 words minimum*: shorter than that and the encoder lacks identity anchors; jaw shape, hair texture, distinctive marks each need an actual phrase to land.
   - *Why under ~80 words*: longer descriptions push the prompt past the point where shot-specific action and lighting fit cleanly, and the tail starts getting truncated or down-weighted on many models.
   - *Why verbatim*: paraphrasing introduces drift — a rewritten description may be treated as a different character. This is a tendency, not a guarantee; some models are more robust, but verbatim reuse is the safe default.
3. **Clothing and prop anchors** — describe distinctive garments and props in the same words every shot. If the character wears "a weathered brown leather jacket with brass buttons," use that exact phrase each time.
4. **Seed locking** — when the platform exposes seeds, lock the seed after the first acceptable generation and reuse it. Seeds constrain the noise initialization; same seed + same prompt + same model version = highly similar output. Different seed = different image even with identical prompt.

#### Bridge Technique (for shot-to-shot continuity)

When shot B needs to begin where shot A ended:

1. Extract the **last frame** of shot A (FFmpeg: `ffmpeg -i shotA.mp4 -vf "select=eq(n\,N-1)" -vframes 1 lastframeA.png` — replace `N-1` with the actual frame count minus one, or use `-sseof -0.1` for a simpler approach).
2. Use that frame as the **start frame (I2V)** for shot B's generation.
3. Prompt shot B's action beginning from that visual state.
4. This works on platforms with start-frame conditioning: Kling, Runway Gen-3/Gen-4, Luma Ray, and most open-source pipelines. Not universally exposed on Veo/Flow or older Pika tiers.

#### Environment Consistency

- Reuse the same environment description verbatim across shots set in the same location.
- Lock a style reference (`--sref` on Midjourney, style images on other platforms) for the duration of a scene.
- For physical environment props, describe them with the same material and color words each time.

### 9. Troubleshooting Silent Generation Failures

When a generation fails silently (no error, no output, or a blank/degraded result):

1. **Check prompt length** — if the tail is being ignored, the prompt may exceed the model's effective token window. Shorten by removing redundant descriptors.
2. **Check for conflicting cues** — a negative prompt that suppresses the very thing the positive prompt requests can sometimes suppress the entire generation. Remove the conflicting negative.
3. **Try one tier higher (or lower)** on the model's quality setting; some failures only occur at draft tier.
4. **Switch T2V to I2V** using a generated still as the anchor. Many failures vanish under I2V because the start frame removes scene ambiguity.
5. **Reduce ambition**: one camera move, one main subject, one light source.

### 10. Inpainting, Outpainting, and Upscaling

Choose the tool by the kind of control you need, not familiarity:

- **Photoshop Generative Fill** — fastest for ad-hoc fixes when you're already in Photoshop. Best for single-pass mask-and-fill on photos, especially backgrounds and small object removal.
- **ComfyUI** — most flexible, node-based; use when you need fine control over masks, model selection, inpainting strength, and parameter sweeps across an iterative pipeline.
- **AUTOMATIC1111 WebUI** — middle ground; more accessible than ComfyUI, more control than hosted tools. Good for batch inpainting with consistent settings.
- **Hosted tools (Magnific, Krea, etc.)** — use when you don't want to run anything locally and the job is straightforward (faces, hands, small swaps).
- **Outpainting** — extend the canvas beyond original bounds; useful for converting 1:1 stills into 16:9 or 9:16 for video work.
- **Upscaling** — for finals, run a dedicated upscaler (Topaz Photo/Video AI, Real-ESRGAN, Magnific) rather than re-rendering at higher resolution. Cheaper, faster, less drift.

### 11. Prompt Versioning

Iteration eats organization. The cheapest reproducibility win is logging, per render: the full prompt, the seed (if exposed), the model + tier, the platform's output ID or URL, and a one-line note on whether it's a keeper. A spreadsheet, a Notion table, or a markdown log all work — what matters is not having to ask "which prompt produced that one good frame?" three days later.

### 12. Credit & Cost Optimization

Generation platforms charge per render, and iteration is where credits evaporate. A two-tier workflow substantially reduces spend on most platforms without hurting final quality. Savings vary widely by platform and tier pricing — budget against your actual usage logs, not a fixed percentage.

- Use the **draft tier** for all iteration and storyboarding. Output is rough but reveals whether framing, motion, and identity are landing.
- Switch to the **quality tier** only for the final render of shots you've already validated at draft.

#### Tier name mapping

Vendors call the same idea different things. Rough current mappings:

| Platform | Draft / iteration tier | Quality / final tier |
| :--- | :--- | :--- |
| Google Flow / Veo | Fast | Quality |
| Kling | Standard | Pro / Master |
| Runway | Turbo | Gen-3 / Gen-4 Alpha |
| Luma Ray | Flash | Ray (default) |
| Pika | (varies by model) | Pro |
| Seedance | Lite | Pro |
| Midjourney | Fast / Draft mode | Standard |

Names change with releases — match by tier *position* (cheapest vs. flagship) rather than by remembered name.

#### Smaller habits that compound

- **Generate stills before videos.** T2I → I2V is almost always cheaper than blind T2V iteration.
  - *Exception*: a few platforms are T2V-only on their consumer surface (Veo via some Gemini entry points, certain Kling modes). There, batch low-cost T2V at draft tier instead of trying to force an I2V workflow that isn't exposed.
- **Batch seeds at draft tier**, pick the best, then re-render only that seed at quality tier.
- **Cache and reuse style references (`--sref`) and character images** across the project; don't regenerate them per shot.

---

## Pitfalls

- **Stacking complex camera moves** (orbit + dolly zoom + crane up) causes models to interpolate competing motion vectors, often resulting in warped subjects or bent backgrounds. Stick to one primary camera move per shot unless using Luma's explicit `+` compound syntax.
- **Using weighted negative prompt syntax on hosted video tools** — Runway, Veo, Kling, Luma, Pika expose a plain negative-prompt field. The `(term:1.3)` wrapper will be read as literal text. Paste bare terms only.
- **Positive-negative prompt collisions** — "cartoon style" in the positive and "cartoon" in the negative. The positive usually wins because it carries direct conditioning signal. Remove the conflicting positive cue rather than stacking more negatives.
- **Paraphrasing character descriptions across shots** — a rewritten description may be treated as a different character by the reference resolver. Reuse feature descriptions verbatim.
- **Character descriptions under 50 words** — the encoder lacks identity anchors. Jaw shape, hair texture, distinctive marks each need an actual phrase.
- **Character descriptions over 80 words** — pushes the prompt past where shot-specific action and lighting fit cleanly; the tail gets truncated or down-weighted.
- **Veo speech verbs in music-video prompts** — `singing`, `speaking`, `saying`, etc. cue both the audible track AND mouth-shape generation. Audio-stripping alone doesn't fix wrong lip shapes. Swap to non-vocal action verbs as the primary fix.
- **Vague color temperature words** — "warm" or "cool" land differently across models, seeds, and even within different parts of the same image. Use explicit Kelvin values (3200K, 5600K) when you care.
- **Volumetric lighting + busy backgrounds** — volumetric lighting is compositionally heavy. Don't stack with busy backgrounds.
- **Device frames in UI mockups** — laptop, phone, or hand frames eat resolution and force a re-crop. Produce the interface alone unless the user asks for context.
- **Re-rendering at higher resolution instead of upscaling** — dedicated upscalers (Topaz, Real-ESRGAN, Magnific) are cheaper, faster, and introduce less drift than re-rendering.
- **Regional availability assumptions** — Kling, Hailuo, Seedance, and Wan often require non-US payment methods, region settings, or VPN access. If a paid signup fails, regional restriction is the most likely cause before billing issues.
- **Trusting version-specific tier names** — vendors rename tiers between releases. Match by tier position (cheapest vs. flagship), not by remembered name.
- **Sub-second temporal markers in Kling** — Kling honors coarse segmentation (`0–2s: ...; 2–4s: ...`) but sub-second adherence is unreliable. Split into shorter clips and stitch for frame-accurate timing.
- **Forcing I2V on T2V-only platforms** — some Veo Gemini entry points and certain Kling modes are T2V-only on their consumer surface. Batch low-cost T2V at draft tier instead.

---

## Verification

### Prompt structure check

Verify your prompt follows the modular architecture by confirming each segment addresses one concern:

1. Camera movement is stated first (or early).
2. Subject/action is clearly separated from environment.
3. Optics and lighting come after subject and environment.
4. Style and technical details come last.
5. No run-on sentence mixing camera, subject, and style.

### Negative prompt syntax check

1. On SDXL / AUTOMATIC1111 / ComfyUI: confirm `(term:weight)` syntax is used with weights above `1.0` for avoidance.
2. On hosted video tools (Runway, Veo, Kling, Luma, Pika): confirm bare terms only — no `(...:1.3)` wrappers.

### Veo speech suppression check

1. Scan prompt for vocalization verbs: `singing`, `speaking`, `saying`, `reciting`, `chanting`, `rapping`, `narrating`, `yelling`, `whispering`, `humming`, `screaming`.
2. Replace with non-vocal action verbs: `performing expressively`, `moving to the rhythm`, `gazing emotionally`, `dancing`, `lips parting softly`, `mouthing wordlessly`.
3. Confirm negative prompt includes: `no dialogue, no speech, no audible voice`.
4. If mouth shapes still form recognizable words, switch to I2V with a still portrait or switch to a no-audio model (Kling, Runway, Luma).

### Bridge technique check

1. Confirm start-frame conditioning is supported on your target platform (Kling, Runway Gen-3/Gen-4, Luma Ray, open-source pipelines).
2. Extract last frame of shot A:
   ```powershell
   ffmpeg -i shotA.mp4 -sseof -0.1 -vframes 1 lastframeA.png
   ```
3. Use `lastframeA.png` as the start frame for shot B's I2V generation.

### Audio stripping (post-production cleanup)

```powershell
ffmpeg -i input.mp4 -c:v copy -an output_no_audio.mp4
```

Confirm: output file has video stream only, no audio stream (`ffmpeg -i output_no_audio.mp4` should show no `Stream #0:1` audio line).

### Credit optimization check

1. Confirm all iteration is happening at draft/cheapest tier.
2. Confirm quality/flagship tier is reserved for final renders only.
3. Confirm style references and character images are cached and reused, not regenerated per shot.

### Model selection check

1. Verify the chosen model's strength matches the job requirement (character consistency, motion fidelity, audio sync, or budget).
2. Verify seed exposure is available if your workflow requires seed locking.
3. Verify start-frame conditioning is available if your workflow requires the Bridge Technique.
4. Verify regional availability and payment method compatibility for the platform.

---

## Related Skills

- **video-editing-pipeline** — FFmpeg splicing, format conversion, and post-production assembly.
- **audio-generation** — TTS, voice cloning, and music generation (ElevenLabs, Suno, Udio).
- **stable-diffusion-workflows** — ComfyUI and AUTOMATIC1111 advanced pipelines, LoRA training, and parameter sweeps.

---

## Curated Sources

### Official model documentation

1. **Runway help center** — [help.runwayml.com](https://help.runwayml.com) — Gen-3/Gen-4 prompting guides, custom generator training.
2. **Midjourney docs** — [docs.midjourney.com](https://docs.midjourney.com) — Parameter syntax, style references, personalization.
3. **Black Forest Labs (FLUX)** — [blackforestlabs.ai](https://blackforestlabs.ai) — Model architecture and release notes.
4. **Flux on Hugging Face** — [huggingface.co/black-forest-labs](https://huggingface.co/black-forest-labs) — Model cards, recommended steps and CFG.
5. **Kling AI** — [klingai.com](https://klingai.com) — Product docs and community showcase.
6. **Luma Labs** — [lumalabs.ai](https://lumalabs.ai) — Dream Machine and Ray docs, camera controls.
7. **Stability AI** — [stability.ai](https://stability.ai) — SDXL and successor model docs.
8. **Pika** — [pika.art](https://pika.art) — Control parameters and effects catalog.
9. **AUTOMATIC1111 WebUI wiki** — [github.com/AUTOMATIC1111/stable-diffusion-webui/wiki](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki) — Sampling, CFG, weighted prompt syntax.
10. **ComfyUI AnimateDiff Evolved** — [github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved](https://github.com/Kosinkadink/ComfyUI-AnimateDiff-Evolved) — Latent walks and motion modules.
11. **ElevenLabs docs** — [elevenlabs.io/docs](https://elevenlabs.io/docs) — TTS, voice cloning, conversational agents.
12. **Suno** — [suno.com](https://suno.com) — Music generation product.
13. **Udio** — [udio.com](https://udio.com) — Music generation product.

### Cinematography & lighting reference

14. **StudioBinder cinematography** — [studiobinder.com/blog/category/cinematography](https://studiobinder.com/blog/category/cinematography) — Shot lists and breakdowns.
15. **American Cinematographer** — [ascmag.com](https://ascmag.com) — Professional lighting and lens articles.
16. **No Film School** — [nofilmschool.com/cinematography](https://nofilmschool.com/cinematography) — Practical cinematography tutorials.
17. **ShotDeck** — [shotdeck.com](https://shotdeck.com) — Searchable database of movie stills for composition reference.
18. **Roger Deakins forum** — [rogerdeakins.com/forum](https://rogerdeakins.com/forum) — DP discussion threads.

### Color, art direction, mood

19. **Adobe Color** — [color.adobe.com](https://color.adobe.com) — Color wheel and palette builder.
20. **MoMA Learning** — [moma.org/learn/moma_learning](https://moma.org/learn/moma_learning) — Modern art movements as style references.
21. **Tate art terms** — [tate.org.uk/art/art-terms](https://tate.org.uk/art/art-terms) — Aesthetic glossary.
22. **ArtStation** — [artstation.com](https://artstation.com) — Concept art for characters and environments.
23. **Pinterest** — [pinterest.com](https://pinterest.com) — Mood-board curation.

### Prompt communities and prompt galleries

24. **r/StableDiffusion** — [reddit.com/r/StableDiffusion](https://reddit.com/r/StableDiffusion) — Parameter and workflow discussion.
25. **r/midjourney** — [reddit.com/r/midjourney](https://reddit.com/r/midjourney) — Style reference (SREF) sharing.
26. **r/runwayml** — [reddit.com/r/runwayml](https://reddit.com/r/runwayml) — Video prompting tips.
27. **Civitai** — [civitai.com](https://civitai.com) — Checkpoints, LoRAs, prompt examples.
28. **Hugging Face** — [huggingface.co](https://huggingface.co) — Model cards and demos.
29. **PromptHero** — [prompthero.com](https://prompthero.com) — Searchable prompt database.

### Editing, audio sync, and pipeline tooling

30. **FFmpeg docs** — [ffmpeg.org/documentation.html](https://ffmpeg.org/documentation.html) — Splicing, format conversion, audio strip (`-an`).
31. **MoviePy** — [zulko.github.io/moviepy](https://zulko.github.io/moviepy) — Programmatic video editing in Python.
32. **Librosa** — [librosa.org/doc/latest](https://librosa.org/doc/latest) — Audio analysis and beat tracking.
33. **Remotion** — [remotion.dev/docs](https://remotion.dev/docs) — Render video timelines in React.
34. **GSAP** — [gsap.com/docs/v3](https://gsap.com/docs/v3) — Animation timeline sequencing.
35. **DaVinci Resolve** — [blackmagicdesign.com/products/davinciresolve](https://blackmagicdesign.com/products/davinciresolve) — Color grading, time remapping, final assembly.
