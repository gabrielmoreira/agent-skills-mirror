---
name: transition
description: >-
  Remotion, CSS, and ffmpeg transition recipes (whip pans, zoom ramps, glitch
  cuts, film burns, parallax) for quote films and Shorts. Use when building
  QuoteLong/QuoteShort beat-synced cuts or caption motion language. Not for
  Remotion project setup and render (remotion-video) and not the /effects
  content-type matrix (inspire-quote-effects).
---

# Transition skill (quote / cinematic Shorts)

## When to use

- Remotion compositions with sequential beats (quotes, chapters, stills)
- User hates long static holds / Ken-Burns-only edits
- Need a repeatable transition language for Inspire to Rise / YT Videos packs

## Hard pacing rules (2025–2026 retention)

| Rule | Value |
|------|--------|
| Gap between quotes | **0.8–1.5s** max (never 10–20s pads) |
| Target long quote film | **6–8 min** unless density justifies longer |
| Cold open | 2–3s hook motion + 1 line |
| Breath beat | Black flash / film burn every ~90s (6–10 frames) |
| Ken Burns alone | Max ~20% of beats — pair with real transitions |

## Trend stack (quote / motivation)

- Hook-heavy first 3s; micro-motion always on screen
- Kinetic / word-reveal captions (1–3 words/line)
- Motivated transitions (whip, zoom snap, light-leak) + whoosh SFX
- Sound design: whoosh on cut, impact on power word, music ducked under VO
- Cinematic grade + film grain (subtle)
- **Likeness:** when user opts in → real archive photos/video (see `inspire-quote-effects`); otherwise Path B = no IP likeness

## Remotion transition types

Prefer `@remotion/transitions` `TransitionSeries` + presentations:

| Name | Use | Typical frames @30fps |
|------|-----|------------------------|
| `fade` | Soft emotional handoff | 10–15 |
| `slide` / whip | Energy / chapter change | 12–18 |
| `wipe` | Symbolic directional change | 12–16 |
| SpeedRampZoom (custom) | Push into next still | 8–12 |
| RGBGlitchCut (custom) | Doubt / conflict beats | 3–6 |
| FilmBurn (custom CSS) | Breath / act break | 18–24 |
| BlackFlashBreath | Mid-film reset | 6–10 |
| ParallaxPush | Cold open / ambient | beat duration |

### Beat mapping (default quote film)

1. Cold open → Parallax / slow fade  
2. Quote → quote: alternate WhipPan / SpeedRampZoom / fade  
3. Doubt / villain line → RGBGlitchCut (low)  
4. Every ~5th cut → FilmBurn  
5. Before SM1 lock → BlackFlashBreath (short)  
6. Final → SpeedRampZoom out + fade to black  

## Caption preset

- Font: Bebas Neue / Anton / strong sans — uppercase  
- Word reveal synced to VO window  
- Accent color on `powerWord` (Neon Dawn gold `#F5C16C` or crimson `#E11D48`)  
- Drop shadow `0 4px 12px rgba(0,0,0,0.8)`; light stroke OK  
- No heavy cards in hero quote region  

## Audio mix

| Layer | Level |
|-------|--------|
| VO | 0 dB target (~−14 LUFS master) |
| Music under VO | ~−18 to −24 dB (duck) |
| Transition SFX | whoosh −12 dB, impact −10 dB |
| Ambience | −28 dB |

## Project layout (YT Videos quote pack)

```
remotion/src/components/transitions/   # WhipPan, SpeedRampZoom, RGBGlitch, FilmBurn, …
remotion/src/components/CaptionWordReveal.tsx
remotion/public/sfx/whoosh.mp3
remotion/src/lib/timelineLong.ts       # transitionIn per beat
```

## Anti-patterns

- 18–20s silence pads to fake “10 minutes”
- Ken Burns only with static full-block quote cards
- Transition spam every frame (keep 0.3–0.6s cuts)
- Marvel suit/mask on Path B packs
- **Hard `Sequence` stacks with only overlay flashes** called “transitions” — FAIL. Multi-beat films need `@remotion/transitions` `TransitionSeries` (or equivalent timed presentations) between beats.
- Shipping quote edits without Cursor **`/effects`** gates + **`/reviewresults`**

## Sibling skills

- `inspire-quote-effects` + Cursor **`/effects`** → primary quote Remotion effects command (matrix, archive, gates)
- `review-results` + **`/reviewresults`** → exit gate after render
- `yt-shorts-flow-director` → Flow generation  
- `remotion-shorts` → assemble Shorts / GPU  
- `effects` (FFmpeg catalog) → optional filter recipes, not Remotion spine  
- `shorts-audio-mix-master` → loudnorm / ducking when present  
