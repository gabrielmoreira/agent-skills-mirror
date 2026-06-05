---
mode: agent
description: Reconcile the five naming registries (`coding-prefixes.md`, `api-conventions.md`, `database-schema.md`, `error-codes.md`, `config-vars.md`) plus the port registry (`ports.md`) with what actually exists in the codebase. Runs the naming agent in Mode 4 (Audit Registry) and port validator, then hands index updates to the curator.
---

# /ai-audit-registries

Run a full registry audit. Use this:

- after a major refactor that may have introduced or retired identifiers,
- as part of a release readiness check,
- when the validator reports unattributed names but the offending names look legitimate.

## Procedure

1. **Run naming agent Mode 4 (Audit Registry)**:
   - Invoke [`naming`](../agents/pds-man-naming.agent.md) agent with `scope_path: project-root` and `mode: audit-registries`.
   - Pass `load-context` per agent contract.

2. **Naming agent sweeps five registries**:
   - **coding-prefixes**: UI element ids, component names, identifiers (ap_/ev_/mt_/wk_/fl_/st_ prefixes)
   - **api-conventions**: HTTP routes, endpoints, methods
   - **database-schema**: tables, columns, indices, migrations
   - **error-codes**: all `ERR_*` literals raised/returned/asserted
   - **config-vars**: env-vars and config-key accesses
   - Diffs in-code population vs registry rows
   - Categorizes: `additions`, `removals`, `renames`, `collisions`

3. **Naming applies safe diffs**:
   - `additions` → write new rows directly (with `naming_source` when known)
   - `collisions` → report to user; do not auto-resolve
   - `removals`/`renames` → propose; await approval

4. **Run port registry audit**:
   - Call `python .ai/engine/port_validator.py . --scope . --audit`
   - Report: collisions, range_violations, unregistered services, drift (hardcoded vs registry), orphaned (in registry but unused)
   - Categorize findings same as naming: additions (new services), removals (stale registry entries), drift (config mismatch)

5. **Hand off to [`curator`](../agents/pds-man-curator.agent.md)**:
   - Pass audit summary: naming findings + port findings
   - Curator updates [`.ai/index.md`](../../.ai/index.md) for new/removed identifiers and services
   - Curator updates `.ai/instruct.md` cross-references

6. **Hand removals/renames to [`cleanup`](../agents/pds-pipe-cleanup.agent.md)**:
   - Via `delegate-task` with stage `cleanup`
   - Cleanup archives files under archive-first protocol

7. **File TODOs** for unresolved items via `append-todo` with severity `minor` and tag `registry-audit`.

## Output

A structured report:

```
NAMING REGISTRIES:
  Registry      Additions  Removals  Renames  Collisions
  prefixes      <n>        <n>       <n>      <n>
  api           <n>        <n>       <n>      <n>
  schema        <n>        <n>       <n>      <n>
  errors        <n>        <n>       <n>      <n>
  config        <n>        <n>       <n>      <n>

PORT REGISTRY:
  Status        Additions  Removals  Drift    Collisions
  ports.md      <n>        <n>       <n>      <n>

Auto-applied: <list of additions written>
Awaiting approval: <list of removals/renames/collisions + port findings>
TODOs filed: <count>
Curator handoff: complete | pending
```

## Hard rules

- The naming agent is the **only** writer of the five registry files during this command. Curator and cleanup are downstream.
- Never delete a registry row without explicit user approval — registries are append-mostly per [`.ai/maintenance.md`](../../.ai/maintenance.md).
- A non-empty `Collisions` row halts auto-application — escalate every collision before any further writes.
