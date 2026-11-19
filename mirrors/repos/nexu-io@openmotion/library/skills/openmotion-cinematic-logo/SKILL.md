---
name: openmotion-cinematic-logo
description: >-
  OpenMotion — Reveal a logo like a film studio ident: dark set, warm light rays, drifting dust, a metallic mark drawn in light and a slow camera pull. Use for channel intros, brand openers and premium launch stings.
---

# OpenMotion · Cinematic Logo

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** brand openers, channel intros, end idents and premium launch stings where the logo is the whole shot.

## Look

| Element | Starting value |
| --- | --- |
| Set | Near-black navy `#0A0B12` with a soft radial lift behind the mark; optional 2.39:1 letterbox bars |
| Light | Warm volumetric rays `#FFD696` at 15–20% opacity, one horizontal lens streak in cool `#AAD2FF` |
| Mark | The supplied logo as vector, filled with a brushed metal gradient (gold `#D9A75A` or steel `#C9D1D9`) and a soft glow |
| Type | Wordmark in a wide geometric sans, tracked 0.4em; tagline smaller, muted, tracked wider |
| Texture | 40–80 dust motes at three depths, far ones blurred; light vignette |

## Motion

- Open on light already in frame: rays and dust are visible from frame one, never a black start.
- Draw the logo outline in light over 1.2–1.8 s, then fill with metal in 0.6 s while the outline fades.
- Fire one lens streak and glint as the fill lands (300 ms in, 900 ms out), then sweep a highlight across the mark in 1.1 s.
- Resolve the wordmark letter by letter from blur (120 ms stagger), add the tagline 1 s later.
- The camera eases from 110% to 100% across the whole shot; hold the final lock-up at least 2 s.

## Inputs

Required: the logo as SVG or a clean transparent PNG, the exact brand name. Optional: tagline, brand colours, preferred metal (gold, steel, copper), duration (5–10 s).

## Avoid

Redrawing or restyling the logo's shape, more than one streak or flare, spinning or flipping the mark in 3D, glow so strong the edges blur, text that the brand did not supply.

## Review

The logo geometry matches the supplied file exactly; frame 0.5 s already shows light; the wordmark is sharp and readable for the final 2 s; no element is clipped by the letterbox.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
