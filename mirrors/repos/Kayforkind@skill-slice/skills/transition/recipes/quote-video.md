# Quote video recipe (Inspire to Rise)

1. Audio-first: tight VO (0.8–1.5s gaps) before picture.
2. Run Cursor **`/effects`** (loads `inspire-quote-effects` + this skill).
3. Prefer archive video/photos over AI stills when user wants real likeness.
4. Assign `contentType` + `transitionIn` per beat from matrix + transition table.
5. Remotion: **`TransitionSeries`** + KineticQuote / CaptionWordReveal + muted `OffthreadVideo` + duck music.
6. Cut density 1.5–3.5s inside long beats; chunk long quotes.
7. GPU render (Remotion ≥4.0.503, HA required, angle, concurrency 6) → **`/reviewresults`** → `final/`.

## Fail if

- Sequence-only hard cuts with no TransitionSeries
- Static full-paragraph quote cards for entire beats
- Near-black cold open or foreign watermarks on archive
