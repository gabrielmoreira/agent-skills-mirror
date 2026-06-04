---
mode: agent
description: Reconcile the five naming registries (`coding-prefixes.md`, `api-conventions.md`, `database-schema.md`, `error-codes.md`, `config-vars.md`) with what actually exists in the codebase. Runs the naming agent in Mode 4 (Audit Registry), then hands index updates to the curator.
---

# /ai-audit-registries

Run a full registry audit. Use this:

- after a major refactor that may have introduced or retired identifiers,
- as part of a release readiness check,
- when the validator reports unattributed names but the offending names look legitimate.

## Procedure

1. **Invoke the [`naming`](../agents/pds-man-naming.agent.md) agent in Mode 4 (Audit Registry).** Pass `scope_path: project-root` so the audit covers every module. Use [`load-context`](../../.ai/agents/tools/load-context.json) per the agent contract.

2. **Naming agent runs the sweep**:
   - Walks the codebase for each registry kind:
     - **coding-prefixes**: every UI element id, component name, and code-side identifier (ap_/ev_/mt_/wk_/fl_/st_) that should match the 2-letter-prefix rule.
     - **api-conventions**: every route declaration in code (HTTP verbs, paths).
     - **database-schema**: every table / column / index / migration filename.
     - **error-codes**: every `ERR_*` literal raised, returned, or asserted.
     - **config-vars**: every env-var or config-key access in code.
   - Diffs the in-code population against the registry rows.
   - Categorizes findings: `additions` (in code, missing from registry), `removals` (in registry, no longer used), `renames` (likely pair: one removed + one added with similar root), `collisions` (two distinct concepts sharing a name).

3. **Naming applies safe diffs in-place** to the five registry files:
   - `additions` — write new rows directly, including the `naming_source` of the originating consultation when known.
   - `collisions` — never auto-resolve; report to user.
   - `removals` and `renames` — propose to user; do not execute. These often represent intentional deprecation that needs human review.

4. **Hand off to [`curator`](../agents/pds-man-curator.agent.md)** via [`delegate-task`](../../.ai/agents/tools/delegate-task.json) with stage `curate` and the audit summary. Curator updates:
   - [`.ai/index.md`](../../.ai/index.md) entries for any newly registered or removed identifiers,
   - cross-references in `.ai/instruct.md` files that pointed at the old/new entries.

5. **Hand any rename approvals to [`cleanup`](../agents/pds-pipe-cleanup.agent.md)** via `delegate-task` with stage `cleanup`. Cleanup performs the file moves under archive-first, never silently.

6. **File a TODO** for any unresolved item via [`append-todo`](../../.ai/agents/tools/append-todo.json) with severity `minor` and tag `registry-audit`.

## Output

A structured report:

```
Registry      Additions  Removals  Renames  Collisions
prefixes      <n>        <n>       <n>      <n>
api           <n>        <n>       <n>      <n>
schema        <n>        <n>       <n>      <n>
errors        <n>        <n>       <n>      <n>
config        <n>        <n>       <n>      <n>

Auto-applied: <list of additions written>
Awaiting approval: <list of removals/renames/collisions>
TODOs filed: <count>
Curator handoff: complete | pending
```

## Hard rules

- The naming agent is the **only** writer of the five registry files during this command. Curator and cleanup are downstream.
- Never delete a registry row without explicit user approval — registries are append-mostly per [`.ai/maintenance.md`](../../.ai/maintenance.md).
- A non-empty `Collisions` row halts auto-application — escalate every collision before any further writes.
