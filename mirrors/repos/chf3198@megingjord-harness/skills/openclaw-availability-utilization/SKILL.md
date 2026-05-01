---
name: openclaw-availability-utilization
description: Keep OpenClaw gateway highly available and actively used through mandatory preflight checks, execution routing, and failover controls.
argument-hint: "[goal: preflight|route|recover|optimize|status] [task: coding|tests|research|deploy]"
user-invocable: true
disable-model-invocation: false
---

# OpenClaw Availability + Utilization Ops

## Purpose

Make OpenClaw usage operational by default instead of optional:
- Keep gateway reachable and healthy.
- Route heavy work to the best machine automatically.
- Enforce utilization targets so local-only execution does not drift.

## Mandatory Session Preflight

Run before implementation sessions and every 60–90 minutes during long sessions.

1. **Network lane check**
   - Auto-detect fleet via `fleet-config.js profile`.
   - If profile is `solo`, skip fleet checks — use cloud fallback chain.
2. **Gateway health check**
   - Confirm OpenClaw service is up and model status responds.
3. **Provider budget check**
   - Confirm OpenRouter daily limits and remaining quota.
4. **Failover integrity check**
   - Confirm primary + fallback chains are still free-only and ordered.

## Utilization Policy

### Task routing matrix

- **Heavy tasks** (multi-suite Playwright runs, broad static analysis, large refactors): run through OpenClaw on Windows.
- **Medium tasks** (single feature + focused tests): split by pressure; prefer OpenClaw if Chromebook memory is constrained.
- **Light tasks** (small docs edits, tiny patches): local execution acceptable.

### Minimum target utilization

For coding sessions longer than 45 minutes **when fleet is available** (profile=full or degraded):
- Prefer fleet lane for heavy workloads when reachable.
- If fleet is unavailable (profile=solo), use cloud free tier (Groq/Cerebras/OpenRouter).
- No fixed percentage mandate — use fleet when it adds value, skip when it doesn't.

## Recovery Playbook

If availability drops:
1. Re-check Tailscale status and SSH path.
2. Re-validate OpenClaw health and model probe.
3. Rotate to next free fallback chain if current model is degraded.
4. If lane remains unstable, run local with explicit degraded-mode note and retry OpenClaw lane at next checkpoint.

## Session Control Loop

Use this loop:

`PRECHECK -> EXECUTE -> VERIFY -> UTILIZATION CHECK -> ADAPT`

- **PRECHECK**: run mandatory preflight.
- **EXECUTE**: route work per matrix.
- **VERIFY**: run task tests/lint checks.
- **UTILIZATION CHECK**: compare actual OpenClaw usage vs target.
- **ADAPT**: re-route next slice if target missed.

## Evidence Logging (required)

Record lightweight evidence in task updates:
- Lane used (`openclaw/windows` vs `local/chromebook`)
- Health outcome (`ok`, `degraded`, `recovered`)
- Utilization estimate for current session (percentage)

## Integration

Load together with:
- `repo-standards-router` (first)
- `network-platform-resources` (connectivity + host inventory)
- `openrouter-free-failover` (model chain quality)
- `workflow-self-anneal` only if repeated lane failures/process drift occur
