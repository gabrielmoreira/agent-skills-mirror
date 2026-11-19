---
name: openmotion-time-freeze
description: >-
  OpenMotion — Freeze one dramatic moment while the camera keeps moving: splash drops, leaves and people hang in the air, the frame dollies around them, then time resumes. Use for sports, dance, product splashes and action highlights.
---

# OpenMotion · Time Freeze

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** action highlights, dance moves and product splashes.

## Look

| Element | Starting value |
| --- | --- |
| Frozen moment | One clear subject at the peak of action, with particles (water, leaves, dust) around it |
| Depth | Three to five layers: far background, mid scenery, subject, foreground particles |
| Freeze grade | A cool tint over the frame while frozen, e.g. `rgba(40,60,110,.4)` at the edges |
| HUD | Small timecode and shutter label on dark pills `rgba(30,20,30,.45)`; the timecode stops on freeze |
| Type | One clean grotesk such as Space Grotesk; a short title after time resumes |

## Motion

- Play real motion for 1.5–2 s, then freeze on the peak with a 60 ms white flash.
- While frozen (3–4 s), move the camera: a slow lateral dolly plus a 15–25% push-in, each layer shifted by its depth (far 0.2×, mid 0.5×, subject 1×, foreground 1.5×).
- Nothing in the scene moves during the freeze; only the camera does.
- Release with a second, softer flash and let the action finish within about 1 s.

## Inputs

Required: the moment to freeze and the action before and after it. Optional: the user's own clip, brand colours, a title line.

Without suitable footage, generate the scene or separated subject, background and particle layers through `openmotion_media_use` → `openmotion_assets_use`. Approve one test image or clip before generating the rest, and label any generated person as generated.

## Avoid

Particles that keep drifting while frozen, a camera move faster than the action, freezing on a blurry frame, more than one freeze per clip.

## Review

The freeze lands on the peak; layers keep consistent parallax; subject edges stay clean; the timecode holds still during the freeze.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
