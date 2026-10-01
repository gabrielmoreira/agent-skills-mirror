---
date: 2026-09-29
title: 'Pick the image and video mode on the page, not in the sidebar'
---

# 2026-09-29 — Pick the image and video mode on the page, not in the sidebar

- **Context:** the sidebar unfolded Images into its seven workflows (Create,
  Transform, Inpaint, Extend, Upscale, Reference, Edit) while Video sat under
  it as a single row. Two sibling sections looked unrelated, and the long list
  suggested Images was the bigger feature. Video will get modes of its own
  (the core already parses `image-to-video` and refuses it until it lands).
- **Decision:** Images and Video are one sidebar row each. The heading of the
  form column is the mode selector on both pages: the active mode's icon,
  title and hint, and the title opens the list of modes with their hints.
  Images keeps `/images/<workflow>` as the source of truth, so a pick
  navigates and deep links still work. Video lists Create and, disabled with
  a "Soon" badge, Image to video. One shared component,
  `MediaModeSelect`, draws both.
- **Consequences:** the sidebar no longer persists an Images expanded state
  (`imagesExpanded` is gone from the left panel store). Changing the image
  workflow is one extra click from outside the page. When image-to-video lands
  it only needs its item enabled and a way to carry the mode into the request.
  The e2e helper `openImages` picks the workflow through the heading.
- **Owner:** team
- **Links:** `web-app/src/containers/images/MediaModeSelect.tsx`,
  `web-app/src/containers/images/ImagePromptForm.tsx`,
  `web-app/src/containers/videos/VideoPromptForm.tsx`,
  `web-app/src/components/left-sidebar/NavMain.tsx`,
  `MediaModeSelect.layout.test.tsx`.
