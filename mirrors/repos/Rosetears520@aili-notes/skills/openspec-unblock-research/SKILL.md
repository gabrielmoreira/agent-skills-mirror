---
name: openspec-unblock-research
description: Supervisor-only, verification-first unblock research engine. Use when a task/attempt is marked BLOCKED and you need to normalize facts vs unknowns, gather evidence via configurable research providers (e.g., mcp__web-search-prime__*, mcp__context7__*, mcp__web-reader__*), and output a portable, auditable unblock report plus executable guidance written to caller-defined sinks (no assumed repo structure).
---

# OpenSpec Unblock Research (Supervisor-Only, Verification-First)

Produce a repeatable unblock package when work is BLOCKED. Do not solve by guessing: separate facts from unknowns, then research to produce evidence-backed guidance.

This skill is intentionally workflow-agnostic: it does not know about run counters, retries, or task systems. The caller provides `blocked_context` and `sinks` (where/how to write outputs).

## Inputs (from caller)

Ask for missing required inputs once, then proceed with what you have.

### Required

- `blocked_context` (structured or semi-structured):
  - `blocker_summary`: 1-2 sentences.
  - `error_excerpt`: exact error text (or `null` if none).
  - `symptoms`: what happens, where, how often.
  - `already_tried`: commands/edits attempted + outcomes.
  - `needs`: what information/artifact is missing (logs, versions, access, files).
  - `environment`: OS, shell, language/runtime versions, tool versions, container/CI context.
- `sinks`: where to persist the report and/or guidance. Do not assume filenames.

### Optional

- `toolchain_config`: research provider routing config (see below). If omitted, use the default provider ordering in this file.
- `budget_config`: limits for research cost and stopping conditions (see below).
- `repo_context` (if relevant): paths, modules involved, prior diffs, related issues/PRs.

## Outputs

1. Portable Unblock Report (JSON, v1): canonical, structured, auditable.
2. Unblock Guidance (markdown): directly executable steps plus verification plus fallbacks.
3. Sink write-back: persist (1) and/or (2) exactly as configured by caller.

Canonical schema plus examples:
- `references/portable-unblock-report.v1.md`
- `references/examples.md`
- `references/templates.md`

## Non-negotiables

- Verification before speculation: never elevate an unverified claim into a Key conclusion.
- Quote exact `error_excerpt` and command outputs as evidence artifacts when available.
- Every Key conclusion MUST have at least one evidence pointer.
- Every guidance step MUST include an explicit verification method.
- If you cannot run tools (no network, tool missing), output a "data to collect" plan instead of guessing.

## Core workflow

### Phase A - Normalize the blocker (facts vs unknowns)

1. Parse inputs into the report fields:
   - Facts: error text, stack trace lines, exit codes, file paths, versions, commands run.
   - Unknowns: missing versions, missing reproduction steps, missing logs, unclear scope.
2. Produce a minimal reproduction checklist:
   - exact command
   - expected vs actual
   - smallest input triggering it (file, snippet, env)
3. Produce a NEEDS list (what to ask for next) if reproduction is impossible.

### Phase B - Plan research (provider routing plus queries)

Build query terms from facts only (error codes, function names, package and version, platform).

Plan providers by role (abstract, not tool-specific):
- Clue source (search): fast, broad, up-to-date pointers.
- Authority source (docs/API): official docs, API references, migration notes.
- Evidence fetcher (reader): pull primary text from candidate links.
- Internal authority (repo/CI logs): local files, lockfiles, tool output.

### Phase C - Execute research within budget

Stop early when you have enough evidence to produce:
- 1-3 key conclusions
- runnable unblock steps plus verification
- at least one fallback path

If evidence conflicts, record the conflict explicitly and list the discriminating experiment.

### Phase D - Synthesize into guidance (actionable plus verifiable)

Produce unblock guidance as ordered steps:
- Step: command/config/code location
- Why: tie back to key conclusion
- Verify: command/assertion/log line to confirm

Add fallbacks:
- If A fails -> B
- If B is blocked -> specify exact missing input required to proceed

### Phase E - Write to sinks (caller-controlled)

Render (JSON report and/or markdown guidance) and write to each configured sink. If a sink cannot be written, record it as an error in the report and still return the outputs in-chat.

## Toolchain config (declarative, extendable)

Treat each research tool (including future MCP servers) as a provider entry. Routing is driven by provider entries, not hard-coded logic.

Example shape:

```json
{
  "providers": [
    {
      "provider_id": "mcp__context7__*",
      "tool_glob": "mcp__context7__*",
      "role": "authority|clue|evidence_fetcher|internal_authority",
      "priority": 10,
      "when": {
        "requires_error_excerpt": false,
        "keywords_any": ["function_name", "package_name"],
        "blocked_types_any": ["api-uncertainty", "version-mismatch"]
      },
      "stop_signals": {
        "confirmed_by_primary_source": true,
        "enough_candidates_to_verify": true
      },
      "budget_overrides": { "max_calls": 3 }
    }
  ]
}
```

To add a new MCP server later:
- Add it to the runtime allowlist (outside this skill).
- Add one provider entry (`tool_glob`, `role`, `priority`, triggers, stop signals) to `toolchain_config`.
Do not change the core workflow.

## Default provider ordering (if caller omits toolchain_config)

1. `mcp__context7__*` (authority source)
   - Use for: API signatures, official examples, breaking changes, migration guides.
   - Trigger when: blocker involves uncertain API usage, version mismatch, or doc uncertainty.
   - Stop when: primary-source excerpt confirms the needed behavior and version.

2. `mcp__web-search-prime__*` (clue source)
   - Use for: recent regressions, platform-specific behavior, new tool usage, common pitfalls.
   - Trigger when: `error_excerpt` includes searchable strings (error codes, exact messages).
   - Stop when: you have candidate links and hypotheses to verify.

3. `mcp__web-reader__*` (evidence fetcher)
   - Use for: converting links into quotable evidence (primary text).
   - Trigger when: you have candidate URLs worth verifying.
   - Stop when: you have enough primary-text evidence pointers for conclusions.

If these tools are unavailable, fall back to local verification: reproduce, inspect versions/lockfiles, locate failing codepaths, and produce a NEEDS list.

## Budget config (overrideable)

If caller did not supply `budget_config`, use:
- `max_tool_calls_total`: 8
- `max_evidence_items`: 6
- `min_independent_sources_high_confidence`: 2
- `timebox_seconds`: 300
- `early_stop_on_confidence`: true

If budget is exhausted:
- Stop research.
- Output best-effort guidance labeled with confidence levels.
- Add open questions plus discriminating next experiments.

## Sink model (declarative, caller-owned)

The caller provides `sinks[]`. Each sink declares:
- what to write: `report_json` and/or `guidance_md`
- where to write: file path (optional; can be "return only")
- how to insert: append or anchor-based insertion

Supported sink types are described in `references/portable-unblock-report.v1.md` (keep the canonical report JSON regardless of sink).

## Supervisor/Worker contract

- Worker: captures a structured blocker record (facts only) and hands it off.
- Supervisor (you): runs this workflow, produces research-backed unblock guidance, and writes the auditable report via sinks.
