---
name: video-prompt-engineering-2026
description: "Directs 2026 T2V/I2V models (Veo 3, Sora, Kling, Runway Gen-4, Vidu, Hailuo, Luma, Pika) with shot recipes: subject/action/setting/camera/style channels, motion budget, negatives, and model-specific grammar. Use when writing or debugging generative video prompts rather than still-image copy. Not for ffmpeg assembly, screenwriting, Blender/Unreal, lip-sync reenactment, or calling the generation API; never spend the motion budget on unspecified camera wander."
version: 1.0.1
---

# Video Prompt Engineering 2026

## Overview

Prompting a 2026 video model is **directing, not describing**. A still-image prompt answers *what is in the frame*; a video prompt must also answer *what changes over time* and *how the camera observes it*. The model allocates a finite budget of **motion** and **coherence** across the clip. If you do not direct that budget, it spends motion on hallucination — drifting textures, morphing anatomy, a wandering camera.

**Governing discipline:** spend the motion budget deliberately — lock what must stay still, specify what must move, name how the camera moves — then suppress everything else.

**Self-contained package.** This skill folder contains only `SKILL.md`. There are no `scripts/`, `references/`, or `assets/` subfolders. Do not invent local helper paths. All procedures, templates, and checklists below are self-contained in this file.

## When to Use

Activate this skill whenever the job-to-be-done is **directing a generative video model with language** — turning an intent ("a detective walks into a neon-lit alley, camera tracks behind her") into a **prompt plus parameters** that a 2026 text-to-video (T2V) or image-to-video (I2V) model will render as a deliberate, coherent shot across the clip's full duration.

This skill begins where **motion** begins and ends at a **shippable shot recipe**: full positive prompt, negative/suppression block, motion and camera settings, duration/aspect/fps, seed, and (when used) anchor frame paths. It does not write the story, does not call the generation API, and does not cut the timeline — it **directs the frame over time** so generation and assembly have a single clear contract per clip.

### Trigger keywords

text-to-video, T2V, image-to-video, I2V, Veo, Veo 3, Sora, Kling, Runway, Gen-4, Vidu, Hailuo, MiniMax, Luma, Dream Machine, Pika, video prompt, camera motion, dolly, tracking shot, crane, pan, tilt, orbit, motion scale, motion strength, negative prompt video, temporal coherence, morphing, sliding feet, keyframe motion, cinematic shot, establishing shot, Motion Brush, first last frame, push-in, pull-out, handheld, locked-off, whip pan, FPV.

### Concrete trigger examples

- "Write a Veo 3 / Sora / Kling / Runway Gen-4 / Vidu / Hailuo / Luma / Pika prompt for [scene]."
- "Turn this image into a video — slow push-in, character turns her head."
- "My generation has morphing hands / sliding feet / the background melts / mid-clip teleport — fix the prompt."
- "Direct a cinematic sequence: establishing, then close-up, then tracking" (as *separate* one-shot prompts).
- "Control the camera: crane-up reveal / whip-pan / slow dolly / orbit / locked-off."
- "Match the look of shot A in shot B" (style/lighting/lens continuity).
- "Set motion intensity / camera-move strength / how do I use `--motion` or the motion slider?"
- "Write a negative prompt to kill warping, flicker, and extra limbs."
- "Which model for [photoreal dialogue / fast action / anime / long landscape], and how do I prompt it?"
- "Safety filter rejected my prompt — rewrite while keeping intent."

### Sitational conditions that raise priority

- Output is a **shot or sequence of shots** with intended camera language, not a random clip.
- Mode is **I2V** and motion must be choreographed *from* a fixed anchor frame.
- Draft was rejected as "it looks AI" — usually motion, coherence, or camera-control failure.
- **Continuity across clips** matters (same character, lighting, lens feel).
- You must **select among models** and use model-specific grammar, not generic adjectives.

### When NOT to use this skill

| Out of scope | Route to |
|---|---|
| **ffmpeg / post encode** (mux, transcode, concat, color-space, subtitle burn-in) | Media pipeline — hand off *after* generation |
| **Screenwriting** (story, dialogue, arcs) | Writing skill — this skill consumes a beat and turns it into a *shot prompt* |
| **Traditional 3D / offline renderers** (Blender, Unreal, Maya) | Geometry is the source of truth; no diffusion prompt |
| **Still-image only** (character sheets, style locks, single frames) | Image-production skills; lock keyframe there → drive with I2V *here* |
| **Lip-sync reenactment** (MuseTalk, LivePortrait) | Dedicated driving stack, not T2V/I2V prompting |
| **NLE editorial** (cut timing, sound design, final grade of a timeline) | Post, not generation |
| **Shot-list / continuity bible authoring** for multi-scene pieces | `cinematic-shot-listing-and-continuity` produces the manifest; this skill phrases each row for a model |
| **API submit → poll → download only** | `video-generation-api` / provider skills — after the recipe exists |

## Prerequisites

- Access to at least one 2026 T2V/I2V model (Veo 3, Sora, Kling, Runway Gen-4, Vidu, Hailuo, Luma, Pika) or its API/UI.
- For I2V workflows: a clean anchor still (good subject/background separation, unoccluded face/hands, correct identity/style/lighting). Generate anchor stills via image-production skills if needed.
- For multi-shot continuity: a shot list or continuity bible from `cinematic-shot-listing-and-continuity` before per-shot phrasing begins.
- Windows host is primary (PowerShell). No local scripts are required — all procedures are self-contained.

## Procedure

### Step 1 — Lock one shot intent

Before writing any prompt text, define the shot boundary:

1. **One camera, one continuous action, one duration.** If the beat contains a cut, two locations, or three simultaneous primary actions, decompose into separate shots now.
2. **Choose T2V vs I2V.** Use I2V when identity, composition, or lighting must match a known frame. Use T2V for imaginative or greenfield scenes.
3. **Choose target model.** See the model temperament table below. Re-verify live capabilities (duration caps, audio, first/last-frame, Motion Brush) before production — product surfaces change.
4. **Define duration.** Default to 4–8 seconds per take (peak coherence window). Longer beats → multiple takes, stitch in post.

### Step 2 — Fill the five channels

Every reliable 2026 video prompt is five ordered **channels**. Keep them mentally separate even when written as flowing prose; each owns a different failure mode.

| Channel | Answers | Owns failure of… | Example tokens |
|---|---|---|---|
| **Subject** | Who/what is the focus | identity drift, subject morphing | "a silver-haired female astronaut," "a vintage red coupe" |
| **Action** | What happens over time | temporal incoherence, no/too-much motion | "slowly removes her helmet," "drifts around the corner" |
| **Setting** | Where / when / atmosphere | background melt, scene instability | "a rain-slicked Tokyo alley at night," "a dawn salt flat" |
| **Cinematography** | How the camera sees it (size, lens, move, fps feel) | camera wander, wrong scale, jitter | "low-angle medium close-up, 35mm, slow dolly-in" |
| **Style** | Rendered look (medium, grade, era, mood) | look inconsistency, off-tone | "cinematic, teal-orange grade, anamorphic, shot on film" |

**Canonical order:** Subject → Action → Style / Setting → Cinematography. Swap Style and Setting when one dominates mood. Front-load the least-negotiable element (usually Subject + the single key Action). Models weight earlier tokens more heavily; a camera move buried at the end of a 90-word prompt is often ignored.

**Channel anti-patterns:**

| Anti-pattern | Why it fails | Fix |
|---|---|---|
| Vague subject ("someone," "a person") | Model invents extras and identity | Count and specify: "a single woman in a red coat" |
| Three primary actions in one prompt | Motion budget fragments; mid-clip teleport | One primary action; demote the rest to secondary motion (hair, steam) |
| Setting only as "beautiful city" | Background melts | Concrete architecture, time of day, weather |
| "Move the camera dramatically" | Unmotivated drift | One named move + speed |
| Style keyword soup (`masterpiece, 8k, ultra detailed…`) | Dilutes real constraints | Prefer lighting/lens/grade terms that change the image |

### Step 3 — Set motion magnitude deliberately

Most platforms expose an explicit or implicit **motion intensity** control: how much the model may move per unit time.

| Control type | Models (typical) | How to drive |
|---|---|---|
| **Numeric / enum** | Kling, Runway, Pika, Luma (varies) | UI slider or param: 1–10, 1–100, or low/medium/high. **Always confirm the scale** — "5" on 1–10 is moderate; "5" on 1–100 is nearly static |
| **Language-driven** | Veo, Sora | Verbs/adverbs *are* the slider: drifts/glides/slowly/gentle = low; races/whips/explosively/rapid = high |

**Magnitude heuristic:**

1. Start **low-to-moderate**.
2. Climb only if the shot reads dead.
3. Prefer reading action through **camera move** rather than subject thrash.
4. Blowout (too high) is more common and uglier than deadness — warping, smear, subject "swimming."
5. **I2V defaults lower than T2V** — the frame is already correct.

**Mental scale (map to platform after confirming units):**

| Intent | Language cues | Rough 1–10 | Rough 1–100 |
|---|---|---|---|
| Near-static portrait | "nearly static," "imperceptible," "minimal" | 1–2 | 5–15 |
| Living still / gentle life | "slow," "gentle," "subtle drift" | 2–4 | 15–35 |
| Standard cinematic | "smooth," "moderate," deliberate action | 4–6 | 35–55 |
| Action / chase | "fast," "dynamic," "running speed" | 6–8 | 55–80 |
| Extreme / whip / crash | "rapid," "explosive," "whip" | 8–10 | 80–100 |

### Step 4 — Name the camera move and speed

Models trained on captioned cinematography respond to **real camera vocabulary**. Vague "move the camera" → unmotivated drift.

| Move | Means | Prompt phrasing |
|---|---|---|
| **Pan** | Horizontal rotation, fixed pivot | "camera pans left to reveal…" |
| **Tilt** | Vertical rotation, fixed pivot | "camera tilts up from her boots to her face" |
| **Dolly / Push-in / Pull-out** | Camera *translates* toward/away | "slow dolly-in," "pull back to reveal the room" |
| **Truck / Track** | Lateral translation, often following | "tracking shot moving left, following the runner" |
| **Pedestal** | Vertical translation without tilt | "camera pedestals up over the desk" |
| **Crane / Jib / Boom** | Large sweeping vertical + arc | "crane up and back to a high wide shot" |
| **Zoom** | Optical focal-length change (flatter than dolly) | "slow zoom in" — choose deliberately vs dolly |
| **Orbit / Arc** | Circles the subject | "camera orbits 180° around the statue" |
| **Roll / Dutch** | Rotation around lens axis | "subtle dutch roll for unease" |
| **Handheld** | Organic micro-shake | "handheld, subtle natural shake" |
| **Static / Locked-off** | Tripod, no camera motion | "static locked-off shot" — *force* stillness |
| **Whip pan / Crash zoom** | Very fast pan/zoom | "whip-pan right" — high budget; expect blur |
| **FPV / Drone** | Flying first-person or aerial | "FPV drone shot diving through the canyon" |

**Two hard rules:**

1. **Name the speed** — "slow," "smooth," "rapid," "gentle." Velocity is a separate axis from move type.
2. **One primary camera move per shot.** Stacking pan + tilt + zoom + orbit → mush. Complex move = multiple shots.

**Direction ambiguity:** "camera pans left" vs "subject moves left" confuses models; left/right may resolve from camera POV or subject POV. Disambiguate:

> "the camera pans to the left, revealing the door on the right side of the frame"

Verify direction on a first generation before mass-producing.

### Step 5 — State shot size and angle

| Size | Frames | Use |
|---|---|---|
| **EWS / extreme wide** | Vast landscape; subject tiny | Scale, world establish |
| **WS / wide** | Full figure + environment | Geography of the scene |
| **FS / full** | Head-to-toe | Body language, blocking |
| **MS / medium** | Waist up | Conversation default |
| **MCU / medium close-up** | Chest to head | Dialogue intimacy |
| **CU / close-up** | Face fills frame | Emotion |
| **ECU / extreme close-up** | Eyes, hands, object | Detail / insert |

| Angle | Connotation |
|---|---|
| Eye-level | Neutral |
| Low angle | Power, threat, heroism |
| High angle | Vulnerability, surveillance |
| Overhead / bird's-eye | Abstraction, pattern |
| Dutch / canted | Unease |
| OTS / POV | Relationship / subjectivity |

State **size + angle + one move + speed** in every shot prompt (or explicit locked-off).

### Step 6 — Specify lighting and color vocabulary

Lighting is half of "cinematic." Prefer professional terms over mood adjectives alone.

- **Quality / direction:** soft / hard light; key, fill, rim/backlight; motivated lighting; golden-hour; blue-hour; overcast; high-key; low-key; chiaroscuro; practicals (neon, lamps, screens).
- **Color / grade:** teal-and-orange; desaturated; monochrome; warm tungsten; cool moonlight; sodium-vapor orange; bleach-bypass; technicolor; "shot on 35mm film, subtle grain."
- **Lens / format:** anamorphic (horizontal flares, oval bokeh); shallow DOF / bokeh; wide-angle; telephoto compression; macro; 24fps cinematic vs 60fps hyperreal; "shot on [camera/lens]" cues.
- **Atmosphere:** volumetric light / god rays; haze; fog; lens flare; bloom; dust motes; rain; snow — production value *and* coherent secondary motion that masks minor instability.

**Continuity rule:** keep lighting/grade/lens tokens in the **Style** channel and freeze them *verbatim* across sibling shots. Vary content and camera; do not casually rewrite the look-tail.

### Step 7 — For I2V, spend tokens on Action + Camera + invariants only

I2V is the **highest-control** production mode in 2026: the first frame locks identity, composition, lighting, and style. The model only animates *outward*.

| Rule | Detail |
|---|---|
| **Image = what; prompt = how it moves** | Drop most Subject/Setting/Style prose; spend tokens on **Action + Camera** |
| **Strong anchors constrain harder** | Clean composition, clear subject/background separation, unoccluded face/hands → stable motion |
| **First/last-frame interpolation** | Kling, Luma, Pika, others: author both endpoints; model fills the in-between. Use when destination state matters |
| **Motion Brush / region mask** | Runway and peers: paint *where* motion is allowed and *direction*; freeze the rest (open door, ripple water, drift clouds) |
| **Clamp magnitude low** | Over-driving I2V melts a perfect anchor |

**I2V contradiction trap:** never prompt an action that fights the still (e.g. "sprints" when the image shows a seated person). That is a fast path to warping. Change the still, or choose a plausible micro-action from the pose.

### Step 8 — Write negatives or in-prompt prohibitions

Suppress the failure modes the model is prone to. Cover at minimum:

- Morphing / warping / melting anatomy
- Extra limbs / fused fingers / duplicated subjects
- Foot sliding / skating
- Background melt / scene pop / mid-clip teleport
- Flicker / jitter / texture shimmer
- Watermark / on-screen text / subtitles / captions
- Camera wander / unmotivated drift

Anchor invariants in **positive** form: "her face and outfit remain identical; the background architecture stays fixed."

### Step 9 — Freeze the style/lighting tail across sibling shots

For multi-shot sequences, copy the Style channel tokens **verbatim** from shot to shot. Vary only content and camera. Use the same model/version and seed family. Share I2V reference images when a character recurs.

### Step 10 — Record a reproducible recipe

Before shipping, record:

- Model + version
- Mode (T2V / I2V / first-last / Motion Brush)
- Anchor frame path(s) if I2V
- Full positive prompt
- Full negative / suppression block
- All parameters: motion value + confirmed scale, camera setting, fps, resolution, aspect ratio, duration, seed
- Any UI panel settings (Motion Brush regions, camera sliders)

### Step 11 — Run the verification gate

See the **Verification** section below. Do not ship until every applicable item passes.

## Model-by-model temperament (2026)

Prompt each model for its bias. Re-verify live capabilities (duration caps, audio, first/last-frame, Motion Brush) before production recommendations — product surfaces change.

| Model | Strengths | Prompt style | Best for |
|---|---|---|---|
| **Google Veo 3** | Prose comprehension; native **synced audio** (dialogue, SFX, ambience); physical realism | Rich **paragraph** natural language; explicit cinematography; optional dialogue in quotes + sound design | Photoreal, dialogue-driven, grounded shots |
| **OpenAI Sora (2-class)** | Long descriptive narrative prompts; world coherence; imaginative scenes | Detailed cinematic paragraphs; language is the slider (few numeric knobs) | Stylized, surreal, or photoreal single takes |
| **Kling (2.x)** | Motion realism; **camera controls**, motion settings, **start/end frame** | Concise structured fields + UI motion/camera params | Fast physical action; precise I2V |
| **Runway Gen-4** | Camera sliders, **Motion Brush**, reference consistency | Short **directive** prompts + on-canvas controls | Controlled I2V, regional motion, production control |
| **Vidu / Vidu 2** | Character/reference consistency; dynamic stylized/anime motion | Explicit camera + motion; style lock early | Anime/stylized character work |
| **Hailuo (MiniMax)** | Aesthetic + director/camera following; often strong cost/quality | Clear beats + camera instructions | Bulk aesthetic clips, camera-led shots |
| **Luma (Dream Machine)** | Fluid natural motion; keyframe first/last; solid I2V | Action + camera; lean magnitude | Naturalistic I2V, interpolations |
| **Pika** | Accessible I2V; quick iterations | Short directive + motion params | Prototyping, quick I2V iterations |

## Examples

### T2V template (general)

```text
[Subject, counted and specific] [single primary Action, with speed adverb] in [concrete Setting with
architecture, time, weather]. [Shot size + angle], [one named camera move + speed], [lens/format].
[Style: medium, grade, era, mood, lighting direction/quality]. [Invariants: what stays fixed].
[Secondary motion: hair, steam, cloth, dust]. No morphing, no warping, no extra limbs, no foot
sliding, no background melt, no flicker, no watermark, no on-screen text.
```

### I2V template (anchor-driven)

```text
[Action + Camera only — what moves, how, how fast]. [Invariants: face, outfit, identity, background
architecture — remains identical and stable]. Minimal motion, no morphing, no warping.
```

### Runway Motion Brush note (pair with short prompt)

```text
Prompt: [short directive]
Motion Brush: paint [regions]; direction [vector]; strength [high on subject / low on bg]
Camera: [panel]
```

### Worked example — Veo 3 T2V

```text
A single woman in a red wool coat walks briskly through a rain-slicked Tokyo alley at night,
her reflection shimmering in puddles. Medium shot, eye-level, slow tracking shot moving right
to left, following her from behind, 35mm anamorphic, shallow depth of field. Cinematic
teal-and-orange grade, neon practicals reflecting on wet surfaces, volumetric haze, shot on
film with subtle grain. Her face and outfit remain identical throughout; the background
architecture stays fixed. Secondary motion: rain streaks, steam from a vent, her coat
billowing slightly. No morphing, no warping, no extra limbs, no foot sliding, no background
melt, no flicker, no watermark, no on-screen text.
```

### Worked example — Kling I2V from anchor still

```text
The woman slowly turns her head to the right, looking toward the neon sign. Camera pushes
in gently over 4 seconds. Her face, hair, outfit, and the alley architecture remain identical
and stable. Minimal motion, no morphing, no warping.
```

## Pitfalls

### Structural pitfalls

| Failure mode | Typical cause | Fix |
|---|---|---|
| **Mid-clip teleport / scene pop** | Prompt implied sequence/cut | "single continuous take, one camera, no cuts"; **decompose into separate shots**; remove second location/action |
| **Three primary actions in one prompt** | Motion budget fragments | One primary action; demote rest to secondary motion |
| **Camera move ignored / wanders** | Buried or vague camera line; stacked moves | Front-load one named move + speed; use panel param; drop competing moves |
| **Camera direction inverted** | Ambiguous left/right POV | Disambiguate camera-POV + what enters frame; test one gen; flip term if model is consistent |

### Motion / coherence pitfalls

| Failure mode | Typical cause | Fix |
|---|---|---|
| **Morphing limbs / hands melting / fingers fusing** | Motion too high; hands small/fast; complex articulation | Lower motion; "stable consistent anatomy, no morphing"; keep hands larger/slower; simplify action; I2V from clean hands-visible anchor |
| **Sliding / gliding feet (foot skating)** | Gait not grounded; budget on body not footfalls | "feet firmly planted with each step, weight on each footfall, no foot sliding"; slow subject; I2V or first/last to lock stride; lower motion |
| **Temporal float / subject swims** | Over-motion; no invariants; weak scene | Clamp motion; "subject stays centered and stable, background fixed"; shorten clip; lower I2V strength |
| **Background melt** | Aggressive camera; thin setting; high motion | Slow camera; concrete setting; "background architecture stays static"; Motion Brush freeze bg |
| **Flicker / texture shimmer** | Fine detail (foliage, fabric, text) + motion; high fps | Reduce motion; avoid dense fine texture; "no flickering, stable textures"; try 24fps over 60 |
| **Motion-scale blowout** | Wrong numeric scale (50 on 1–100 thinking 1–10) | Re-confirm scale; halve value; "smooth, controlled, minimal motion"; prefer camera-led action |
| **Dead / static clip** | Magnitude too low; no actionable verb | Raise modestly; add micro-motion (blink, hair, steam); gentle camera life |

### Content / safety pitfalls

| Failure mode | Typical cause | Fix |
|---|---|---|
| **Extra people / wrong objects / invented text** | Under-constrained scene; vague nouns | Tighten subject + counts; negative "duplicate subjects, extra people, text, watermark"; shorten, front-load keys |
| **Safety filter reject** | Violence, real public figures, brands, sensitive terms | Cinematic abstraction; generic roles not named people; drop brands; rights/consent for real likeness; no deception |
| **Burned-in subtitles appear** | Training bias on captioned clips | "(no subtitles, no on-screen text, no captions)"; avoid quote-only dialogue without anti-caption line |

### I2V-specific pitfalls

| Failure mode | Typical cause | Fix |
|---|---|---|
| **I2V melts perfect anchor** | I2V motion too high | Drop to minimum; Motion Brush localized; first/last interpolation |
| **I2V warps because action fights still** | Prompted motion impossible from pose | Change action to plausible micro-motion or regenerate anchor pose |

### Continuity pitfalls

| Failure mode | Typical cause | Fix |
|---|---|---|
| **Sequence continuity breaks** | Style/lighting/lens rewritten; different models/seeds | Freeze style tail verbatim; same model/version; shared I2V reference; reuse recipe |
| **Lip-sync / dialogue mismatch** | Line too long; mouth under-constrained | Shorten dialogue; Veo quotes + delivery; precise lip-sync → reenactment pipeline |
| **Multi-shot morph soup** | Hard cuts on single-shot model | Confirm multi-shot support; else one continuous action only; cut in post |

### Cross-cutting recovery order (always)

1. Fix **input** (anchor quality, action complexity, motion scale, one-shot constraint).
2. Fix **mechanism** (T2V → I2V → first/last → Motion Brush → different model) after three failed re-rolls.
3. Fix **wording** last (channel order, invariants, negatives).
4. Re-run the verification gate; discard off-target clips — do not ship them.

## Verification

Do not ship a video prompt (or sequence package) until every applicable item passes. Hard gate, not a suggestion.

### Prompt structure & subject clarity

- [ ] **All five channels present and ordered** — Subject, Action, Setting, Cinematography, Style — most important front-loaded.
- [ ] **Subject unambiguous and counted** — no vague nouns that invite extras.
- [ ] **Exactly one shot, one camera, one continuous take** — no implied cut, second location, or sequence smuggled in.
- [ ] **Single concrete primary action** (not three simultaneous primaries).

### Cinematography & motion control

- [ ] **Shot size and angle stated** (wide/medium/close-up; eye-level/low/high/dutch).
- [ ] **Exactly one primary camera move named with a speed** — or explicit "static locked-off."
- [ ] **Camera direction disambiguated** (camera-POV vs subject-POV) and verified on a first gen before mass production.
- [ ] **Motion magnitude deliberate**; numeric value matches **confirmed scale** (1–10 vs 1–100 vs enum); default low, climb only if dead.
- [ ] **fps / resolution / aspect / duration** set to model-native values and coherence budget (default 4–8 s per take).

### Look & continuity

- [ ] **Lighting and color/grade** specified with professional vocabulary.
- [ ] **Style tail frozen verbatim** across sibling shots; identity via I2V/reference when a character recurs.

### I2V (when applicable)

- [ ] **Anchor clean** (separation, unoccluded face/hands, exact identity/style/lighting).
- [ ] **Prompt spends on Action+Camera only**; translation/rotation named; **invariants stated**.
- [ ] **First/last or Motion Brush** used when destination or regional motion matters; **I2V motion clamped low**.
- [ ] Action is **physically plausible from the still**.

### Suppression & safety

- [ ] **Negative prompt or in-prompt prohibitions** cover morphing/warping, anatomy, flicker/jitter, foot-sliding, melt, duplicates, watermark/text, scene-cut.
- [ ] **Invariants anchored** in positive form.
- [ ] **No unauthorized real-person likeness or brands**; policy-safe intent; rights/consent confirmed where real people appear (no impersonation/deception).

### Production / reproducibility

- [ ] **Recipe recorded** — model+version, mode, anchors, full prompt + negative, all parameters (motion + scale, camera setting, fps, res, AR, duration, seed).
- [ ] **Handoff identified** — stitch/encode/grade/caption skill receives the clip(s); generative prompting stops at the clip boundary.
- [ ] **Off-target results discarded** — every delivered clip passes artifact checks (no morphing, no skating, no pops, intended camera move present).

If any box fails: identify the failure mode in the Pitfalls table, **fix the input first**, switch mechanism if three re-rolls fail, regenerate the affected shot, re-run the gate. Ship only fully passing shots or sequences.

## Related skills

| Need | Route |
|---|---|
| Multi-scene shot list + continuity bible | `cinematic-shot-listing-and-continuity` → then return here per shot |
| API submit / poll / download multi-vendor | `video-generation-api` / provider API skills |
| Full story → multi-clip film pipeline | `story-to-video` / `video-ai-production` (call this skill for per-clip craft) |
| Google Flow / Veo UI automation | `google-flow-veo` |
| Still character/style anchors | image-production / consistent-character skills |
| Lip-sync reenactment | dedicated lipsync / avatar pipeline |
| Concat, encode, filter existing MP4s | `video-processing-pipeline` / ffmpeg skills |
| Captions / kinetic type on finished footage | `kinetic-typography-and-captions` |

This skill remains the **per-shot directing and model-grammar craft layer** those pipelines call into.

## Mental model (one line)

**Direct the motion budget:** one shot, one camera, one action — lock invariants, name the move and its speed, clamp magnitude, suppress artifacts, freeze the look-tail across siblings, and record the recipe so the same intent regenerates the same directed clip.
