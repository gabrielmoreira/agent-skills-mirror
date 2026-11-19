---
name: openmotion-coral-title-cards
description: >-
  OpenMotion — Make an app launch video that alternates full-screen coral title cards with phone mockups of the real app. Use for mobile app launches and app store videos.
---

# OpenMotion · Coral Title Cards

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** mobile app launches where short title lines set up each app screen.

## Look

| Element | Starting value |
| --- | --- |
| Title cards | Full-frame coral `#FF6A48` (a second, slightly deeper `#FF5B37` for variety); deep brown-black text `#2A1712` |
| App scenes | Peach background `#FFE6DC`; phone mockups with a dark frame, rounded 46 px, real app screens inside |
| Type | Rounded geometric sans, bold, 90–120 px on cards; 60–64 px headings beside the phone with the key word in coral |
| Layout | One phone left with a heading right, or three phones fanned with a caption above |
| Logo | A simple mark plus the app name on the final coral card, store line underneath |

## Motion

- Title words rise in with a 70–90 ms stagger (400 ms each) and the card scales 4% slowly while held.
- Hard cut between title cards; the last card slides up or sideways (500 ms, expo in-out) to reveal the app scene.
- A tap ripple on a key button shows one real action, and the screen state changes (e.g. a check mark).
- Phones fan in from left, centre and right 100 ms apart; the middle phone floats gently.

## Inputs

Required: app name, logo, 3–5 real app screenshots to rebuild, 3–4 short title lines, store availability. Optional: brand colour to replace coral.

## Avoid

Lorem ipsum in the mockups, more than two coral shades, title lines over seven words, store badges for stores the app is not in, invented ratings.

## Review

Each title card reads in under a second; screens match the real app; the logo card holds at least one second.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
