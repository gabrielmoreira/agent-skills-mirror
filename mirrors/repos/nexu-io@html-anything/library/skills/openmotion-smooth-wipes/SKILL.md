---
name: openmotion-smooth-wipes
description: >-
  OpenMotion — Make a punchy product promo where flat colour panels with rounded corners wipe across the frame between big type beats. Use for app launches, offers and short social promos.
---

# OpenMotion · Smooth Wipes

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** app launches, feature promos and offers told in 4–6 short beats.

## Look

| Element | Starting value |
| --- | --- |
| Colours | Three flat brand colours, e.g. forest `#0E3B2E`, cream `#F3EFE4`, coral `#FF6B4A`; text always in one of the other two |
| Panels | Full-frame rectangles with 60–120 px corner radius on the leading edge |
| Type | Heavy condensed sans (e.g. Anton or Oswald 700), all caps, 2–3 words per beat, 30–60% of frame height |
| Product | One product UI card or phone frame for the proof beat |
| Logo | Small logo top left on every beat; large lockup on the end card |

## Motion

- Each wipe crosses the frame in 450–650 ms with a strong ease-in-out; the rounded leading edge leads.
- The new beat's type rides in on the panel, 80–150 ms behind its edge, so text and panel move as one.
- Alternate wipe directions (right, up, left) to keep rhythm; one beat every 1.2–1.8 s.
- The proof beat can count a number up or tick a UI state while it holds.
- End on the logo with a 2 s hold.

## Inputs

Required: product name, logo, 4–6 copy beats in the user's words, brand colours. Optional: product screenshot, real number for the proof beat.

## Avoid

Sharp-cornered or diagonal wipes, gradients, more than three colours, numbers the user did not give.

## Review

Every beat reads at a glance; no text is clipped by a panel edge in transit; colour contrast stays at least 4.5:1.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
