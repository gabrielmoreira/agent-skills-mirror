---
name: openmotion-pastel-flat-2d
description: >-
  OpenMotion — Make a narrated explainer in soft pastel flat 2D scenes: rounded shapes, gentle light changes, small character actions and short uppercase caption chips. Use for product introductions, brand education and calm how-it-works stories.
---

# OpenMotion · Pastel Flat 2D

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** product introductions, brand stories, onboarding and "how it works" explainers narrated without a presenter.

## Look

| Element | Starting value |
| --- | --- |
| Palette | Lavender `#B9A7D6`, peach `#F8D9C4`, mint `#BFE3D6`, blush `#F4A9A8`, butter `#FFD98A`; no pure black or white fills |
| Shapes | Flat vector, rounded corners (8–40 px), no outlines, at most one soft shadow tone per object |
| Characters | Simple round heads, dot eyes, small bodies; same proportions in every scene |
| Light | Sky and window colours shift to show time or progress |
| Captions | Dark rounded chip `#24212B`, cream uppercase monospace text, 18–22 px, bottom centre, two to five words |

## Motion

- Hold each shot 3–5 s with a slow 4–8% push or pull so nothing is static.
- Show progress through small changes: windows lighting one by one (250 ms each, 300–400 ms apart), a shutter rising in 0.9 s, bread rising over 1.5–2 s.
- Change shots with a 300–400 ms cross-fade on a sentence boundary.
- Swap captions on the spoken phrase with a small 200 ms scale-in.

## Inputs

Required: topic or exact script, target duration, aspect ratio. Optional: brand colours, voice, product screenshots. Scene images and animated clips are generated through `openmotion_media_use` → `openmotion_assets_use`: approve one scene image and a short voice sample first, then the full still preview, then one animated clip before generating the rest. Label generated characters as generated.

## Avoid

Saturated or neon colours, gradients on every object, long captions, characters changing proportions between shots, product claims the brief does not support.

## Review

Every shot shows one visible change; characters stay consistent; captions match the narration word for word in meaning; pastel contrast still keeps captions readable.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
