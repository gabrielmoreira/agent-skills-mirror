---
name: openmotion-color-pop-poster
description: >-
  OpenMotion — Animate a colour-pop promo poster: two high-contrast saturated colours, a huge headline that slams in, the product in the centre and callout arrows. Use for sales, drinks, snacks and launch promos that need to stop the scroll.
---

# OpenMotion · Color Pop Poster

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** promotions, flavour launches, seasonal offers and any product post that needs one loud message.

## Look

| Element | Starting value |
| --- | --- |
| Colours | Two clashing brights plus white, e.g. cobalt `#1D3FE0` and tangerine `#FF7A1A` on off-white `#F7F3EA` |
| Headline | Heavy rounded or grotesque sans, 2–3 words, 140–200 px at 720p, tight leading 0.9 |
| Product | Centre-bottom, 50–65% of the frame height, slight shadow, rays or circles behind it |
| Callouts | Hand-drawn-style arrows with 2–3 word labels in the accent colour |
| Footer | Small offer line and call to action in caps |

## Motion

- The headline slams in word by word, scale 1.3 → 1.0 in 180–250 ms with a short 2–4 px shake.
- Background rays or rings spin slowly (20–30° over the shot) or pulse once on the beat.
- The product pops up from the bottom with a 6% overshoot, 400 ms.
- Callout arrows draw on in 300 ms each, then their labels type in; offer line lands last.

## Inputs

Required: product photo, the exact headline, offer or price if any. Optional: 1–3 callout facts, brand colours, call to action.

Missing product cut-outs or props (fruit slices, ice) are generated through `openmotion_media_use` → `openmotion_assets_use`; approve one test image before generating the rest. Use the real product photo for the product itself.

## Avoid

More than two bright colours, headline longer than one line per word group, fake discounts, rays so busy the product disappears.

## Review

The headline reads in under one second; the colour pair passes contrast for every text block; callouts point at real features; the final frame holds 1.5 s.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
