---
name: playwright-vision-low-resource
description: Apply a low-resource operating profile for Playwright MCP + Claude Vision on constrained machines. Use this at session start, before visual QA, or after browser-context/OOM failures. Establishes bounded retries, local-vs-remote execution split, and optimized screenshot/vision practices.
argument-hint: [mode: local-smoke|local-debug|remote-full] [scope: mcp|playwright|vision|all]
user-invocable: true
disable-model-invocation: false
---

# Playwright + Vision Low-Resource Profile

## Purpose

Stabilize browser automation and visual analysis on low-memory environments without sacrificing verification quality.

This skill is **global** (user-level) and intended for reuse across all repositories.

## Trigger conditions

Use this skill when any of the following apply:

- RAM <= 8 GB total
- Repeated error: `Target page, context or browser has been closed`
- VS Code extension host instability or OOM events
- Need reliable visual checks with constrained local resources

## Hard constraints

1. No unbounded retries.
2. Max browser-context retries: **2**.
3. Prefer `workers=1` for local runs.
4. Prefer single-browser project (Chromium) locally.
5. Collect heavy artifacts only on failure/retry.

## Standard operating profile

### 1) Environment preflight (always first)

Run:

- `~/.copilot/skills/playwright-vision-low-resource/scripts/preflight-playwright-mcp.sh`

If available memory is low (< 1.5 GB), do not start headed or multi-worker runs.

### 2) MCP profile (workspace)

For `.vscode/mcp.json` prefer:

- `--headless`
- `--isolated`
- `--no-sandbox`
- bounded `--timeout-navigation` and `--timeout-action`
- file output mode and explicit output dir

Template: `./templates/mcp.low-resource.jsonc`

### 3) Playwright profile (workspace)

For local constrained runs:

- `workers: 1`
- `maxFailures: 1`
- single local project (`chromium`)
- `trace: 'on-first-retry'`
- `video: 'retain-on-failure'`
- `screenshot: 'only-on-failure'`

Template: `./templates/playwright.low-resource.config.ts`

### 4) Vision profile

For Claude vision calls:

- Prefer image long edge <= 1568 px
- Avoid tiny images (< 200 px edge)
- Use 1-3 targeted screenshots per question (not full dumps)
- Prefer viewport/element screenshots over full-page unless layout context is required

### 5) Failure protocol

If browser-context loss occurs twice in a row:

- Stop browser retries
- Switch to deterministic fallback:
  - HTML fetch / DOM inspection
  - targeted CSS/JS edits
  - CI/quality-gate verification
- Mark visual verification as deferred/manual if required

## Mode guidance

- `mode=local-smoke`: fastest, minimal artifacts, single worker
- `mode=local-debug`: still single worker, enable traces/videos on failure
- `mode=remote-full`: run full matrix in remote/CI environment; keep local machine for orchestration only

## Output contract (when invoked)

Return:

1. Current risk classification (`low|medium|high`)
2. Exact profile selected (`local-smoke|local-debug|remote-full`)
3. Minimal file/settings deltas required
4. Verification plan with objective pass/fail checks

## Automation helper

To scaffold low-resource defaults into the current repo:

- `~/.copilot/skills/playwright-vision-low-resource/scripts/apply-workspace-lowram.sh <workspace-path>`

Behavior:

- If `.vscode/mcp.json` exists, it is backed up and a recommended low-resource file is written as `.vscode/mcp.low-resource.recommended.json`.
- If `.vscode/mcp.json` does not exist, it is created from template.
- Creates `playwright.low-resource.config.ts` if missing.

---

## System daemon interop (§6 — Watchdog pause pattern)

### Problem

On machines running a **PSI-aware memory watchdog** (e.g. a `systemd --user` service that monitors VS Code RSS and free-RAM percentage), the watchdog's **RSS acceleration trigger** fires continuously during active VS Code sessions — even when overall free RAM is healthy. It SIGTERMs helper processes (tsserver, extension host workers) every 40–90 s. When Playwright launches Chrome for a ≥60 s automation run, the watchdog SIGTERM hits the browser before the save/verify cycle completes, causing silent or explicit mid-run failures.

**Symptom pattern:**

- Terminal exits with code 0 or non-zero before publish log prints final ✅ lines
- `sq-error-*.png` screenshots show partially-saved state
- `journalctl --user -u mem-watchdog --since "5 min ago"` shows `SIGTERM` events coinciding with Chrome launch

### Diagnosis steps

1. Check watchdog status:
   ```bash
   systemctl --user status mem-watchdog
   ```
2. Confirm ACCEL trigger is firing:
   ```bash
   journalctl --user -u mem-watchdog -n 40 | grep -E "ACCEL|SIGTERM|SIGKILL|RSS"
   ```
3. If ACCEL events appear within 90 s of the publish attempt → watchdog is the cause.

### Solution: stop → run → restart

```bash
# 1. Stop watchdog (safe for ≤5 min publish window)
systemctl --user stop mem-watchdog

# 2. Run automation headless with bundled browser (minimum overhead)
DEPLOY_TARGET=uat USE_SYSTEM_CHROME=0 node scripts/publish-to-squarespace.js

# 3. Restart watchdog immediately after
systemctl --user start mem-watchdog && systemctl --user is-active mem-watchdog
```

**Why it is safe to pause:** The system-level swap (e.g. 16 GB zram on ChromeOS/Crostini) provides OOM protection during the ~60–90 s gap. The watchdog pause is bounded; do not leave it stopped for more than ~5 minutes.

### Hard constraints

- **Never permanently disable** the watchdog — only pause for the automation window.
- Always confirm `is-active mem-watchdog` returns `active` before ending the session.
- Prefer `USE_SYSTEM_CHROME=0` (bundled Chromium) and `HEADED=0` (headless default) to minimise peak RSS during the window.

### Trigger conditions (additions to §§ above)

Also apply this skill when:

- A `systemd --user` memory watchdog is active on the machine
- `journalctl` shows SIGTERM/SIGKILL events near Chrome launch timestamps
- Browser automation exits prematurely with no JS-level error (watchdog kill leaves no in-process trace)

---

## MCP/Vision interoperability findings (§7 — 2026-03 hardening update)

### A) Why Claude Vision text can appear “missing” in tool responses

**Confirmed behavior in VS Code MCP stack:** when a tool returns both `content[].text` and `structuredContent`, model-visible payload handling may prioritize/replace with structured data, causing the natural-language analysis text to be hidden or degraded for agent reasoning.

Reference:

- VS Code issue: https://github.com/microsoft/vscode/issues/290063

**Practical rule:** for LLM-readable analysis tools, keep the primary analysis in `content[].text` and avoid relying on `structuredContent` to carry critical narrative.

### B) `content` array is still required

Even when returning structured data, keep `content` present (empty is allowed by maintainers; non-empty text is preferred for reliability and debugging UX).

Reference:

- VS Code issue: https://github.com/microsoft/vscode/issues/297669

### C) `envFile` semantics in VS Code MCP

`envFile` variables are loaded into the spawned MCP process environment, but `${env:VAR}` substitution in `mcp.json` happens earlier and does **not** read values from `envFile`.

References:

- Feature merged: https://github.com/microsoft/vscode/pull/244059
- Behavior clarification: https://github.com/microsoft/vscode/issues/250074

### D) Playwright browser-closed errors are often host-level kills, not MCP logic bugs

`Target page, context or browser has been closed` is frequently a symptom of external process termination (OOM watchdog / cgroup / host kill). Retry once; if it repeats, treat as infrastructure pressure and apply watchdog pause protocol.

Reference:

- Playwright MCP issue example: https://github.com/microsoft/playwright-mcp/issues/1381

### E) Stable operating sequence for Claude Visualization on low-RAM Linux

1. Stop watchdog:
   - `systemctl --user stop mem-watchdog`
2. Run visual MCP capture/analyze calls (bounded count, targeted scope).
3. Restart watchdog:
   - `systemctl --user start mem-watchdog && systemctl --user is-active mem-watchdog`

Never leave watchdog disabled after verification.

### F) Recommended workspace MCP profile adjustments

- Prefer persistent profile over `--isolated` for iterative debugging:
  - `--user-data-dir <workspace>/.playwright-mcp/profile`
- Keep:
  - `--headless`
  - `--no-sandbox` (Linux containers as needed)
  - bounded navigation/action timeouts
- For vision-analysis MCP servers, include bounded retry (max 2) for browser-closed failures and emit failure text with attempt count.

### G) Required response contract for vision analysis tools

For every analysis tool result, return model-readable text in `content[].text` with:

1. Human-readable verdict
2. Specific UX/readability findings
3. Compact metadata block (model/stop_reason/token counts)

Do not store critical analysis only in `structuredContent`.

---

## Mandatory visual publish gate (§8 — required before publish/deploy sign-off)

For any workflow that changes UX-rendered assets (CSS, page blocks, injection HTML/JS, templates):

1. **Do not declare publish success from DOM checks alone.**
2. Run Claude Vision inspection at least once on the live/UAT URL after publish.
3. Required minimum pass criteria:
   - Hero/primary above-the-fold section is visibly rendered (no blank/collapsed viewport)
   - Primary CTA is visible and legible
   - No major section collapse/missing blocks in first full-page capture
   - No unreadable foreground/background contrast regressions
4. If Vision and DOM checks disagree, treat result as **fail** until reconciled with a second capture.
5. If visual verification cannot be completed (infra instability, browser kill), outcome must be:
   - `publish: unverified`
   - explicit blocker details
   - next verification action

### Required verification evidence block

Every publish-touching task must include:

- URL inspected
- capture mode (`viewport` or `fullPage`)
- Vision verdict (`pass|fail`)
- top defects list (or `none`)

No evidence block → no success claim.

---

## Squarespace LESS safety rules (§9 — compiler-compat guardrail)

When targeting Squarespace custom CSS (LESS-processed pipeline):

1. Do not use CSS custom property `var(...)` inside `transition:` shorthand values.
2. Do not use CSS custom property `var(...)` inside `animation:` shorthand values.
3. Prefer explicit literal timing values in shorthands (e.g. `150ms`, `240ms`).
4. If variables are desired, use them in non-shorthand properties where parser behavior is stable.

### Mandatory compilation health check (post-publish)

After publish, fetch live `site.css` and fail if parse errors are present.

Fail patterns include (case-insensitive):

- `SyntaxError`
- `INCOMPLETE_PARSE`
- `Unable to complete parse`

If any fail pattern appears: rollback/fix CSS and republish before closing the task.
