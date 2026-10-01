---
date: 2026-09-29
title: "Notify the desktop when a download or a generation finishes"
---

# 2026-09-29 — Notify the desktop when a download or a generation finishes

- **Context:** OS notifications existed for a finished reply (`chat-session-store`), finished
  images and a finished clip (their generation stores). Only the reply one obeyed Settings →
  Desktop notifications, and each caller checked focus its own way. Downloads ended with an
  in-app toast only: a model (llama.cpp, MLX, an image or video checkpoint) or an engine (the
  llama.cpp backend, the image and video engine) takes minutes, the user switches to another app
  in the meantime and never sees the toast.
- **Decision:** one gate, `notifyWhenAway` in `web-app/src/lib/notifications.ts`: the Settings
  switch is on (undefined counts as on) and the window is hidden or not focused. Downloads,
  images and clips go through it; a reply keeps its extra rule that another open conversation
  also counts as away. `DownloadManagement` notifies from both success events, but only for a
  download that still has a panel row, so a download reporting success twice, or a success the
  panel never showed, makes at most one notification. `lib/downloadNotification.ts` words it: a
  model by its name (the catalog family for an image or video model, the last id segment
  otherwise), an engine by what it runs, and nothing for the CUDA runtime that comes with an
  engine. The switch's description now names replies, images, videos and downloads.
- **Consequences:**
  - One switch silences every desktop notification; it still sits in the "Chat behavior" card.
  - A focused window gets no OS notification — the toast or the studio already shows the result.
  - Engine installs the app starts on its own (first run, a backend update) also notify while
    the user is away; they show in the download panel too.
  - A failed download or generation still only toasts.
- **Owner:** `team`.
- **Links:** `web-app/src/lib/notifications.ts`, `web-app/src/lib/downloadNotification.ts`,
  `web-app/src/containers/DownloadManegement.tsx`,
  `web-app/src/containers/__tests__/DownloadManagement.notifications.test.tsx`.
