---
name: tutti-architecture-review
description: Review tutti git diffs for project structure, layering, module ownership, and duplicate event-center infrastructure by planning focused architecture review tasks, then having the main agent orchestrate sub-agents for only the changed areas.
---

# Tutti Architecture Review

Use this skill when reviewing a `tutti` change or a named module for repository structure, module ownership, or layering compliance. This is a focused architecture review, not a general bug hunt.

## Vocabulary

Use the architecture vocabulary consistently:

- **Module**: anything with an interface and an implementation.
- **Interface**: everything a caller must know to use the module correctly.
- **Implementation**: the code inside a module.
- **Depth**: leverage at the interface; deep modules hide useful behavior behind a small interface.
- **Seam**: where an interface lives.
- **Adapter**: a concrete thing satisfying an interface at a seam.
- **Leverage**: what callers get from depth.
- **Locality**: what maintainers get from depth.

Prefer these words in findings. Avoid vague substitutes such as "component", "service", "utility", or "boundary" when a vocabulary term fits.

## Workflow

1. Resolve the user's review intent:
   - plain `git diff` review for the current change
   - module-focused diff review when the user names a module inside the current change
   - static module review when the user wants a named module inspected even without current diff overlap

   Use light natural-language guidance when the request is ambiguous. Do not force the user through a fixed mode menu.

2. When the user names a module, let the main agent infer a few candidate path keywords and gather candidate paths. Then normalize those paths into a scope file:

   ```bash
   node ./.codex/skills/tutti-architecture-review/scripts/build-review-scope.mjs \
     --input /tmp/tutti-review-candidates.json \
     --output /tmp/tutti-review-scope.json
   ```

   Candidate input is agent-produced. The script does not invent module keywords or search the repository itself; it only normalizes candidate paths into a stable scope contract for the planner.

   Read `references/scope-contract.md` when changing or consuming the candidate input, normalized scope output, or planner scope metadata.

3. Run the review planner from the repository root:

   ```bash
   pnpm review:architecture:package
   ```

   For module-focused review, pass the generated scope file:

   ```bash
   node ./.codex/skills/tutti-architecture-review/scripts/plan-review.mjs \
     --scope-file /tmp/tutti-review-scope.json \
     --format json \
     --output-temp
   ```

   The planner remains `git diff` first. With `--scope-file`, it reviews `scope ∩ diff` when there is overlap, and falls back to scoped-file review only when there is no diff overlap.

   For explicit static module review, force scope-only planning:

   ```bash
   node ./.codex/skills/tutti-architecture-review/scripts/plan-review.mjs \
     --scope-file /tmp/tutti-review-scope.json \
     --scope-mode static-only \
     --format json \
     --output-temp
   ```

4. Read the generated JSON task package from `workflowEntry.packagePath`. Each task includes `riskLevel`, `spawnRecommendation`, `summaryForMainAgent`, `matchedFiles`, `preflightSignals`, and a ready-to-use `prompt`.

5. Spawn `explorer` sub-agents according to `spawnRecommendation`:
   - `required`: spawn unless the user explicitly asked for a narrower review
   - `recommended`: spawn when the review is not trivially small
   - `optional`: the main agent may review locally

   Do not ask sub-agents to edit files. Their job is to inspect the relevant diff and report architecture findings.

6. Continue local work while sub-agents run only if there is non-overlapping review or summarization work. Do not duplicate a sub-agent's assigned scope.

7. Merge sub-agent reports into a code-review style answer:
   - findings first, ordered by severity
   - cite file paths and line numbers when possible
   - explain the violated rule and why it matters for locality, leverage, or dependency direction
   - include "No architecture findings" when a reviewer found no issues

## Reviewer Expectations

Every sub-agent should:

- read `AGENTS.md` and the closest area `AGENTS.md` for its changed files
- read only the reference files listed in the task package, plus files needed to understand the diff
- inspect the relevant git diff directly instead of relying only on file names
- report only actionable architecture issues, not taste preferences
- distinguish hard rule violations from speculative deepening opportunities
- avoid proposing new interfaces unless the changed code already creates pressure for a real seam
- when eventing, pub-sub, or bidirectional coordination appears, check whether the shared business event stream's `global`, `desktop`, or `workspace` scope modules already own the seam before accepting new event-center infrastructure

## Task Planner

The planner is deterministic and repository-local:

- `scripts/plan-review.mjs` reads `git diff`, optional untracked files, and an optional normalized scope file
- `scripts/build-review-scope.mjs` normalizes agent-produced candidate paths into a stable scope contract
- `references/review-rules.json` declares reviewer tasks, path rules, and regex-style preflight signals
- the script maps changed paths to architecture reviewer tasks
- it adds lightweight preflight signals for suspicious imports, generated-contract drift, possible hardcoded copy, and cross-area seams
- it assigns task risk and spawn recommendations for the main agent
- it emits JSON or Markdown for the main agent to orchestrate
- it never starts sub-agents itself

Useful options:

```bash
pnpm review:architecture
pnpm review:architecture:package
pnpm review:architecture:test
node ./.codex/skills/tutti-architecture-review/scripts/plan-review.mjs --format markdown
node ./.codex/skills/tutti-architecture-review/scripts/plan-review.mjs --format summary
node ./.codex/skills/tutti-architecture-review/scripts/plan-review.mjs --base origin/main
node ./.codex/skills/tutti-architecture-review/scripts/plan-review.mjs --staged
node ./.codex/skills/tutti-architecture-review/scripts/plan-review.mjs --no-untracked
node ./.codex/skills/tutti-architecture-review/scripts/plan-review.mjs --scope-file /tmp/tutti-review-scope.json --format summary
node ./.codex/skills/tutti-architecture-review/scripts/plan-review.mjs --scope-file /tmp/tutti-review-scope.json --scope-mode static-only --format summary
node ./.codex/skills/tutti-architecture-review/scripts/plan-review.mjs --task desktop-layering --format markdown
node ./.codex/skills/tutti-architecture-review/scripts/plan-review.mjs --output /tmp/tutti-review-tasks.json
node ./.codex/skills/tutti-architecture-review/scripts/plan-review.mjs --output-temp
node ./.codex/skills/tutti-architecture-review/scripts/plan-review.mjs --from-package /tmp/tutti-review-tasks.json --format markdown
node ./.codex/skills/tutti-architecture-review/scripts/plan-review.mjs --from-package /tmp/tutti-review-tasks.json --task desktop-layering --format summary
```

## Task Package Entry

A task package file is a stable workflow entrypoint. Prefer creating one before spawning sub-agents, especially for large reviews:

```bash
node ./.codex/skills/tutti-architecture-review/scripts/plan-review.mjs --format json --output-temp
```

Then use `workflowEntry.packagePath` as the source of truth for the review. If the conversation resumes later, reload the same package instead of recomputing the plan:

```bash
node ./.codex/skills/tutti-architecture-review/scripts/plan-review.mjs --from-package /tmp/tutti-architecture-review-YYYYMMDDTHHMMSSZ.json --format markdown
```

Use `--format summary` before spawning agents when you need a compact orchestration view. Use `--task <id>` to inspect or rerender one reviewer from either the current diff or an existing task package.

Run the planner self-test after changing task matching, risk rules, output formats, or task-package behavior:

```bash
node --test ./.codex/skills/tutti-architecture-review/scripts/plan-review.test.mjs ./.codex/skills/tutti-architecture-review/scripts/build-review-scope.test.mjs
```

Read `references/tutti-layering.md` when a task needs the compact project rules.
Read `references/scope-contract.md` when changing the scope-file contract or the main-agent handoff around module review.
Read `docs/architecture/business-event-stream.md` when reviewing event-center modules, typed pub-sub, or WebSocket-based product coordination. Do not use the architecture review to enforce generated event-protocol drift; that belongs to `pnpm check:event-protocol-generated`.

Read or edit `references/review-rules.json` when changing:

- reviewer task titles, focus, references, or path matching
- simple preflight regex rules
- task assignment for preflight signals

Keep combination logic in `scripts/plan-review.mjs`, such as cross-cutting trigger reasons, generated-source pairing, risk calculation, spawn recommendations, and output rendering.

Keep module-phrase interpretation in the main agent, not in `build-review-scope.mjs` or `plan-review.mjs`. Those scripts should stay deterministic and repository-local.
