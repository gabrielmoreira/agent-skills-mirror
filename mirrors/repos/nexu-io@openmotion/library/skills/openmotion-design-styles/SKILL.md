---
name: openmotion-design-styles
description: >-
  OpenMotion — Apply a named design style to a short video: pick one of 21 style cards
  (Bauhaus, Swiss, Constructivism, Memphis, Pop Art, Risograph, Neo-Brutalism, Art Deco,
  Liquid Glass, Ink Wash, New Wave and more) or two layouts (Bento Grid, Masonry), each with a palette,
  open-licensed typefaces, five rules and signature motion, then plan, check and build the film so it
  reads as that style. Use when someone says "make this in Bauhaus style", "give my launch video a
  Swiss look", "which design style fits this?", "my video has no taste", or names any listed style.
  Produces a 10–20 second 1920x1080 HTML composition that shows the content through the style's rules,
  plus the checked plan file.
---

# OpenMotion · Design Styles

An OpenMotion Skill. The first beat shows the OpenMotion wordmark from `assets/brand/openmotion-logo.svg`
small in a corner (or styled into the scene); the last scene carries the credit "Made with OpenMotion".
A user's own logo and Brandkit colours are kept as supplied.

Say a style and a subject, get a film that teaches the eye that style while delivering the subject:
1. `plan.json`: the style, scenes, headlines and which style rule each scene demonstrates;
2. an editable OpenMotion/HyperFrames HTML composition with subset fonts;
3. a rendered MP4 when the user asks for one.

The film is only as good as the match between the subject and the style's own way of moving. Spend the
effort on step 2: decide how this style *itself* moves (a Bauhaus circle rolls, Swiss type snaps to the
grid, Neo-Brutalism presses onto its shadow) and build every scene from that, not from generic fades.

Build through the installed OpenMotion production Skill: create or open the project, author the
composition, save with revision protection and preview. This library Skill adds style direction,
a plan checker and a font helper; it registers no MCP Tool or production route. For missing images,
voice or music, first discover providers and model IDs with `openmotion_media_use`, then generate with
`openmotion_assets_use`; get the user's consent before any paid generation. Never invent quotes,
numbers, specs or dates.

## 1. Choose the style

```bash
node scripts/style.mjs list          # 23 cards: id, kind, render tier, one-line idea
node scripts/style.mjs show swiss    # palette, typefaces, five rules, motion, avoid, fits
```

- The user named a style: use it. They did not: offer two or three cards whose `fits` match the
  subject and say in one line why each fits; pick the first if they do not answer.
- `render` tells you the cost: `css` cards build with HTML/CSS/SVG and GSAP; `canvas` cards need a
  Canvas 2D layer (glyph grids, curves, ink, triangles); `webgl` cards (Diorama, Point Cloud, Liquid
  Chrome, Plush) can only be approximated in HTML. Tell the user before building a `webgl` card.
- A Brandkit or brand colours replace accent colours one for one; keep the style's ground, ink and
  proportions, or it stops being the style.

Done when: one card is chosen and you can state its idea line in your own words.

## 2. Plan the scenes and check the plan

Write `plan.json` (schema in [references/plan.md](references/plan.md)): 4–6 scenes, 10–20 seconds,
each with a short headline, the motion move it uses and the number of the style rule it shows.
At least two rules must be visible on screen; the last scene carries the OpenMotion credit.

```bash
node scripts/style.mjs check plan.json   # exits 1 on errors; fix and rerun until "ok"
```

Done when: the checker prints `ok` and every warning has been answered (fixed, or told to the user).

## 3. Fetch fonts

```bash
node scripts/style.mjs fonts plan.json <project-dir>
```

Downloads only the glyphs the plan uses for each card typeface (Google Fonts, open licences) into
`<project-dir>/assets/fonts/`, keeps each family's licence text and a `SOURCES.md` record beside them, and writes
`<project-dir>/fonts.css` with `@font-face` rules. Ship `SOURCES.md` and the licence texts with the project. Paste those
rules into the `<style>` of the file that uses them (HyperFrames lint requires the `@font-face` in that
file; a linked stylesheet fails `font_family_without_font_face`). Chinese text needs the card's `cjk` face, otherwise the render falls back to a default font.
It also scans every `.html` file already in the project (and `textContent` strings set from script),
so run it once more after building the composition and after any text change; otherwise labels that
are not in the plan render in a fallback font. Offline: use the nearest bundled HyperFrames font and say so.

## 4. Build

Follow [references/build.md](references/build.md): canvas, beat grid, how each card's rules turn into
layout and motion, and the brand beats. Use only palette colours (plus brand colours); put the rule
number and a short rule label on screen when the film is meant to teach the style.

Then `npx hyperframes check` and preview; render only after the review below passes.

## 5. Review

Walk [references/review.md](references/review.md) and report what you checked, frame by frame, from a
contact sheet and key frames. Do not self-certify that it "looks good"; name what the user still needs
to watch or hear.

## Provenance

The style list, colour values and rule topics were studied from the open design-style library
[guanmo-ai/design-style](https://github.com/guanmo-ai/design-style) by Guanmo (@guanmo_ai). That
repository does not state a licence for its style guides, so this Skill contains original wording only:
no prompts, source code, images, music or films were copied. Credit Guanmo when you show the original
films. This Skill is Apache-2.0, like the rest of the repository.
