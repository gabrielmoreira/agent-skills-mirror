---
name: openmotion-retro-print-poster
description: >-
  OpenMotion — Build a two-ink risograph-style poster: cream paper, halftone shapes, condensed type, slight misregistration and grain, with each ink layer stamping in. Use for gigs, events, sales and nostalgic announcements.
---

# OpenMotion · Retro Print Poster

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** gig and event posters, pop-ups and markets, seasonal sales and nostalgic brand moments.

## Look

| Element | Starting value |
| --- | --- |
| Paper | Cream `#F1E6CF` with fine noise grain and a soft warm edge burn |
| Inks | Two spot colours that overprint with multiply, such as red `#E2483A` and blue `#1F3F94`; never more than two plus paper |
| Shapes | Halftone dots (12–16 px grid) whose size grows toward one side; simple bold forms such as sun, waves, stripes |
| Type | Condensed display caps (150–180 px) for the headline; condensed sans caps for details |
| Details | A round badge, a rotated stamp or a ring of circular text; 1–3 px misregistration between inks |

## Motion

- Halftone blooms from the centre outward over 1.5 s, so frame one already shows dots.
- Line work slides in 0.5 s per layer with a 100 ms stagger, like a second pass through the press.
- Headline lines stamp in one by one (320 ms, fast-in ease) with a short offset ghost in the other ink that settles into register.
- Details type on in steps (0.6–0.7 s); a stamp lands at about 60% of the timeline with a 2-frame shake.
- Keep a stepped 1 px registration wobble (6 per second) on one ink and slow drift on the big shape.

## Inputs

Required: headline, date, time and place, exactly as they will be printed. Optional: a second ink colour, a simple motif (sun, waves, an instrument), a stamp line such as an offer.

## Avoid

Gradients, glossy highlights, photos of people, more than two inks, decorative text the user did not supply, misregistration so large the headline doubles.

## Review

Every date, time and place matches the brief; the headline reads at thumbnail size; overprint areas look darker, not muddy; nothing is cut at the frame edge.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
