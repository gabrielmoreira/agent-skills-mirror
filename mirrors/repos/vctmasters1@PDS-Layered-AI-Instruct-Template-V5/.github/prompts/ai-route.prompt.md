---
mode: agent
description: Route a task through the generic agent triad — Router resolves scope and governance, Supervisor orchestrates worker stages (scaffold → generate → validate → test → review).
---

# /ai-route

Hand a task to the generic agent triad. The Router resolves the authoritative `.ai/instruct.md` scope and any governance overlay, then the Supervisor orchestrates workers stage-by-stage with gates between each.

> **→ [Router](../agents/pds-meta-router.agent.md)** — picks scope and next-hop agent.
> **→ [Supervisor](../agents/pds-pipe-super.agent.md)** — orchestrates the worker pipeline.
> **→ [Governance overlay](../../.ai/governance/README.md)** — pluggable external-rule facility (separate from depth-priority).
> **→ [Tool: route-to-scope](../../.ai/agents/tools/route-to-scope.json)** | [delegate-task](../../.ai/agents/tools/delegate-task.json) | [review-output](../../.ai/agents/tools/review-output.json) | [get-governance-rules](../../.ai/agents/tools/get-governance-rules.json)

---

## Steps

### 1. Collect the task

- Capture the user's request verbatim.
- Extract any explicit `path:`, `topic:`, or `context:` hints. If none, infer from the request and confirm before proceeding.

### 2. Run the Router

Invoke the **Router** agent. It will:

- Resolve `scope_path` (deepest `.ai/instruct.md` for the affected paths).
- Call `get-governance-rules` for any active overlay.
- Pick the next hop: `supervisor` for multi-step generative tasks, a single worker for single-step tasks, `project-explorer` for read-only exploration.

Output a routing decision block:

```
Scope:           <scope_path>
Authority file:  <scope_path>/.ai/instruct.md
Background:      <list of ancestor .ai/instruct.md files>
Governance:      <list or "none">
Next hop:        <agent>
```

### 3. Hand off

- **If next hop is the Supervisor** → invoke the Supervisor with the full routing decision. The Supervisor runs the pipeline (scaffold → generate → validate → test → review), gating each stage with `review-output`.
- **If next hop is a single worker** → invoke that worker directly with the routing decision; on completion, gate the output with `review-output` once.
- **If next hop is project-explorer** → invoke read-only and stop.

### 4. Surface gates and decisions

After every gate, post a one-line status:
```
[stage] PASS  → advancing to <next_stage>
[stage] FAIL  → retrying with guidance: <summary>
[stage] BLOCK → escalating to user
```

### 5. Stop conditions

- All stages PASS → summarize the final change set and any `.ai/instruct.md` updates made.
- Any stage BLOCKs twice → stop, show the failure list, ask the user how to proceed.
- A stage requires editing outside `scope_path` → return to step 2 with the new affected paths.

---

## Notes

- This command **respects** the AI-INSTRUCT Maintenance Rule: if any architectural change is made, the relevant `.ai/instruct.md` is updated in the same operation by the Generator/Reviewer, not deferred.
- Governance is **additive only**. The deepest `.ai/instruct.md` remains authoritative for codebase design; governance adds external constraints on top.
- If the project has not registered any governance rules, the overlay is empty and depth-priority alone governs — that is valid and expected for most projects.
