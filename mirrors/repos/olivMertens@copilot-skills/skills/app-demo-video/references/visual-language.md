# Visual language reference

The established "exec cut" look, implemented by `assets/scene-components.jsx`.
Reuse these conventions verbatim; only the content (copy, screenshots, colors,
voice) changes per project. Composition: **1920×1080, fps 30**.

## Palette (override in `assets/shared.jsx`)
- `NAVY_DARK` `#0a1230` — outer background
- `NAVY` `#0f183d` — gradient inner
- `TEAL` `#2dd4bf` — accent 1 (kicker dot/label, pills border, badge)
- `AMBER` `#e8a84a` — accent 2 (secondary pills)
- Body text `#c8d6e6`, footer `#7f92ad`

## Background
Radial gradient `radial-gradient(1200px 700px at 50% 24%, NAVY, NAVY_DARK)`
that slowly scales `1 → ~1.07` over the first ~210 frames — a subtle "breathing"
motion. This supplies all ambient movement, so you do **not** need Ken-Burns pans
on real screen-recording clips (those read as fake).

## Per-scene layout (top → bottom)
1. **Kicker** — small teal dot + bold uppercase teal label, pill-outlined.
2. **Headline** — 46px bold white, centered.
3. **Subtitle** — 22px `#c8d6e6`, centered, `maxWidth` ~1240px. Must NOT
   paraphrase text already visible in the screenshot at the same moment.
4. **Pill tags** — 2–3 short amber-outlined chips (name the underlying tech /
   the concrete benefit).
5. **Screenshot card** — rounded 14px, `boxShadow 0 30px 70px rgba(0,0,0,0.55)`,
   **`marginTop: 28`** (hard convention so titles "breathe" above the card).
   Optional accent **badge** on the top-right corner to spotlight one number.

## Entrance animation
Shared `useCinematicIn(delayFrames, fps)` — spring scale `1.18→1`, blur `10→0`,
opacity `0→1` over ~12 frames. Stagger delays: kicker 0, headline 6, subtitle 12,
pills 18, card 24. A settled frame is ~frame 150 (render stills there).

## Ken Burns (screenshot cards only, never on text/numbers)
`useKenBurns(sceneDuration, 1, 1.045, 8, startFrame)` — gentle zoom + tiny drift
that starts when the card fades in. **Pass the scene's own duration**: inside a
`Series.Sequence`, `useVideoConfig().durationInFrames` returns the whole
composition length, so a raw call barely moves.

## Two-panel comparisons
- Stacked "BEFORE"/"AFTER" cards (~1480px wide, arrow glyph between) when both
  panels must be individually legible.
- Side-by-side "IN THE APP"/"EXPORTED PDF" with an arrow when comparing an app
  view to an artifact.

## Footer
One constant line across every scene, translated per language (e.g.
"AI-assisted underwriting · Microsoft Azure"). Name concrete Azure services
(Azure AI Foundry, Azure OpenAI, Azure AI Content Understanding, Azure Speech)
in kickers/subtitles/pills where relevant — concrete tech names build credibility.

## Reusing broll across language variants
`assets/shared.jsx` ships `CroppedVideo` for real screen-recording broll (crop a
fixed rect out of footage without ffmpeg math). If broll exists for one language
but not another, do **not** fake a re-recording — substitute the equivalent
static screenshot (`Img`), cropped/sized the same way, and note the substitution
in the deliverable summary.

## Standing content rules
- Never use "LIVE ·" / "live capture" wording, nor "NEW ·" / "NOUVEAU ·" kicker
  prefixes. Describe capabilities plainly ("Real application" / "Application réelle").
- One scene = one new idea; each sentence transitions to the next scene.
- Use native vocabulary, never word-for-word translations.
