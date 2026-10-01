---
date: 2026-09-30
title: 'Name the Images and Video pages in their heading, and pick the mode under it'
---

# 2026-09-30 — Name the Images and Video pages in their heading, and pick the mode under it

- **Context:** since 2026-09-29 the heading of the Images and Video form
  columns was the mode selector itself ("Create images ⌄"). The column's
  biggest text changed with every mode, the page never said what it was for,
  and the dropdown read as a title rather than a control, so the modes were
  easy to miss.
- **Decision:** the column opens with the page name ("Images", "Video") and
  a one-line subtitle of what the page does locally. Reset sits over the
  knobs instead ([Put Reset beside the media knobs](2026-09-30-reset-beside-the-media-knobs-and-warn-about-swap-in-the-dialog-only.md)).
  The mode is a separate, full-width select pill under the heading, styled
  like the form's other selects; its list still shows every mode with its
  hint. `MediaPageHeading` draws the heading on both pages and
  `MediaModeSelect` is only the pill. This narrows the heading part of
  [2026-09-29 — Pick the image and video mode on the page](2026-09-29-pick-the-image-and-video-mode-on-the-page.md);
  the rest of that record stands.
- **Consequences:** the active mode's hint is no longer on screen outside
  the open list. The heading repeats the page name shown in the top bar.
  The test ids `<image|video>-workflow-{select,title,menu,option-<id>}` are
  unchanged, so the e2e helpers still pick modes the same way; the heading
  adds `<image|video>-page-{heading,title,subtitle}`. New strings
  `images:page.subtitle` and `videos:page.subtitle` are English in every
  locale, like the rest of the media form.
- **Owner:** team
- **Links:** `web-app/src/containers/images/MediaPageHeading.tsx`,
  `web-app/src/containers/images/MediaModeSelect.tsx`,
  `web-app/src/containers/images/ImagePromptForm.tsx`,
  `web-app/src/containers/videos/VideoPromptForm.tsx`,
  `MediaModeSelect.layout.test.tsx`.
