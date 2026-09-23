# Opus 5.5 defaults — QA evidence (2026-09-22)

## What was tested
The shipped chain tables and the surfaces that read them. These are data consumed by
`resolveModelWithFallback` (model-core) and `resolveCategory` / `resolveAgent` (senpi-task),
so the resolution tests drive the production seam directly rather than asserting the literal.

| Command | Result |
|---|---|
| `cd packages/model-core && bun test` | 403 pass / 0 fail |
| `cd packages/senpi-task && bun test` | 2584 pass / 0 fail |
| `cd packages/omo-senpi && bun test src/components/telemetry` | 210 pass / 0 fail |
| `node packages/omo-senpi/plugin/scripts/build-extension.mjs --check` | build is current |

## RED before GREEN
`21bba6be3` commits the chain expectations alone, with the source untouched: 9 failed / 21 passed
across `model-requirements-categories`, `category-routing-policy` and `model-requirements-agents`.
`67fbdeb5a` moves the source and those suites go green.

## Bundle proof (the check that can lie)
`build-extension.mjs --check` compares the working tree to itself, so after resolving a bundle
conflict by taking dev's copy it reports "current" against a bundle that does NOT carry this change.
Counted the symbol instead:

    claude-opus-5-5 occurrences, nine tracked plugin/extensions files
      on origin/dev:            0 0 0 0 0 0 0 0 0
      after regeneration:       omo.js 1, omo-task.js 1, omo-init-deep-advisor.js 1 (rest 0)

Only then does `--check` report current.

## Docs sweep audit (collateral caught)
Eight doc rows list an Opus rung and a GPT rung on the same line, so a line-scoped
`xhigh` -> `max` replacement also flipped GPT-6 Astra and GPT-5.6 Sol. Detected by counting
`<model>...xhigh` occurrences per model against HEAD; all eight restored, final count of
non-Opus `xhigh` losses = 0. The `claude-opus-5.ts` file keeps its name.

## What was omitted
No live OpenCode/Senpi session drive: this change ships no new hook, tool, command or runtime
path — it changes chain DATA plus one prompt string, and both are covered by the resolution
tests above plus the byte-pinned telemetry doc gate. The prompt string change is exercised by
the Sisyphus factory tests.
