---
date: 2026-09-30
title: "Accept embedded MTP on every upstream MTP architecture"
---

# 2026-09-30 — Accept embedded MTP on every upstream MTP architecture

- **Context:** The MTP toggle for `llamacpp-upstream` accepted an embedded head only for `qwen35` and
  `qwen35moe` GGUFs (2026-07-13, detect embedded Qwen MTP from canonical GGUF metadata); every other model
  that is not a Gemma 4 31B / 26B-A4B target got the "MTP isn't available" dialog, and the core dropped the
  flag at load. Upstream b10809 (commit 5266f24da, the recommended backend) builds the MTP graph for 14
  architectures. Owner feedback of 2026-09-30: the refusal looked far narrower than what upstream supports.
- **Decision:** `EMBEDDED_MTP_ARCHITECTURES` in `extensions/llamacpp-upstream-extension/src/util.ts` lists all
  14: `bailingmoe3`, `cohere2moe`, `deepseek2`, `deepseek32`, `deepseek4`, `glm-dsa`, `glm4moe`, `hy_v3`,
  `mimo2`, `nemotron_h_moe`, `qwen35`, `qwen35moe`, `qwen3next`, `step35`. The core's gate
  (`src/models/gguf/classify.ts`, core ADR of the same date) lists the same names. The GGUF must still report
  `{arch}.nextn_predict_layers` > 0.
- **Consequences:** GLM-4.5/4.6/4.7, Qwen3-Next, DeepSeek and the rest accept the toggle when their GGUF kept
  the head. The load only honours it once the app pins a core with the wider gate; until then the core drops
  the flag as before. The dialog text still names only the Qwen and Gemma repositories. The two copies of the
  list are kept in step by hand and re-checked against upstream when the recommended backend moves.
- **Owner:** team.
- **Links:** `extensions/llamacpp-upstream-extension/src/util.ts`,
  `web-app/src/routes/settings/providers/$providerName.tsx`, atomic-chat-core
  `docs/decisions/2026-09-30-gate-embedded-mtp-on-every-upstream-mtp-architecture.md`.
