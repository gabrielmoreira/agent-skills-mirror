---
name: openmotion-editorial-explainer
description: >-
  OpenMotion — Package a presenter video as a calm news explainer: lined-notebook agenda pages, grey-paper data charts with serif figures and one yellow accent. Use for current affairs, money explainers and data stories recorded by the creator.
---

# OpenMotion · Editorial Explainer

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

Use the creator's own recording and measured speech timing. Do not place graphics over someone else's speech, and keep the face and mouth clear.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** news explainers, personal-finance talks and data stories where one or two numbers carry the argument.

## Look

| Element | Starting value |
| --- | --- |
| Agenda page | Notebook paper `#F7F5EF`, pale blue rules `#CBD6E2`, one red margin line `#E2A0A0` |
| Chart page | Warm grey paper `#D3D0CA` with light grain; axis and labels in `#3A3A3A` |
| Type | One editorial serif for headlines and figures; small italic serif for axis notes and sources |
| Accent | Yellow `#FFE500`: the highlighted agenda line, the answer bar, the lower-third tick. Everything else grey |
| Layout | Full-screen pages alternate with clean presenter shots; lower third sits bottom-left |

## Motion

- Agenda lines fade up 250–350 ms apart; the highlighter sweeps behind the current line in 400–500 ms.
- Lower third: yellow tick grows first (200 ms), then name and role slide 12 px from the left.
- Chart bars grow from the baseline over 0.8–1.2 s while the figure above counts up; the comparison bar starts only after the first one settles.
- Hold each finished chart at least 1.5 s.

## Inputs

Required: the presenter's recording, measured speech timing, the agenda points and every figure with its source. Optional: presenter name and role, a chart note (period, method).

## Avoid

More than two bars per comparison, colour beyond grey and yellow, unsourced figures, 3D charts.

## Review

Each figure matches the script and source exactly; the yellow marks only the answer; chart text is readable on a phone; face and mouth stay clear in presenter shots.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
