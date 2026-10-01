---
date: 2026-09-28
title: "Show the core's video estimate, and confirm before a clip that swaps"
---

# 2026-09-28 — Show the core's video estimate, and confirm before a clip that swaps

- **Context:** A clip was started blind: the Video form said nothing about time or memory, and the live
  preview showed `Step i/N` and elapsed seconds only. Telemetry has a Wan 2.2 run on an 18 GB Mac cancelled
  after 21 060 s and a 16 GB laptop that waited about 12 000 s, both in swap. The only memory check in the
  app is `fit.ts`'s picker badge (weights + 1.5 GiB per megapixel, no frames). ADR 2026-09-27 makes the
  core the only source of hardware facts; the core now estimates a video request and reports the whole
  job live (core ADR 2026-09-28-estimate-video-generation-before-and-during-the-job). OpenSpec change
  `add-video-generation-estimate`.
- **Decision:** The app shows what the core says and decides only when to ask.
  - `DiffusionService.estimateVideo` calls `POST /diffusion/video/estimate` and reads any refusal as
    `null` (an older core's 404, no model, a failure). `useVideoEstimate` asks 400 ms after the size,
    length, steps, guidance or model last changed, only while a video model is loaded, with a fixed
    placeholder prompt (the estimate does not depend on it, the core validates the body as a job, and the
    user's text never leaves for it); a ticket drops answers for numbers that have since changed.
  - `VideoEstimateLine` under Generate: a range of time (`fits`), the range with a warning tone and
    "memory is tight" (`tight`), and in the error tone what it needs against what there is, that it will
    swap for hours, and what to change (`exceeds`); "from past runs" when the basis is `history`; nothing
    without an estimate, so the form works as before on an older core. Durations read "~45 s", "~13 min",
    "~1 h 20 min", "~4–7 min" (`lib/video/format-duration.ts`), units as translated abbreviations
    because the app's i18n has no plurals.
  - `ConfirmVideoExceedsMemory` asks on Generate **only** for `exceeds`, following the download dialog of
    ADR 2026-09-17 (warn before a download that won't fit): Cancel is focused and is the default answer
    (Enter, Escape, the close button and a click outside start nothing); "Generate anyway" starts the
    draft that was asked about. At Generate the hook uses the estimate only when it is for the current
    numbers, and otherwise asks the core at once, so a change made within the 400 ms pause is still
    judged. `tight` is not asked: it still runs, and asking there would cry wolf.
  - The live preview carries a bar from the core's whole-job `fraction`, "~N left" from `etaSeconds`
    (the job's estimate stands in before the first progress event), and "Finishing the clip…" when the
    decode runs past its forecast. `slowdown` shows a warning above the viewer, in any viewer mode, with a
    Stop that is the existing cancel; an absent flag (older core) reads as `false`.
  - `video_generate` gains `estimate_verdict` (`none` without an estimate), `estimate_low_s`,
    `estimate_high_s`, `estimate_basis` and `slowdown_seen` (the core keeps the flag, so the job's last
    progress tells), to compare the forecast with `duration_ms` and recalibrate the heuristic.
- **Consequences:** No estimate logic lives in the app; another host of the core gets the same numbers.
  The picker's `fit.ts` badge stays as the only signal before a model is loaded. The estimate costs one
  small control call per pause in editing. Pinning a core without the route is safe: the line and the
  dialog simply do not appear.
- **Owner:** team.
- **Links:** `web-app/src/hooks/{useVideoEstimate,useVideoGeneration}.ts`,
  `web-app/src/containers/videos/{VideoEstimateLine,ConfirmVideoExceedsMemory,VideoGenerationProgress,VideoPromptForm,VideoGenerationPage}.tsx`,
  `web-app/src/lib/video/format-duration.ts`, `web-app/src/services/diffusion/{types,tauri,default}.ts`,
  `web-app/src/lib/diffusion/telemetry.ts`, `web-app/src/stores/video-generation-store.ts`; ADRs
  2026-09-17-warn-before-a-download-that-wont-fit-in-memory,
  2026-09-27-the-core-is-the-only-source-of-hardware-facts-and-backend-decisions.
