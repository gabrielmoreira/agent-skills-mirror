---
name: addvalue
description: "Deep-reviews a GitHub repo, local project, CLI, docs, or product for high-leverage bugs, features, UX gaps, and inspiring upgrades—not typo farms. Use when the user says /addvalue, add value, find improvements, or what to build next. Do not use for a /better polish pass, a reproduce-then-fix hunt (bug-hunter), or mass good-first-issue PRs."
---

# /addvalue — Find and ship real value

## Purpose

Review a **target** carefully (remote Git repo, local folder, library, CLI, UI,
docs site, or product surface) and produce a ranked plan of improvements that
actually help users or maintainers. Then optionally implement the top item.

This is **not** “open 20 tiny PRs.” Prefer one hard, reviewable change over many shallow ones.

## Triggers

- `/addvalue [path|owner/repo|.]`
- “add value”, “how can this be improved”, “inspiring updates”, “what should we build”
- Track B contribution hunting when quality > volume

## Partners (optional)

| Partner | When | How |
|---------|------|-----|
| **This agent (default)** | Always | Full review + implement |
| **Ollama Cloud GLM** | User says `/addvalue --ollama` or `/ollama` mid-pass | Load `ollama` skill; one high-reasoning plan call; execute or merge with your plan |
| **Local Ollama** | User says `/addvalue --local` or `/local` | Load local skill; use as second opinion only |
| **agy / agent CLIs** | User names a CLI (`agy`, `hermes`, project scripts) | Prefer project engines over inventing parallel tools; pass paths not huge file dumps |

Paid/cloud partners: honor the user’s **Paid Models — Ask First** rule. `/ollama` is standing approval for one GLM planner call on that turn. Ask before other paid APIs.

## Hard rules

1. **Scope lock** — name the target and one primary outcome before editing.
2. **Read before invent** — README, CONTRIBUTING, AI_POLICY, recent issues/PRs, architecture entrypoints. No drive-by.
3. **Value > vanity** — reject star-farm, typo-only, comment-churn, duplicate open PRs.
4. **Hard + inspirational bar (non-negotiable)** — Prefer work a sharp maintainer would **not** clear in an afternoon. Reject “correct but small” DX/docs/pattern-rebase fixes unless the user explicitly lowers the bar. Winning work should be either:
   - **Hard:** races, protocol/semantics bugs, cross-layer design, subtle correctness with non-obvious tests, or
   - **Inspirational:** a capability users invent workarounds for; something that changes what the tool can do, not just how you debug it.
5. **Human gate for upstream** — for third-party GitHub PRs, stop at draft + `Take OWNER/REPO#N` unless already approved.
6. **Reproduce / accept** — bugs need a failing test or exact repro; features need acceptance checks from issues/docs/users.
7. **Verify with evidence** — project’s own test/lint/build; report commands + exit codes.
8. **No fake done** — ledger or session note: what changed, how verified, what remains.

### Explicit rejects (fail the bar)

- Explain/debug CLIs for existing behavior
- Single-file pattern/rebase fixes with clear recipes
- Good-first-issue labeled work unless it hides a deep bug
- Anything a competent maintainer would ship between meetings
- Competing open PRs / already-assigned maintainer work you cannot uniquely advance

## Workflow

Copy and track:

```
ADDVALUE Progress:
- [ ] 1. Target + intent
- [ ] 2. Map the system
- [ ] 3. Signal scan (issues, users, friction)
- [ ] 4. Opportunity bank + score
- [ ] 5. Pick ONE winner
- [ ] 6. Plan (smallest correct change)
- [ ] 7. Implement + verify (if in scope)
- [ ] 8. Report
```

### 1. Target + intent

Identify:

| Field | Example |
|-------|---------|
| Target | `pypa/hatch`, `~/projects/foo`, `.` |
| Kind | library / app / CLI / docs / monorepo / playbook |
| Intent | contribute upstream / improve own product / invent roadmap |
| Constraint | max 1 PR, no UI, Windows-only, etc. |

If target missing, default to **current workspace root**.

### 2. Map the system

Spend tokens on structure, not trivia:

- Entry points (CLI, `main`, routes, `pyproject` scripts)
- Core domain modules (where value lives)
- Test/verify path (`hatch test`, `pytest`, `npm test`, …)
- Contribution/AI policy if present
- Recent release notes / changelog tone

For remote repos: `gh repo view`, `gh issue list`, `gh pr list`, clone only when implementing.

For **local / non-git** projects: same mapping via filesystem + run scripts; VCS optional.

### 3. Signal scan

Gather friction from:

- Open issues (bugs **and** enhancements; “help wanted”; milestone)
- Closed-but-painful issues / “won’t fix” that aging may reopen
- Docs vs reality (README steps that fail)
- Error paths, Windows/macOS gaps, silent failures
- Competitor / sibling tools (what users already expect)
- Your own dry-run of the happy path

Optional partner pass: ask Ollama Cloud (`/ollama`) for a **ranked opportunity list** given only paths + issue titles (not full dumps).

### 4. Opportunity bank + score

Write 5–12 candidates. Score each 1–5 on:

| Axis | High score means |
|------|------------------|
| **User impact** | Pain or desire is real and frequent |
| **Leverage** | One change unlocks many workflows |
| **Fit** | Matches project style and maintainer taste |
| **Feasibility** | Clear repro/acceptance; you can verify |
| **Novelty** | Not already PR’d / not trivial |
| **Hardness** | Would take a sharp maintainer >1 day, or needs deep domain/design |
| **Inspiration** | Users will say “finally” — new capability, not polish |
| **Risk** | (invert) low chance of breaking core contracts |

**Winner score** = impact + leverage + fit + feasibility + novelty + hardness + inspiration − risk.

**Floor:** reject candidates with hardness < 4 **and** inspiration < 4 unless the user asked for a small win.

Discard: duplicates of open PRs, policy violations, scope bombs, “rewrite the world.”

### 5. Pick ONE winner

State in one paragraph:

- Problem / missing capability
- Who benefits
- Why this beats the runners-up
- Out of scope for this pass

### 6. Plan

Minimum plan:

1. Repro or acceptance checks
2. Files likely touched
3. Smallest design that matches existing patterns
4. Verify commands
5. Upstream gate (if any)

Use Plan mode when trade-offs are large; otherwise implement.

### 7. Implement

- Smallest diff; match project style
- Tests first when fixing bugs
- No `Co-authored-by` LLM on third-party PRs
- Disclose AI if the project’s CONTRIBUTING requires it
- Stop before `gh pr create` unless user said `Take OWNER/REPO#N`

### 8. Report

```markdown
## ADDVALUE: <target>

**Winner:** <title> (<issue/url or local>)
**Why:** <one line>

### Also considered
- ...

### Done / next
- Implemented: ...
- Verified: `<cmd>` → exit N
- Blocked / gate: ...
```

## Domains the review must consider

Do not only hunt bugs. Explicitly scan:

| Lens | Questions |
|------|-----------|
| **Correctness** | Silent data loss? Wrong defaults? Race? |
| **Features** | What’s half-built? What’s documented but missing? |
| **UX / DX** | Confusing errors? Missing `--help` examples? Slow feedback? |
| **Perf** | Hot paths? Accidental O(n²)? |
| **Security / safety** | Trust boundaries? Path traversal? Secret leakage? |
| **Platform** | Windows path/newline/env gaps? |
| **Docs** | Lies, missing recipes, no migration notes |
| **Inspiration** | What would make a power user say “finally”? |

## Anti-patterns

- Mass AI PRs / typo farms / readme churn for graph greens
- Picking an issue that already has an active PR
- “Improvements” that fight the maintainer’s stated design
- Partner model dumps that you paste as the PR body unread
- Claiming value without verify evidence
- Opening a third upstream PR while two are already waiting (unless user overrides)

## Compose with other modes

| Need | Use |
|------|-----|
| Contract before multi-session work | `/goal` |
| Autonomous until criteria | `/goal-loop` |
| Quality polish after implement | `/better` |
| Many unique variants | `/scale` |
| Cloud planner partner | `/ollama` inside or after `/addvalue` |
| Recurring re-scan | `/loop 1d /addvalue .` |

## Progressive disclosure

- Scoring templates + output schemas → [reference.md](reference.md)
- Worked examples → [examples.md](examples.md)

## Installation paths

- Skill: this folder's `SKILL.md`
- Command: optional `/addvalue` command file in the host agent
