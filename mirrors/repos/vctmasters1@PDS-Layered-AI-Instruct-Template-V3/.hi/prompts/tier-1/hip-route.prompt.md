---
mode: agent
description: Route a task through the generic agent triad — Router resolves scope and governance, Supervisor orchestrates worker stages (scaffold → generate → validate → test → review).
---

# /hip-route

Hand a task to the generic agent triad. The Router resolves the authoritative `.hi/instruct.md` scope and any governance overlay, then the Supervisor orchestrates workers stage-by-stage with gates between each.

> **→ [Router](../../agents/tier-1/hia-router.agent.md)** — picks scope and next-hop agent.
> **→ [Supervisor](../../agents/tier-1/hia-super.agent.md)** — orchestrates the worker pipeline.
> **→ [Governance overlay](../../governance/README.md)** — pluggable external-rule facility (separate from depth-priority).
> **→ [Model-dispatch](../../plugins/model-dispatch/instruct.md)** — local-AI detection, tier proposal/self-implement, and healing primitives the Router uses.
> **→ [Tool: route-to-scope](../../agents/tools/route-to-scope.json)** | [delegate-task](../../agents/tools/delegate-task.json) | [review-output](../../agents/tools/review-output.json) | [get-governance-rules](../../agents/tools/get-governance-rules.json)

---

## Steps

### 1. Collect the task

- Capture the user's request verbatim.
- Extract any explicit `path:`, `topic:`, or `context:` hints. If none, infer from the request and confirm before proceeding.

### 2. Run the Router

Invoke the **Router** agent. It will:

- Resolve `scope_path` (deepest `.hi/instruct.md` for the affected paths).
- Call `get-governance-rules` for any active overlay.
- Pick the next hop: `supervisor` for multi-step generative tasks, a single worker for single-step tasks, `project-explorer` for read-only exploration.

Output a routing decision block:

```
Scope:           <scope_path>
Authority file:  <scope_path>/.hi/instruct.md
Background:      <list of ancestor .hi/instruct.md files>
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

- All stages PASS → summarize the final change set and any `.hi/instruct.md` updates made.
- Any stage BLOCKs twice → stop, show the failure list, ask the user how to proceed.
- A stage requires editing outside `scope_path` → return to step 2 with the new affected paths.

---

## Notes

- This command **respects** the Hierarchical-Instruct Maintenance Rule: if any architectural change is made, the relevant `.hi/instruct.md` is updated in the same operation by the Generator/Reviewer, not deferred.
- Governance is **additive only**. The deepest `.hi/instruct.md` remains authoritative for codebase design; governance adds external constraints on top.
- If the project has not registered any governance rules, the overlay is empty and depth-priority alone governs — that is valid and expected for most projects.

---

## Explain / audit mode (why does this scope win?)

Use this read-only mode in code review when you need to **justify or question** a
resolution — e.g. "why is the module rule overriding the root rule here?"

Run the canonical resolver's explain report for the path in question:

```bash
python .hi/engine/get_effective_instructions.py --path <path> --explain
# machine-readable for tooling / PR bots:
python .hi/engine/get_effective_instructions.py --path <path> --explain --json
```

The report shows:

- **Governing layers** — every `.hi/instruct.md` from root to the path, shallowest first, with the deepest marked `★ AUTHORITY` (the winner).
- **Override map** — each topic (section heading) declared by more than one layer, the deepest layer that owns it, and the shallower layers it **shadows**. These are exactly the override decisions a reviewer should scrutinize.

This makes "deepest wins" auditable: the choice is no longer implicit — the
override map names every place a deeper file supersedes a shallower one, so it
can be questioned in review like any other diff.

---

## Local-AI mode (`/hip-route --models`)

A read-only-by-default entry point into the Router's [Local-AI self-awareness](../../agents/tier-1/hia-router.agent.md#local-ai-self-awareness) step. Use it to ask the Router to look at the box and offer to run agent work on local models.

The Router will:

1. **Detect** local runtimes (LM Studio / Ollama) and hardware — read-only, fail-soft:
   ```bash
   pwsh .hi/plugins/model-dispatch/scripts/detect-local-llms.ps1
   python .hi/plugins/model-dispatch/suggest_tiers.py
   ```
2. **Propose** a tier list from the loaded models if `tiers.yaml` is missing/stale — and **ask** before writing anything.
3. **Self-implement** on your approval (backs up any existing config):
   ```bash
   python .hi/plugins/model-dispatch/suggest_tiers.py --apply
   ```
4. **Heal + notify** — if a tier that was serving work drops mid-session, the Router reroutes via `plan_healing(...)` and **surfaces every notification to you**. Privacy-pinning and the `policy.allow_cloud` kill-switch still hold while healing: a `local_only` tier never heals onto cloud.

This mode never adopts local AI silently and never crosses a privacy boundary on its own — it proposes, you approve, it implements, and it tells you whenever the compute picture changes.
