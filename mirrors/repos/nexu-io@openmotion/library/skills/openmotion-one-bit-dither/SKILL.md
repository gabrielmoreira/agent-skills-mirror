---
name: openmotion-one-bit-dither
description: >-
  OpenMotion — Make a two-colour product promo where pixel-grid dither patterns assemble into shapes, product UI and headline cards. Use for developer tools, infrastructure and SaaS launches that want a crisp technical feel.
---

# OpenMotion · One Bit Dither

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** software launches, API and infrastructure products, changelog teasers and feature promos with 3–5 short claims.

## Look

| Element | Starting value |
| --- | --- |
| Palette | Exactly two inks: deep navy `#0F1830` and warm paper `#F5F1E8`. One small accent (`#FF4F6D`) only on the logo mark |
| Texture | Ordered 4×4 dither on a canvas, 6–10 px cells; 40–80 px checker blocks for transitions |
| Type | One grotesk sans, 600 weight, tight leading (1.0), set on solid navy or paper cards so it never sits on noise |
| Layout | Full-frame dither field, one headline card, product UI shown as a dithered thumbnail inside a hard-edged frame |

## Motion

- Fields resolve from sparse dots to full pattern by raising the dither threshold over 600–900 ms; never blur.
- Shapes (rings, waves, a product screenshot) form from noise in 1–1.5 s, then hold still for at least 1 s.
- Scene changes use a checkerboard wipe: blocks flip in a diagonal stagger of 20–30 ms per block, about 500 ms in total.
- Headline cards pop in with a 2-frame offset glitch, then stay perfectly still while read.

## Inputs

Required: product name and logo, 3–5 claims taken from the product's own site, one real UI screenshot to dither. Optional: a customer quote with attribution, a URL for the end card.

## Avoid

More than two inks in the dither, text placed over moving noise, smooth gradients, dithering the logo itself, claims the site does not make.

## Review

Every headline reads on a solid card; no frame is pure noise for more than 1 s; the screenshot is still recognisable after dithering; end card shows name and URL for at least 1.5 s.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
