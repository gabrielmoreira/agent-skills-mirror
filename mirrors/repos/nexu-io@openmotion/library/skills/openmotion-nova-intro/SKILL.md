---
name: openmotion-nova-intro
description: >-
  OpenMotion — Make a cinematic opener on a dark nebula sky: stars spiral in and form a glowing ring, the product name resolves inside it, a mint ripple carries the hook, and the ring returns for the end card. Use for app launches, astronomy, AI and tech products that want a premium night-sky intro.
---

# OpenMotion · Nova Intro

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** launch openers, astronomy, AI and tech products, event teasers.

## Look

| Element | Starting value |
| --- | --- |
| Sky | Navy `#070B1A` with 2–3 blurred nebula glows: violet `#6B4BFF`, teal `#19D3C5`, magenta `#E85AB4` at 30–55% |
| Stars | 300–450 soft white dots, 2–4.5 px, varying opacity |
| Ring | Pale cyan `#DDF7FF` stroke 8–12 px with an outer and inner glow; radius about a third of frame height |
| Type | One geometric sans, 100–120 px for the name, 28–32 px light subline in `#A9B4E6` |
| Ripple | Mint concentric bands `#2FD8C4` / `#8FF0E2` with a pale centre disc carrying one short dark navy hook line |

## Motion

- Stars are visible from frame 0 and spiral inward over about 2 s (power3-in-out, staggered 0.6 s), landing exactly on the ring path.
- The ring ignites where the stars land (600 ms) and pulses once; stars fade out as it takes over.
- Name letters rise and de-blur one by one (60 ms stagger, 450 ms each); subline follows 400 ms later.
- The ring blows outward into the mint ripple (600 ms), ripple expands slowly for 1.4 s, then the dark sky returns with a dimmed ring, twinkling stars and four-point sparkles for the end card.

## Inputs

Required: product name, a one-line description, a two-word hook, a closing call to action the user confirms. Optional: logo, brand colours for nebula and ripple, store badges.

## Avoid

Busy star fields that fight the text, more than one ring, hard cuts from dark to mint without the ring transition, lens flares, availability claims the user has not confirmed.

## Review

Frame 0.5 s shows stars; stars visibly form the ring; the name is sharp 1.2 s+.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
