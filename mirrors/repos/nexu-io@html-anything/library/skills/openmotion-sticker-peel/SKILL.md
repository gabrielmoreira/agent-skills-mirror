---
name: openmotion-sticker-peel
description: >-
  OpenMotion — Peel each scene off like a sticker to reveal the next: a corner curls, the paper back shows, and the next frame sits underneath. Use for drops, announcements, playful promos and list videos.
---

# OpenMotion · Sticker Peel

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** playful transitions in promos, drops and list videos.

## Look

| Element | Starting value |
| --- | --- |
| Scenes | Full-frame flat colours, e.g. `#FF6B35`, `#127C77`, `#F4EEE2`, each with one big line of type |
| Paper back | Off-white `#F1ECE3` shading to `#BFB5A6` at the fold, so the curl reads as paper |
| Shadow | Soft drop shadow under the lifted part, about 10 px offset and 14 px blur |
| Stickers | Small die-cut badges with an 8–12 px white outline and a short drop shadow |
| Type | One heavy display font plus one editorial serif; text stays inside the safe area |

## Motion

- Start with a small corner lift (about 0.5 s) so the viewer sees what is about to happen.
- Peel along a straight diagonal fold in 1.2–1.7 s with an ease-in-out; vary the corner between transitions.
- The next scene's content is already in place underneath; only small stickers pop in after the peel (back-out, 400–500 ms).
- Keep at least 1.5 s of readable hold between peels.

## Inputs

Required: three or four short lines or images for the scenes. Optional: brand colours, product stills, the user's own photos or clips as scene backgrounds.

Build the peel in code: clip the top scene with a half-plane and draw the flap as its mirror across the fold line. Only generate imagery through `openmotion_media_use` → `openmotion_assets_use` when the user has none, and approve one test image first.

## Avoid

Peeling in random directions, a flap with no shading (it reads as a wipe), two peels at once.

## Review

Every fold edge is straight and the flap mirrors the removed corner; no scene shows blank space mid-peel; all text is readable during the holds.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
