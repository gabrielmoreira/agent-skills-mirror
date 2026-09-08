# AGENTS.md

This file provides guidance to AI coding agents (pi, Claude Code, Codex, OpenCode, etc.) working in this repository.

## Project Overview

**AI Native PM Agent** — a methodology-driven AI product coach packaged as **95 executable Skills** across an idea-to-production pipeline (P0 needs discovery → P14 aesthetic authority), plus cross-stage combos and a routing orchestrator. This repo is the **canonical source of the skill library**, not a runnable application.

Each stage is an independent skill (a directory with a `SKILL.md`); the orchestrator routes by stage and detects conflicts.

## Repository Layout

```
skills/               # 95 skills, one dir per skill. Naming:
                      #   p*       stage skill (p0, p1, ... p14)
                      #   p<stage><letter>-*  sub-skill (e.g. p0a-micro-needs-detector)
                      #   combo-*  cross-stage combo
orchestrator/SKILL.md # main orchestrator: stage routing + conflict detection
skill-registry.yaml   # authoritative registry (type / status / source_book)
references/           # stage-routing.md, conflict-detection.md, product-context-schema.md
scripts/              # validation & test scripts
install.sh            # one-click installer
README.md / README_CN.md / ARCHITECTURE.md / AUDIT-REPORT-*.md
```

## Commands

```bash
python3 scripts/test_orchestrator.py     # test stage routing
python3 scripts/final_validation.py      # validate skills (frontmatter / structure)
python3 scripts/init_product_context.py  # initialize a product context
bash install.sh                          # install skills into ~/.hermes/skills/
```

## Editing Skills

- Each skill is a directory containing `SKILL.md` (YAML frontmatter + markdown body).
- `skill-registry.yaml` is the authoritative registry — keep it in sync when adding, renaming, or changing a skill's `type` / `status` / `source_book`.
- Follow the existing naming conventions; do not invent new stage ids.
- Keep README.md / README_CN.md in sync for user-facing changes (new skills, stage changes).

## Behavioral Guidelines

Guidelines to reduce common LLM coding mistakes. **Tradeoff:** these bias toward caution over speed — for trivial tasks, use judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it — don't delete it.
- Remove imports/variables/functions that YOUR changes made unused; don't remove pre-existing dead code unless asked.

The test: every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

- "Add validation" → "Write tests for invalid inputs, then make them pass."
- "Fix the bug" → "Write a test that reproduces it, then make it pass."
- "Refactor X" → "Ensure tests pass before and after."

For multi-step tasks, state a brief plan:

```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.
