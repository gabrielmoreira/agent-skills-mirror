---
date: 2026-09-29
title: "List image and video models in the Hub, from the curated catalog only"
---

# 2026-09-29 — List image and video models in the Hub, from the curated catalog only

- **Context:** The Hub listed chat models only (GGUF/MLX staff picks, the catalog index and Hugging Face).
  Image and video checkpoints could be found and downloaded only inside the Images and Video pages
  (`ImageModelSelector`), so the one screen called "Hub" did not show a third of what the app runs.
  A diffusion checkpoint is not usable on its own: it runs only with the VAE, text encoders and (LTX-2)
  audio VAE that `atomic-chat-conf/models/diffusion.json` pairs with it, and only on a family whose
  workflows the sd.cpp plugin knows.
- **Decision:** A Chat / Images / Video switch sits above the Hub filters (desktop builds with
  `MEDIA_GENERATION`). Images and Video list the families of the curated diffusion catalog — the same
  ones the studio pages offer — installed first, searched by name, developer, description or repo; no
  Hugging Face search. The right panel downloads, removes and opens a quant through `useImageArtifact`,
  the state the studio lists already use. The category lives only in the URL (`?category=image|video`)
  and an absent one means Chat, because every link into the Hub from elsewhere in the app asks for a
  chat model.
- **Consequences:** A new image or video family appears in the Hub the moment the catalog ships it, with
  no app release. Arbitrary diffusion repos cannot be downloaded from the Hub; adding one stays a catalog
  change. The Chat category's Hugging Face feeds are not mounted while Images or Video is open. Returning
  to the Hub from the sidebar always opens Chat.
- **Owner:** team
- **Links:** `web-app/src/lib/hub-media.ts`, `web-app/src/containers/hub/MediaHub.tsx`,
  `web-app/src/containers/hub/MediaFamilyDetailPanel.tsx`, `web-app/src/routes/hub/index.tsx`.
