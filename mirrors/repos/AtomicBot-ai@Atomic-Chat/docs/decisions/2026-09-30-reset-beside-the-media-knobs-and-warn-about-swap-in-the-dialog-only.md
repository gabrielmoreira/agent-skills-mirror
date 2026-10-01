---
date: 2026-09-30
title: 'Put Reset beside the media knobs, and warn about a swapping clip in the dialog only'
---

# 2026-09-30 — Put Reset beside the media knobs, and warn about a swapping clip in the dialog only

- **Context:** owner feedback on the Video page. Reset was an icon button in the
  page heading, next to the mode selector, while the size, length, steps,
  guidance and seed it puts back sit below the prompt card — far apart, so the
  button read as unrelated to them. Images had the same layout. And a clip the
  core's estimate says exceeds memory was announced twice: a red box under
  Generate (what it needs against what there is, that it will swap, what to
  change), then the "This clip won't fit in memory" dialog on Generate, which
  repeats it and is the actual gate.
- **Decision:**
  - `MediaSettingsHeading` (shared by Images and Video) is a "Settings" heading
    over the knobs, drawn like the Advanced fold at the bottom, with a labelled
    Reset on its right. It sits after the negative prompt and before the size,
    since Reset keeps both prompts. The page heading keeps the mode selector
    only. Without a model's defaults the heading shows no Reset, as before.
  - `VideoEstimateLine` shows nothing for `exceeds`; the time line for `fits`
    and `tight` is unchanged. `ConfirmVideoExceedsMemory` now also says what to
    change (`videos:estimate.exceedsAdvice`), so the advice is not lost.
    `videos:estimate.exceedsSwap` is removed from every locale.
- **Consequences:** the form stays quiet until Generate is pressed on a clip
  that will swap; the dialog, with Cancel as its default answer, is the one
  place that says so. Reset is one heading away from what it changes. Image
  workflow knobs above the prompt card (strength, upscale factor, sides) are
  still reset by it, as before. The rest of ADR 2026-09-28 (estimate, dialog,
  progress, telemetry) stands.
- **Owner:** team
- **Links:** `web-app/src/containers/images/MediaSettingsHeading.tsx`,
  `web-app/src/containers/images/ImagePromptForm.tsx`,
  `web-app/src/containers/videos/{VideoPromptForm,VideoEstimateLine,ConfirmVideoExceedsMemory}.tsx`,
  `MediaModeSelect.layout.test.tsx` (settings heading geometry).

<!--
Supersedes: 2026-09-28-show-a-video-estimate-and-confirm-before-swapping.md (the `exceeds` line only)
-->
