---
date: 2026-10-01
title: "Download decision models in the Hub, run them on the TurboQuant page"
---

# 2026-10-01 — Download decision models in the Hub, run them on the TurboQuant page

- **Context:** atomic-chat-core gained a decision module (core ADR
  `2026-09-30-the-decision-model-is-its-own-core-module`): `llama-server --decision` on the TurboQuant fork,
  driven through `/atomic/v1/decision/*` and served as `POST /v1/systemone` and `POST /v1/router/score` on the
  Local API Server. The core accepts a laya checkpoint folder and has the engine convert it once into
  `<data>/decision/gguf-cache`. The app had no way to get a model onto disk or to start one. Owner decisions of
  2026-09-30: the catalog lives in atomic-chat-conf, only the three verified models ship (`laya-multilingual`
  by default, `laya`, `laya-typed-decisions`), the router stays `systemone` with `allow_uncalibrated` off and
  no toggle, and the model runs on the CPU. Owner decision of 2026-10-01: models are found in the Hub, the
  downloaded ones are run from the llama.cpp TurboQuant provider page, and there is no Settings page and no
  endpoint display for them.
- **Decision:** The Hub's category switch (2026-09-29) becomes a dropdown in the shape of the Images and Video
  mode picker, each type with its icon and what its models do, and gains a fourth type, Decision
  (`?category=decision`). It lists only the types the machine runs: Images and Video with `MEDIA_GENERATION`,
  Decision on desktop builds where TurboQuant has a build (not macOS x64, Windows arm64, Linux arm64). The
  Decision category lists the catalog `models/decision.json` from atomic-chat-conf, cached for an hour, with a
  generated offline baseline (`decision-catalog-baseline.ts`, written by `sync-upstream-baseline.mjs`);
  downloaded models first, searched by name, description, repo or backbone. A model is downloaded file by file
  from its pinned Hugging Face revision into `<data>/decision/models/<id>/` through the ordinary downloader, so
  the download panel, the proxy and the size/sha256 check apply; the task id is `decision-<id>`, cancel-only in
  the panel. "Downloaded" means every catalog file is on disk; Open leads to the provider page. There, under
  the chat models, a Decision models card lists the downloaded models. Start writes `enabled`, `model_path` and
  `model_id` to the core's decision config and loads it, then raises the Local API Server under the same
  auto-start rule as image and video models. Stop turns `enabled` off, because an unload alone is undone by the
  next call. One model runs at a time. Remove clears an active model from the core before deleting its folder,
  so the process lets go of it and the core drops the converted copy. `DECISION_ENGINE_UNSUPPORTED` offers a
  TurboQuant install: the newest release when one is out, otherwise the build that fits the machine. The API
  screen names the served decision model, and its request log shows a decision call's state and answers,
  which the core supplies while the screen is open.
- **Consequences:** Decision models never live under `llamacpp/models`, and the picker filters `decision` and
  `laya` ids as artifacts, so they cannot surface as chat models. Disk use is the checkpoint plus about the
  same again for the converted GGUF; the Hub and the provider page quote the sum. Starting a model needs the
  TurboQuant release named in the catalog's `min_engine`; until that release is out, the provider page shows
  the engine error. The card shows whether or not the TurboQuant provider is switched on, since the core finds
  the engine on disk either way. This needs core 0.7.5 (folder `model_path`, the conversion cache,
  `convert_type`, decision previews in `api:request`).
- **Owner:** team.
- **Links:** `web-app/src/services/decision-catalog-registry.ts`, `web-app/src/services/decision/tauri.ts`,
  `web-app/src/lib/decision/models.ts`, `web-app/src/stores/decision-store.ts`,
  `web-app/src/hooks/useDecisionModel.ts`, `web-app/src/containers/hub/HubCategorySelect.tsx`,
  `web-app/src/containers/hub/DecisionHub.tsx`, `web-app/src/containers/DecisionModelsSection.tsx`,
  atomic-chat-conf `models/decision.json`.
