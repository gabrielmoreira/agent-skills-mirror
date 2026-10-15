# Composition / lighting / motion receptors (deep criteria)

> Supports **COMP-***, **LIGHT-***, **MOT-*** in [taste-receptors.md](taste-receptors.md).
> Still WebP is primary; use a **2–8 frame sequence** when MOT / hit-peak / shake decay is ambiguous.

---

## Still vs sequence

| Signal | Still enough? | Sequence when |
|--------|---------------|---------------|
| Thirds, lines, depth, silhouette | Yes | Camera pan changes focal |
| Motivated light / rim lottery | Usually | Flicker / TOD blend |
| Bloom / DOF mush | Yes | Threshold ramps |
| Hit spark peak | Partial | Peak &lt;90ms |
| Screen shake | Partial (offset) | Confirm decay + UI re-anchor |
| Squash / UI overshoot | Mid-pose tell | Confirm settle |

---

## Composition (COMP-*)

### Power points vs HUD

Rule of thirds is a **guide**. **COMP-POWER-CONFLICT** is a hard readability fail: crosshair + telegraph + CTA competing at one third → **0**.

| Receptor | PASS | FAIL |
|----------|------|------|
| COMP-THIRD-ACTION | Subject near intersection / framed | Dead center with no reason |
| COMP-THIRD-HUD | Persistent HUD on edges | HP sits on power point |
| COMP-CENTER-CLEAR | ~60% center free | Center chrome + combat |
| COMP-MASS-EDGE | Heavy chrome at edges | Edge + center both heavy |
| COMP-SAFE-EDGE | Critical inside safe margins | Clipped / bezel-adjacent |

### Leading lines & value

- **COMP-LEAD-ENV / LIGHT / UI** — Tracks, shafts, rails aim at intent; competing rails → 0.
- **COMP-VALUE-GROUP / COMP-FOCAL-*** — Subject pops in mental B/W; hue-only focal → 0.
- **COMP-DEPTH-LAYERS** — FG/MG/BG separation; flat single plane → 0.
- **COMP-SIL-ACTION / THREAT** — Limbs and telegraphs readable as fill.
- **COMP-NEG-SPACE / BALANCE / HORIZ / FRAME / SCAN / DIEG-META** — Breath, intentional mass, level or owned dutch, env framing, predictable scan, meta ≠ HUD replacement.

---

## Lighting / FX (LIGHT-*)

Juice layers must **obey** hierarchy — not replace it.

### Motivated light

| Receptor | PASS | FAIL |
|----------|------|------|
| LIGHT-MOTIV | Shared key vector | Sourceless wash |
| LIGHT-KEY-FILL | Form readable | Crushed mud |
| LIGHT-RIM-OWN | Rim supports sep | Identical rim on all assets |
| LIGHT-PLAY-SEP | Interactive layer pops | Player melts into BG |

### Bloom / DOF / post

| Receptor | PASS | FAIL |
|----------|------|------|
| LIGHT-BLOOM-HIER | Bloom on story beats only | Bloom = hierarchy |
| LIGHT-BLOOM-ABUSE | Edges preserved | Detail mush |
| LIGHT-DOF-SUBJ / UI | Subject sharp; HUD sharp | Gameplay or UI blurred |
| LIGHT-POST-STACK | ≤2 dominant posts | AO+bloom+DOF+CA+grain scream |

### Particles / hit / vignette

| Receptor | PASS | FAIL |
|----------|------|------|
| LIGHT-PART-READ | Sparks explain direction/material | Semantic-free noise |
| LIGHT-PART-OCCLUDE | FX clear of HP/ammo/crosshair | Particles cover HUD |
| LIGHT-PART-OVER | Impact ≤~12–18% viewport | Screen-filling soft quads |
| LIGHT-FX-LANE | Telegraph ≠ flourish hue | Same lane |
| LIGHT-HIT-SPARK / FLASH / SCALE | Consistent color; brief flash; L/M/H tiers | Rainbow; full white; uniform max |
| LIGHT-VIGN-DMG / META | Edge vignette; shape backup | Eats center/UI; color-only low HP |
| LIGHT-EMISS-HIER / SPEC-LOT | Emissive for danger/interact; consistent spec | Every prop emissive; shiny lottery |

---

## Motion tells in stills (MOT-*)

Freeze-frames leak motion grammar.

| Receptor | PASS | FAIL |
|----------|------|------|
| MOT-BLUR-READ / SMEAR | Direction clear; vector smear | Omnidirectional mush |
| MOT-TRAIL-SOUP / GHOST | Short trails; sparse ghosts | Trail soup; clone soup |
| MOT-SQUASH / STRETCH / VOL | Volume law holds | Inflating blob |
| MOT-ANTIC | Wind-up readable | No telegraph |
| MOT-SHAKE-OFF / TIER / ROT | UI re-anchors; tiered; minimal roll | HUD floats; coin=boss; sickness roll |
| MOT-HITSTOP | Micro-freeze | Slideshow freeze |
| MOT-TWEEN-OS / UI-BOUNCE | Settles on grid; ≤~1.05/0.95 | Buttons off baseline; oversized bounce |

---

## Co-occurrence → SLOP

| Slop cluster | COMP/LIGHT/MOT co-tells |
|--------------|-------------------------|
| SLOP-NEON | LIGHT-BLOOM-ABUSE + LIGHT-BLOOM-HIER=0 |
| SLOP-RIM | LIGHT-RIM-OWN=0 |
| SLOP-SMOOTH | LIGHT-SPEC-LOT=0 + ORIG-STRUCT soft |
| SLOP-EQUAL | COMP-FOCAL-SINGLE=0 + COMP-MASS-EDGE=0 |

---

## Sources

- GDC / Game Developer — leading lines (Ethan Carter), level design tips, animation principles
- GameJuice — screen shake, shader juice / hit flash
- LearnOpenGL — physically based bloom
- GamineAI — top-down combat VFX readability (lanes, occupancy)
- Magnopus / composition craft — value grouping, focal clarity
