---
name: openmotion-wireframe-style
description: >-
  OpenMotion — Package a presenter video with letter-by-letter wide red keywords, small script lead-ins and quick cuts to hollow line-drawn wireframes of the objects being named. Use for tech, gear and setup talks recorded by the creator.
---

# OpenMotion · Wireframe Style

Build the video as a native OpenMotion HTML/CSS/JS composition through the installed OpenMotion production Skill: create or open the project, author the composition, save with revision protection and preview. This library Skill adds creative direction only; it registers no MCP Tool or production route. Treat palette, font and timing values below as starting points; a supplied Brandkit or the user's brand wins. For missing images, voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with `openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes, numbers, specs or dates.

Use the creator's own recording and measured speech timing. Do not place graphics over someone else's speech, and keep the face and mouth clear.

**Status:** recipe / draft. No executable template or rendered comparison yet.

**Use for:** setup tours, gear talks and tech opinions with one presenter.

## Look

| Element | Starting value |
| --- | --- |
| Base | The real recording; object inserts sit on a dark teal backdrop `#10313A` |
| Keyword | Extra-wide sans in red `#E3264A`, 80–110 px, wide tracking, one or two words per beat |
| Lead-in | Small white handwritten script `#F4EFE6` above the keyword, three to five words |
| Wireframe | Hollow white line drawing `#EAF6F8`, 1.5 px strokes, mesh rings, thin grey dimension lines `#9FC3C9` with a short measurement label |

## Motion

- Keywords appear letter by letter on the spoken word: each letter pops from 30% to 100% in 200–250 ms, 50–70 ms apart.
- Cut to an object insert with a soft white flash (50% opacity, under 250 ms) when the speech names the object.
- Draw the wireframe along its strokes in 0.8–1.2 s; dimension lines follow 200–300 ms later.
- Push 3–5% on every insert; return to the presenter for the conclusion.

## Inputs

Required: the presenter's recording, its transcript with word timing, and the objects worth showing. Optional: clean photos or clips of each object to trace. Wireframes are drawn as editable SVG from those references; missing object references may be generated through `openmotion_media_use` → `openmotion_assets_use` after one test image is approved.

## Avoid

Keywords on every sentence, wireframes of objects never mentioned, measurements that were not supplied, inserts longer than their sentence.

## Review

Keywords land within ±3 frames of their spoken words; each wireframe matches its object; face and mouth stay clear; text never overlaps the drawing.

## Provenance

Written for OpenMotion after surveying publicly listed workflow names and descriptions in ChatCut's preset gallery (November 2026). Original text; no ChatCut prompts, source code, templates or media are included. Apache-2.0, like the rest of the repository.
