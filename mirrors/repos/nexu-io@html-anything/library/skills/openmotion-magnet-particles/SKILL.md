---
name: openmotion-magnet-particles
description: >-
  OpenMotion — Make a minimal brand reveal where a loose cloud of dots is pulled into a line of text, scattered into an orbit, then pulled again into the logo. Use for product intros, collaboration and planning tools, and launches whose message is bringing things together.
---

# OpenMotion · Magnet Particles

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** logo intros and tools whose message is bringing scattered parts together.

## Look

| Element | Starting value |
| --- | --- |
| Background | Flat warm paper `#F4F1EA`; no gradient (it bands and costs file size) |
| Particles | 800–1,500 square dots, 3–4 px, charcoal `#1E2A2F` at 90%; the logo mark's dots switch to teal `#0F9C8C` |
| Type | Text targets drawn from a bold grotesk at 170–200 px so the dot shapes stay legible; supporting line in a clean sans at 32–36 px |
| Accent | Teal only on the logo mark and one phrase of the tagline |
| Caption | Optional small uppercase label top-left, letter spacing 0.18 em, grey |

## Motion

- Open on the dot cloud already filling the frame, sliding slowly as one body (about 30 px/s).
- Pull into the first line with expo-in-out over 0.9 s per dot, start times spread by 0.3 s so the word assembles from many directions; hold 1–1.5 s perfectly still.
- Release into an elliptical orbit (800 ms power3-out), rotate slowly, then pull into the logo with a slight sideways curve (1 s).
- Teal fades into the logo dots after they land; tagline fades up 600 ms later and holds 1.5 s.

## Inputs

Required: brand name, one short line (two to four words), logo mark as a simple shape or SVG, tagline. Optional: brand accent colour, a label for the top corner.

## Avoid

Thin or script fonts as targets, jittering dots during holds, more than one line of particle text, thousands of tiny dots (they turn to noise and bloat the file), colour on every dot.

## Review

Both particle texts read clearly when settled; holds are still; the logo matches the supplied mark; the exported file stays small enough for its destination (check bitrate on the dot-motion segments).

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
