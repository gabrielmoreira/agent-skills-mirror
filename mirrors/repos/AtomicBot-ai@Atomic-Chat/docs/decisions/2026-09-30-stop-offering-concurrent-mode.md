---
date: 2026-09-30
title: "Stop offering Concurrent Mode"
---

# 2026-09-30 — Stop offering Concurrent Mode

- **Context:** Both llama.cpp providers showed a Concurrent Mode switch (`concurrent_mode`, with
  `concurrent_slots`): a multi-slot server that splits the context across up to 16 slots and overrides
  Parallel Sequences and Continuous Batching. It is a demo feature (`scripts/concurrent-demo/`), and in the
  settings list it reads as something a user should turn on. Owner decision of 2026-09-30: hide it in the app;
  the core keeps the setting.
- **Decision:** The provider settings screen no longer renders the `concurrent_mode` and `concurrent_slots`
  rows, and drops the code that dimmed Parallel / Continuous Batching / Prometheus and forced `expose_metrics`
  on with it. Both llama.cpp extensions switch a stored `concurrent_mode: true` off on every start
  (`migrateConcurrentModeOff`); the next core load imports the change as an app-side edit.
- **Consequences:** No one can reach Concurrent Mode from the UI, and a profile that had it on gets its full
  context back. The keys stay in the core's schema, the vendored copy and the extensions' `settings.json`, so
  the descriptions of Parallel Sequences and Prometheus /metrics still mention Concurrent Mode. Removing it
  for good means a core change and release. A value set through the CLI is switched off at the next app start.
- **Owner:** team.
- **Links:** `web-app/src/routes/settings/providers/$providerName.tsx`,
  `extensions/llamacpp-upstream-extension/src/index.ts`, `extensions/llamacpp-extension/src/index.ts`.
