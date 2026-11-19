---
name: openmotion-translucent-glass
description: >-
  OpenMotion — Make a soft product promo on layered translucent gradient ribbons: a frosted glass card, short lines that swap one at a time and a thin line icon that changes with each line. Use for calm SaaS launches, productivity apps and feature intros that should feel premium and light.
---

# OpenMotion · Translucent Glass

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** calm launches and feature intros told as problem → fix → name.

## Look

| Element | Starting value |
| --- | --- |
| Background | Off-white `#FFF4EE` with 3–4 large ribbons in peach `#FFB199`, coral `#FF6F7D`, apricot `#FFD39A`, rose `#F7A6C1`; 50–85% opacity, multiply, 6 px blur |
| Glass card | Centred, ~60% of frame width, 40 px radius, white 30–60% fill, 14 px backdrop blur, white edge |
| Type | One rounded geometric sans, bold 50–60 px for the line, one accent word in coral `#E2575B`; wordmark 90–110 px |
| Icons | Single-weight line icons (6–8 px stroke) with a peach-to-coral gradient, drawn inside the card |
| Extras | At most two small glass chips with feature names; one dotted sunburst above the final wordmark |

## Motion

- Ribbons drift the whole time (60–140 px over 8 s, sine); the card only settles 6% on entry.
- Swap lines every 1.5–2 s (out 350 ms, in 450 ms); one line at a time.
- The icon follows the story: scattered shapes wobble on the problem, then collapse into one connected symbol on the fix (600–900 ms).
- End on the wordmark under a rotating sunburst (1.4 s); hold at least 1.5 s.

## Inputs

Required: product name, problem line, fix line and promise from the user's site or brief. Optional: logo, brand colours (kept soft), two feature names for chips, a UI screenshot inside the card.

## Avoid

Saturated or dark backgrounds, more than one accent colour on the card, long paragraphs, hard cuts, icons in mixed stroke weights, claims the site does not make.

## Review

Lines readable at 1×; ribbons move in every frame; each icon matches its line; text on glass passes 4.5:1.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
