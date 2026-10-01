---
date: 2026-09-30
title: "Shape the media form for the picked model, and let Generate start it"
---

# 2026-09-30 — Shape the media form for the picked model, and let Generate start it

- **Context:** On the Images and Video pages the form only knew a model once it was loaded: the negative
  prompt, the Reset button and the ranges appeared when the start finished (the column jumped), Generate stayed
  off until the user pressed the model's own Start, and `loadModel` replaced the draft with the family's
  defaults whenever the resident model changed — including the first start after a launch. The owner's
  recording of 2026-09-30: 640 × 480, 10 steps, cfg 3 set with Qwen-Image 2.1 stopped came back as
  1024 × 1024, 40 steps, cfg 6 after Start.
- **Decision:** The page works with one checkpoint, the one its picker shows (`useMediaTarget`: the resident
  model when it suits the page, else the installed pick). Before it is resident, its capabilities are derived
  from the catalog exactly as the core derives them from the load request (`lib/diffusion/capabilities.ts`:
  negative prompt when the default cfg is above 1, distilled guidance when the family has a default, the
  family's ranges and presets); the core's report replaces them after the load. The draft records the family
  its numbers are for (`recipeFamily`, persisted); `adoptModel` gives a different family its defaults and only
  clamps the same family's, and it runs when the page's model is picked or loaded, never inside `loadModel`.
  Generate is on for an installed, stopped model: it starts the model, then generates the draft as it is.
- **Consequences:** Controls are in place from the moment a model is picked, and a start changes nothing the
  user set. A switch of family still resets the numbers (a FLUX checkpoint at Qwen's 40 steps and cfg 6
  produces garbage), now visibly at the pick instead of silently at the start. Loads started elsewhere (the
  API, Settings) no longer touch the draft; the page adopts on its next render. A draft saved before this
  change has no `recipeFamily`, so the first model it meets resets it once. The preview must follow the core's
  rules (`capabilities()` / `videoCapabilities()` in atomic-chat-core `src/diffusion/session.ts`); the catalog's
  own `capabilities.negative_prompt` flag is not used, since it disagrees with the core for Qwen-Image 2.1.
  A resident model whose report lacks the workflow keeps Generate off unless a restart adds it (the vision
  encoder of a family that has one).
- **Owner:** team.
- **Links:** `web-app/src/hooks/useMediaTarget.ts`, `web-app/src/lib/diffusion/capabilities.ts`,
  `web-app/src/hooks/useImageForm.ts`, `web-app/src/hooks/useVideoForm.ts`,
  `web-app/src/hooks/useImageGeneration.ts`, `web-app/src/hooks/useVideoGeneration.ts`,
  `web-app/src/stores/image-generation-store.ts` (`loadModel`).
