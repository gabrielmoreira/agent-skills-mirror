---
name: general-video
description: >
  Use as the fallback for custom HyperFrames HTML video composition authoring
  when no specialized workflow fits. Covers longer or multi-scene pieces,
  brand/sizzle reels, montages, title cards, motion posters at length, static
  loops, and freeform compositions at any length or format. Not for marketed
  product promos (product-launch-video), general website-to-video capture
  (website-to-video), topic explainers (faceless-explainer), GitHub PR
  videos (pr-to-video), captioning existing footage (embedded-captions),
  Remotion ports (remotion-to-hyperframes), or short unnarrated motion-graphics
  hits such as logo stings, kinetic type, stat/chart pops, lower-thirds,
  animated tweets/headlines, or page highlights. If a specialized workflow clearly fits the input, prefer it
  (see /hyperframes-read-first); use this only as the input/length-agnostic fallback.
metadata: { "tags": "orchestrator, general-video, fallback, freeform, composition-authoring" }
---

# general-video — general composition authoring

> **Confirm the route before you build.** This is the **fallback** for custom composition authoring. If the input clearly fits a specialized workflow, prefer it: marketed product → `/product-launch-video`; general site → `/website-to-video`; topic explainer → `/faceless-explainer`; GitHub PR → `/pr-to-video`; existing footage → `/embedded-captions` · `/graphic-overlays`; short unnarrated motion graphic → `/motion-graphics`; Remotion port → `/remotion-to-hyperframes`. **Out of scope**: live / at-render-time data, NLE-style editing of a finished video, or producing footage HyperFrames can't capture. Unsure? **Read `/hyperframes-read-first` first.**

**Build exactly what was asked.** A title card is a title card — not a title card + three supporting scenes + ambient music + captions. If extra scenes or elements would genuinely improve the piece, _propose_ them; don't add them silently. For small edits (fix a color, adjust one duration, add one element), skip the planning steps and go straight to the build.

## Approach

### Discovery — open-ended requests only

For vague, exploratory requests ("make something for our brand", "a cool intro") — understand intent before picking colors:

- **Audience** — who watches? developers / executives / general consumers?
- **Platform** — where does it play? social (15s) / website hero / product demo / internal?
- **Priority** — what matters most? motion quality / content accuracy / brand fidelity / speed?
- **Variations** — one best shot, or 2-3 meaningfully different options (different pacing, energy, or structure — not just color swaps)?

For specific requests ("add a title card", "fix the timing on scene 3"), skip discovery.

### Step 1 — Design system → `hyperframes-creative`

Establish the visual identity first. If the project has a design spec, read it (precedence `frame.md` → `design.md` → `DESIGN.md`; treat it as brand truth — exact colors, fonts, constraints).

**If no spec exists, you MUST read BOTH `hyperframes-creative/references/house-style.md` AND `hyperframes-creative/references/video-composition.md` before choosing any color or font.** `house-style.md` gives the "interpret the prompt / generate real content" opener, lazy-default list, and layer recipe; `video-composition.md` gives the video-medium density / scale / **foreground detailing** (data bars, registration marks, monospace metadata, "8-10 elements, two the user didn't ask for") that separates "produced" from "generated." Reading only one is the most common miss — `video-composition.md` is the one agents skip, and it is exactly the one that prevents flat, centered, web-page-looking output. Do not self-invent a palette and skip these; crossing into `hyperframes-creative` is mandatory here, not an optional branch. From there, also pull a named style/mood → `references/visual-styles.md`, or the interactive picker → `references/design-picker.md`, as needed. The spec/style defines the **brand**, not the composition rules.

**Find the angle (vague brief, no spec):** before picking colors, write ONE sentence — what does this name/word/topic evoke, and what visual _world_ (metaphor, setting, instrument, motif) expresses it? E.g. a cybersecurity tool → vault doors / perimeter scan lines / lock tumblers; a meditation app → tide, breath, slow light bloom. Read the _meaning_ of the subject, not just its letters; pick a concrete angle over a literal restyle. This is the cheap substitute for prompt expansion (Step 2) on single-scene pieces, where expansion is correctly skipped — and it is the difference between a designed concept and a generic logo-on-a-gradient.

<HARD-GATE>
Before writing ANY composition HTML, verify you have ALL FOUR:
1. **A visual identity** grounded in the spec or `house-style.md` — not invented on the spot. (Reaching for `#333`, `#3b82f6`, or `Roboto`? You skipped it.)
2. **A one-sentence concept angle** (the "find the angle" step) for anything beyond a trivial edit — not a literal restyle of the prompt words.
3. **A font pairing from the embed list** (`hyperframes-creative/references/typography.md` → "Fonts that embed") chosen on purpose — not `Inter`/`Helvetica Neue`/`system-ui` by default, and never an un-embedded display font you're just hoping renders (un-bundled names embed only if auto-captured locally — and cloud renders won't capture them).
4. **A foreground/density plan from `video-composition.md`** — the anchor-to-edges, 8-10-elements, foreground-metadata, background-texture rules. (Centered stack on a flat color with fewer than ~6 elements and no edge-anchored detail? You skipped it — that is the generic tell.)
</HARD-GATE>

### Step 2 — Prompt expansion → `hyperframes-creative`

Run for every multi-scene composition (skip for single-scene pieces and trivial edits). Ground the request against the design spec + house style into a consistent intermediate that downstream work reads the same way. See `hyperframes-creative/references/prompt-expansion.md`.

### Step 3 — Plan

Before writing HTML, think at a high level:

1. **What** — the viewer experience: narrative arc, key moments, emotional beats.
2. **Structure** — how many compositions, sub-comp vs inline, which tracks carry video / audio / overlays / captions. For the monolithic-single-file vs modular-sub-comp call, see `hyperframes-core/references/composition-patterns.md` § Two Architectures (rule of thumb: ≥3 hard scene cuts, or any reused scene → modularize; a short single-scene piece stays one file).
3. **Rhythm** — name the pattern before implementing (e.g. `fast-fast-SLOW-SHADER-hold`); see `hyperframes-creative/references/beat-direction.md`.
4. **Timing** — which clips drive duration, where transitions land, the pacing.
5. **Layout** — build the end state first (see below).
6. **Animate** — then add motion via `hyperframes-animation`.

## Layout Before Animation

Position every element where it sits at its **most visible moment** — fully entered, correctly placed, not yet exiting. Write that as static HTML + CSS first. **No GSAP yet.**

**Why:** if you position elements at their animated start state (offscreen, scaled to 0, opacity 0) and tween to where you _think_ they land, you are guessing the final layout — overlaps stay invisible until render. Build the end state first and you see and fix layout problems before adding motion.

1. **Identify the hero frame** for each scene — the moment the most elements are simultaneously visible. That is the layout you build.
2. **Write static CSS** for that frame. The content container must fill the scene with padding, not absolute offsets:

```css
.scene-content {
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 100%;
  height: 100%;
  padding: 120px 160px; /* padding positions content; fills any scene size */
  gap: 24px;
  box-sizing: border-box;
}
```

Never use `position: absolute; top: Npx` on a content container — it overflows when content is taller than the space. Reserve absolute positioning for decoratives.

> ⚠ **The `width/height: 100%` above only resolves if every ancestor has a resolved height.** The root `<div data-composition-id>` and any wrapper between it and `.scene-content` must be sized (`position: relative; width: 1920px; height: 1080px` on the root — see `hyperframes-core` → "Root must be sized"). Skip this and the flex container collapses to ~0, content piles into the **top-left corner**, and the first glyph clips at x=0 — while `lint`/`inspect` still report 0 issues. And **always keep the `padding`** (≥80px) on `.scene-content`: it is the title-safe margin. Never replace it with bare `gap`.

3. **Add entrances** — animate FROM offscreen/invisible TO the CSS position with `gsap.from()` (in sub-compositions prefer `gsap.fromTo()` so the start state is explicit; see `hyperframes-core/references/sub-compositions.md`). The CSS position is ground truth; the tween is the journey to it.
4. **Exits are transition-handled** — per the scene-transition rules in `hyperframes-animation/transitions/`, only the **final** scene animates elements out; between scenes the transition IS the exit.

**Shared space across time:** if element A exits before element B enters in the same area, both still need correct CSS positions for their respective hero frames — timeline ordering keeps them from coexisting, and the layout step catches accidental overlap. Layered glows/shadows and z-stacked depth are _intentional_ overlap; the step is about catching _unintentional_ collisions (two headlines on top of each other, content bleeding off-frame).

## Build — delegate to the domain skills

This maps the skill's full surface (see the `description`) to its references — non-exhaustive; when an intent isn't listed, route through `hyperframes-creative` (look/concept), `hyperframes-animation` (motion), `hyperframes-core` (contract), `hyperframes-media` (audio/captions). **The first row is ADDITIVE — read it AND your intent row, not one or the other.**

| Building…                                                             | Read first (in order)                                                                                                                                                       |
| --------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **ALWAYS — every non-trivial piece, on top of your intent row below** | `hyperframes-creative/references/house-style.md` + `references/video-composition.md` (also gated in Step 1 / HARD-GATE; the "produced, not generated" foreground detailing) |
| **Kinetic typography / text-forward**                                 | `hyperframes-animation/techniques.md` (kinetic type) + `adapters/gsap-easing-and-stagger.md` + `rules/kinetic-beat-slam.md`                                                 |
| **Title card / lower-third / overlay / PiP / text-behind-subject**    | `hyperframes-creative/references/composition-patterns.md` + (for the centered/sized frame) `hyperframes-core` → "Root must be sized"                                        |
| **Logo / brand-mark reveal**                                          | `hyperframes-animation/rules/svg-path-draw.md` (draw-on) + `rules/3d-text-depth-layers.md` + `rules/scale-swap-transition.md`                                               |
| **Data / stats / numbers**                                            | `hyperframes-animation/rules/counting-dynamic-scale.md` + `rules/stat-bars-and-fills.md` + `hyperframes-creative/references/data-in-motion.md`                              |
| **Product / app / UI demo**                                           | `hyperframes-animation/rules/3d-page-scroll.md` + `rules/cursor-click-ripple.md` + `rules/press-release-spring.md`                                                          |
| **Audio-reactive / music-driven**                                     | `hyperframes-creative/references/audio-reactive.md` (pre-extract bands; map to motion)                                                                                      |
| **Narrated / voiceover / captions / subtitles**                       | `hyperframes-media` (`tts`, `transcribe`, caption authoring) → place assets via `hyperframes-core`                                                                          |
| **Multi-scene / transitions**                                         | `hyperframes-animation/transitions/overview.md` **then** `transitions/catalog.md` (you are not done after the overview — the GSAP recipe is in the catalog)                 |
| **Modular / sub-compositions**                                        | `hyperframes-core/references/composition-patterns.md` + `references/sub-compositions.md`                                                                                    |

## Output checklist → `hyperframes-cli`

- [ ] `npx hyperframes lint` and `npx hyperframes validate` pass (block on results)
- [ ] design adherence verified if a spec (`frame.md` / `design.md`) exists — checklist in `hyperframes-creative/references/design-adherence.md`
- [ ] `npx hyperframes inspect` passes, or every overflow is intentionally marked
- [ ] contrast warnings addressed; for multi-scene work, review the animation map (`hyperframes-animation/scripts/animation-map.mjs`)
- [ ] deliver the preview; render to MP4 only on explicit request
- [ ] surface the preview **only at handoff** (it is the stable, final preview); don't pop one mid-build — build-phase snapshots are headless

## Not this workflow

- A specific **product / company / SaaS / website** being marketed, launched, or promoted → `/product-launch-video`
- A **concept / topic / article / how-X-works** being explained, no product → `/faceless-explainer`
- A **GitHub PR / code change** → `/pr-to-video`
- An **existing talking-head video** to add captions to → `/embedded-captions`
- Porting an existing **Remotion** composition → `/remotion-to-hyperframes`
- Cutting / editing a **finished video file** like an NLE → out of scope (HyperFrames composites HTML and media into a deterministic timeline; it does not edit footage)
