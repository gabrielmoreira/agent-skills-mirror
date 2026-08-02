---
name: run-workflow
description: Orchestrate parallel subagent pipelines from a JavaScript workflow script — fan out work across many items (tickers, filings, findings) then synthesize, or run a saved workflow by name. Unlocks the RunWorkflow tool.
---

# Programmatic Workflows (RunWorkflow)

Use `RunWorkflow` when a deterministic pipeline should orchestrate multiple subagents — fan-out research then synthesize, classify then act per item, generate then verify. Prefer it over issuing many `Task` calls yourself when the dispatches are data-driven (one per ticker, per filing, per finding). Do NOT use it for a single subagent (use `Task`) or for code that dispatches nothing (use `ExecuteCode`).

## The script

You write JavaScript (ES2020). It executes server-side: the script itself cannot touch the workspace filesystem — the subagents it dispatches can. The script must declare a pure object literal first:

```js
export const meta = { name: 'ticker-briefs', description: 'Fan out research, synthesize' }
```

`name` (letters, digits, `-`, `_`) and `description` are required; no variables or function calls inside the literal. The rest of the body is free-form async JS — top-level `await` and `return` both work, and the `return` value (JSON-serializable) becomes the run result.

## Built-ins

- `await agent(prompt, opts?)` — dispatch one subagent, resolve to its result text. `opts`: `agentType` (default `'general-purpose'`; same types as `Task`), `label` (display name), `phase` (progress group), `schema` (JSON Schema — the child is instructed to answer as matching JSON and the resolved value is the **parsed object**; one corrective retry on invalid output, then `null`).
- `await parallel(thunks)` — run an array of `() => Promise` concurrently; resolves to results in order. Never rejects: a failed thunk yields `null` in its slot.
- `await pipeline(items, ...stages)` — each item flows through the stages independently with NO barrier between stages. Each stage receives `(prevResult, originalItem, index)`; a throwing stage nulls that item and skips its remaining stages.
- `phase(title)` / `log(message)` — progress markers streamed live to the user.
- `args` — the `params` value passed to `RunWorkflow`, verbatim.

Failure semantics: `agent()` **throws** only on calls your script got wrong (unknown `agentType`, oversized prompt or schema, dispatch cap). Everything else resolves to **`null`**: the child failed, timed out, or never launched because the platform was unavailable. Treat `null` as "no result from this call", not as "the child ran and had nothing" — a run whose children all return `null` has produced nothing, so check before reporting success, and write your synthesis to handle partial results. Child concurrency is capped run-wide; extra `agent()` calls queue automatically, so fan out freely.

## Example

```js
export const meta = { name: 'ticker-briefs', description: 'Research each ticker, then synthesize' }

phase('Research')
const briefSchema = {
  type: 'object',
  properties: { summary: { type: 'string' }, risks: { type: 'array', items: { type: 'string' } } },
  required: ['summary'],
}
const results = await parallel(args.tickers.map((t) => () =>
  agent(`Research ${t}: fundamentals, recent news, key risks.`, { agentType: 'research', label: t, schema: briefSchema })))

phase('Synthesize')
const briefs = {}
const failed = []
results.forEach((r, i) => { if (r) briefs[args.tickers[i]] = r; else failed.push(args.tickers[i]) })
log(`${Object.keys(briefs).length} briefs, ${failed.length} failed`)
return { briefs, failed }
```

## Saved workflows

- Workflows live at `.agents/workflows/<name>.js` — the file is the whole script, `meta` included, and `meta.name` must equal `<name>`. Run one with `RunWorkflow(workflow="<name>", params={...})`.
- Write `.agents/workflows/<name>.js` to save a workflow you expect to run again; it stays available across threads.

## Running

`RunWorkflow(script=..., params={...})` (or `script_path=...`, or `workflow="<name>"`) returns a task id immediately and runs in the background — continue other work, then poll `TaskOutput(task_id="...")` for progress or the final result (add `timeout=120` to block). Each dispatched child is a real background task: drill into a truncated result with `TaskOutput(task_id="<child task_id>")`. Run artifacts (per-child records, `result.json`) land under `.agents/threads/<thread>/workflows/<run-id>/`.
