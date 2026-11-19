---
name: openmotion-footage-to-handpainted
description: >-
  OpenMotion — Turn real footage into a hand-painted look: live clips open into flat, brush-edged painted versions of the same shot, framed by a bold-caps and italic-serif title pair. Use for travel, lifestyle and reflective explainers without an on-camera host.
---

# OpenMotion · Footage to Handpainted

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** travel diaries, lifestyle essays and calm idea pieces built from B-roll, where one moving subject (a ferry, a train, a cyclist) carries each beat.

## Look

| Element | Starting value |
| --- | --- |
| Footage | Real clips, warm graded, 1–3 s each, one clear moving subject |
| Painted layer | Flat brush-edged colour blocks with paper grain, e.g. coral `#D9533F`, teal `#4F9BA8`, cream `#F1E6CF`, moss `#6E8B3D` |
| Type | Heavy sans caps word plus a large italic serif line, cream on colour |
| Layout | Rounded painted window over the footage, ending on a full-frame painted hold |

## Motion

- Open on live footage for 1–1.5 s.
- A rounded window grows from one corner (600–800 ms, ease-out) and shows the same frame painted; the subject keeps moving inside it.
- Wipe the whole frame to the painted version along a brush-shaped edge in 500–700 ms.
- Title pair arrives after the paint settles: caps word fades up (300 ms), the italic line writes on 200 ms later.
- Hold the final painted frame at least 1.5 s; no camera shake.

## Inputs

Required: the user's footage and one key line per beat. Painted frames are generated: one frame per shot goes through `openmotion_media_use` → `openmotion_assets_use` as an image-to-image paint pass; approve one test frame before painting the rest, then animate stills with gentle drift. Optional: music, place names. Generated people are labelled as generated.

## Avoid

Painting real people's faces without consent, filter-style posterising, more than two type families, text over busy footage.

## Review

Painted frame matches the live shot's composition; the moving subject stays recognisable after painting; every title readable at 1× for two full reads; colours repeat across beats.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
