---
date: 2026-09-30
title: "Keep image and video models on a discrete GPU"
---

# 2026-09-30 — Keep image and video models on a discrete GPU

- **Context:** A tester's report of 2026-09-30: on an RTX 3060 (12 GB) an image takes about two minutes and
  its decode about ten seconds with the Memory setting on "Keep on GPU", and far longer on "Auto". "Auto"
  took the fit estimate's policy (`lib/diffusion/fit.ts`), which counts the transformer, the VAE, the text
  encoder (on the GPU outside macOS) and 1.5 GiB per megapixel of activations as resident together and keeps
  the model on the GPU only up to 70 % of the budget. On 12 GB that is `group` offload for Z-Image, Krea 2 and
  Wan 2.2 5B, and `model` offload (text encoder and VAE on the CPU too) for FLUX.2 Klein and Qwen-Image 2.1.
- **Decision:** `autoOffload` (`lib/diffusion/fit.ts`) decides "Auto". Where hardware enumeration found a GPU
  of its own (`memoryKind === 'vram'`), the load asks for `offload: 'none'` with `offloadFallback` set to the
  estimate's policy, or `group` when the estimate would keep the model resident (it prices the family's
  default size). The core retries a load or a job that runs out of memory once under the fallback (core ADR
  2026-09-30-fall-back-to-offload-when-the-gpu-runs-out-of-memory). macOS, CPU-only machines and unknown
  hardware keep the estimate's policy, and Qwen-Image keeps `model` offload on Metal. A forced Memory setting
  sends no fallback.
- **Consequences:** Discrete GPUs render with the model resident unless it does not fit; a shortage costs a
  restart of the engine and, mid-job, the work done so far, and the session stays on the fallback until the
  model is loaded again. Needs a core that reads `offloadFallback`; an older one ignores it, and a shortage
  then fails as before. The fit badge and the estimate itself are unchanged. A driver that spills into shared
  system memory (NVIDIA on Windows) never reports a shortage, so such a job just runs slower.
- **Owner:** team.
- **Links:** `web-app/src/lib/diffusion/fit.ts`, `web-app/src/stores/image-generation-store.ts`,
  `web-app/src/lib/diffusion/models.ts` and their tests; atomic-chat-core ADR
  2026-09-30-fall-back-to-offload-when-the-gpu-runs-out-of-memory.
