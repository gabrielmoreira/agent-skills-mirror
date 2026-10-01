---
date: 2026-09-30
title: "Hide the Apple on-device provider"
---

# 2026-09-30 — Hide the Apple on-device provider

- **Context:** The `foundation-models` provider (Apple's on-device model, served by the core's
  `foundation-models-server`) was offered whenever the server's `--check` answered `available`. The owner's
  report of 2026-09-30: chats with it do not work at all on a Mac where it is offered. Until then the app only
  hid it where the check said no, and a provider persisted by an earlier version stayed in the store
  regardless, because `setProviders` keeps every persisted provider it is not sent.
- **Decision:** Withdraw the provider everywhere until it works. The extension's `onLoad` returns before it
  registers (`OFFERED = false` in `extensions/foundation-models-extension/src/index.ts`), so no provider list,
  picker or availability check sees it; `useModelProvider.setProviders` drops a persisted `foundation-models`
  provider (`WITHDRAWN_PROVIDERS`), which also clears a selection on its model. The extension, the core's
  runtime and the Swift server stay as they are.
- **Consequences:** Nothing on any Mac offers the on-device model, and a thread that used it opens without its
  model, as for any missing model. The desktop e2e `foundation-models.spec.ts` now checks that the picker leaves
  the provider out even when the server says `available`; the chat case is in its history. Offering it again
  is `OFFERED = true`, removing it from `WITHDRAWN_PROVIDERS`, and restoring that e2e case.
- **Owner:** team.
- **Links:** `extensions/foundation-models-extension/src/index.ts`, `web-app/src/hooks/useModelProvider.ts`,
  `tests/e2e/desktop/foundation-models.spec.ts`, `docs/testing-critical-flows.md`.
