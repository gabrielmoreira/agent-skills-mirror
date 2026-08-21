---
name: ai-loop
description: Runs a bounded Spec-Build-Review cycle with an iteration budget, recorded verification commands, and human approval gates. Use when an isolated feature needs a full build from scratch or a heavy modification with checkable requirements. Not for open-ended architecture refactors, /goal contracts, or work whose tests depend on missing credentials.
version: 1.0.1
category: workflow
risk: safe
source: community
date_added: "2026-06-27"
tags: [agent-workflow, specification, implementation, review, verification, feedback-loop]
tools: [claude, cursor, codex, gemini]
---

# AI-Loop Skill

## Overview

The `ai-loop` skill structures a bounded development cycle for agentic workflows. It divides work into three explicit phases — **Spec**, **Build**, **Review** — and loops between Build and Review until every requirement passes verification, a stop condition is reached, or human approval is needed.

Before invoking the loop, the agent must define and record:

- **Iteration budget**: maximum number of Build→Review cycles (default: 3).
- **Verification evidence**: the exact commands or manual checks that count as proof.
- **Approval gates**: any action requiring explicit human sign-off (destructive commands, production changes, external service writes, credential changes, broad architectural pivots).

## When to Use

- A feature needs to be built from scratch or heavily modified, and the agent should own the full lifecycle (specification, implementation, verification) inside one bounded workflow.
- The work targets an isolated component, module, or feature with well-defined scope and constraints.
- The user asks for a complete development pass and there are clear success criteria, a reasonable verification path, and no unresolved safety or product decisions.

Do **not** use for open-ended architectural refactoring, security-sensitive changes, or work where verification depends on unavailable credentials or systems — stop instead.

## Prerequisites

- A working directory where `specs/` can be created (PowerShell: `New-Item -ItemType Directory -Path specs -Force`).
- Verification commands that can actually run in the current environment (tests, linters, type-checkers, build scripts).
- Sufficient user context available during the Spec phase to pin down requirements.

## Procedure

### 0. Pre-Loop Setup

1. Confirm the feature name with the user. Use a kebab-case `<feature-name>` for file paths.
2. Create the specs directory if it does not exist:
   ```powershell
   New-Item -ItemType Directory -Path specs -Force
   ```
3. Agree on and record the iteration budget, verification commands, and approval gates before any design discussion.

### Phase 1: Spec (Planning)

1. Interview the user about the feature. Ask **one focused question at a time** until the goal, must-have requirements, constraints, and definition of done are clear.
2. **Do not start building yet.**
3. Write a detailed specification and save it to `specs/<feature-name>.md`.
4. The spec must include:
   - The objective.
   - The exact requirements (numbered or bulleted, individually checkable).
   - Edge cases to handle.
   - A concrete definition of done that someone could check the build against.
   - The iteration budget.
   - The verification commands or manual checks.
   - The approval gates (destructive ops, production changes, external writes, credential changes, architectural pivots).

### Phase 2: Build (Implementation)

1. Read the spec at `specs/<feature-name>.md`.
2. Build **exactly** what it describes.
3. **Do not add features.** Do not refactor unrelated code. Do not invent requirements not in the spec.
4. After implementing, list which spec requirements you covered so the Review phase can check them.

### Phase 3: Review (Verification)

1. Compare the implementation against `specs/<feature-name>.md`.
2. Go requirement by requirement and verify whether each was met. List every gap, bug, or missing piece, naming the **exact spec item** each failure maps to.
3. Run the declared verification commands and record their output as evidence.
4. If anything fails and the iteration budget is **not exhausted**, write the specific fixes needed and **loop back to Phase 2 (Build)**.
5. **Stop and ask for human input** when the next fix would:
   - Change the spec.
   - Exceed the iteration budget.
   - Require risky operations (destructive, production, credentialed, externally visible).
   - Depend on product decisions not captured in the spec.
6. Only conclude the skill when **every** requirement in the spec is fully met and the declared verification evidence has passed.

## Examples

### Example: Basic Statistics Helper

**User:**
> I want to add a utility for calculating basic statistics (mean, median, mode) of an array of numbers.

**Agent (Phase 1 - Spec):**
> I can help with that. To get started, what programming language should this statistics calculator be implemented in? Also, how should empty arrays or invalid inputs be handled?

**User:**
> JavaScript. If the array is empty, return null. If there are non-numbers, ignore them.

**Agent (Phase 1 - Spec):**
> Thank you. I have created the specification file at `specs/stats-calculator.md` with the requirements we discussed. Now, I will start implementing it.

**Agent (Phase 2 - Build):**
> *(Creates `stats_calculator.js` and implements `mean`, `median`, and `mode` matching the spec exactly)*
> I have finished implementing the calculator. I will now verify the implementation.

**Agent (Phase 3 - Review):**
> Checking implementation against `specs/stats-calculator.md`:
> - Requirement: mean calculation -> PASS
> - Requirement: median calculation -> PASS
> - Requirement: mode calculation -> PASS
> - Requirement: empty array returns null -> PASS
> - Requirement: non-numbers are ignored -> FAIL (`mode` doesn't filter out non-numbers).
>
> I will now loop back to Phase 2 to fix the `mode` function.

**Agent (Phase 2 - Build Loop-Back):**
> *(Fixes `mode` to filter out non-numbers)*
> I have updated the implementation. Let's re-verify.

**Agent (Phase 3 - Review):**
> - Requirement: mode filters non-numbers -> PASS
>
> All requirements passed! The statistics calculator is complete and verified.

## Pitfalls

- **Problem:** Agent tries to build a huge system all at once, leading to an overcomplicated spec and incomplete implementation.
  **Solution:** Keep `ai-loop` scope to small, modular features. Break larger systems into multiple independent loops.
- **Problem:** Spec is vague, causing the Build phase to rely on assumptions.
  **Solution:** Spend extra time in Spec asking targeted questions one at a time. Do not proceed to Build until every requirement is individually checkable.
- **Problem:** Agent keeps retrying the same failing fix without progress.
  **Solution:** Do not repeat the same fix without new evidence or a changed approach. If the budget is exhausted, stop and report exactly what remains.
- **Problem:** Agent adds extra features or unrelated refactors during Build.
  **Solution:** Build strictly to the spec. Any addition requires a spec update and re-approval.
- **Problem:** Review passes without running verification commands.
  **Solution:** Review must execute the declared verification commands and record output. Self-assessment alone is insufficient for critical systems.
- **Problem:** Hardcoded secrets leak into code or specs.
  **Solution:** Never add secrets, keys, or credentials to code or specs. Use `YOUR_KEY` placeholders and environment variables.

## Verification

Confirm the loop completed correctly with these checks:

1. Spec file exists and is complete:
   ```powershell
   Test-Path specs\<feature-name>.md
   ```
   Expected output: `True`

2. Spec contains all required sections:
   ```powershell
   Select-String -Path specs\<feature-name>.md -Pattern "objective","requirements","definition of done","iteration budget","verification","approval"
   ```
   Expected: matches for each pattern.

3. Run the declared verification commands from the spec (e.g., tests, linters):
   ```powershell
   npm test
   ```
   Expected: all tests pass with exit code `0`.

4. Review log covers every numbered requirement:
   - Each requirement in `specs/<feature-name>.md` has an explicit PASS or FAIL entry.
   - Any FAIL was either fixed in a subsequent Build loop-back or escalated to the user with a stop reason.

5. No unapproved risky actions were taken:
   - No destructive commands, production deploys, external writes, or credential changes executed without explicit human approval.

## Security & Safety Notes

- Run and test Build-phase code in a safe, sandboxed environment.
- Do not execute arbitrary shell commands provided directly by the user without validating their safety.
- Never add hardcoded secrets, keys, or credentials to code or specifications. Use `YOUR_KEY` placeholders.
- Treat production deploys, data migrations, payment flows, credential changes, and external write actions as approval-gated work.
- Stop rather than continue if requirements conflict, tests cannot run, or verification depends on unavailable credentials or systems.

## Related Skills

- `@plan-writing` — For writing more detailed implementation plans for larger projects.
- `@ask-questions-if-underspecified` — For standard guidelines on interviewing the user.
