---
date: 2026-09-29
title: 'Keep the video progress inside the preview frame'
---

# 2026-09-29 — Keep the video progress inside the preview frame

- **Context:** ADR 2026-09-28 put the whole-job bar and its line ("~N left",
  or "Finishing the clip…" once the decode ran past its forecast) under the
  live preview, outside its frame. The frame already said the phase
  ("Decoding frames…") and the elapsed time, so while decoding the page
  showed two captions for one state, one of them outside the frame.
- **Decision:** the preview frame carries all of it. The phase comes first,
  then the bar from the core's `fraction`, then one line with the step, the
  elapsed time and the time left. Past the forecast there is no time left to
  show, and the phase already names the running work, so "Finishing the
  clip…" and its string are removed. The shared placeholder takes the bar and
  the time left as optional viewer props; the Images page passes neither and
  is unchanged.
- **Consequences:** the viewer has one caption and nothing under the frame.
  In a narrow portrait frame the line truncates from its end, so the time
  left goes first (`VideoGenerationProgress.layout.test.tsx`). The rest of
  ADR 2026-09-28 stands.
- **Owner:** team
- **Links:** `web-app/src/containers/videos/VideoGenerationProgress.tsx`,
  `web-app/src/containers/images/ImageGenerationPlaceholder.tsx`.

<!--
Supersedes: 2026-09-28-show-a-video-estimate-and-confirm-before-swapping.md (the progress placement only)
-->
