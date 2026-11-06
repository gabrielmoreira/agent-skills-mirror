# Shorts codes (Reels, TikTok, YouTube Shorts)

## Format

- 1080x1920, 9:16, 30 fps, H.264, AAC 48k. Loudness -14 LUFS integrated, true peak at or below -1 dBTP.
- Length: 30 to 60 s. Under 45 s is best for Reels and TikTok completion rate.

## Safe zones (keep text and key visuals inside)

- Top 220 px: platform header, search and tabs.
- Bottom 420 px: caption, username, music ticker. The CTA sits at y at most 1420, and captions at y at most 1400.
- Right 140 px, from y 900 to 1700: like, comment and share buttons. Keep text centred or left.
- The safe content box is about x 60 to 940, y 220 to 1500.

## Hook (first 1 to 2 s)

- Frame 1 must already show the promise: a card, a number or a bold line. No blank intro, no logo sting, no "salut".
- Start on speech. `tighten.lead` is .03 s.
- A visual change lands within 1 s.

## Pacing

- Something moves every 2 to 4 s: a layout seam move, a new card, a counter, typing or a punch-in zoom.
- Alternate proof (paper takes over) with face (full-bleed camera) so the viewer never sits on one layout.
- SUPER FAST by default. Every micro silence is cut: the cutter finds the real quiet run in the audio at each word boundary and keeps only a tiny breath (`tighten.sentence` .08, `comma` .05, `word` .03). `speed: 1.1` (the creator style, from the profile `pace.speed`) plays the whole short faster (voice via atempo, no pitch shift). Expect a 64 s take to land around 44 s.

## Mobile legibility

- Everything is read on a phone. The minimum on-screen text is 34 px (UI details), labels are 38 to 42 px, and captions are 84 px.
- If a label would need to be smaller to fit, shorten the label instead.

## Captions

- Always on (80%+ watch muted). They are word-synced, 1 to 3 words per chunk, and emphasis words are blue.
- Hide captions when a scene shows the same words (title lines, typed prompt, CTA).
- Numbers are written as digits (`replace: [['cent pour cent', '100%']]`).

## Ending

- A CTA card (follow or subscribe) in the last 2 to 3 s, with a pointer click.
- The music resolves on a held chord so the loop back to frame 1 feels clean.
