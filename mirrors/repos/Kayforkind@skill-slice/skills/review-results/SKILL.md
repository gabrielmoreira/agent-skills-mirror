---
name: review-results
description: >-
  Evidence-based PASS/FAIL exit gate for sensory deliverables (video, UI, audio,
  SVG, packs): Read every visual sample, quarantine fakes, require regenerate.
  Use when the user runs /reviewresults, after Remotion/ffmpeg/effects renders,
  or as /scale wave gates. Not for polish/harden loops (that is better) and not
  for generating the footage (localvideo or remotion-video).
---

# review-results

**Slash:** `/reviewresults`  
**This file** is the procedure. Follow `single` or `wave` mode as specified.

## Non-negotiables

1. No PASS without **Read** on every visual sample + written `$rev\reports\review.md`
2. **Never** tell the user a video is ready until `/reviewresults` returns **PASS** (or documented BLOCKER)
3. Immersion breaks are **HARD FAIL**, not soft notes
4. Wave mode mandatory for `/scale` sensory waves and N≥10 bulk sensory jobs

## Video craft HARD FAIL (must remediate)

| ID | Fail condition | Required fix |
|----|----------------|--------------|
| **A Fake text** | Gibberish / wrong / melted labels on image plates (newspapers, maps, signs, docs) | Quarantine asset → regenerate **text-free** `/localimage` **or** Remotion/SVG/real archive type |
| **B Maps** | Ugly / wrong / toy AI geography carrying the thesis | Remotion `MapCamera` / SVG / geoJSON / real map — remove AI map stills from timeline |
| **C Appeal** | Slop hero, mush blur, near-duplicate plates, unfinished vs pack best | Quarantine → regenerate or replace |
| **D Hook / end** | First ~12s no energy/premise; last ~20s no payoff | Story/edit fix — not more random stills |
| **E Toolkit** | KenBurns-only when energy needed | Add TransitionSeries overlays, light-leak/whip, SVG diagrams, FFmpeg grade, varied motion |

### Standing generation policy (review enforces)

- **Flux / Krea / diffusion:** text-free B-roll only (mines, jewelry, process, landscapes)
- **Readable words / stats:** Remotion, ASS, SVG — never diffusion typography
- **Maps:** programmatic or real archive — never AI-drawn finals

## Craft toolkit (review must consider)

Learned / preferred stack when a cut feels flat:

- Remotion: `interpolate` + bezier; `@remotion/transitions` TransitionSeries; light-leak **overlays** (do not shorten VO); kinetic type
- SVG / geo: maps, pins, process diagrams
- FFmpeg: grade, grain, vignette, transitions when outside Remotion (`effects` skill)
- Patterns from remotion-dev/skills, remotion-templates, remocn/remotion-bits — copy in-pack when useful

Document **Craft toolkit** used vs missing in `review.md`. Missing toolkit on a boring cut → FAIL rubric #19.

## Remediation loop

```
FAIL (§2.4 A–E)
  → list quarantine paths + reasons under $rev\quarantine\
  → replace (regen text-free still | Remotion/SVG/FFmpeg | story beat)
  → re-render
  → full /reviewresults again
```

Max 5 iterations → BLOCKER.md + ask user.  
Do **not** PASS with soft notes that belong in A–E.

## Modes

| Mode | Use |
|------|-----|
| `single` (default) | One ship candidate — full exit gate |
| `wave` | Bulk harness — same craft bar including A–E; fail_rate drives continue/shrink/STOP |

## Report must include

Deliverable + hash · samples · per-frame notes · **quarantine list** · **craft toolkit** · full rubric (incl. rows 14–19) · PASS/FAIL/BLOCKER
