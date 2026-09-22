# Routing default change QA - issue #8616

## What was tested

Three runtime default-preset changes, each proven at the resolver seam that the `task` tool and the
agent planner actually call:

1. `unspecified-high` must stop resolving to `gpt-6-astra` and start at `claude-opus-5 (xhigh)`.
2. `quick` must stop resolving to `kimi-for-coding-highspeed` and start at `gpt-5.6-luna-fast (low)`.
3. `explore` / `librarian` must lead with `kimi-for-coding-highspeed` at the no-thinking variant (`off`).

Driver: `qa-unspecified-high-resolution.ts` (kept out of the commit; body reproduced below) calling
`resolveCategory` from `packages/senpi-task/src/category/index` and `resolveAgent` from
`packages/senpi-task/src/agents/resolve-agent` against a fake registry that serves every rung of
both chains at once (gpt-6-astra, gpt-5.6-luna-fast, claude-opus-5, glm-5.3, kimi-k3,
kimi-for-coding-highspeed, deepseek-v4-flash). A registry serving every candidate is the decisive
fixture: the winner is the chain order, not availability.

```ts
const models = [
  { provider: "openai-codex", id: "gpt-6-astra" },
  { provider: "openai-codex", id: "gpt-5.6-luna-fast" },
  { provider: "anthropic", id: "claude-opus-5" },
  { provider: "zai-coding-plan", id: "glm-5.3" },
  { provider: "kimi-coding", id: "kimi-k3" },
  { provider: "kimi-coding", id: "kimi-for-coding-highspeed" },
  { provider: "deepseek", id: "deepseek-v4-flash" },
]
const registry = {
  getAvailable: () => models,
  find: (provider, modelId) => models.find((m) => m.provider === provider && m.id === modelId),
}
resolveCategory("unspecified-high", {}, registry)
resolveCategory("quick", {}, registry)
resolveAgent("explore", { explore: { name: "explore", categories: [] } }, registry)
resolveAgent("librarian", { librarian: { name: "librarian", categories: [] } }, registry)
```

## What was observed

BEFORE (unmodified tree at origin/dev 6885e24ad), unspecified-high only:

```
category: unspecified-high
provider: openai-codex
modelId: gpt-6-astra
variant: high
fallbacks: ["anthropic/claude-opus-5","zai-coding-plan/glm-5.3"]
```

AFTER (this branch):

```
unspecified-high: anthropic/claude-opus-5 variant=xhigh reasoningEffort=undefined
quick: openai-codex/gpt-5.6-luna-fast variant=low reasoningEffort=undefined
explore: kind=resolved model=kimi-coding/kimi-for-coding-highspeed variant=off reasoning=off
librarian: kind=resolved model=kimi-coding/kimi-for-coding-highspeed variant=off reasoning=off
```

`explore` / `librarian` carry `variant=off reasoning=off`. Senpi's own catalog
(`node_modules/@code-yeongyu/senpi/dist/bundle/chunks/chunk-XRHUMMIW.js`) declares
`kimi-for-coding-highspeed` with `reasoning: true`, `compat.forceAdaptiveThinking: true` and no
`supportsDisabledThinking`, and the anthropic-messages lane's `disableThinkingForRequest` therefore
deletes the thinking block and sets `output_config = { effort: "low" }` instead of sending
`thinking: { type: "disabled" }`. That is the minimum-thinking request the Kimi endpoint accepts.

## Gates

- `bun test packages/senpi-task packages/model-core packages/omo-senpi/src/components/task packages/omo-opencode/src/tools/delegate-task`
  -> 4055 pass / 1 skip / 0 fail (502 files). Log: `gate-tests.txt`.
- RED capture before the source change: 10 failures for the unspecified-high pins, then 22 for the
  quick/explore pins, each failing on the expected-vs-received model id. Logs: `red-unspecified-high.txt`,
  `red-quick-explore.txt`.
- `tsgo --noEmit` on `packages/senpi-task`, `packages/model-core`, `packages/omo-senpi` -> exit 0 each.

## Why it is enough

The changed surface is data: two fallback-chain tables, two builtin category definitions and two agent
chains. The resolver reading those tables is the same function the task tool and the child planner call
at spawn time, so driving it with a registry that serves every rung proves the shipped routing order
rather than a mock of it. The chain-order pins in both editions plus the cross-edition parity test
cover the tables themselves.

## What was omitted

No live provider call: the models in the fixture registry are identifiers, no credential is used and no
request leaves the machine. No secret-bearing logs are included.
